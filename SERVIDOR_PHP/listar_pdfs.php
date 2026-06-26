<?php
/**
 * API para listar PDFs de evaluaciones OSCE
 * URL: https://tmeduca.org/osce/listar_pdfs.php
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// Configuración
$directorio_pdfs = __DIR__ . '/pdfs_osce/';
$directorio_json = __DIR__ . '/json_osce/';

// Verificar que los directorios existen
if (!file_exists($directorio_pdfs) || !file_exists($directorio_json)) {
    echo json_encode([
        'exito' => false,
        'error' => 'Directorios no encontrados',
        'pdfs' => [],
        'estadisticas' => [
            'total_archivos' => 0,
            'tamanio_total' => 0,
            'ultimo_envio' => null
        ]
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// Obtener todos los archivos JSON de metadatos
$archivos_json = glob($directorio_json . '*.json');

// Leer metadatos
$pdfs = [];
$tamanio_total = 0;
$ultimo_timestamp = 0;

foreach ($archivos_json as $archivo_json) {
    $contenido = file_get_contents($archivo_json);
    $metadata = json_decode($contenido, true);

    if ($metadata && isset($metadata['archivo_pdf'])) {
        $ruta_pdf = $directorio_pdfs . $metadata['archivo_pdf'];

        // Verificar que el PDF existe
        if (file_exists($ruta_pdf)) {
            $tamanio = filesize($ruta_pdf);
            $tamanio_total += $tamanio;

            // Actualizar último timestamp
            $timestamp_unix = $metadata['timestamp_unix'] ?? 0;
            if ($timestamp_unix > $ultimo_timestamp) {
                $ultimo_timestamp = $timestamp_unix;
            }

            $pdfs[] = [
                'archivo_pdf' => $metadata['archivo_pdf'],
                'nombre_estudiante' => $metadata['nombre_estudiante'] ?? 'Desconocido',
                'numero_estudiante' => $metadata['numero_estudiante'] ?? 'N/A',
                'fecha_subida' => $metadata['fecha_subida'],
                'tamanio_bytes' => $tamanio,
                'ip_origen' => $metadata['ip_origen'] ?? 'desconocida'
            ];
        }
    }
}

// Ordenar por fecha (más reciente primero)
usort($pdfs, function($a, $b) {
    return strtotime($b['fecha_subida']) - strtotime($a['fecha_subida']);
});

// Preparar estadísticas
$estadisticas = [
    'total_archivos' => count($pdfs),
    'tamanio_total' => $tamanio_total,
    'ultimo_envio' => $ultimo_timestamp > 0 ? date('Y-m-d H:i:s', $ultimo_timestamp) : null
];

// Respuesta
echo json_encode([
    'exito' => true,
    'pdfs' => $pdfs,
    'estadisticas' => $estadisticas
], JSON_UNESCAPED_UNICODE);
?>
