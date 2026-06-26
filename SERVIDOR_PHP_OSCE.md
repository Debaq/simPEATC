# Configuración del Servidor PHP para Impresión Remota de PDFs OSCE

Este documento explica cómo configurar un servidor PHP para recibir los PDFs generados por el simulador simPEATC y permitir su impresión desde cualquier equipo de la red.

## 📋 Requisitos del Servidor

- **Servidor Web**: Apache o Nginx
- **PHP**: Versión 7.4 o superior
- **Sistema Operativo**: Linux (Ubuntu/Debian recomendado) o Windows Server

## 🚀 Instalación y Configuración

### Paso 1: Instalar Apache y PHP (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install apache2 php libapache2-mod-php
sudo systemctl start apache2
sudo systemctl enable apache2
```

### Paso 2: Crear Directorio para PDFs

```bash
sudo mkdir -p /var/www/html/osce/pdfs_osce
sudo chown -R www-data:www-data /var/www/html/osce
sudo chmod 755 /var/www/html/osce/pdfs_osce
```

### Paso 3: Crear el Script PHP

Crear el archivo `/var/www/html/osce/recibir_pdf.php` con el siguiente contenido:

```php
<?php
/**
 * Script PHP para recibir PDFs de evaluaciones OSCE
 * Guarda los archivos y genera una URL para impresión
 *
 * Universidad Austral de Chile - Sede Puerto Montt
 * simPEATC - Simulador de PEATC
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *'); // Permitir CORS si es necesario

// Configuración
$directorio_pdfs = __DIR__ . '/pdfs_osce/';
$url_base = 'http://' . $_SERVER['HTTP_HOST'] . '/osce/pdfs_osce/';

// Crear directorio si no existe
if (!file_exists($directorio_pdfs)) {
    mkdir($directorio_pdfs, 0755, true);
}

// Log de solicitud
$log_file = $directorio_pdfs . 'log.txt';
file_put_contents(
    $log_file,
    date('Y-m-d H:i:s') . " - Solicitud recibida desde " . $_SERVER['REMOTE_ADDR'] . "\n",
    FILE_APPEND
);

// Verificar que se recibió un archivo
if (!isset($_FILES['pdf']) || $_FILES['pdf']['error'] !== UPLOAD_ERR_OK) {
    $error_msg = 'No se recibió el archivo PDF correctamente';
    if (isset($_FILES['pdf']['error'])) {
        $error_codes = [
            UPLOAD_ERR_INI_SIZE => 'El archivo excede upload_max_filesize',
            UPLOAD_ERR_FORM_SIZE => 'El archivo excede MAX_FILE_SIZE',
            UPLOAD_ERR_PARTIAL => 'El archivo se subió parcialmente',
            UPLOAD_ERR_NO_FILE => 'No se subió ningún archivo',
            UPLOAD_ERR_NO_TMP_DIR => 'Falta carpeta temporal',
            UPLOAD_ERR_CANT_WRITE => 'Error al escribir en disco',
            UPLOAD_ERR_EXTENSION => 'Una extensión PHP detuvo la subida'
        ];
        $error_msg .= ': ' . ($error_codes[$_FILES['pdf']['error']] ?? 'Error desconocido');
    }

    echo json_encode([
        'exito' => false,
        'error' => $error_msg
    ]);
    exit;
}

// Verificar que sea un PDF
$file_type = mime_content_type($_FILES['pdf']['tmp_name']);
if ($file_type !== 'application/pdf') {
    echo json_encode([
        'exito' => false,
        'error' => 'El archivo debe ser un PDF (tipo recibido: ' . $file_type . ')'
    ]);
    exit;
}

// Obtener datos adicionales
$nombre_estudiante = $_POST['nombre_estudiante'] ?? 'Desconocido';
$numero_estudiante = $_POST['numero_estudiante'] ?? 'N/A';
$tipo = $_POST['tipo'] ?? 'osce_peatc';

// Sanitizar número de estudiante para nombre de archivo
$numero_sanitizado = preg_replace('/[^a-zA-Z0-9_-]/', '_', $numero_estudiante);

// Generar nombre único para el archivo
$timestamp = date('Ymd_His');
$nombre_archivo = "OSCE_{$numero_sanitizado}_{$timestamp}.pdf";
$ruta_destino = $directorio_pdfs . $nombre_archivo;

// Mover archivo subido
if (move_uploaded_file($_FILES['pdf']['tmp_name'], $ruta_destino)) {

    // Guardar metadatos en un archivo JSON
    $metadatos = [
        'nombre_estudiante' => $nombre_estudiante,
        'numero_estudiante' => $numero_estudiante,
        'tipo' => $tipo,
        'fecha_subida' => date('Y-m-d H:i:s'),
        'archivo_pdf' => $nombre_archivo,
        'ip_origen' => $_SERVER['REMOTE_ADDR'],
        'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'Desconocido',
        'tamano_bytes' => filesize($ruta_destino)
    ];

    $archivo_metadatos = $directorio_pdfs . $numero_sanitizado . '_' . $timestamp . '_meta.json';
    file_put_contents(
        $archivo_metadatos,
        json_encode($metadatos, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)
    );

    // Log exitoso
    file_put_contents(
        $log_file,
        date('Y-m-d H:i:s') . " - PDF guardado: $nombre_archivo (Estudiante: $nombre_estudiante)\n",
        FILE_APPEND
    );

    // Respuesta exitosa
    echo json_encode([
        'exito' => true,
        'mensaje' => 'PDF recibido y guardado correctamente',
        'url_impresion' => $url_base . $nombre_archivo,
        'archivo' => $nombre_archivo,
        'estudiante' => $nombre_estudiante,
        'numero' => $numero_estudiante
    ]);

} else {
    // Error al mover archivo
    $error_msg = 'Error al guardar el archivo en el servidor';

    // Verificar permisos
    if (!is_writable($directorio_pdfs)) {
        $error_msg .= ': El directorio no tiene permisos de escritura';
    }

    file_put_contents(
        $log_file,
        date('Y-m-d H:i:s') . " - ERROR: $error_msg\n",
        FILE_APPEND
    );

    echo json_encode([
        'exito' => false,
        'error' => $error_msg
    ]);
}
?>
```

### Paso 4: Configurar PHP para Permitir Uploads Grandes

Editar `/etc/php/8.1/apache2/php.ini` (ajustar versión según corresponda):

```ini
upload_max_filesize = 20M
post_max_size = 25M
max_execution_time = 60
memory_limit = 256M
```

### Paso 5: Reiniciar Apache

```bash
sudo systemctl restart apache2
```

### Paso 6: Configurar Firewall (si aplica)

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp  # Si usa HTTPS
```

## 🧪 Probar la Configuración

### Desde la línea de comandos del servidor:

```bash
# Crear un PDF de prueba
echo "%PDF-1.4" > test.pdf
echo "Test PDF" >> test.pdf

# Probar el upload
curl -X POST \
  -F "pdf=@test.pdf" \
  -F "nombre_estudiante=Juan Perez" \
  -F "numero_estudiante=2021001" \
  http://localhost/osce/recibir_pdf.php
```

### Desde el navegador:

Acceder a: `http://IP_SERVIDOR/osce/recibir_pdf.php`

Debería mostrar un error JSON indicando que no se recibió archivo (esto es correcto).

## 📱 Usar desde simPEATC

1. **Completar las 3 estaciones OSCE**
2. Cuando se complete, aparecerá el mensaje de OSCE completado
3. Hacer clic en **"Sí"** cuando pregunte si desea enviar al servidor
4. Ingresar la URL del servidor, por ejemplo:
   ```
   http://192.168.1.100/osce/recibir_pdf.php
   ```
5. El PDF se enviará y recibirá una URL para impresión

## 🖨️ Imprimir desde Otro PC

1. Abrir un navegador en cualquier equipo de la red
2. Acceder a la URL proporcionada, por ejemplo:
   ```
   http://192.168.1.100/osce/pdfs_osce/OSCE_2021001_20251130_143022.pdf
   ```
3. El navegador abrirá el PDF
4. Usar **Ctrl+P** o **Archivo → Imprimir** para imprimir

## 📁 Estructura de Archivos en el Servidor

```
/var/www/html/osce/
├── recibir_pdf.php           # Script principal
├── pdfs_osce/               # Directorio de PDFs
│   ├── OSCE_2021001_20251130_143022.pdf
│   ├── OSCE_2021001_20251130_143022_meta.json
│   ├── OSCE_2021002_20251130_144530.pdf
│   ├── OSCE_2021002_20251130_144530_meta.json
│   └── log.txt              # Log de eventos
```

## 🔒 Seguridad

### Recomendaciones:

1. **Autenticación básica** (opcional):

```apache
# Crear archivo .htpasswd
sudo htpasswd -c /etc/apache2/.htpasswd admin

# Agregar en /etc/apache2/sites-available/000-default.conf
<Directory "/var/www/html/osce">
    AuthType Basic
    AuthName "OSCE Protected Area"
    AuthUserFile /etc/apache2/.htpasswd
    Require valid-user
</Directory>
```

2. **Limitar acceso por IP** (solo red local):

```apache
<Directory "/var/www/html/osce">
    Require ip 192.168.1.0/24
</Directory>
```

3. **HTTPS** (recomendado para producción):

```bash
sudo apt install certbot python3-certbot-apache
sudo certbot --apache
```

## 🔧 Solución de Problemas

### Error: "No se recibió el archivo PDF correctamente"

**Solución**: Verificar tamaño máximo de upload en `php.ini`

### Error: "Error al guardar el archivo en el servidor"

**Solución**:
```bash
sudo chown -R www-data:www-data /var/www/html/osce/pdfs_osce
sudo chmod 755 /var/www/html/osce/pdfs_osce
```

### Error: "Error de conexión: No se pudo conectar al servidor"

**Solución**:
- Verificar que Apache esté corriendo: `sudo systemctl status apache2`
- Verificar firewall: `sudo ufw status`
- Verificar IP del servidor: `ip addr show`

### Ver logs del servidor:

```bash
# Logs de Apache
sudo tail -f /var/log/apache2/error.log
sudo tail -f /var/log/apache2/access.log

# Logs de la aplicación
tail -f /var/www/html/osce/pdfs_osce/log.txt
```

## 📞 Soporte

Para problemas o consultas:
- **Email**: contacto@tmeduca.org
- **Repositorio**: https://github.com/Debaq/simPEATC

---

**Universidad Austral de Chile - Sede Puerto Montt**
**Tecnología Médica - simPEATC v0.0.0**
