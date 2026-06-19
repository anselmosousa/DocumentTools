# Doc2ImageConverter

> Converte páginas de documentos PDF e DOCX em imagens PNG ou JPG com fidelidade pixel a pixel ao documento original, funcionando nativamente em dispositivos Android via Termux.

<p align="center">
  <img src="docs/icon.png" width="110" alt="Doc2ImageConverter"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Poppler-26.x-orange"/>
  <img src="https://img.shields.io/badge/Pillow-12.x-blueviolet"/>
  <img src="https://img.shields.io/badge/Android-Termux-black?logo=android"/>
  <img src="https://img.shields.io/badge/Versão-4.0-brightgreen"/>
  <img src="https://img.shields.io/badge/License-AGPL--3.0%20%2B%20Commercial-blue"/>
</p>

---

## Índice

- [Visão Geral](#visão-geral)
- [Demonstração](#demonstração)
- [Funcionalidades](#funcionalidades)
- [Arquitetura e Decisões Técnicas](#arquitetura-e-decisões-técnicas)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Modos de Conversão](#modos-de-conversão)
- [Estrutura do Código](#estrutura-do-código)
- [Histórico de Versões](#histórico-de-versões)
- [Desafios Técnicos](#desafios-técnicos)
- [Roadmap](#roadmap)
- [Licença](#licença)

---

## Visão Geral

O **Doc2ImageConverter** surgiu da necessidade de converter documentos PDF e Word em imagens de alta qualidade diretamente no celular, sem depender de computadores ou aplicativos pagos. O projeto evoluiu por 12 versões iterativas, cada uma superando um desafio técnico específico relacionado à estrutura interna do formato PDF.

O resultado é uma ferramenta de linha de comando simples, leve e poderosa que processa documentos localmente (offline) para PDFs e, opcionalmente, usa a API do CloudConvert para arquivos DOCX.

### Casos de Uso

- Converter folhas de fotos (ex: fotos 3x4) de PDF para PNG para envio digital
- Arquivar documentos como imagens para portfólios e galerias
- Pré-processamento de imagens para pipelines de OCR e visão computacional
- Geração de thumbnails e previews de documentos
- Impressão digital via aplicativos que aceitam apenas imagens

---

## Demonstração

```
╔══════════════════════════════════════╗
║      Doc2ImageConverter v4.0         ║
║  Converte DOCX e PDF para PNG/JPG    ║
╚══════════════════════════════════════╝

Ferramentas:
  ✓ Poppler (PDF → imagem)
  ✓ CloudConvert API (DOCX → PDF online)

Caminho do arquivo:
  PDF:  /sdcard/Download/arquivo.pdf
  DOCX: /sdcard/Download/documento.docx
> /sdcard/Download/fotos_3x4.pdf

Documento com 2 pagina(s). Quais deseja converter?
  1. Pagina unica
  2. Todas as paginas
  3. Intervalo de paginas (ex: 2-8)
> 1

Qual pagina? [1-2]: 1

Formato:
  1. PNG (recomendado)
  2. JPG
> 1

Qualidade:
  1. 150 DPI
  2. 300 DPI (recomendado)
  3. 600 DPI
> 2

Convertendo 1 pagina(s) em 300 DPI...

  [1/1] Pagina 1... OK (2481x3509px, 2840 KB)

========================================
✓ Concluido: 1 imagem(ns) gerada(s)
Pasta: /sdcard/Pictures/Doc2ImageConverter
```

### Entrada vs. Saída

| Entrada | Saída |
|:---:|:---:|
| PDF A4 com grade de fotos 3×4 | PNG 2481×3509px, 300 DPI, 2,8 MB |
| DOCX com layout complexo | PNG pixel a pixel idêntico ao original |

---

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| **PDF → PNG/JPG** | Renderização local via Poppler, offline, sem limite de uso |
| **DOCX → PNG/JPG** | Conversão via CloudConvert API (25 conv./dia grátis) |
| **Página única** | Converte uma página específica escolhida pelo usuário |
| **Todas as páginas** | Converte todas as páginas em sequência, gerando um arquivo por página |
| **Intervalo de páginas** | Converte um intervalo definido (ex: páginas 3 a 15) |
| **Qualidade configurável** | 150 DPI (tela), 300 DPI (impressão), 600 DPI (arquivo) |
| **Fidelidade total** | Resultado pixel a pixel idêntico ao documento original |
| **Nomenclatura automática** | Arquivos nomeados com página e timestamp (ex: `doc_pag001_20260610.png`) |
| **Detecção de ferramentas** | Detecta automaticamente LibreOffice local e API disponível |
| **Limpeza automática** | Remove arquivos temporários após cada conversão |

---

## Arquitetura e Decisões Técnicas

### Pipeline de Conversão

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Arquivo    │     │  Intermediário   │     │  Imagem Final   │
│  de Entrada │────▶│  PDF             │────▶│  PNG / JPG      │
└─────────────┘     └──────────────────┘     └─────────────────┘
     │                      ▲
     │ .pdf                 │ LibreOffice (local)
     │ .docx ───────────────┘ CloudConvert API (nuvem)
```

### Por que Poppler e não pypdf para renderização?

Durante o desenvolvimento, foram testadas três abordagens para renderizar páginas de PDF:

| Abordagem | Resultado | Problema |
|---|---|---|
| `pypdf` + extração manual de XObjects | Parcial | Não renderiza vetores, textos, transparências |
| `pymupdf` (fitz) | Perfeito | Não compilável em Android ARM64 |
| `pdftoppm` via Poppler | **Perfeito** | ✓ Disponível no Termux |

O Poppler é um renderizador PDF completo que interpreta todos os operadores do formato ISO 32000, produzindo resultado idêntico ao visualizador de PDF.

### Análise da Estrutura Interna do PDF

Durante o desenvolvimento, foi necessário analisar manualmente o content stream de PDFs gerados pelo Microsoft Word para entender como as imagens e linhas de corte eram codificadas. Foram identificados três padrões distintos:

**1. Imagens reais (XObjects com dimensão ≥ 10×10px):**
```
85 0 0 113.33 18.875 713.92 cm
/Image54 Do
```

**2. Linhas de corte como pixels esticados (XObjects com dimensão < 10px):**
```
0.5 0 0 114.05 14.25 26.0 cm
/Image34 Do
```

**3. Linhas de borda como retângulos preenchidos (operadores `re` + `f*`):**
```
14.75 25.5 94.05 0.5 re
f*
```

A conversão de coordenadas entre o sistema PDF (Y cresce para cima) e o sistema de imagens digitais (Y cresce para baixo) exigiu a fórmula:

```python
y_pixel = int((altura_pagina_pts - y_pdf - altura_objeto) * escala)
```

### Cálculo de DPI e Escala

O formato PDF usa pontos tipográficos como unidade interna (72 pt = 1 polegada). A conversão para pixels usa:

```python
escala  = dpi / 72          # Ex: 300 DPI → escala = 4.167
w_pixel = int(w_pts * escala)
h_pixel = int(h_pts * escala)
```

Uma página A4 (595 × 842 pt) a 300 DPI resulta em **2480 × 3508 pixels**.

---

## Instalação

### Android — Termux (recomendado)

```bash
# 1. Instalar dependências do sistema
pkg install python poppler git

# 2. Permitir acesso ao armazenamento
termux-setup-storage

# 3. Instalar dependências Python
pip install pdf2image Pillow pypdf requests

# 4. Clonar o repositório
git clone https://github.com/anselmosousa/DocumentTools.git
cd DocumentTools/Doc2ImageConverter/src
```

### Linux (Ubuntu/Debian)

```bash
sudo apt install python3 python3-pip poppler-utils
pip install pdf2image Pillow pypdf requests
git clone https://github.com/anselmosousa/DocumentTools.git
```

### macOS

```bash
brew install poppler python
pip install pdf2image Pillow pypdf requests
git clone https://github.com/anselmosousa/DocumentTools.git
```

### Configuração do CloudConvert (para DOCX)

Para converter arquivos DOCX, é necessária uma chave de API gratuita do CloudConvert (25 conversões/dia):

1. Cadastre-se em [cloudconvert.com](https://cloudconvert.com/register)
2. Acesse: `Dashboard > API Keys > Create New API Key`
3. Escopos necessários: `task.read` e `task.write`
4. Configure no arquivo:

```bash
# No Termux, substitua a chave no arquivo
sed -i 's/CLOUDCONVERT_API_KEY = ""/CLOUDCONVERT_API_KEY = "sua_chave"/' src/doc2img.py
```

---

## Como Usar

```bash
python src/doc2img.py
```

O programa exibe um menu interativo no terminal. Siga as instruções fornecidas.

---

## Modos de Conversão

### Modo 1 — Página Única

Converte uma página específica do documento.

```
Documento com 10 pagina(s). Quais deseja converter?
  1. Pagina unica        ← selecione
  2. Todas as paginas
  3. Intervalo de paginas
> 1
Qual pagina? [1-10]: 5
```

**Saída:** `documento_pag005_20260610_143022.png`

---

### Modo 2 — Todas as Páginas

Converte todas as páginas em sequência.

```
Documento com 10 pagina(s). Quais deseja converter?
  1. Pagina unica
  2. Todas as paginas    ← selecione
  3. Intervalo de paginas
> 2
```

**Saída:**
```
documento_pag001_20260610_143022.png
documento_pag002_20260610_143023.png
...
documento_pag010_20260610_143031.png
```

---

### Modo 3 — Intervalo de Páginas

Converte um intervalo definido.

```
Documento com 20 pagina(s). Quais deseja converter?
  1. Pagina unica
  2. Todas as paginas
  3. Intervalo de paginas  ← selecione
> 3
Digite o intervalo (ex: 2-8) [1-20]: 3-7
```

**Saída:**
```
documento_pag003_20260610_143022.png
documento_pag004_20260610_143023.png
...
documento_pag007_20260610_143026.png
```

---

## Estrutura do Código

```
Doc2ImageConverter/
├── src/
│   └── doc2img.py              # Código principal
├── docs/
│   ├── icon.png                # Ícone do projeto
│   └── guia_codigo.docx        # Guia explicativo do código
├── examples/
│   ├── input_sample.pdf        # PDF de exemplo
│   └── output_sample.png       # PNG gerado de exemplo
└── README.md                   # Este arquivo
```

### Funções principais

| Função | Responsabilidade |
|---|---|
| `main()` | Loop principal de interação com o usuário |
| `selecionar_paginas(total)` | Menu de seleção: única / todas / intervalo |
| `converter_paginas(...)` | Orquestra a conversão em lote com progresso |
| `docx_para_pdf_api(...)` | Integração com a API do CloudConvert |
| `docx_para_pdf_local(...)` | Conversão local via LibreOffice (se disponível) |

---

## Histórico de Versões

| Versão | Descrição |
|---|---|
| **v1.0** | Extração direta de imagens do PDF com pypdf (limitado) |
| **v2.0** | Tentativa com fitz/PyMuPDF (falhou em ARM64) |
| **v3.0** | Renderização via pdf2image + Poppler (offline) |
| **v4.0** | Suporte a DOCX via CloudConvert API |
| **v5.0** | Conversão em lote: todas as páginas e intervalo de páginas |

---

## Desafios Técnicos

### 1. Renderização fiel do PDF

PDFs gerados pelo Microsoft Word codificam linhas de corte em três formatos distintos, exigindo análise direta do content stream binário para identificar e renderizar cada elemento corretamente.

### 2. Incompatibilidade de bibliotecas em ARM64

O PyMuPDF (fitz), que seria a solução ideal para renderização, falha na compilação em Android ARM64 devido à dependência do SWIG. A solução foi usar o Poppler via pdftoppm, disponível como pacote nativo no Termux.

### 3. Inversão do eixo Y

O sistema de coordenadas do PDF é cartesiano (Y cresce para cima), enquanto imagens digitais usam Y crescendo para baixo. Sem a conversão correta, todas as imagens ficam verticalmente espelhadas.

### 4. Permissões no Android

O Termux opera em sandbox e requer `termux-setup-storage` para acessar o armazenamento externo (`/sdcard`), o que exigiu tratamento de fallback para a pasta home quando a permissão não está disponível.

---

## Roadmap

- [x] Conversão PDF → PNG/JPG (offline)
- [x] Suporte a DOCX via CloudConvert API
- [x] Conversão em lote (todas as páginas)
- [x] Intervalo de páginas
- [ ] Interface gráfica com Kivy (Android)
- [ ] Suporte a PPTX e XLSX
- [ ] Compressão configurável para JPG
- [ ] Exportação direta para Google Drive
- [ ] Empacotamento como APK instalável

---

## Dependências

| Pacote | Versão mínima | Finalidade |
|---|---|---|
| `pdf2image` | 1.16+ | Interface Python para pdftoppm |
| `Pillow` | 9.0+ | Processamento e salvamento de imagens |
| `pypdf` | 3.0+ | Leitura de metadados do PDF |
| `requests` | 2.28+ | Integração com a API do CloudConvert |
| `poppler` | 22.0+ | Renderizador PDF nativo (sistema) |

---

## Licença

Este projeto é distribuído sob **licença dual**:

- **AGPL-3.0** para uso pessoal, educacional e projetos open source — veja [LICENSE](../LICENSE).
- **Licença Comercial** para uso em produtos fechados, SaaS ou redistribuição proprietária.

Para uso comercial sem as obrigações da AGPL, entre em contato:

> **Anselmo de Araujo Sousa** — [GitHub](https://github.com/anselmosousa)

### O que a AGPL-3.0 permite e proíbe

| Ação | Permitido |
|---|:---:|
| Usar pessoalmente | ✅ |
| Modificar e usar internamente | ✅ |
| Distribuir com o código-fonte aberto | ✅ |
| Usar em projetos acadêmicos/educacionais | ✅ |
| Incorporar em produto fechado sem abrir o código | ❌ |
| Rodar como SaaS sem disponibilizar o código | ❌ |
| Vender sem licença comercial | ❌ |

---

## Autor

**Anselmo de Araujo Sousa**
Analista de Sistemas | Desenvolvedor Python

Contato:
anselmo.sousa@gmail.com

LinkedIn:
linkedin.com/in/anselmosousa

[![GitHub](https://img.shields.io/badge/GitHub-anselmosousa-black?logo=github)](https://github.com/anselmosousa)
