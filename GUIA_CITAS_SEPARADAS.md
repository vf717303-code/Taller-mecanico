# Guía de Implementación: Citas Separadas por Origen

## Cambios Implementados

### 1. Base de Datos
Se agregó un nuevo campo `origen` a la tabla `citas` para diferenciar entre:
- **'cliente'**: Citas creadas por los clientes desde el portal web
- **'empleado'**: Citas asignadas por empleados desde los módulos de Python (Tkinter)

### 2. Portal Web del Cliente

#### Nuevas Páginas:
- **Mis Citas** (`/mis_citas`): Muestra solo las citas que el cliente ha agendado por sí mismo
- **Citas Asignadas** (`/citas_asignadas`): Muestra las citas que los empleados han programado para el cliente

#### Navegación:
El menú lateral ahora incluye ambas opciones:
- Agendar cita
- Mis citas
- **Citas asignadas** (NUEVO)
- Mis autos
- Pedidos de piezas
- Historial
- Cerrar sesión

### 3. Módulos de Python (Empleados)

Cuando los empleados crean citas desde la aplicación Tkinter ([citas.py](citas.py)):
- Las citas se marcan automáticamente con `origen='empleado'`
- Estas citas aparecerán en "Citas Asignadas" para el cliente
- NO aparecerán en "Mis Citas" del cliente

### 4. Archivos Modificados

#### Python:
- [init_db.py](init_db.py): Agregado soporte para campo `origen`
- [app.py](app.py):
  - Modificada ruta `/mis_citas` para filtrar por origen='cliente'
  - Agregadas rutas `/citas_asignadas` y `/api/citas_asignadas`
  - Modificada función `agendar` para marcar origen='cliente'
- [citas.py](citas.py): Modificada función `guardar_cita` para marcar origen='empleado'

#### HTML:
- [templates/cliente_inicio.html](templates/cliente_inicio.html): Actualizado menú
- [templates/mis_citas.html](templates/mis_citas.html): Filtrado por origen='cliente'
- [templates/citas_asignadas.html](templates/citas_asignadas.html): NUEVO - Muestra citas de empleados
- [templates/historial.html](templates/historial.html): Actualizado menú
- [templates/agendar_cita.html](templates/agendar_cita.html): Actualizado menú

### 5. Características

#### Citas Asignadas (Nuevo):
- Muestra fecha, hora, servicio, estado, vehículo, placas y mecánico asignado
- Incluye badges de colores para los estados
- Actualización automática cada 5 segundos
- API REST para consultas: `/api/citas_asignadas`

#### Mis Citas (Actualizado):
- Ahora muestra SOLO las citas que el cliente creó
- Las citas asignadas por empleados NO aparecen aquí
- Mantiene funcionalidad de actualización automática

## Cómo Usar

### Para Clientes (Portal Web):
1. **Agendar Cita**: Sigue usando el botón "Agendar cita" normalmente
2. **Ver Mis Citas**: Clic en "Mis citas" para ver las citas que tú agendaste
3. **Ver Citas Asignadas**: Clic en "Citas asignadas" para ver las citas que el taller programó para ti

### Para Empleados (Módulos Python):
1. Abre la aplicación Tkinter principal ([main.py](main.py))
2. Ve al módulo de "Gestión de Citas"
3. Crea citas normalmente - automáticamente se marcarán como origen='empleado'
4. El cliente verá estas citas en su sección "Citas Asignadas"

## Migración de Datos Existentes

Las citas existentes en la base de datos sin el campo `origen` se tratarán como citas de clientes:
- La consulta usa: `WHERE ... AND (citas.origen = 'cliente' OR citas.origen IS NULL)`
- Esto asegura compatibilidad con datos antiguos

## Verificación

Para verificar que todo funciona:

1. **Ejecutar inicialización de BD**:
```bash
python init_db.py
```

2. **Iniciar servidor web**:
```bash
python app.py
```

3. **Probar como cliente**:
   - Login en http://localhost:5000
   - Agendar una cita
   - Verificar que aparece en "Mis citas"
   - Verificar que NO aparece en "Citas asignadas"

4. **Probar como empleado**:
   - Abrir aplicación Tkinter: `python main.py`
   - Crear una cita para un cliente
   - Login como ese cliente en el portal web
   - Verificar que la cita aparece en "Citas asignadas"
   - Verificar que NO aparece en "Mis citas"

## Notas Técnicas

- **Base de datos**: SQLite (`database.db`)
- **Campo origen**: TEXT DEFAULT 'cliente'
- **APIs REST**: 
  - `/api/mis_citas` - citas del cliente
  - `/api/citas_asignadas` - citas de empleados
- **Auto-refresh**: Ambas páginas actualizan datos cada 3-5 segundos

## Resolución de Problemas

Si las citas no aparecen correctamente:

1. Verificar que el campo `origen` existe:
```bash
python init_db.py
```

2. Verificar que las citas tienen el campo correcto:
```sql
SELECT id, fecha, servicio, origen FROM citas;
```

3. Si las citas antiguas no aparecen, ejecutar:
```sql
UPDATE citas SET origen = 'cliente' WHERE origen IS NULL;
```
