#!/bin/bash

# Script de instalação para Termux - PDF2TextExtractor

echo "========================================"
echo "PDF2TextExtractor - Instalação no Termux"
echo "========================================"

# Atualizar repositórios
echo "Atualizando repositórios..."
apt update && apt upgrade -y

# Instalar dependências do sistema
echo "Instalando dependências do sistema..."
apt install -y python python-pip build-essential libffi-dev libjpeg-turbo-dev zlib-dev

# Instalar Tesseract OCR
echo "Instalando Tesseract OCR..."
apt install -y tesseract

# Instalar ghostscript (necessário para pdf2image)
echo "Instalando Ghostscript..."
apt install -y ghostscript

# Instalar poppler-utils (necessário para pdf2image)
echo "Instalando poppler-utils..."
apt install -y poppler-utils

# Atualizar pip
echo "Atualizando pip..."
pip install --upgrade pip

# Instalar pacotes Python necessários
echo "Instalando pacotes Python..."
pip install pillow pdf2image pytesseract python-docx opencv-python numpy

echo ""
echo "========================================"
echo "Instalação concluída!"
echo "========================================"
echo ""
echo "Para usar o PDF2TextExtractor:"
echo "python PDF2TextExtractor.py seu_arquivo.pdf"
echo ""
