# Sistema OSCE - simPEATC

## Resumen de Modificaciones

Este documento describe las modificaciones realizadas al sistema simPEATC para implementar un sistema de evaluación tipo OSCE con 3 estaciones independientes.

**Branch**: `evaluación_2025`
**Fecha**: Enero 2025

## Características Implementadas

### 1. Diálogo de Selección de Estaciones

**Clase**: `OsceStationDialog` (main.py líneas 255-354)

Nuevo diálogo modal con las siguientes características:

- **3 botones principales**: "ESTACIÓN 3", "ESTACIÓN 4", "ESTACIÓN 5"
- **Seguimiento visual**: Muestra "Estaciones completadas: X/3"
- **Deshabilitación inteligente**: Botones de estaciones completadas se deshabilitan automáticamente
- **Prevención de cierre**: No se puede cerrar sin seleccionar estación (en primera ejecución)
- **Estilo visual**: Botones azules con hover, grises cuando deshabilitados

### 2. Sistema de Timer por Estación

**Duración**: 5 minutos (300 segundos) por estación

Características:
- Timer visible en título de ventana: "simPEATC - ESTACIÓN X - Tiempo: MM:SS"
- Actualización cada segundo
- **Advertencia automática**: A los 30 segundos restantes
- **Finalización automática**: Cuando el tiempo llega a 0

**Método principal**: `update_station_timer()` (main.py línea 516)

### 3. Gestión de Datos por Estación

**Archivo de persistencia**: `osce_session_data.json`

#### Estructura de Datos:

```json
{
  "sessions": [
    {
      "session_id": "20250126_143000",
      "completed_stations": [3, 4, 5],
      "stations": {
        "3": {
          "station": 3,
          "start_time": "2025-01-26T14:30:00.123456",
          "end_time": "2025-01-26T14:35:00.456789",
          "data": {},
          "curves": [],
          "store": {
            "75_R:1": {
              "curve": [...],
              "gap": 1.8,
              "marks": [...]
            }
          },
          "completed": true
        },
        "4": {...},
        "5": {...}
      }
    }
  ]
}
```

#### Guardado Automático:

- **Durante la estación**: Los datos se almacenan en `self.station_data[station_number]`
- **Al finalizar estación**: Se guarda automáticamente en `osce_session_data.json`
- **Al completar 3 estaciones**: Se genera reporte final `osce_report_YYYYMMDD_HHMMSS.json`

**Métodos**:
- `save_station_data()` (línea 572)
- `save_final_report()` (línea 660)

### 4. Reset Automático entre Estaciones

**Método**: `reset_station()` (línea 613)

Limpieza realizada:
- Gráficos: `graph_right.clearGraph()` y `graph_left.clearGraph()`
- Store de datos: `self.store.clear()`
- Variables de estado: `current_curves`, `count_prom`, `new_curve`
- Timer de captura: Detención si está activo
- UI: Reset de controles deshabilitados
- Título de ventana: Vuelta a "simPEATC"

### 5. Flujo de Trabajo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                    INICIO DE APLICACIÓN                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│       DIÁLOGO DE SELECCIÓN (Estaciones: 3, 4, 5)                │
│       - Muestra progreso: X/3 completadas                       │
│       - Deshabilita estaciones completadas                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ESTACIÓN SELECCIONADA                          │
│       - Timer inicia: 5:00 minutos                              │
│       - Usuario trabaja en la estación                          │
│       - Advertencia a los 30 segundos                           │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                  TIEMPO AGOTADO (0:00)                           │
│       - Guardar datos automáticamente                           │
│       - Agregar estación a completadas                          │
│       - Reset de gráficos y variables                           │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              ¿SE COMPLETARON 3 ESTACIONES?                       │
└────────┬───────────────────────────────────────┬────────────────┘
         │ NO                                     │ SÍ
         ▼                                        ▼
┌──────────────────────┐             ┌────────────────────────────┐
│  Volver al diálogo   │             │   GUARDAR REPORTE FINAL    │
│  de selección        │             │   - Archivo JSON completo  │
└──────────────────────┘             └─────────────┬──────────────┘
                                                   │
                                                   ▼
                                     ┌────────────────────────────┐
                                     │  ¿Iniciar nueva sesión?    │
                                     └──┬─────────────────────┬───┘
                                        │ SÍ                  │ NO
                                        ▼                     ▼
                                  ┌──────────┐         ┌──────────┐
                                  │  RESET   │         │  CERRAR  │
                                  │  TODO    │         │   APP    │
                                  └──────────┘         └──────────┘
```

## Variables de Estado en MainWindow

```python
# Configuración OSCE
self.osce_mode = True  # True: modo OSCE, False: modo normal

# Estado de estaciones
self.completed_stations = []  # Lista de números [3, 4, 5]
self.current_station = None   # Número de estación actual (3, 4 o 5)

# Datos
self.station_data = {}  # Diccionario {3: {...}, 4: {...}, 5: {...}}

# Timer
self.station_time_remaining = 0  # Segundos restantes (300 = 5 min)
self.station_timer = QTimer()   # Timer Qt

# Persistencia
self.osce_data_file = "osce_session_data.json"
```

## Métodos Principales

### Métodos Públicos:

| Método | Línea | Descripción |
|--------|-------|-------------|
| `show_station_dialog()` | 482 | Muestra diálogo de selección de estaciones |
| `start_station(station_number)` | 488 | Inicia una estación específica (3, 4 o 5) |
| `update_station_timer()` | 516 | Actualiza timer cada segundo |
| `on_station_time_up()` | 543 | Maneja finalización por tiempo |
| `save_station_data()` | 572 | Guarda datos de estación actual en JSON |
| `reset_station()` | 613 | Limpia todo para siguiente estación |
| `complete_all_stations()` | 638 | Finaliza las 3 estaciones |
| `save_final_report()` | 660 | Genera reporte final JSON |
| `reset_all_osce()` | 689 | Reinicia sistema completo para nueva sesión |

### Conexiones de Señales:

```python
# En __init__:
self.station_timer.timeout.connect(self.update_station_timer)

# En show_station_dialog:
dialog.station_selected.connect(self.start_station)
```

## Archivos Generados

### 1. osce_session_data.json
- **Propósito**: Almacenamiento incremental de todas las sesiones
- **Actualización**: Después de cada estación completada
- **Contenido**: Datos de todas las sesiones, todas las estaciones

### 2. osce_report_YYYYMMDD_HHMMSS.json
- **Propósito**: Reporte final de una sesión completa
- **Generación**: Al completar las 3 estaciones
- **Contenido**: Datos específicos de la sesión actual
- **Ejemplo**: `osce_report_20250126_143000.json`

## Configuración y Personalización

### Activar/Desactivar Modo OSCE

En `MainWindow.__init__()` (línea 409):
```python
self.osce_mode = True  # Cambiar a False para modo normal
```

### Modificar Duración de Estaciones

En `start_station()` (línea 491):
```python
self.station_time_remaining = 300  # Cambiar segundos (300 = 5 min)
```

### Modificar Tiempo de Advertencia

En `update_station_timer()` (línea 531):
```python
if self.station_time_remaining == 30:  # Cambiar umbral de advertencia
```

### Personalizar Números de Estaciones

En `OsceStationDialog.__init__()` (líneas 285-287):
```python
self.btn_station_3 = QPushButton("ESTACIÓN 3")  # Cambiar texto/número
self.btn_station_4 = QPushButton("ESTACIÓN 4")
self.btn_station_5 = QPushButton("ESTACIÓN 5")
```

## Integración con Sistema Existente

### Compatibilidad:
- ✅ Sistema mantiene toda la funcionalidad original
- ✅ Modo normal sigue funcionando (cambiar `osce_mode = False`)
- ✅ No afecta la generación de curvas ABR
- ✅ Compatible con sistema de guardado PDF existente

### Cambios Mínimos:
- Importaciones añadidas: `QDialog`, `QHBoxLayout`, `json`, `os`
- Nueva clase: `OsceStationDialog`
- Variables de estado OSCE en `__init__`
- 9 métodos nuevos para manejo OSCE
- Sin cambios en lógica de simulación

## Testing y Validación

### Escenarios de Prueba:

1. **Flujo Normal**:
   - Seleccionar Estación 3 → Esperar 5 min → Seleccionar Estación 4 → etc.

2. **Advertencia de Tiempo**:
   - Verificar mensaje a los 30 segundos

3. **Persistencia**:
   - Verificar creación de `osce_session_data.json`
   - Verificar datos guardados correctamente

4. **Reset entre Estaciones**:
   - Verificar limpieza de gráficos
   - Verificar que estación anterior se deshabilita

5. **Reporte Final**:
   - Completar 3 estaciones
   - Verificar generación de archivo final

6. **Nueva Sesión**:
   - Elegir "Sí" al finalizar
   - Verificar que todo se resetea correctamente

## Problemas Conocidos y Limitaciones

### Actuales:
- ⚠️ Si el usuario cierra la ventana durante una estación, los datos no se guardan
- ⚠️ No hay botón para pausar el timer
- ⚠️ No hay opción para saltar una estación

### Posibles Mejoras Futuras:
- [ ] Agregar botón de pausa/reanudar
- [ ] Confirmación antes de cerrar ventana durante estación
- [ ] Guardado incremental cada minuto
- [ ] Mostrar tiempo en pantalla (no solo en título)
- [ ] Permitir extender tiempo con contraseña
- [ ] Exportar datos a CSV/Excel

## Uso en Producción

### Recomendaciones:

1. **Backup de datos**: Hacer respaldo periódico de `osce_session_data.json`
2. **Limpieza**: Archivar reportes antiguos periódicamente
3. **Testing previo**: Probar flujo completo antes de evaluación real
4. **Instrucciones claras**: Explicar a estudiantes el sistema de timer
5. **Plan B**: Tener método alternativo si hay fallas técnicas

### Checklist Pre-Evaluación:

- [ ] Verificar que `osce_mode = True`
- [ ] Limpiar archivos JSON antiguos si es necesario
- [ ] Probar sistema completo con caso de prueba
- [ ] Verificar que los 3 botones funcionan
- [ ] Confirmar que timer cuenta correctamente
- [ ] Verificar guardado de datos

## Soporte y Contacto

Para problemas o modificaciones, contactar al equipo de desarrollo o revisar el código en:

- **Archivo principal**: `src/main/python/main.py`
- **Líneas OSCE**: 255-703
- **Branch**: `evaluación_2025`

---

**Última actualización**: Enero 2025
**Versión**: 1.0
**Autor**: Sistema implementado por Claude Code
