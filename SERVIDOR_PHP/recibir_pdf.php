<?php
/**
 * Script PHP para recibir PDFs de evaluaciones OSCE - PEATC
 * URL: https://tmeduca.org/osce/recibir_pdf.php
 * Universidad Austral de Chile - Sede Puerto Montt
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// Configuración
$directorio_pdfs = __DIR__ . '/pdfs_osce/';
$directorio_html = __DIR__ . '/html_osce/';
$directorio_json = __DIR__ . '/json_osce/';
$directorio_imagenes = __DIR__ . '/imagenes_osce/';

// Crear directorios si no existen
$directorios = [$directorio_pdfs, $directorio_html, $directorio_json, $directorio_imagenes];
foreach ($directorios as $dir) {
    if (!file_exists($dir)) {
        mkdir($dir, 0755, true);
    }
}

// Verificar que se recibió un archivo
if (!isset($_FILES['pdf']) || $_FILES['pdf']['error'] !== UPLOAD_ERR_OK) {
    echo json_encode([
        'exito' => false,
        'error' => 'No se recibió el archivo PDF correctamente',
        'codigo_error' => $_FILES['pdf']['error'] ?? 'desconocido'
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// Obtener datos adicionales
$nombre_estudiante = $_POST['nombre_estudiante'] ?? 'Desconocido';
$numero_estudiante = $_POST['numero_estudiante'] ?? 'N/A';
$tipo = $_POST['tipo'] ?? 'osce_peatc';

// Generar timestamp y nombre sanitizado
$timestamp = date('Y-m-d_H-i-s');
$nombre_sanitizado = preg_replace('/[^a-zA-Z0-9_-]/', '_', $numero_estudiante);
$nombre_base = "OSCE_PEATC_{$nombre_sanitizado}_{$timestamp}";

// Nombres de archivos
$nombre_pdf = $nombre_base . ".pdf";
$nombre_metadata = $nombre_base . ".json";
$ruta_pdf = $directorio_pdfs . $nombre_pdf;
$ruta_metadata = $directorio_json . $nombre_metadata;

// Mover archivo PDF subido
if (!move_uploaded_file($_FILES['pdf']['tmp_name'], $ruta_pdf)) {
    echo json_encode([
        'exito' => false,
        'error' => 'Error al guardar el archivo PDF en el servidor'
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// Recibir archivo HTML si existe
if (isset($_FILES['html']) && $_FILES['html']['error'] === UPLOAD_ERR_OK) {
    $nombre_html = $nombre_base . ".html";
    $ruta_html = $directorio_html . $nombre_html;
    move_uploaded_file($_FILES['html']['tmp_name'], $ruta_html);
}

// Recibir archivo JSON de datos si existe
if (isset($_FILES['datos_json']) && $_FILES['datos_json']['error'] === UPLOAD_ERR_OK) {
    $nombre_datos_json = $nombre_base . "_datos.json";
    $ruta_datos_json = $directorio_json . $nombre_datos_json;
    move_uploaded_file($_FILES['datos_json']['tmp_name'], $ruta_datos_json);
}

// Recibir archivos de imágenes si existen
if (isset($_FILES['imagenes'])) {
    $dir_imagenes_caso = $directorio_imagenes . $nombre_base . '/';
    if (!file_exists($dir_imagenes_caso)) {
        mkdir($dir_imagenes_caso, 0755, true);
    }

    // $_FILES['imagenes'] puede ser un array de archivos
    $archivos_imagenes = $_FILES['imagenes'];

    // Verificar si es un array de múltiples archivos
    if (is_array($archivos_imagenes['name'])) {
        for ($i = 0; $i < count($archivos_imagenes['name']); $i++) {
            if ($archivos_imagenes['error'][$i] === UPLOAD_ERR_OK) {
                $nombre_imagen = basename($archivos_imagenes['name'][$i]);
                $ruta_imagen = $dir_imagenes_caso . $nombre_imagen;
                move_uploaded_file($archivos_imagenes['tmp_name'][$i], $ruta_imagen);
            }
        }
    } else {
        // Un solo archivo
        if ($archivos_imagenes['error'] === UPLOAD_ERR_OK) {
            $nombre_imagen = basename($archivos_imagenes['name']);
            $ruta_imagen = $dir_imagenes_caso . $nombre_imagen;
            move_uploaded_file($archivos_imagenes['tmp_name'], $ruta_imagen);
        }
    }
}

// Guardar metadatos
$metadatos = [
    'nombre_estudiante' => $nombre_estudiante,
    'numero_estudiante' => $numero_estudiante,
    'tipo' => $tipo,
    'fecha_subida' => date('Y-m-d H:i:s'),
    'timestamp_unix' => time(),
    'archivo_pdf' => $nombre_pdf,
    'ip_origen' => $_SERVER['REMOTE_ADDR'] ?? 'desconocida',
    'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'desconocido',
    'tamanio_bytes' => filesize($ruta_pdf)
];

file_put_contents(
    $ruta_metadata,
    json_encode($metadatos, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)
);

// Registrar en log general
$log_file = __DIR__ . '/osce_log.txt';
$log_entry = sprintf(
    "[%s] PDF recibido: %s - Estudiante: %s (%s) - IP: %s - Tamaño: %s bytes\n",
    date('Y-m-d H:i:s'),
    $nombre_pdf,
    $nombre_estudiante,
    $numero_estudiante,
    $_SERVER['REMOTE_ADDR'] ?? 'desconocida',
    filesize($ruta_pdf)
);
file_put_contents($log_file, $log_entry, FILE_APPEND);

// Respuesta exitosa
$url_base = 'https://tmeduca.org/osce/';
echo json_encode([
    'exito' => true,
    'mensaje' => 'PDF recibido y guardado correctamente',
    'archivo' => $nombre_pdf,
    'url_pdf' => $url_base . 'pdfs_osce/' . $nombre_pdf,
    'url_visualizacion' => $url_base . 'ver_pdf.php?archivo=' . urlencode($nombre_pdf),
    'timestamp' => $timestamp,
    'tamanio' => filesize($ruta_pdf)
], JSON_UNESCAPED_UNICODE);
?>
