# Cambios Realizados: Sistema OSCE para simPEATC

## Resumen
Se ha implementado un sistema completo de evaluación OSCE (Objective Structured Clinical Examination) con 3 estaciones secuenciales en el simulador simPEATC.

## Modificaciones Principales

### 1. Nuevas Constantes Globales (main.py líneas 41-46)
```python
STATE_INIT = "osce"  # Modo por defecto cambiado a OSCE
TIEMPO_ESTACION_OSCE = 5  # 5 minutos por estación
N_ESTACIONES = 3  # Número de estaciones OSCE
```

### 2. Nueva Clase: `CuadroDialogoOSCE` (líneas 130-234)
**Características:**
- Ventana modal con 3 botones para estaciones 3, 4 y 5
- Sistema de habilitación/deshabilitación progresiva
- Solo se puede acceder a una estación tras completar la anterior
- No se puede cerrar con Escape o Alt+F4
- Marca visual (✓) cuando una estación está completada
- Label de estado que informa el progreso

**Métodos principales:**
- `seleccionar_estacion(numero_estacion)`: Maneja la selección de estación
- `marcar_estacion_completada(numero_estacion)`: Marca estación como completada y habilita la siguiente
- `todas_completadas()`: Verifica si las 3 estaciones están completas

### 3. Clase `IsOver` Modificada (líneas 59-103)
**Nuevas características:**
- Soporte para modo OSCE con parámetros `modo_osce` y `estacion`
- Mensajes personalizados según el modo
- Prevención de cierre accidental (Escape/Alt+F4)

### 4. Variables de Estado OSCE en MainWindow (líneas 453-461)
```python
self.modo_osce = (STATE_INIT == "osce")
self.estacion_actual = None
self.dialog_osce = None
self.datos_estaciones = {
    3: {'memory': {}, 'case': None, 'completada': False},
    4: {'memory': {}, 'case': None, 'completada': False},
    5: {'memory': {}, 'case': None, 'completada': False}
}
```

### 5. Método `actualizar_tiempo()` Modificado (líneas 469-505)
**Cambios:**
- Detecta modo OSCE y aplica lógica diferente
- Al terminar el tiempo en modo OSCE:
  - Guarda datos de la estación actual
  - Muestra ventana de "Estación completada"
  - Resetea el programa
  - Vuelve a mostrar el diálogo de selección de estaciones

### 6. Método `open_modal()` Modificado (líneas 548-569)
**Cambios:**
- Detecta el modo de operación (osce/exam/test)
- Si es modo OSCE, llama a `abrir_dialogo_osce()`
- Mantiene compatibilidad con modos anteriores

### 7. Nuevos Métodos OSCE (líneas 837-960)

#### `abrir_dialogo_osce()`
- Crea o reabre el diálogo de estaciones
- Marca estaciones ya completadas
- Verifica si todas están completadas para guardar y resetear
- Inicia la estación seleccionada

#### `iniciar_estacion(numero_estacion)`
- Configura la estación actual
- Selecciona caso aleatorio para la estación
- Actualiza UI con información de estación
- Inicia timer de 5 minutos

#### `guardar_datos_estacion()`
- Guarda memoria y datos de la estación actual
- Hace copia profunda (deepcopy) de la memoria
- Marca estación como completada
- Actualiza el diálogo visual

#### `guardar_todas_estaciones()`
- Se ejecuta al completar las 3 estaciones
- Crea directorio `resultados_osce` si no existe
- Guarda JSON con timestamp: `osce_completo_YYYYMMDD_HHMMSS.json`
- Incluye fecha, número de caso y memoria de cada estación
- Muestra mensaje de confirmación al usuario

#### `resetear_programa_completo()`
- Limpia todas las curvas
- Reinicia datos de estaciones
- Limpia memoria y variables
- Vuelve a abrir diálogo de selección para nueva evaluación

### 8. Método `closeEvent()` Modificado (líneas 963-968)
- Verifica existencia del observer antes de detenerlo
- Previene errores al cerrar la aplicación

## Flujo de Trabajo OSCE

### 1. Inicio
```
Aplicación inicia → Modo OSCE detectado → Muestra diálogo con 3 estaciones
```

### 2. Estación 3 (Primera)
```
Usuario presiona "ESTACIÓN 3" →
Caso aleatorio asignado →
Timer 5 minutos inicia →
Usuario realiza evaluación →
Tiempo termina →
Datos guardados →
Ventana "Estación 3 completada" →
Vuelve al diálogo de estaciones
```

### 3. Estación 4 (Segunda)
```
Botón "ESTACIÓN 4" ahora habilitado →
Estación 3 marcada con ✓ →
(Mismo proceso que Estación 3)
```

### 4. Estación 5 (Tercera)
```
Botón "ESTACIÓN 5" ahora habilitado →
Estaciones 3 y 4 marcadas con ✓ →
(Mismo proceso que anteriores)
```

### 5. Finalización
```
Todas las estaciones completadas →
Guarda JSON completo con timestamp →
Mensaje de confirmación →
Reseteo completo del programa →
Vuelve al diálogo de selección (listo para nuevo estudiante)
```

## Estructura de Datos Guardados

### Archivo JSON generado: `osce_completo_YYYYMMDD_HHMMSS.json`
```json
{
    "fecha": "2025-11-26T15:30:45.123456",
    "estaciones": {
        "estacion_3": {
            "caso": 5,
            "memory": {
                "R1": {
                    "side": "OD",
                    "int": 75,
                    "average": 2000,
                    "LatAmp": {
                        "I": [1.6, 0.3],
                        "III": [3.7, 0.4],
                        "V": [5.6, 0.5]
                    }
                }
            }
        },
        "estacion_4": { ... },
        "estacion_5": { ... }
    }
}
```

## Ubicación de Archivos
- **Código modificado:** `src/main/python/main.py`
- **Resultados guardados:** `src/main/resources/base/resultados_osce/`

## Características Importantes

### Seguridad y Control
- ✅ No se puede saltar estaciones (secuencial obligatorio)
- ✅ No se pueden cerrar diálogos accidentalmente
- ✅ Cada estación usa un caso aleatorio diferente
- ✅ Timer de 5 minutos estricto por estación
- ✅ Datos persistentes de cada estación

### Almacenamiento
- ✅ Datos separados por estación
- ✅ Copia profunda de memoria para evitar referencias
- ✅ JSON con timestamp único
- ✅ Incluye fecha ISO y número de caso
- ✅ Estructura organizada y legible

### UI/UX
- ✅ Botones grandes y claros
- ✅ Marcas visuales de progreso (✓)
- ✅ Labels informativos de estado
- ✅ Ventana centrada en pantalla
- ✅ Mensajes específicos por estación
- ✅ Confirmación al completar todo

## Compatibilidad
El sistema mantiene compatibilidad con los modos anteriores:
- **Modo "test":** Práctica libre (sin cambios)
- **Modo "exam":** Evaluación de 2 casos con 40 minutos (sin cambios)
- **Modo "osce":** Nuevo sistema de 3 estaciones con 5 minutos cada una

## Configuración
Para cambiar el modo, editar en `main.py` línea 41:
```python
STATE_INIT = "osce"  # o "exam" o "test"
```

Para cambiar tiempo de estaciones, editar línea 43:
```python
TIEMPO_ESTACION_OSCE = 5  # minutos por estación
```

## Próximos Pasos Sugeridos
1. ✅ Probar flujo completo manualmente
2. ⏳ Verificar que los datos se guarden correctamente
3. ⏳ Probar con varios estudiantes consecutivos
4. ⏳ Validar que el reset funcione correctamente
5. ⏳ Considerar añadir identificación de estudiante (RUT/Nombre)
6. ⏳ Posible generación de reportes PDF por estación

## Notas Técnicas
- Se usa `copy.deepcopy()` para evitar referencias compartidas en memoria
- Los casos son aleatorios por estación (evita repetición)
- El sistema previene cierre accidental en puntos críticos
- Compatible con el sistema de verificación de activación existente
