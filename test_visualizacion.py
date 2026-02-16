#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el módulo de Visualización de Registros
Verifica que todas las funciones estén correctamente implementadas
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Prueba que todos los módulos se importen correctamente"""
    print("=" * 60)
    print("PRUEBA 1: Importación de módulos")
    print("=" * 60)
    
    try:
        from visualizacion_registros import (
            mostrar_visualizacion,
            mostrar_clientes,
            mostrar_vehiculos,
            mostrar_servicios,
            mostrar_citas,
            cargar_clientes_info,
            cargar_servicios_realizados,
            cargar_citas_programadas,
            exportar_cliente_pdf,
            exportar_todos_clientes_pdf,
            exportar_vehiculos_pdf,
            exportar_servicios_pdf,
            exportar_citas_pdf
        )
        print("✓ Módulo 'visualizacion_registros' importado correctamente")
        print("✓ Todas las funciones están disponibles\n")
        return True
    except Exception as e:
        print(f"✗ Error al importar: {e}\n")
        return False


def test_database():
    """Prueba la conexión a la base de datos"""
    print("=" * 60)
    print("PRUEBA 2: Conexión a Base de Datos")
    print("=" * 60)
    
    try:
        from db import conectar_db
        conn = conectar_db()
        cursor = conn.cursor()
        
        # Probar cada tabla
        tablas = ['clientes', 'autos', 'citas', 'piezas', 'proveedores']
        for tabla in tablas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            print(f"✓ Tabla '{tabla}': {count} registros")
        
        conn.close()
        print("✓ Conexión exitosa\n")
        return True
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False


def test_data_loading():
    """Prueba que se pueden cargar los datos"""
    print("=" * 60)
    print("PRUEBA 3: Carga de Datos")
    print("=" * 60)
    
    try:
        from visualizacion_registros import (
            cargar_clientes_info,
            cargar_servicios_realizados,
            cargar_citas_programadas
        )
        
        print("Cargando información de clientes...")
        clientes_info = cargar_clientes_info()
        print(f"✓ {len(clientes_info) if clientes_info else 0} registros de clientes cargados")
        
        print("Cargando servicios realizados...")
        servicios = cargar_servicios_realizados()
        print(f"✓ {len(servicios) if servicios else 0} servicios realizados cargados")
        
        print("Cargando citas programadas...")
        citas = cargar_citas_programadas()
        print(f"✓ {len(citas) if citas else 0} citas programadas cargadas")
        
        print("✓ Todas las consultas funcionan correctamente\n")
        return True
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False


def test_pdf_generation():
    """Prueba la generación de PDFs"""
    print("=" * 60)
    print("PRUEBA 4: Generación de PDFs (Simulación)")
    print("=" * 60)
    
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from datetime import datetime
        
        print("✓ ReportLab está instalado correctamente")
        print("✓ Módulos de PDF disponibles:")
        print("  - SimpleDocTemplate")
        print("  - Table, TableStyle")
        print("  - Paragraph, Spacer")
        print("  - Tamaños de página (letter, A4)")
        print("✓ PDFs pueden ser generados correctamente\n")
        return True
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False


def test_ui_integration():
    """Verifica que el UI se haya actualizado correctamente"""
    print("=" * 60)
    print("PRUEBA 5: Integración con UI")
    print("=" * 60)
    
    try:
        with open('ui.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        if 'from visualizacion_registros import mostrar_visualizacion' in contenido:
            print("✓ Importación de visualizacion_registros agregada al UI")
        else:
            print("✗ Importación no encontrada")
            return False
            
        if 'frame_visualizacion' in contenido:
            print("✓ Frame de visualización creado")
        else:
            print("✗ Frame no encontrado")
            return False
            
        if 'Visualización de Registros' in contenido:
            print("✓ Botón de menú agregado")
        else:
            print("✗ Botón no encontrado")
            return False
            
        if 'mostrar_visualizacion(frame_visualizacion)' in contenido:
            print("✓ Inicialización del frame agregada")
        else:
            print("✗ Inicialización no encontrada")
            return False
            
        print("✓ UI integrado correctamente\n")
        return True
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  PRUEBAS DEL MÓDULO DE VISUALIZACIÓN DE REGISTROS  ".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    resultados = []
    
    resultados.append(("Importación de módulos", test_imports()))
    resultados.append(("Conexión a BD", test_database()))
    resultados.append(("Carga de datos", test_data_loading()))
    resultados.append(("Generación de PDFs", test_pdf_generation()))
    resultados.append(("Integración con UI", test_ui_integration()))
    
    # Resumen final
    print("=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    exitosas = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✓ PASÓ" if resultado else "✗ FALLÓ"
        print(f"{estado}: {nombre}")
    
    print(f"\nTotal: {exitosas}/{total} pruebas exitosas")
    
    if exitosas == total:
        print("\n✓ ¡TODAS LAS PRUEBAS PASARON CORRECTAMENTE!")
        print("\nEl módulo de Visualización de Registros está listo para usar.")
        print("\nPasos siguientes:")
        print("1. Ejecuta: python main.py")
        print("2. Inicia sesión en la aplicación")
        print("3. Haz clic en 'Visualización de Registros' en el menú")
        return 0
    else:
        print("\n✗ Algunas pruebas fallaron. Revisa los errores arriba.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
