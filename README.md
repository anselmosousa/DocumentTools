# DocumentTools

> Conjunto de ferramentas Python para automação de processamento de documentos digitais, desenvolvido para execução nativa em dispositivos Android via Termux e Pydroid 3.

<p align="center">
  <img src="Doc2ImageConverter/docs/icon.png" width="100" alt="DocumentTools"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Platform-Android%20%7C%20Linux%20%7C%20macOS-green"/>
  <img src="https://img.shields.io/badge/License-AGPL-3.0-yellow"/>
  <img src="https://img.shields.io/badge/Status-Ativo-brightgreen"/>
  <img src="https://img.shields.io/badge/Termux-Compatível-black?logo=android"/>
</p>

---

## Sobre o Projeto

**DocumentTools** nasceu de uma necessidade real: profissionais e estudantes que precisam processar documentos digitais — converter PDFs para imagens ou extrair texto de documentos escaneados — sem depender de computadores ou softwares pagos.

Todas as ferramentas foram projetadas com dois princípios centrais:

- **Mobile-first:** funcionam 100% no celular Android via Termux, sem interface gráfica obrigatória
- **Offline-first:** sempre que possível, processam os documentos localmente, sem enviar dados para servidores externos

---

## Ferramentas

### [Doc2ImageConverter](./Doc2ImageConverter/)
Converte páginas de documentos PDF e DOCX em imagens PNG ou JPG com qualidade configurável (150, 300 ou 600 DPI). Suporta conversão em lote, página única e intervalos de páginas. Renderiza a página exatamente como ela aparece no documento original — pixel a pixel.

**Tecnologias:** Python · Poppler (pdftoppm) · Pillow · pypdf · CloudConvert API

---

### [PDF2TextExtractor](./PDF2TextExtractor/)
Extrai texto de documentos PDF, incluindo PDFs escaneados (imagens), usando OCR (Reconhecimento Óptico de Caracteres). Gera arquivos DOCX editáveis a partir de documentos não-pesquisáveis, com suporte a múltiplos idiomas.

**Tecnologias:** Python · Tesseract OCR · python-docx · pypdf · Pillow

---

## Motivação Técnica

O desenvolvimento dessas ferramentas envolveu a análise direta da estrutura interna do formato PDF (ISO 32000), incluindo:

- Parsing de content streams e operadores PDF (`cm`, `Do`, `re`, `f*`)
- Conversão de sistemas de coordenadas (eixo Y invertido PDF vs. imagens digitais)
- Identificação e separação de XObjects por tipo (imagens reais vs. máscaras de transparência)
- Pipeline de renderização: vetor → raster em DPI configurável

Esses desafios técnicos foram resolvidos iterativamente, documentados e transformados em código reutilizável.

---

## Estrutura do Repositório

```
DocumentTools/
│
├── Doc2ImageConverter/       # Conversor de documentos para imagem
│   ├── src/                  # Código-fonte principal
│   ├── docs/                 # Documentação e guias
│   ├── examples/             # Exemplos de entrada e saída
│   └── README.md
│
├── PDF2TextExtractor/        # Extrator de texto com OCR
│   ├── src/                  # Código-fonte principal
│   ├── docs/                 # Documentação e guias
│   ├── examples/             # Exemplos de entrada e saída
│   └── README.md
│
├── LICENSE                   # Licença AGPL-3.0
└── README.md                 # Este arquivo
```

---

## Instalação Rápida (Termux)

```bash
# Dependências do sistema
pkg install python poppler tesseract

# Dependências Python
pip install pdf2image Pillow pypdf python-docx pytesseract requests

# Clonar o repositório
git clone https://github.com/anselmosousa/DocumentTools.git
cd DocumentTools
```

---

## Autor

**Anselmo de Araujo Sousa**
Analista de Sistemas | Desenvolvedor Python

Contato:
anselmo.sousa@gmail.com

LinkedIn:
linkedin.com/in/anselmosousa

[![GitHub](https://img.shields.io/badge/GitHub-anselmosousa-black?logo=github)](https://github.com/anselmosousa)

---

## Licença

Este projeto é distribuído sob **licença dual**:

- **AGPL-3.0** para uso pessoal, educacional e projetos open source — veja [LICENSE](LICENSE).
- **Licença Comercial** para uso em produtos fechados, SaaS ou redistribuição proprietária.

Para uso comercial sem as obrigações da AGPL (por exemplo, incorporar em produto fechado sem abrir o código), entre em contato para licenciamento:

> **Anselmo de Araujo Sousa** — [GitHub](https://github.com/anselmosousa)

Este modelo é adotado por projetos como MongoDB, MySQL e Qt.

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
