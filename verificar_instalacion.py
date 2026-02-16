#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICACIÓN RÁPIDA - Visualización de Registros
Script para verificar que todo está instalado correctamente
"""

import sys
import os

def banner():
    print("\n")
    print("╔" + "═"*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "VERIFICACIÓN RÁPIDA - VISUALIZACIÓN DE REGISTROS".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "═"*58 + "╝")
    print()

def check_file(filename, description):
    """Verifica si un archivo existe"""
    exists = os.path.isfile(filename)
    status = "✓" if exists else "✗"
    symbol = "🆕" if filename.startswith("visualizacion_") or filename.startswith("config_") or filename.startswith("test_") else "✏️"
    print(f"{status} {symbol} {filename:<40} - {description}")
    return exists

def check_import(module_name, description):
    """Verifica si un módulo puede importarse"""
    try:
        __import__(module_name)
        print(f"✓ ✓ {module_name:<40} - {description}")
        return True
    except ImportError as e:
        print(f"✗ ✗ {module_name:<40} - ERROR: {str(e)}")
        return False

def main():
    banner()
    
    # Verificar archivos nuevos
    print("📁 ARCHIVOS NUEVOS:")
    print("-" * 58)
    files_ok = 0
    files = [
        ("visualizacion_registros.py", "Módulo principal"),
        ("config_reportes.py", "Configuración"),
        ("test_visualizacion.py", "Pruebas"),
        ("VISUALIZACION_REGISTROS.md", "Documentación técnica"),
        ("GUIA_VISUALIZACION_REGISTROS.md", "Guía de usuario"),
        ("IMPLEMENTACION_COMPLETADA.md", "Resumen técnico"),
        ("README_VISUALIZACION.md", "Inicio rápido"),
    ]
    
    for filename, desc in files:
        if check_file(filename, desc):
            files_ok += 1
    
    print()
    
    # Verificar archivos modificados
    print("📝 ARCHIVOS MODIFICADOS:")
    print("-" * 58)
    check_file("ui.py", "✏️ Agregado botón y frame")
    check_file("requirements.txt", "✏️ Agregado reportlab")
    
    print()
    
    # Verificar imports
    print("📦 DEPENDENCIAS:")
    print("-" * 58)
    imports_ok = 0
    imports = [
        ("tkinter", "Interfaz gráfica"),
        ("sqlite3", "Base de datos"),
        ("reportlab", "Generación PDF"),
        ("datetime", "Manejo de fechas"),
    ]
    
    for module, desc in imports:
        if check_import(module, desc):
            imports_ok += 1
    
    print()
    
    # Resumen
    print("📊 RESUMEN:")
    print("-" * 58)
    print(f"Archivos nuevos encontrados: {files_ok}/{len(files)}")
    print(f"Dependencias disponibles: {imports_ok}/{len(imports)}")
    
    if files_ok == len(files) and imports_ok == len(imports):
        print("\n✅ ¡TODO ESTÁ CORRECTO! Puedes comenzar a usar el módulo.")
        print("\nPróximos pasos:")
        print("  1. python test_visualizacion.py    (ejecutar pruebas)")
        print("  2. python main.py                  (iniciar aplicación)")
        print("  3. Haz clic en 'Visualización de Registros' en el menú")
        return 0
    else:
        print("\n⚠️  Algunos elementos no están disponibles.")
        print("Por favor, revisa la documentación para instalar las dependencias faltantes.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
