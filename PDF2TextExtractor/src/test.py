#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para verificar instalação do PDF2TextExtractor
"""

import sys
import subprocess

def test_module(module_name, import_name=None):
    """Testa se um módulo Python está instalado"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        print(f"✓ {module_name:<20} - OK")
        return True
    except ImportError:
        print(f"✗ {module_name:<20} - NÃO INSTALADO")
        return False

def test_command(command_name):
    """Testa se um comando está disponível"""
    try:
        subprocess.run([command_name, '--version'], 
                      capture_output=True, timeout=5)
        print(f"✓ {command_name:<20} - OK")
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"✗ {command_name:<20} - NÃO ENCONTRADO")
        return False

def main():
    print("\n" + "="*50)
    print("PDF2TextExtractor - Teste de Instalação")
    print("="*50 + "\n")
    
    all_ok = True
    
    print("Módulos Python:")
    print("-" * 50)
    modules = [
        ('PIL/Pillow', 'PIL'),
        ('pdf2image', 'pdf2image'),
        ('pytesseract', 'pytesseract'),
        ('python-docx', 'docx'),
        ('cv2/OpenCV', 'cv2'),
        ('numpy', 'numpy'),
    ]
    
    for module_name, import_name in modules:
        if not test_module(module_name, import_name):
            all_ok = False
    
    print("\nComandos do Sistema:")
    print("-" * 50)
    commands = ['python', 'pip', 'tesseract', 'convert', 'pdftoppm']
    
    for cmd in commands:
        if not test_command(cmd):
            all_ok = False
    
    print("\n" + "="*50)
    
    if all_ok:
        print("✓ Tudo está instalado corretamente!")
        print("="*50)
        print("\nVocê pode usar PDF2TextExtractor agora:")
        print("  python PDF2TextExtractor.py seu_documento.pdf")
        return 0
    else:
        print("✗ Faltam algumas dependências!")
        print("="*50)
        print("\nExecute o script de instalação:")
        print("  bash install_termux.sh")
        return 1

if __name__ == '__main__':
    sys.exit(main())
