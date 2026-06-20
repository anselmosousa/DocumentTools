#!/bin/bash

# ============================================================================
# PDF2TextExtractor - INSTALAÇÃO CORRIGIDA PARA TERMUX
# Testado em: Termux 0.118+ com Android (ARM64)
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   PDF2TextExtractor - Instalação para Termux (CORRIGIDA)               ║"
echo "║   Compatível com: Android 5.0+, Termux 0.110+                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir sucesso
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Função para imprimir erro
error() {
    echo -e "${RED}✗${NC} $1"
}

# Função para imprimir aviso
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# ============================================================================
# PASSO 1: Atualizar repositórios
# ============================================================================

echo ""
echo "PASSO 1: Atualizando repositórios do Termux..."
echo "─────────────────────────────────────────────────────────────────"

if apt update; then
    success "Repositórios atualizados"
else
    error "Falha ao atualizar repositórios"
    exit 1
fi

# ============================================================================
# PASSO 2: Instalar dependências do sistema (NOMES CORRETOS PARA TERMUX)
# ============================================================================

echo ""
echo "PASSO 2: Instalando dependências do sistema..."
echo "─────────────────────────────────────────────────────────────────"

# Lista de pacotes para Termux (sem -dev no final!)
PACKAGES=(
    "python"
    "python-pip"
    "python-dev"
    "clang"
    "make"
    "libffi"
    "libjpeg-turbo"
    "zlib"
)

for package in "${PACKAGES[@]}"; do
    echo "Instalando $package..."
    if apt install -y "$package" 2>/dev/null; then
        success "$package instalado"
    else
        warning "$package não disponível ou já instalado"
    fi
done

# ============================================================================
# PASSO 3: Instalar Tesseract (IMPORTANTE para OCR)
# ============================================================================

echo ""
echo "PASSO 3: Instalando Tesseract OCR..."
echo "─────────────────────────────────────────────────────────────────"

if apt install -y tesseract; then
    success "Tesseract instalado"
    # Verificar versão
    if tesseract --version &>/dev/null; then
        success "Tesseract funcionando"
    else
        error "Tesseract instalado mas não funciona"
    fi
else
    error "Falha ao instalar Tesseract"
    warning "Tente instalar manualmente: apt install tesseract"
fi

# ============================================================================
# PASSO 4: Instalar ferramentas de PDF (OPCIONAL mas RECOMENDADO)
# ============================================================================

echo ""
echo "PASSO 4: Instalando ferramentas de PDF..."
echo "─────────────────────────────────────────────────────────────────"

# Tenta instalar imagemagick (para conversão de PDF)
if apt install -y imagemagick; then
    success "ImageMagick instalado"
else
    warning "ImageMagick não disponível (será usada alternativa Python)"
fi

# ============================================================================
# PASSO 5: Atualizar pip
# ============================================================================

echo ""
echo "PASSO 5: Atualizando pip..."
echo "─────────────────────────────────────────────────────────────────"

if pip install --upgrade pip setuptools wheel; then
    success "pip atualizado"
else
    error "Falha ao atualizar pip"
fi

# ============================================================================
# PASSO 6: Instalar pacotes Python ESSENCIAIS
# ============================================================================

echo ""
echo "PASSO 6: Instalando pacotes Python (PARTE 1 - ESSENCIAL)..."
echo "─────────────────────────────────────────────────────────────────"

PYTHON_PACKAGES_ESSENTIAL=(
    "pillow"
    "pytesseract"
    "python-docx"
)

for package in "${PYTHON_PACKAGES_ESSENTIAL[@]}"; do
    echo "Instalando $package..."
    if pip install "$package"; then
        success "$package instalado"
    else
        error "Falha ao instalar $package"
        warning "Continuando com outros pacotes..."
    fi
done

# ============================================================================
# PASSO 7: Instalar pacotes Python OPCIONAIS
# ============================================================================

echo ""
echo "PASSO 7: Instalando pacotes Python (PARTE 2 - OTIMIZAÇÃO)..."
echo "─────────────────────────────────────────────────────────────────"

# Estes são opcionais - instalar com cuidado
warning "Instalando pacotes opcionais (pode levar tempo)..."

# pdf2image com fallback
echo "Instalando pdf2image..."
if pip install pdf2image; then
    success "pdf2image instalado"
else
    warning "pdf2image não instalado (usaremos ImageMagick como alternativa)"
fi

# numpy - importante para processamento
echo "Instalando numpy..."
if pip install numpy; then
    success "numpy instalado"
else
    warning "numpy não instalado (funcionalidade reduzida)"
fi

# opencv - opcional para pré-processamento
echo "Instalando opencv (isto pode levar um tempo)..."
if pip install opencv-python; then
    success "opencv instalado"
else
    warning "opencv não instalado (usaremos PIL como alternativa)"
fi

# ============================================================================
# PASSO 8: Verificação final
# ============================================================================

echo ""
echo "PASSO 8: Verificando instalação..."
echo "─────────────────────────────────────────────────────────────────"

ERROS=0

# Verificar Python
if python --version &>/dev/null; then
    success "Python: $(python --version)"
else
    error "Python não encontrado"
    ERROS=$((ERROS + 1))
fi

# Verificar pip
if pip --version &>/dev/null; then
    success "pip: $(pip --version)"
else
    error "pip não encontrado"
    ERROS=$((ERROS + 1))
fi

# Verificar Tesseract
if tesseract --version &>/dev/null; then
    success "Tesseract: $(tesseract --version | head -n1)"
else
    error "Tesseract não encontrado"
    ERROS=$((ERROS + 1))
fi

# Verificar módulos Python críticos
echo ""
echo "Verificando módulos Python..."
python3 << 'PYEOF'
import sys
modules = {
    'PIL': 'Pillow',
    'pytesseract': 'pytesseract',
    'docx': 'python-docx',
}

for mod, name in modules.items():
    try:
        __import__(mod)
        print(f"✓ {name}")
    except ImportError:
        print(f"✗ {name} NÃO INSTALADO")
PYEOF

# ============================================================================
# RESULTADO FINAL
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"

if [ $ERROS -eq 0 ]; then
    echo "║                    INSTALAÇÃO CONCLUÍDA! ✓                  ║"
    echo "║                                                              ║"
    echo "║  Próximas etapas:                                           ║"
    echo "║  1. python test_installation.py  (verificar)                ║"
    echo "║  2. python PDF2TextExtractor.py seu_pdf.pdf  (converter)             ║"
    echo "║                                                              ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    exit 0
else
    echo "║                   ⚠ INSTALAÇÃO COM PROBLEMAS                 ║"
    echo "║                                                              ║"
    echo "║  Foram encontrados $ERROS erro(s)                                  ║"
    echo "║  Tente executar:                                            ║"
    echo "║  python test_installation.py                                ║"
    echo "║                                                              ║"
    echo "║  Para mais ajuda, veja FAQ.md                               ║"
    echo "║                                                              ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    exit 1
fi