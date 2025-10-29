<?php
/**
 * ABR Activation Endpoint
 * Verifica si la versión de desarrollo está activa
 * 
 * Responde solo: true o false
 */

// Headers para CORS y tipo de contenido
header('Content-Type: text/plain');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');

// Estado de activación
// Cambiar a false para deshabilitar todas las versiones de desarrollo
$activation_enabled = true;

// Logging opcional (comentar en producción si no se necesita)
$log_access = true;

if ($log_access) {
    $log_entry = date('Y-m-d H:i:s') . ' | ' . 
                 $_SERVER['REMOTE_ADDR'] . ' | ' . 
                 ($_SERVER['HTTP_USER_AGENT'] ?? 'Unknown') . PHP_EOL;
    
    file_put_contents(
        __DIR__ . '/abr_activation_log.txt', 
        $log_entry, 
        FILE_APPEND | LOCK_EX
    );
}

// Responder solo true o false
echo $activation_enabled ? 'true' : 'false';

// Opcional: Control por IP específicas (descomentar si necesitas)
/*
$allowed_ips = [
    '192.168.1.100',
    '10.0.0.50',
];

$client_ip = $_SERVER['REMOTE_ADDR'];

if (in_array($client_ip, $allowed_ips)) {
    echo 'true';
} else {
    echo 'false';
}
*/

// Opcional: Control por fecha de expiración (descomentar si necesitas)
/*
$expiration_date = '2025-12-31';

if (date('Y-m-d') <= $expiration_date) {
    echo 'true';
} else {
    echo 'false';
}
*/
?>