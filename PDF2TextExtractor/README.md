# PDF2TextExtractor

> Extrai texto de documentos PDF — incluindo PDFs escaneados — usando OCR (Reconhecimento Óptico de Caracteres) e gera arquivos Word (.docx) editáveis, funcionando nativamente em dispositivos Android via Termux.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Tesseract-5.x-red"/>
  <img src="https://img.shields.io/badge/OCR-Multilíngue-orange"/>
  <img src="https://img.shields.io/badge/Android-Termux-black?logo=android"/>
  <img src="https://img.shields.io/badge/Saída-DOCX-blue?logo=microsoftword"/>
  <img src="https://img.shields.io/badge/License-AGPL--3.0%20%2B%20Commercial-blue"/>
</p>

---

## Índice

- [Visão Geral](#visão-geral)
- [Como Funciona](#como-funciona)
- [Funcionalidades](#funcionalidades)
- [Arquitetura Técnica](#arquitetura-técnica)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Idiomas Suportados](#idiomas-suportados)
- [Estrutura do Código](#estrutura-do-código)
- [Desafios Técnicos](#desafios-técnicos)
- [Limitações e Boas Práticas](#limitações-e-boas-práticas)
- [Roadmap](#roadmap)
- [Licença](#licença)

---

## Visão Geral

O **PDF2TextExtractor** resolve um problema frequente: documentos PDF que contêm apenas imagens escaneadas — sem texto selecionável — impossibilitando cópia, busca ou edição do conteúdo.

A ferramenta aplica OCR (Optical Character Recognition) página a página, reconhece o texto presente nas imagens e gera um arquivo Word (`.docx`) editável, preservando a estrutura de parágrafos do documento original.

### Casos de Uso

- Digitalizar contratos, formulários e documentos físicos escaneados
- Tornar PDFs de livros e artigos pesquisáveis e editáveis
- Extrair texto de notas fiscais, boletos e documentos governamentais
- Pré-processamento de documentos para pipelines de NLP e IA
- Acessibilidade: converter documentos visuais em texto para leitores de tela

---

## Como Funciona

O pipeline de processamento segue as seguintes etapas:

```
┌─────────────┐   ┌───────────────┐   ┌────────────────┐   ┌──────────────┐
│  PDF de     │   │  Rasterização │   │  OCR por       │   │  Arquivo     │
│  Entrada    │──▶│  de Páginas   │──▶│  Página        │──▶│  DOCX        │
│  (qualquer) │   │  (Pillow)     │   │  (Tesseract)   │   │  Editável    │
└─────────────┘   └───────────────┘   └────────────────┘   └──────────────┘
```

### Etapa 1 — Verificação do tipo de PDF

Antes de aplicar OCR, o programa verifica se o PDF já contém texto selecionável usando `pypdf`. Se sim, extrai o texto diretamente (mais rápido e preciso). Se não (PDF escaneado), aplica o pipeline de OCR.

```python
reader = pypdf.PdfReader(caminho_pdf)
texto_direto = reader.pages[0].extract_text()
if texto_direto and len(texto_direto.strip()) > 20:
    # PDF com texto — extração direta
else:
    # PDF escaneado — aplicar OCR
```

### Etapa 2 — Rasterização das páginas

Cada página do PDF é convertida em imagem de alta resolução (300 DPI) usando `pdf2image` + Poppler, garantindo qualidade suficiente para o OCR:

```python
from pdf2image import convert_from_path
paginas = convert_from_path(caminho_pdf, dpi=300)
```

### Etapa 3 — OCR com Tesseract

Cada imagem é submetida ao Tesseract OCR, que retorna o texto reconhecido como string:

```python
import pytesseract
texto = pytesseract.image_to_string(imagem, lang='por')
```

### Etapa 4 — Geração do arquivo DOCX

O texto extraído de todas as páginas é estruturado e salvo como documento Word usando `python-docx`:

```python
from docx import Document
doc = Document()
for paragrafo in texto.split('\n\n'):
    doc.add_paragraph(paragrafo.strip())
doc.save(caminho_saida)
```

---

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| **OCR em PDFs escaneados** | Reconhece texto em imagens dentro de PDFs |
| **Extração direta** | Para PDFs com texto nativo, extrai sem OCR (mais rápido) |
| **Saída em DOCX** | Gera arquivo Word editável estruturado por parágrafos |
| **Suporte multilíngue** | Português, inglês e outros idiomas via pacotes Tesseract |
| **Processamento por página** | Exibe progresso página a página |
| **Diagnóstico de ambiente** | Verifica e reporta todas as dependências na inicialização |
| **Configuração de DPI** | DPI ajustável para balancear velocidade vs. precisão do OCR |
| **Fallback automático** | Usa extração direta quando disponível, OCR apenas quando necessário |

---

## Arquitetura Técnica

### Fluxo de decisão

```
                    ┌─────────────────┐
                    │  PDF de entrada │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Tem texto      │
                    │  selecionável?  │
                    └────────┬────────┘
                     Sim     │     Não
              ┌──────────────┤     ├──────────────┐
              ▼              │     │              ▼
    ┌──────────────┐         │     │   ┌─────────────────────┐
    │  Extração    │         │     │   │  Rasterização       │
    │  direta com  │         │     │   │  (pdf2image, 300DPI)│
    │  pypdf       │         │     │   └──────────┬──────────┘
    └──────┬───────┘         │     │              │
           │                 │     │   ┌──────────▼──────────┐
           │                 │     │   │  OCR por página     │
           │                 │     │   │  (Tesseract 5)      │
           │                 │     │   └──────────┬──────────┘
           └─────────────────┤     ├──────────────┘
                             │     │
                    ┌────────▼─────▼────┐
                    │  Geração do DOCX   │
                    │  (python-docx)     │
                    └───────────────────┘
```

### Pré-processamento de imagem para OCR

A qualidade do OCR é diretamente afetada pela qualidade da imagem. O pipeline aplica técnicas de pré-processamento quando necessário:

```python
from PIL import Image, ImageFilter, ImageEnhance

def preprocessar(img):
    # Converter para escala de cinza
    img = img.convert('L')
    # Aumentar contraste
    img = ImageEnhance.Contrast(img).enhance(2.0)
    # Nitidez
    img = img.filter(ImageFilter.SHARPEN)
    return img
```

### Configuração do Tesseract

O Tesseract é configurado com Page Segmentation Mode (PSM) adequado ao tipo de documento:

```python
config = '--psm 6 --oem 3'
# PSM 6: assume um bloco uniforme de texto
# OEM 3: usa o motor LSTM (mais preciso)
texto = pytesseract.image_to_string(img, lang='por+eng', config=config)
```

---

## Instalação

### Android — Termux (recomendado)

```bash
# 1. Instalar dependências do sistema
pkg install python poppler tesseract git

# 2. Instalar dados de idioma português
pkg install tesseract-language-por

# 3. Permitir acesso ao armazenamento
termux-setup-storage

# 4. Instalar dependências Python
pip install pytesseract pdf2image Pillow pypdf python-docx

# 5. Clonar o repositório
git clone https://github.com/anselmosousa/DocumentTools.git
cd DocumentTools/PDF2TextExtractor/src
```

### Linux (Ubuntu/Debian)

```bash
# Dependências do sistema
sudo apt install python3 python3-pip poppler-utils \
     tesseract-ocr tesseract-ocr-por tesseract-ocr-eng

# Dependências Python
pip install pytesseract pdf2image Pillow pypdf python-docx

# Clonar
git clone https://github.com/anselmosousa/DocumentTools.git
```

### macOS

```bash
brew install poppler tesseract tesseract-lang python
pip install pytesseract pdf2image Pillow pypdf python-docx
git clone https://github.com/anselmosousa/DocumentTools.git
```

### Verificar instalação do Tesseract

```bash
tesseract --version
tesseract --list-langs
```

A saída deve incluir `por` (português) e `eng` (inglês).

---

## Como Usar

```bash
python src/pdf2ocr.py
```

### Fluxo interativo

```
╔══════════════════════════════════════╗
║    PDF2TextExtractor v1.0 — Termux   ║
║  Extrai texto de PDFs com OCR        ║
╚══════════════════════════════════════╝

Verificando dependências:
  ✓ Tesseract OCR (v5.3.1)
  ✓ Poppler (pdftoppm)
  ✓ Idiomas disponíveis: por, eng

Caminho do PDF:
Ex: /sdcard/Download/documento.pdf
> /sdcard/Download/contrato.pdf

PDF com 8 pagina(s).

Idioma do texto:
  1. Português (por)
  2. Inglês (eng)
  3. Português + Inglês (por+eng)
> 1

Processando página 1/8... OK (342 palavras)
Processando página 2/8... OK (418 palavras)
Processando página 3/8... OK (395 palavras)
...
Processando página 8/8... OK (287 palavras)

✓ SUCESSO!
  Páginas processadas : 8
  Total de palavras   : 3.124
  Arquivo gerado      : /sdcard/Documents/contrato_ocr_20260610.docx
```

---

## Idiomas Suportados

O Tesseract suporta mais de 100 idiomas. No Termux, instale o pacote de idioma desejado:

```bash
# Português
pkg install tesseract-language-por

# Espanhol
pkg install tesseract-language-spa

# Francês
pkg install tesseract-language-fra
```

Para usar múltiplos idiomas simultaneamente:

```python
# No código, combine com '+'
texto = pytesseract.image_to_string(img, lang='por+eng')
```

---

## Estrutura do Código

```
PDF2TextExtractor/
├── src/
│   └── pdf2ocr.py              # Código principal
├── docs/
│   └── guia_ocr.md             # Guia de boas práticas de OCR
├── examples/
│   ├── input_scanned.pdf       # PDF escaneado de exemplo
│   └── output_extracted.docx   # DOCX gerado de exemplo
└── README.md                   # Este arquivo
```

### Funções principais

| Função | Responsabilidade |
|---|---|
| `main()` | Loop principal de interação com o usuário |
| `verificar_dependencias()` | Checa Tesseract, Poppler e idiomas instalados |
| `tem_texto_nativo(pdf)` | Detecta se o PDF já tem texto selecionável |
| `extrair_texto_direto(pdf)` | Extração via pypdf (PDFs com texto nativo) |
| `extrair_texto_ocr(pdf, lang, dpi)` | Pipeline de OCR página a página |
| `preprocessar_imagem(img)` | Melhora a imagem antes do OCR |
| `salvar_docx(texto, caminho)` | Gera o arquivo Word estruturado |

---

## Desafios Técnicos

### 1. Configuração do TESSDATA_PREFIX no Android

No Termux, o Tesseract precisa que a variável de ambiente `TESSDATA_PREFIX` aponte para o diretório correto dos modelos de idioma. O código configura isso automaticamente:

```python
import os
os.environ['TESSDATA_PREFIX'] = '/data/data/com.termux/files/usr/share/tessdata'
```

### 2. Saída vazia do Tesseract

Um problema recorrente durante o desenvolvimento foi o Tesseract retornar texto vazio mesmo com imagens legíveis. As causas identificadas foram:

- **DPI insuficiente:** abaixo de 200 DPI, o Tesseract falha em reconhecer caracteres pequenos
- **Imagem colorida:** o Tesseract performa melhor em escala de cinza com alto contraste
- **PSM incorreto:** documentos com layout complexo precisam de PSM diferente do padrão

**Solução aplicada:** pipeline de pré-processamento que converte para cinza, aumenta contraste e aplica nitidez antes de submeter ao Tesseract.

### 3. Preservação de estrutura no DOCX

O texto bruto retornado pelo Tesseract inclui quebras de linha simples dentro de parágrafos e duplas entre parágrafos. O código distingue esses dois casos para gerar um DOCX bem estruturado:

```python
paragrafos = [p.strip() for p in texto.split('\n\n') if p.strip()]
for par in paragrafos:
    # Remover quebras de linha simples (continuação de parágrafo)
    texto_par = ' '.join(par.split('\n'))
    doc.add_paragraph(texto_par)
```

---

## Limitações e Boas Práticas

### Limitações conhecidas

| Situação | Comportamento |
|---|---|
| PDF com colunas múltiplas | OCR pode misturar a ordem de leitura |
| Tabelas complexas | Estrutura de tabela não é preservada no DOCX |
| Manuscritos | Precisão reduzida; Tesseract foi treinado em texto impresso |
| Imagens com baixa resolução | Precisão reduzida abaixo de 150 DPI |
| PDFs protegidos por senha | Não suportado (requer descriptografia prévia) |

### Boas práticas para melhor resultado

- Use PDFs com resolução mínima de 200 DPI
- Prefira documentos com texto impresso (não manuscrito)
- Para documentos bilíngues, use `lang='por+eng'`
- Revise o DOCX gerado, pois OCR pode conter erros pontuais
- Para documentos críticos, compare o DOCX com o original

---

## Roadmap

- [x] OCR de PDFs escaneados com Tesseract
- [x] Extração direta de PDFs com texto nativo
- [x] Geração de DOCX estruturado
- [x] Suporte a múltiplos idiomas
- [ ] Preservação de formatação básica (negrito, itálico)
- [ ] Suporte a tabelas no DOCX de saída
- [ ] Processamento em lote de múltiplos PDFs
- [ ] Interface gráfica com Kivy (Android)
- [ ] Integração com API de tradução automática
- [ ] Exportação para TXT e Markdown além de DOCX

---

## Dependências

| Pacote | Versão mínima | Finalidade |
|---|---|---|
| `pytesseract` | 0.3.10+ | Interface Python para o Tesseract OCR |
| `pdf2image` | 1.16+ | Rasterização de páginas PDF |
| `Pillow` | 9.0+ | Processamento e pré-processamento de imagens |
| `pypdf` | 3.0+ | Extração de texto nativo e metadados do PDF |
| `python-docx` | 0.8.11+ | Geração de arquivos Word editáveis |
| `tesseract` | 5.0+ | Motor de OCR (instalado no sistema) |
| `poppler` | 22.0+ | Renderizador PDF para rasterização |

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
