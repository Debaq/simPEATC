"""
Módulo para enviar archivos PDF a un servidor PHP para impresión remota
Versión 1.0
"""

import requests
import os
from pathlib import Path


class EnviadorPDF:
    """Clase para enviar PDFs a un servidor PHP"""

    def __init__(self, url_servidor="https://tmeduca.org/osce/recibir_pdf.php"):
        """
        Inicializa el enviador de PDF

        Args:
            url_servidor: URL del script PHP que recibirá el PDF
        """
        self.url_servidor = url_servidor

    def enviar_pdf(self, ruta_pdf, datos_adicionales=None):
        """
        Envía un archivo PDF al servidor PHP

        Args:
            ruta_pdf: Ruta completa al archivo PDF
            datos_adicionales: dict con datos adicionales a enviar (nombre, número estudiante, etc.)

        Returns:
            dict con:
                - 'exito': bool indicando si el envío fue exitoso
                - 'mensaje': str con mensaje de respuesta del servidor
                - 'url_impresion': str con URL para imprimir (si aplica)
                - 'error': str con mensaje de error (si aplica)
        """
        # Verificar que el archivo existe
        if not os.path.exists(ruta_pdf):
            return {
                'exito': False,
                'mensaje': '',
                'error': f'El archivo no existe: {ruta_pdf}'
            }

        # Verificar que es un PDF
        if not ruta_pdf.lower().endswith('.pdf'):
            return {
                'exito': False,
                'mensaje': '',
                'error': 'El archivo debe ser un PDF'
            }

        try:
            # Preparar el archivo para envío
            with open(ruta_pdf, 'rb') as pdf_file:
                files = {
                    'pdf': (os.path.basename(ruta_pdf), pdf_file, 'application/pdf')
                }

                # Preparar datos adicionales
                data = datos_adicionales or {}

                # Realizar la solicitud POST
                print(f"Enviando PDF a: {self.url_servidor}")
                print(f"Archivo: {os.path.basename(ruta_pdf)}")
                print(f"Tamaño: {os.path.getsize(ruta_pdf)} bytes")

                response = requests.post(
                    self.url_servidor,
                    files=files,
                    data=data,
                    timeout=30  # Timeout de 30 segundos
                )

                # Verificar respuesta
                if response.status_code == 200:
                    try:
                        # Intentar parsear JSON
                        resultado = response.json()
                        return {
                            'exito': resultado.get('exito', True),
                            'mensaje': resultado.get('mensaje', 'PDF enviado correctamente'),
                            'url_impresion': resultado.get('url_impresion', ''),
                            'error': resultado.get('error', '')
                        }
                    except ValueError:
                        # Si no es JSON, usar texto plano
                        return {
                            'exito': True,
                            'mensaje': response.text,
                            'url_impresion': '',
                            'error': ''
                        }
                else:
                    return {
                        'exito': False,
                        'mensaje': '',
                        'error': f'Error HTTP {response.status_code}: {response.text}'
                    }

        except requests.exceptions.Timeout:
            return {
                'exito': False,
                'mensaje': '',
                'error': 'Timeout: El servidor no respondió en 30 segundos'
            }
        except requests.exceptions.ConnectionError:
            return {
                'exito': False,
                'mensaje': '',
                'error': f'Error de conexión: No se pudo conectar al servidor {self.url_servidor}'
            }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': '',
                'error': f'Error inesperado: {str(e)}'
            }


def enviar_pdf_osce(ruta_pdf, nombre_estudiante, numero_estudiante, url_servidor=None):
    """
    Función de conveniencia para enviar PDFs de OSCE

    Args:
        ruta_pdf: Ruta al archivo PDF
        nombre_estudiante: Nombre completo del estudiante
        numero_estudiante: Número de estudiante
        url_servidor: URL del servidor PHP (opcional)

    Returns:
        dict con resultado del envío
    """
    # Usar URL por defecto si no se proporciona
    if url_servidor is None:
        url_servidor = "https://tmeduca.org/osce/recibir_pdf.php"

    enviador = EnviadorPDF(url_servidor=url_servidor)

    datos_adicionales = {
        'nombre_estudiante': nombre_estudiante,
        'numero_estudiante': numero_estudiante,
        'tipo': 'osce_peatc'
    }

    return enviador.enviar_pdf(ruta_pdf, datos_adicionales)


# ============================================================================
# Script PHP de ejemplo para el servidor
# ============================================================================

SCRIPT_PHP_EJEMPLO = """<?php
/**
 * Script PHP para recibir PDFs de evaluaciones OSCE
 * Guarda los archivos y genera una URL para impresión
 */

header('Content-Type: application/json');

// Configuración
$directorio_pdfs = __DIR__ . '/pdfs_osce/';
$url_base = 'http://' . $_SERVER['HTTP_HOST'] . '/osce/pdfs_osce/';

// Crear directorio si no existe
if (!file_exists($directorio_pdfs)) {
    mkdir($directorio_pdfs, 0755, true);
}

// Verificar que se recibió un archivo
if (!isset($_FILES['pdf']) || $_FILES['pdf']['error'] !== UPLOAD_ERR_OK) {
    echo json_encode([
        'exito' => false,
        'error' => 'No se recibió el archivo PDF correctamente'
    ]);
    exit;
}

// Obtener datos adicionales
$nombre_estudiante = $_POST['nombre_estudiante'] ?? 'Desconocido';
$numero_estudiante = $_POST['numero_estudiante'] ?? 'N/A';

// Generar nombre único para el archivo
$timestamp = date('Y-m-d_H-i-s');
$nombre_sanitizado = preg_replace('/[^a-zA-Z0-9_-]/', '_', $numero_estudiante);
$nombre_archivo = "OSCE_{$nombre_sanitizado}_{$timestamp}.pdf";
$ruta_destino = $directorio_pdfs . $nombre_archivo;

// Mover archivo subido
if (move_uploaded_file($_FILES['pdf']['tmp_name'], $ruta_destino)) {
    // Guardar metadatos en un archivo JSON
    $metadatos = [
        'nombre_estudiante' => $nombre_estudiante,
        'numero_estudiante' => $numero_estudiante,
        'fecha_subida' => date('Y-m-d H:i:s'),
        'archivo_pdf' => $nombre_archivo,
        'ip_origen' => $_SERVER['REMOTE_ADDR']
    ];

    file_put_contents(
        $directorio_pdfs . $nombre_sanitizado . '_' . $timestamp . '.json',
        json_encode($metadatos, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)
    );

    // Respuesta exitosa
    echo json_encode([
        'exito' => true,
        'mensaje' => 'PDF recibido y guardado correctamente',
        'url_impresion' => $url_base . $nombre_archivo,
        'archivo' => $nombre_archivo
    ]);
} else {
    echo json_encode([
        'exito' => false,
        'error' => 'Error al guardar el archivo en el servidor'
    ]);
}
?>
"""


if __name__ == "__main__":
    # Imprimir script PHP de ejemplo
    print("="*80)
    print("SCRIPT PHP DE EJEMPLO PARA EL SERVIDOR")
    print("="*80)
    print("\nGuardar este código en: /var/www/html/osce/recibir_pdf.php\n")
    print(SCRIPT_PHP_EJEMPLO)
    print("\n" + "="*80)
    print("CONFIGURACIÓN DEL SERVIDOR")
    print("="*80)
    print("""
1. Crear directorio en el servidor:
   mkdir -p /var/www/html/osce/pdfs_osce
   chmod 755 /var/www/html/osce/pdfs_osce

2. Configurar PHP para permitir uploads grandes (php.ini):
   upload_max_filesize = 20M
   post_max_size = 20M

3. Reiniciar servidor web:
   sudo service apache2 restart  # o nginx

4. Probar acceso:
   http://TU_SERVIDOR/osce/recibir_pdf.php
    """)

    # Test de ejemplo (comentado)
    print("\n" + "="*80)
    print("EJEMPLO DE USO EN PYTHON")
    print("="*80)
    print("""
# Ejemplo de uso:
from lib.EnviarPDFServidor import enviar_pdf_osce

resultado = enviar_pdf_osce(
    ruta_pdf="/ruta/al/informe.pdf",
    nombre_estudiante="Juan Pérez",
    numero_estudiante="2021234567",
    url_servidor="http://192.168.1.100/osce/recibir_pdf.php"
)

if resultado['exito']:
    print(f"✓ PDF enviado correctamente")
    print(f"URL para imprimir: {resultado['url_impresion']}")
else:
    print(f"✗ Error: {resultado['error']}")
    """)
