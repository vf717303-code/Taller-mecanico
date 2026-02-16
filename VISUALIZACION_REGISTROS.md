# Módulo de Visualización de Registros

## Descripción

El módulo de **Visualización de Registros** es una nueva sección que permite consultar de forma clara y ordenada toda la información almacenada en la base de datos del taller mecánico.

## Características

### 1. **Visualización de Clientes Registrados**
- Muestra una tabla con todos los clientes registrados en el sistema
- Información visible:
  - ID del cliente
  - Nombre
  - Teléfono
  - Correo electrónico
- **Funcionalidad de Exportación**: Cada cliente puede ser exportado individualmente a PDF
- **Exportación Masiva**: Opción para exportar todos los clientes en un único PDF

### 2. **Visualización de Vehículos Asociados**
- Muestra la relación entre clientes y sus vehículos
- Información visible:
  - Datos del cliente (nombre, teléfono, correo)
  - Marca y modelo del vehículo
  - Placas del vehículo
  - Estado de citas (Sí/No)
- **Exportación a PDF**: Genera un reporte completo de todos los vehículos registrados

### 3. **Visualización de Servicios Realizados**
- Muestra todas las citas que han sido completadas (estado = "Completado")
- Información visible:
  - Cliente responsable
  - Vehículo al que se le prestó el servicio
  - Fecha y hora del servicio
  - Tipo de servicio realizado
  - Estado del servicio
  - Piezas utilizadas (si aplica)
- **Exportación a PDF**: Crea un historial de servicios realizados

### 4. **Visualización de Citas Programadas**
- Muestra todas las citas pendientes o en proceso
- Información visible:
  - Cliente
  - Teléfono del cliente
  - Vehículo asociado
  - Fecha y hora de la cita
  - Tipo de servicio a realizar
  - Estado actual
- **Exportación a PDF**: Genera un calendario de citas programadas

## Funcionalidades de Exportación a PDF

### Tipos de Reportes PDF Disponibles

1. **Cliente Individual**: Reporte detallado de un cliente con todos sus vehículos, citas y servicios
2. **Todos los Clientes**: Tabla consolidada de todos los clientes
3. **Vehículos**: Reporte de todos los vehículos con datos de sus propietarios
4. **Servicios Realizados**: Historial de servicios completados
5. **Citas Programadas**: Calendario de citas futuras

### Características de los PDFs

- Encabezados con información del taller
- Tablas formateadas profesionalmente
- Colores corporativos (naranja #ff9800)
- Fecha y hora de generación del reporte
- Orientación óptima para cada tipo de reporte
- Fácil de imprimir y guardar

## Cómo Usar

### Acceder a Visualización de Registros

1. Abre la aplicación del sistema
2. En el menú lateral izquierdo, haz clic en **"Visualización de Registros"**
3. Se mostrará el menú principal con 4 opciones

### Visualizar Datos

1. Selecciona una de las opciones del menú principal
2. Se cargará automáticamente la información correspondiente
3. Usa el botón **"← Volver al menú"** para regresar

### Exportar a PDF

1. Dentro de cada sección, encontrarás botones verdes de exportación
2. **Para clientes individuales**: Haz clic en el botón "PDF" en la fila del cliente
3. **Para reportes completos**: Haz clic en el botón de exportación al final de la tabla
4. Se abrirá un diálogo para seleccionar la ubicación y nombre del archivo
5. El PDF se guardará en la carpeta que especifiques

## Instalación de Dependencias

El módulo requiere la librería `reportlab` para generar PDFs.

```bash
pip install reportlab
```

Ya se ha incluido en `requirements.txt`:

```
reportlab>=3.6.0
```

## Estructura de Archivos

```
visualizacion_registros.py  - Módulo principal de visualización y exportación
VISUALIZACION_REGISTROS.md  - Este archivo de documentación
```

## Funciones Principales

### `mostrar_visualizacion(frame_visualizacion)`
Muestra el menú principal de visualización de registros.

### `mostrar_clientes(frame_visualizacion)`
Carga y muestra todos los clientes registrados.

### `mostrar_vehiculos(frame_visualizacion)`
Carga y muestra todos los vehículos con información de clientes.

### `mostrar_servicios(frame_visualizacion)`
Carga y muestra servicios completados.

### `mostrar_citas(frame_visualizacion)`
Carga y muestra citas programadas.

### Funciones de Exportación
- `exportar_cliente_pdf(cliente_id, cliente_nombre)` - Exporta cliente individual
- `exportar_todos_clientes_pdf()` - Exporta todos los clientes
- `exportar_vehiculos_pdf()` - Exporta todos los vehículos
- `exportar_servicios_pdf()` - Exporta servicios realizados
- `exportar_citas_pdf()` - Exporta citas programadas

## Consultas SQL Utilizadas

### Clientes con Vehículos y Citas
```sql
SELECT c.id, c.nombre, c.telefono, c.correo,
       a.id, a.marca, a.modelo, a.placas,
       cit.id, cit.fecha, cit.hora, cit.servicio, cit.estado
FROM clientes c
LEFT JOIN autos a ON c.id = a.cliente_id
LEFT JOIN citas cit ON a.id = cit.auto_id
ORDER BY c.nombre, a.id, cit.fecha DESC
```

### Servicios Realizados
```sql
SELECT c.nombre, a.marca, a.modelo, a.placas,
       cit.fecha, cit.hora, cit.servicio, cit.estado,
       p.pieza_refaccion, p.estado
FROM citas cit
JOIN autos a ON cit.auto_id = a.id
JOIN clientes c ON a.cliente_id = c.id
LEFT JOIN piezas p ON cit.id = p.id
WHERE cit.estado = 'Completado'
```

### Citas Programadas
```sql
SELECT c.nombre, c.telefono, c.correo,
       a.marca, a.modelo, a.placas,
       cit.fecha, cit.hora, cit.servicio, cit.estado
FROM citas cit
JOIN autos a ON cit.auto_id = a.id
JOIN clientes c ON a.cliente_id = c.id
WHERE cit.estado != 'Completado'
ORDER BY cit.fecha ASC, cit.hora ASC
```

## Beneficios

✅ **Consulta rápida**: Evita búsqueda manual de datos  
✅ **Historiales completos**: Verifica servicios por vehículo  
✅ **Validación de garantías**: Consulta histórico de reparaciones  
✅ **Reportes profesionales**: PDFs formateados y listos para imprimir  
✅ **Interfaz intuitiva**: Menús claros y organizados  
✅ **Ahorro de tiempo**: Reportes automáticos sin configuración manual  

## Notas Técnicas

- Los PDFs se guardan en formato letter (8.5 x 11 pulgadas)
- Los reportes de vehículos usan tamaño A4 optimizado
- Todos los PDFs incluyen marca de fecha y hora
- Las tablas usan estilos profesionales con colores corporativos
- Se soporta exportación de datos vacíos (mostrarán mensajes informativos)

## Próximas Mejoras

Posibles funcionalidades futuras:
- Filtros por rango de fechas
- Búsqueda avanzada dentro de los registros
- Exportación a Excel (.xlsx)
- Gráficos estadísticos
- Resúmenes mensuales de servicios
- Reportes personalizables
