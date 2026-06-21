"""
Doc2ImageConverter v4.0 — Termux
Converte DOCX e PDF para PNG ou JPG
- PDF: converte localmente via Poppler (offline)
- DOCX: converte via API gratuita online (requer internet)
- Modos: pagina unica, todas as paginas, intervalo de paginas

Requer: pkg install poppler python
        pip install pdf2image Pillow pypdf requests
"""
import os, sys, shutil, tempfile, time
from pathlib import Path
from datetime import datetime

# ── Instalar dependências ──────────────────────────────────────────────────
for modulo, pacote in [
    ("pdf2image","pdf2image"),
    ("PIL","Pillow"),
    ("pypdf","pypdf"),
    ("requests","requests")
]:
    try:
        __import__(modulo)
    except ImportError:
        print(f"Instalando {pacote}...")
        os.system(f"pip install {pacote}")

from pdf2image import convert_from_path
import pypdf, requests

# ══════════════════════════════════════════════════════════════════════════════
# CONVERSÃO DOCX → PDF via API online gratuita (CloudConvert)
# Crie sua chave GRATUITA em: https://cloudconvert.com/register
# Plano gratuito: 25 conversões/dia
# ══════════════════════════════════════════════════════════════════════════════
CLOUDCONVERT_API_KEY = "sua chave cloudconvert.com aqui" # Cole sua chave aqui após cadastro


# ── CloudConvert: DOCX → PDF ───────────────────────────────────────────────
def docx_para_pdf_api(caminho_docx, pasta_temp):
    if not CLOUDCONVERT_API_KEY:
        raise ValueError(
            "Chave da API nao configurada!\n"
            "1. Acesse: https://cloudconvert.com/register\n"
            "2. Crie uma conta gratuita (25 conversoes/dia)\n"
            "3. Va em: Dashboard > API Keys > Create API Key\n"
            "4. Cole a chave no topo deste arquivo em CLOUDCONVERT_API_KEY"
        )

    headers = {
        "Authorization": f"Bearer {CLOUDCONVERT_API_KEY}",
        "Content-Type": "application/json"
    }
    base_url = "https://api.cloudconvert.com/v2"

    print("Enviando arquivo para conversao online...")

    job_data = {
        "tasks": {
            "upload-file":  { "operation": "import/upload" },
            "convert-file": { "operation": "convert", "input": "upload-file",
                              "input_format": "docx", "output_format": "pdf" },
            "export-file":  { "operation": "export/url", "input": "convert-file" }
        }
    }

    resp = requests.post(f"{base_url}/jobs", json=job_data, headers=headers, timeout=30)
    if resp.status_code != 201:
        raise RuntimeError(f"Erro ao criar job: {resp.status_code} {resp.text[:200]}")

    job    = resp.json()["data"]
    job_id = job["id"]

    upload_task   = next(t for t in job["tasks"] if t["name"] == "upload-file")
    upload_url    = upload_task["result"]["form"]["url"]
    upload_params = upload_task["result"]["form"]["parameters"]

    with open(caminho_docx, "rb") as f:
        resp2 = requests.post(upload_url, data=upload_params,
                              files={"file": (Path(caminho_docx).name, f)}, timeout=60)
    if resp2.status_code not in (200, 201, 204):
        raise RuntimeError(f"Erro no upload: {resp2.status_code}")

    print("Arquivo enviado. Aguardando conversao...")
    for _ in range(30):
        time.sleep(2)
        resp3      = requests.get(f"{base_url}/jobs/{job_id}", headers=headers, timeout=15)
        job_status = resp3.json()["data"]
        status     = job_status["status"]
        print(f"  Status: {status}...", end="\r")
        if status == "finished":
            break
        elif status == "error":
            raise RuntimeError("Erro na conversao pela API.")
    print()

    export_task  = next(t for t in job_status["tasks"] if t["name"] == "export-file")
    download_url = export_task["result"]["files"][0]["url"]

    print("Baixando PDF convertido...")
    pdf_path = pasta_temp / (Path(caminho_docx).stem + ".pdf")
    resp4 = requests.get(download_url, timeout=60, stream=True)
    with open(pdf_path, "wb") as f:
        for chunk in resp4.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"PDF baixado: {pdf_path.stat().st_size // 1024} KB")
    return pdf_path


def docx_para_pdf_local(caminho_docx, pasta_temp):
    lo = next((c for c in ["libreoffice","soffice","/usr/bin/libreoffice"]
               if shutil.which(c)), None)
    if not lo:
        return None
    import subprocess
    subprocess.run([lo, "--headless", "--convert-to", "pdf",
                    "--outdir", str(pasta_temp), str(caminho_docx)],
                   capture_output=True, text=True, timeout=120)
    pdf_path = pasta_temp / (Path(caminho_docx).stem + ".pdf")
    return pdf_path if pdf_path.exists() else None


# ── Selecionar intervalo de páginas ───────────────────────────────────────
def selecionar_paginas(total):
    """
    Retorna uma lista de números de página baseada na escolha do usuário.
    Modos: página única, todas, intervalo (ex: 2-8)
    """
    if total == 1:
        return [1]

    print(f"\nDocumento com {total} pagina(s). Quais deseja converter?")
    print("  1. Pagina unica")
    print("  2. Todas as paginas")
    print("  3. Intervalo de paginas (ex: 2-8)")
    op = input("> ").strip()

    if op == "1":
        print(f"Qual pagina? [1-{total}]:")
        p = input("> ").strip()
        num = int(p) if p.isdigit() else 1
        num = max(1, min(num, total))
        return [num]

    elif op == "2":
        return list(range(1, total + 1))

    elif op == "3":
        while True:
            print(f"Digite o intervalo (ex: 2-8) [1-{total}]:")
            intervalo = input("> ").strip()
            try:
                partes = intervalo.split("-")
                inicio = int(partes[0].strip())
                fim    = int(partes[1].strip())
                if inicio < 1 or fim > total or inicio > fim:
                    print(f"Intervalo invalido. Use valores entre 1 e {total}.")
                    continue
                return list(range(inicio, fim + 1))
            except (ValueError, IndexError):
                print("Formato invalido. Use: inicio-fim (ex: 2-8)")

    else:
        # Padrão: página 1
        return [1]


# ── Converter lista de páginas ─────────────────────────────────────────────
def converter_paginas(caminho_pdf, paginas, dpi, formato, pasta_saida, stem):
    """Converte uma lista de páginas e retorna resumo dos arquivos gerados."""
    total_doc = len(pypdf.PdfReader(str(caminho_pdf)).pages)
    ext       = "jpg" if formato == "JPG" else "png"
    gerados   = []
    erros     = []

    total_pags = len(paginas)
    print(f"\nConvertendo {total_pags} pagina(s) em {dpi} DPI...\n")

    for i, num_pag in enumerate(paginas, 1):
        if num_pag < 1 or num_pag > total_doc:
            erros.append(f"Pagina {num_pag} invalida (documento tem {total_doc})")
            continue

        try:
            print(f"  [{i}/{total_pags}] Pagina {num_pag}...", end=" ")

            imgs = convert_from_path(
                str(caminho_pdf), dpi=dpi,
                first_page=num_pag, last_page=num_pag)

            img   = imgs[0]
            ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
            saida = pasta_saida / f"{stem}_pag{num_pag:03d}_{ts}.{ext}"

            if formato == "JPG":
                img.convert("RGB").save(str(saida), "JPEG", quality=95)
            else:
                img.save(str(saida), "PNG")

            kb = os.path.getsize(str(saida)) // 1024
            print(f"OK ({img.size[0]}x{img.size[1]}px, {kb} KB)")
            gerados.append(saida)

        except Exception as e:
            print(f"ERRO: {e}")
            erros.append(f"Pagina {num_pag}: {e}")

    return gerados, erros


# ── Interface principal ────────────────────────────────────────────────────
def main():
    print("\n╔══════════════════════════════════════╗")
    print("║      Doc2ImageConverter v4.0 — Termux           ║")
    print("║  Converte DOCX e PDF para PNG/JPG    ║")
    print("║  Suporte a pagina unica, todas       ║")
    print("║  as paginas e intervalo de paginas   ║")
    print("╚══════════════════════════════════════╝\n")

    if not shutil.which("pdftoppm"):
        print("ERRO: Poppler nao instalado.")
        print("Execute: pkg install poppler")
        sys.exit(1)

    tem_lo  = any(shutil.which(c) for c in ["libreoffice","soffice"])
    tem_api = bool(CLOUDCONVERT_API_KEY)

    print("Ferramentas:")
    print(f"  ✓ Poppler (PDF → imagem)")
    print(f"  {'✓' if tem_lo  else '✗'} LibreOffice local")
    print(f"  {'✓' if tem_api else '✗'} CloudConvert API")

    if not tem_lo and not tem_api:
        print("\n  Para DOCX: cadastre-se em cloudconvert.com")
        print("  e cole sua chave em CLOUDCONVERT_API_KEY\n")

    while True:
        # ── Selecionar arquivo ─────────────────────────────────────────────
        print("\nCaminho do arquivo:")
        print("  PDF:  /sdcard/Download/arquivo.pdf")
        print("  DOCX: /sdcard/Download/documento.docx")
        caminho = input("> ").strip().strip('"').strip("'")
        p = Path(caminho)

        if not p.exists():
            print(f"Arquivo nao encontrado: {caminho}")
            continue

        ext_arq = p.suffix.lower()
        if ext_arq not in (".pdf", ".docx"):
            print("Use apenas .pdf ou .docx")
            continue

        # ── DOCX → PDF ────────────────────────────────────────────────────
        pasta_temp  = None
        caminho_pdf = p

        if ext_arq == ".docx":
            pasta_temp = Path(tempfile.mkdtemp())
            try:
                pdf_local = docx_para_pdf_local(p, pasta_temp)
                if pdf_local:
                    print("Convertido via LibreOffice local.")
                    caminho_pdf = pdf_local
                elif tem_api:
                    caminho_pdf = docx_para_pdf_api(p, pasta_temp)
                else:
                    print("Nao foi possivel converter o DOCX.")
                    print("Configure CLOUDCONVERT_API_KEY ou exporte para PDF no Word.")
                    shutil.rmtree(pasta_temp, ignore_errors=True)
                    continue
            except Exception as e:
                print(f"Erro: {e}")
                shutil.rmtree(pasta_temp, ignore_errors=True)
                continue

        # ── Contar páginas ─────────────────────────────────────────────────
        try:
            total_pags = len(pypdf.PdfReader(str(caminho_pdf)).pages)
        except Exception as e:
            print(f"Erro ao ler documento: {e}")
            if pasta_temp:
                shutil.rmtree(pasta_temp, ignore_errors=True)
            continue

        # ── Selecionar páginas ─────────────────────────────────────────────
        paginas = selecionar_paginas(total_pags)
        print(f"Paginas selecionadas: {len(paginas)} "
              f"({'pag '+str(paginas[0]) if len(paginas)==1 else str(paginas[0])+'-'+str(paginas[-1])})")

        # ── Formato ────────────────────────────────────────────────────────
        print("\nFormato:\n  1. PNG (recomendado)\n  2. JPG")
        formato = "JPG" if input("> ").strip() == "2" else "PNG"

        # ── DPI ────────────────────────────────────────────────────────────
        print("\nQualidade:\n  1. 150 DPI\n  2. 300 DPI (recomendado)\n  3. 600 DPI")
        dpi = {"1":150,"2":300,"3":600}.get(input("> ").strip(), 300)

        # ── Pasta de saída ─────────────────────────────────────────────────
        pasta = Path("/sdcard/Pictures/Doc2ImageConverter")
        try:
            pasta.mkdir(parents=True, exist_ok=True)
        except Exception:
            pasta = Path.home() / "Doc2ImageConverter"
            pasta.mkdir(parents=True, exist_ok=True)

        # ── Converter ─────────────────────────────────────────────────────
        try:
            gerados, erros = converter_paginas(
                caminho_pdf, paginas, dpi, formato, pasta, p.stem)

            print(f"\n{'='*40}")
            print(f"✓ Concluido: {len(gerados)} imagem(ns) gerada(s)")
            if erros:
                print(f"✗ Erros: {len(erros)}")
                for e in erros:
                    print(f"  - {e}")
            print(f"Pasta: {pasta}")

        except Exception as e:
            print(f"Erro: {e}")
        finally:
            if pasta_temp:
                shutil.rmtree(pasta_temp, ignore_errors=True)

        print("\n1=Converter outro  2=Sair")
        if input("> ").strip() != "1":
            break

    print("\nAte logo!\n")

if __name__ == "__main__":
    main()