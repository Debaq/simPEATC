# CLAUDE.md - simPEATC

## Resumen del Proyecto

**simPEATC** es un simulador educativo de Potenciales Evocados Auditivos de Tronco Cerebral (PEATC/ABR - Auditory Brainstem Response) desarrollado en Python con interfaz gráfica PySide6 (Qt6). El proyecto está diseñado para estudiantes de electrofisiología auditiva de la Universidad Austral de Chile - Sede Puerto Montt.

### Información General
- **Nombre**: simPEATC (Simulador de Potenciales Evocados de Tronco Cerebral)
- **Versión**: 0.0.0
- **Autor Principal**: Nicolás Quezada Quezada (código base) / David Ávila Quezada (investigador principal)
- **Licencia**: MIT
- **Framework**: fbs (fman build system) para empaquetado
- **GUI**: PySide6 (Qt6)

## Arquitectura del Proyecto

### Estructura de Directorios

```
simPEATC/
├── src/
│   ├── main/
│   │   ├── python/
│   │   │   ├── main.py              # Punto de entrada principal
│   │   │   ├── base.py              # Contexto de la aplicación
│   │   │   ├── verificacion.py     # Sistema de activación online
│   │   │   ├── UI/                  # Interfaces Qt generadas
│   │   │   │   ├── AbrMain_ui.py
│   │   │   │   ├── AbrControl_ui.py
│   │   │   │   ├── AbrReport_ui.py
│   │   │   │   └── ...
│   │   │   └── lib/                 # Lógica de negocio
│   │   │       ├── ABR_generator_v2.py    # Generador de curvas ABR
│   │   │       ├── AbrControl.py          # Panel de control
│   │   │       ├── AbrGraph.py            # Gráficos de curvas
│   │   │       ├── AbrTable.py            # Tablas de latencias/amplitudes
│   │   │       ├── AbrReport.py           # Generación de reportes
│   │   │       ├── PdfCreator.py          # Creación de PDFs
│   │   │       ├── EEG.py                 # Simulación de EEG
│   │   │       ├── FSP.py                 # Factor Señal/Promedio
│   │   │       ├── conbinaciones.py       # Casos clínicos
│   │   │       └── ...
│   │   └── resources/
│   │       └── base/
│   │           ├── json/            # Configuraciones
│   │           │   ├── ABR.json
│   │           │   ├── normative_data.json
│   │           │   └── abr_confg.json
│   │           ├── cases/           # Casos clínicos
│   │           │   └── cases.json
│   │           └── qss/             # Estilos Qt
│   └── build/
│       └── settings/                # Configuración de empaquetado
│           ├── base.json
│           ├── linux.json
│           └── mac.json
├── Images/                          # Imágenes y recursos gráficos
├── target/                          # Build output (PyInstaller)
├── README.md
└── install.txt                      # Dependencias
```

## Componentes Principales

### 1. Sistema de Ventanas (main.py)

**MainWindow** es la clase principal que gestiona toda la aplicación:

- **Gestión de estado**: Controla el modo de operación (test/exam)
- **Temporizador**: Sistema de tiempo límite para evaluaciones (40 minutos por caso)
- **Captura de señales**: Simula la adquisición de potenciales evocados
- **Gestión de casos**: Sistema de casos clínicos aleatorios o específicos
- **Memoria de curvas**: Almacena y gestiona todas las curvas capturadas

#### Modos de Operación
- **test**: Modo de práctica libre, sin límite de tiempo
- **exam**: Modo evaluación con 2 casos y 40 minutos por caso

### 2. Generador de Curvas ABR (ABR_generator_v2.py)

**ABRGenerator** es el núcleo del simulador:

#### Características Principales:
- **Sistema FSP (Factor Señal/Promedio)**: Simula la mejora progresiva de la señal según las promediaciones
- **Transición progresiva**: Genera evolución desde ruido aleatorio → curva objetivo
- **Datos normativos**: Utiliza valores de referencia clínica
- **Casos clínicos**: Diferentes patologías y condiciones auditivas

#### Parámetros de Simulación:
- Latencias absolutas de ondas I, III, V
- Intervalos interpicos (I-III, III-V, I-V)
- Reproducibilidad (±0.1 ms)
- Morfología de ondas
- Ratio V/I
- Diferencias interaurales

### 3. Interfaz Gráfica

#### Componentes UI:
- **AbrControl**: Panel de control de parámetros (intensidad, lado, promediaciones, etc.)
- **AbrGraph**: Visualización de curvas ABR (oído derecho e izquierdo)
- **AbrTable**: Tablas de mediciones de latencias y amplitudes
- **AbrDetail**: Panel de detalles con EEG y FSP
- **AbrReport**: Generador de reportes en HTML/PDF
- **GraphLatInt**: Gráficos de latencias-intensidad

### 4. Sistema de Casos (conbinaciones.py)

Define casos clínicos con diferentes características:
- Configuraciones normales
- Patologías específicas
- Variaciones de reproducibilidad
- Diferentes umbrales auditivos

### 5. Generación de Reportes (PdfCreator.py)

Genera PDFs con:
- Curvas ABR de ambos oídos
- Gráficos latencia-intensidad
- Tablas de mediciones
- Datos del evaluado
- Interpretación clínica

### 6. Sistema de Verificación (verificacion.py)

**Sistema de activación online**:
- Consulta servidor: `https://tmeduca.org/abr_activate.php`
- Requiere conexión a internet
- Muestra mensajes de error si la versión está desactivada
- Maneja timeouts y errores de conexión

## Dependencias Principales

```
PySide6==6.9.3              # Framework Qt6
numpy==2.3.3                # Cálculos numéricos
scipy==1.16.2               # Procesamiento de señales
pyqtgraph==0.13.7           # Gráficos científicos
fpdf==1.7.2                 # Generación de PDFs
PyMuPDF==1.26.4             # Manipulación de PDFs
pyinstaller==6.16.0         # Empaquetado
fbs==1.1.2                  # Build system
requests==2.32.5            # Verificación online
watchdog==6.0.0             # Monitor de archivos
```

## Flujo de Trabajo de la Aplicación

### Inicio
1. Verificación de activación (consulta servidor)
2. Mostrar diálogo de inicio (Test o Examen)
3. En modo Examen: Solicitar nombre e iniciar timer
4. Cargar casos clínicos desde `cases.json`

### Captura de Señal
1. Usuario configura parámetros (intensidad, lado, promediaciones)
2. Presiona "Grabar"
3. El sistema:
   - Crea nueva curva en memoria
   - Inicia timer de captura (300ms entre promediaciones)
   - Genera curva ABR progresivamente usando `ABR_generator_v2`
   - Actualiza gráficos en tiempo real
   - Calcula FSP según promediaciones acumuladas

### Análisis
1. Usuario marca ondas (I, II, III, IV, V)
2. Sistema calcula latencias y amplitudes
3. Almacena en memoria y tablas
4. Genera gráficos latencia-intensidad

### Reporte
1. Exporta SVG de gráficos a PNG
2. Combina texto HTML con imágenes
3. Genera PDF final con `PdfCreator`

## Características Técnicas

### Sistema de Promediaciones
- **Simulación realista**: No usa el número real de promediaciones
- **Fórmula de ajuste**: `a * (averages^b)` donde a=0.52991151, b=0.52207181
- **Tiempo entre promediaciones**: 300ms (TIEMPO_ENTR_PROM)

### Almacenamiento de Curvas
Estructura en memoria:
```python
{
    'R1': {  # Curva oído derecho 1
        'side': 'OD',
        'int': 75,
        'average': 2000,
        'LatAmp': {
            'I': [latencia, amplitud],
            'II': [latencia, amplitud],
            'III': [latencia, amplitud],
            'IV': [latencia, amplitud],
            'V': [latencia, amplitud]
        }
    }
}
```

### Sistema de Coordenadas
- Eje X: Tiempo en ms (0-12ms típicamente)
- Eje Y: Amplitud en μV
- Escalado dinámico con botones +/-

## Valores de Referencia Clínica

### Latencias Absolutas a 75 dBnHL (±0.2ms)
- Onda I: 1.6 ms
- Onda III: 3.7 ms
- Onda V: 5.6 ms

### Intervalos Interpicos (±0.4ms)
- I-III: 2.0 ms
- III-V: 1.8 ms
- I-V: 3.8 ms

### Otros Parámetros
- Reproducibilidad: ±0.1 ms
- Desviación por 10 dB: 0.3 ms
- Ratio V/I: > 1
- Diferencia interaural: < 0.4 ms

## Empaquetado y Distribución

### Build con fbs/PyInstaller
```bash
# Instalar fbs pro
pip install https://build-system.fman.io/pro/12a9a98c-755b-4d95-9c60-a17ae1a74d6c/0.9.8#egg=fbs

# Generar ejecutable
fbs freeze
```

### Configuración
- **Linux**: `src/build/settings/linux.json`
- **Mac**: `src/build/settings/mac.json`
- **Base**: `src/build/settings/base.json`

## Áreas Clave para Modificaciones

### 1. Añadir Nuevos Casos Clínicos
**Archivo**: `src/main/python/lib/conbinaciones.py`
- Añadir casos a la lista `combinaciones`
- Definir parámetros específicos de cada patología

### 2. Modificar Generación de Curvas
**Archivo**: `src/main/python/lib/ABR_generator_v2.py`
- Ajustar algoritmo FSP: método `calcular_fsp()`
- Modificar ruido: método `generar_caos_inicial()`
- Cambiar curva objetivo: clase `ABRGenerator`

### 3. Personalizar Interfaz
**Archivos**: `src/main/python/UI/*.py`
- Modificar archivos `.ui` en Qt Designer
- Regenerar archivos Python con `pyside6-uic`

### 4. Cambiar Reportes PDF
**Archivo**: `src/main/python/lib/PdfCreator.py`
- Modificar layout de PDF
- Añadir secciones al reporte

### 5. Ajustar Datos Normativos
**Archivo**: `src/main/resources/base/json/normative_data.json`
- Actualizar valores de referencia clínica
- Modificar rangos de normalidad

### 6. Modificar Sistema de Activación
**Archivo**: `src/main/python/verificacion.py`
- Cambiar URL de verificación
- Modificar lógica de activación
- Añadir modo offline

### 7. Estilos Visuales
**Archivo**: `src/main/resources/base/qss/style_base.qss`
- Modificar colores y fuentes
- Ajustar diseño Qt con CSS

## Consideraciones para Desarrollo

### Estado Actual del Proyecto
- ✅ GUI principal completa
- ✅ Generación de curvas ABR
- ✅ Sistema de casos
- 🚧 i18n (internacionalización en construcción)
- 🚧 Configuración de hardware

### Limitaciones Conocidas
1. **Dependencia de internet**: Requiere conexión para verificar activación
2. **Modo examen bloqueado**: No se puede cerrar sin ingresar nombre
3. **Timer fijo**: 40 minutos por caso (hardcoded en `TIEMPO_TEST`)
4. **Observador de archivos**: Deshabilitado en producción (líneas comentadas en main.py:675-683)

### Debugging
- Variables de estado en `main.py` líneas 290-323
- Constantes globales: `STATE_INIT`, `TIEMPO_TEST`, `N_CASES`
- Print statements para tracing (línea 491, 652, etc.)

## Contexto Educativo

### Objetivo Pedagógico
Simular el proceso completo de realización de PEATC:
1. Colocación de electrodos (visual)
2. Configuración de parámetros
3. Captura de señales
4. Identificación de ondas
5. Medición de latencias
6. Interpretación clínica
7. Generación de informe

### Casos Clínicos Simulados
El sistema genera casos que representan:
- Audición normal
- Hipoacusias conductivas
- Hipoacusias neurosensoriales
- Neuropatías auditivas
- Diferentes grados de pérdida auditiva

## Comandos Útiles

### Instalación de Dependencias
```bash
pip install -r install.txt
```

### Ejecutar Aplicación
```bash
python src/main/python/main.py
```

### Generar Interfaces Qt
```bash
pyside6-uic archivo.ui -o archivo_ui.py
```

## Notas de Seguridad

⚠️ **Sistema de Verificación**: El archivo `verificacion.py` implementa un sistema de activación que consulta un servidor externo. Para desarrollo local, considerar:
- Comentar líneas 700-701 en `main.py` para deshabilitar verificación
- Modificar `verificar_activacion()` para retornar siempre `True`

## Recursos Externos

### Enlaces
- **Universidad**: http://www.pmontt.uach.cl/
- **Tecnología Médica**: http://tmedicapm.uach.cl/
- **Repositorio**: https://github.com/Debaq/simPEATC

### Imágenes de Referencia
- Logo: `Images/logo.png`
- Screenshots: `Images/Screenshot1.png`
- Demo GIF: `Images/video.gif`

## Para Claude: Contexto Rápido

Si necesitas hacer modificaciones:

1. **Backend de simulación**: ABR_generator_v2.py
2. **Lógica principal**: main.py (clase MainWindow)
3. **Casos clínicos**: conbinaciones.py
4. **Visualización**: AbrGraph.py, pyqtgraph
5. **Datos**: JSON files en resources/base/

La aplicación es un simulador educativo médico que genera curvas auditivas realistas basadas en modelos matemáticos de señales biológicas.
