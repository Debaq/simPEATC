"""
Generador de Informe Final del OSCE - PEATC
Genera un documento HTML/PDF con todos los datos de las 3 estaciones para evaluación docente
Versión 1.0
"""

import datetime
from pathlib import Path


class GeneradorInformeOSCE:
    """Genera el informe final del OSCE con todas las estaciones"""

    def __init__(self, datos_estaciones, nombre_estudiante="Estudiante", numero_estudiante="N/A", imagenes_casos=None):
        self.datos_estaciones = datos_estaciones
        self.nombre_estudiante = nombre_estudiante
        self.numero_estudiante = numero_estudiante
        self.fecha_generacion = datetime.datetime.now()
        self.imagenes_casos = imagenes_casos or {}

    def generar_html(self):
        """Genera el HTML completo del informe"""
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe OSCE - PEATC</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            font-size: 11pt;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #333;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            color: #2c3e50;
        }}
        .header .info {{
            margin-top: 10px;
            font-size: 10pt;
            color: #666;
        }}
        .estacion {{
            page-break-before: always;
            margin-bottom: 30px;
        }}
        .estacion:first-child {{
            page-break-before: avoid;
        }}
        .estacion-titulo {{
            background-color: #3498db;
            color: white;
            padding: 10px;
            margin-bottom: 15px;
            font-size: 14pt;
            font-weight: bold;
        }}
        .caso {{
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #f9f9f9;
        }}
        .caso-titulo {{
            font-weight: bold;
            font-size: 12pt;
            color: #2c3e50;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 2px solid #3498db;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        table th, table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        table th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        .informe-texto {{
            white-space: pre-wrap;
            background-color: #ffffff;
            border: 1px solid #ddd;
            padding: 10px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
        }}
        .graficos-container {{
            margin: 15px 0;
            page-break-inside: avoid;
        }}
        @media print {{
            .estacion {{
                page-break-before: always;
            }}
            .estacion:first-child {{
                page-break-before: avoid;
            }}
            img {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>INFORME OSCE - PEATC</h1>
        <div class="info">
            <p><strong>Estudiante:</strong> {self.nombre_estudiante}</p>
            <p><strong>Número:</strong> {self.numero_estudiante}</p>
            <p><strong>Fecha:</strong> {self.fecha_generacion.strftime("%d/%m/%Y %H:%M")}</p>
            <p><strong>Institución:</strong> Universidad Austral de Chile - Sede Puerto Montt</p>
        </div>
    </div>

{self._generar_estacion_3()}

{self._generar_estacion_4()}

{self._generar_estacion_5()}

</body>
</html>
        """
        return html

    def _generar_estacion_3(self):
        """Genera el HTML de la Estación 3 - Solo datos sin evaluación"""
        from lib.casos_estacion_3 import CASOS_ESTACION_3

        estacion_3 = self.datos_estaciones.get(3, {})
        casos = estacion_3.get('casos', {})

        html_casos = ""

        for num_caso in [1, 2, 3]:
            caso_data = casos.get(num_caso, {})
            configuracion = caso_data.get('configuracion', {})

            # Información del caso esperado
            caso_esperado = CASOS_ESTACION_3.get(num_caso, {})
            nombre_caso = caso_esperado.get('nombre', f'Caso {num_caso}')
            instrucciones = caso_esperado.get('instrucciones', '')

            # Tabla de configuración - SOLO DATOS, SIN VALIDACIÓN
            config_html = "<table><tr><th>Parámetro</th><th>Valor Configurado</th></tr>"
            for param, valor in configuracion.items():
                config_html += f"<tr><td>{param}</td><td>{valor}</td></tr>"
            config_html += "</table>"

            html_casos += f"""
            <div class="caso">
                <div class="caso-titulo">Caso {num_caso}: {nombre_caso}</div>
                <p><strong>Contexto clínico:</strong> {instrucciones}</p>
                <h4>Configuración realizada:</h4>
                {config_html}
            </div>
            """

        return f"""
    <div class="estacion">
        <div class="estacion-titulo">ESTACIÓN 3: CONFIGURACIÓN DEL EQUIPO</div>
        {html_casos}
    </div>
        """

    def _generar_estacion_4(self):
        """Genera el HTML de la Estación 4"""
        import base64
        import os

        estacion_4 = self.datos_estaciones.get(4, {})
        casos = estacion_4.get('casos', {})

        html_casos = ""

        descripciones_casos = {
            1: "OD: Normal, OI: Transmisión/Conductivo",
            2: "OD: Coclear, OI: Normal",
            3: "OD: Neural (Schwannoma), OI: Neural (Schwannoma)"
        }

        for num_caso in [1, 2, 3]:
            caso_data = casos.get(num_caso, {})
            memory = caso_data.get('memory', {})
            case_id = caso_data.get('case_id', 'N/A')

            descripcion = descripciones_casos.get(num_caso, f'Caso {num_caso}')

            # Resumen de curvas capturadas
            curvas_od = [k for k in memory.keys() if k.startswith('R')]
            curvas_oi = [k for k in memory.keys() if k.startswith('L')]

            curvas_html = f"""
            <p><strong>Curvas capturadas:</strong></p>
            <ul>
                <li>Oído Derecho: {len(curvas_od)} curvas</li>
                <li>Oído Izquierdo: {len(curvas_oi)} curvas</li>
            </ul>
            """

            # Gráficos de curvas ABR
            graficos_html = ""
            imagenes_caso = self.imagenes_casos.get(num_caso, {})

            if imagenes_caso:
                graficos_html += "<h4>Gráficos de Curvas ABR:</h4>"
                graficos_html += "<div style='display: flex; justify-content: space-between; margin: 15px 0;'>"

                # Gráfico OD
                img_od = imagenes_caso.get('OD')
                if img_od and os.path.exists(img_od):
                    with open(img_od, 'rb') as f:
                        img_data_od = base64.b64encode(f.read()).decode()
                    graficos_html += f"""
                    <div style='width: 48%;'>
                        <h5 style='text-align: center; margin-bottom: 5px;'>Oído Derecho</h5>
                        <img src="data:image/png;base64,{img_data_od}" style="width: 100%; border: 1px solid #ddd;" />
                    </div>
                    """

                # Gráfico OI
                img_oi = imagenes_caso.get('OI')
                if img_oi and os.path.exists(img_oi):
                    with open(img_oi, 'rb') as f:
                        img_data_oi = base64.b64encode(f.read()).decode()
                    graficos_html += f"""
                    <div style='width: 48%;'>
                        <h5 style='text-align: center; margin-bottom: 5px;'>Oído Izquierdo</h5>
                        <img src="data:image/png;base64,{img_data_oi}" style="width: 100%; border: 1px solid #ddd;" />
                    </div>
                    """

                graficos_html += "</div>"

                # Gráfico Latencia-Intensidad
                img_lat = imagenes_caso.get('LatInt')
                if img_lat and os.path.exists(img_lat):
                    with open(img_lat, 'rb') as f:
                        img_data_lat = base64.b64encode(f.read()).decode()
                    graficos_html += f"""
                    <h5 style='text-align: center; margin-top: 15px; margin-bottom: 5px;'>Gráfico Latencia-Intensidad</h5>
                    <div style='text-align: center; margin: 10px 0;'>
                        <img src="data:image/png;base64,{img_data_lat}" style="width: 80%; max-width: 800px; border: 1px solid #ddd;" />
                    </div>
                    """

            # Detalles de cada curva
            detalles_html = "<h4>Detalles de las curvas:</h4>"
            for curve_id, curve_data in memory.items():
                lado = curve_data.get('side', 'N/A')
                intensidad = curve_data.get('int', 'N/A')
                promediaciones = curve_data.get('average', 'N/A')
                lat_amp = curve_data.get('LatAmp', {})

                ondas_marcadas = []
                for onda in ['I', 'II', 'III', 'IV', 'V']:
                    # Solo incluir ondas que tengan al menos un valor real (no None)
                    if onda in lat_amp and lat_amp[onda]:
                        lat, amp = lat_amp[onda]
                        # Verificar que al menos uno de los valores no sea None
                        if lat is not None or amp is not None:
                            if lat is not None and amp is not None:
                                ondas_marcadas.append(f"{onda}: Lat={lat:.2f}ms, Amp={amp:.2f}μV")
                            else:
                                ondas_marcadas.append(f"{onda}: Marcada (sin medición)")

                detalles_html += f"""
                <div style="margin-left: 20px; margin-bottom: 10px; border-left: 3px solid #3498db; padding-left: 10px;">
                    <strong>{curve_id}</strong> - {lado} @ {intensidad} dB, {promediaciones} prom.
                    <br>Ondas: {', '.join(ondas_marcadas) if ondas_marcadas else 'Ninguna marcada'}
                </div>
                """

            html_casos += f"""
            <div class="caso">
                <div class="caso-titulo">Caso {num_caso}: {descripcion}</div>
                <p><strong>ID de caso:</strong> {case_id}</p>
                {curvas_html}
                {graficos_html}
                {detalles_html}
            </div>
            """

        return f"""
    <div class="estacion">
        <div class="estacion-titulo">ESTACIÓN 4: OBTENCIÓN DEL REGISTRO</div>
        {html_casos}
    </div>
        """

    def _generar_estacion_5(self):
        """Genera el HTML de la Estación 5 - Solo datos sin evaluación"""
        estacion_5 = self.datos_estaciones.get(5, {})
        caso_3_data = estacion_5.get('casos', {}).get(3, {})
        informe = caso_3_data.get('informe', {})

        if not informe:
            informe_html = """
            <div class="caso">
                <p><em>El estudiante no completó el informe de esta estación.</em></p>
            </div>
            """
        else:
            datos_caso = informe.get('datos_caso', {})
            hallazgos = informe.get('hallazgos', '')
            normativos = informe.get('normativos', '')
            conclusion = informe.get('conclusion', '')

            informe_html = f"""
            <div class="caso">
                <h3>Datos del Caso</h3>
                <p><strong>Identificación:</strong> {datos_caso.get('identificacion', 'No especificada')}</p>
                <p><strong>Fecha:</strong> {datos_caso.get('fecha', 'No especificada')}</p>
                <p><strong>Condiciones:</strong> {datos_caso.get('condiciones', 'No especificadas')}</p>
            </div>

            <div class="caso">
                <h3>Descripción de Hallazgos</h3>
                <div class="informe-texto">{hallazgos if hallazgos else '<em>(No completado)</em>'}</div>
            </div>

            <div class="caso">
                <h3>Conclusión Diagnóstica</h3>
                <div class="informe-texto">{conclusion if conclusion else '<em>(No completado)</em>'}</div>
            </div>
            """

        return f"""
    <div class="estacion">
        <div class="estacion-titulo">ESTACIÓN 5: INTERPRETACIÓN E INFORME</div>
        {informe_html}
    </div>
        """

    def guardar_html(self, ruta_archivo):
        """Guarda el informe en un archivo HTML"""
        html = self.generar_html()
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Informe guardado en: {ruta_archivo}")
        return ruta_archivo

    def guardar_pdf(self, ruta_archivo):
        """
        Guarda el informe en PDF usando wkhtmltopdf o weasyprint
        Nota: Requiere tener instalado wkhtmltopdf o weasyprint
        """
        html = self.generar_html()

        # Intentar con weasyprint primero
        try:
            from weasyprint import HTML
            HTML(string=html).write_pdf(ruta_archivo)
            print(f"PDF generado exitosamente: {ruta_archivo}")
            return ruta_archivo
        except ImportError:
            print("weasyprint no está instalado. Intentando con pdfkit...")

        # Si weasyprint no está disponible, intentar con pdfkit
        try:
            import pdfkit
            pdfkit.from_string(html, ruta_archivo)
            print(f"PDF generado exitosamente: {ruta_archivo}")
            return ruta_archivo
        except ImportError:
            print("pdfkit no está instalado.")

        # Si ninguno está disponible, guardar como HTML
        print("No se pudo generar PDF. Guardando como HTML...")
        ruta_html = ruta_archivo.replace('.pdf', '.html')
        return self.guardar_html(ruta_html)


if __name__ == "__main__":
    # Ejemplo de uso con datos de prueba
    datos_prueba = {
        3: {
            'casos': {
                1: {
                    'configuracion': {
                        'stim': 'Click',
                        'pol': 'Alternante',
                        'rate': 21.1,
                        'filter_down': '100',
                        'filter_passhigh': '3000',
                        'average': 2000,
                        'ventana': 12,
                        'transductor': 'Fono inserción'
                    },
                    'validacion': {
                        'correcto': True,
                        'puntaje': 8,
                        'errores': [],
                        'advertencias': []
                    }
                },
                2: {
                    'configuracion': {
                        'stim': 'Click',
                        'pol': 'Alternante',
                        'rate': 21.1,
                        'filter_down': '100',
                        'average': 2000
                    },
                    'validacion': {
                        'correcto': False,
                        'puntaje': 0,
                        'errores': ['rate: 21.1 (esperado: 11.1)', 'ventana: 12 (esperado: 15)']
                    }
                },
                3: {
                    'configuracion': {},
                    'validacion': {}
                }
            }
        },
        4: {
            'casos': {
                3: {
                    'memory': {
                        'R1': {
                            'side': 'OD',
                            'int': 80,
                            'average': 2000,
                            'LatAmp': {
                                'I': [1.6, 0.5],
                                'III': [3.7, 0.6],
                                'V': [5.6, 0.8]
                            }
                        }
                    }
                }
            }
        },
        5: {
            'casos': {
                3: {
                    'informe': {
                        'datos_caso': {
                            'identificacion': 'Caso 3',
                            'fecha': '2025-11-30',
                            'condiciones': 'Simulación OSCE'
                        },
                        'hallazgos': 'OD: Latencias normales...',
                        'normativos': 'Dentro de rangos...',
                        'conclusion': 'Compatible con lesión neural...'
                    }
                }
            }
        }
    }

    generador = GeneradorInformeOSCE(datos_prueba, nombre_estudiante="Juan Pérez")
    generador.guardar_html("/tmp/informe_osce.html")
    print("Informe de prueba generado en /tmp/informe_osce.html")
