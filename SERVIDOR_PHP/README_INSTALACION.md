# Instalación del Sistema OSCE en https://tmeduca.org/osce

## Archivos a Subir al Servidor

Sube estos archivos a `https://tmeduca.org/osce/`:

```
/osce/
├── index.html              # Página principal de listado
├── listar_pdfs.php        # API para listar PDFs
├── recibir_pdf.php        # Endpoint para recibir PDFs
├── .htaccess              # Configuración Apache
└── (directorios se crean automáticamente)
```

## Configuración del Servidor

### 1. Permisos de Directorios

Los siguientes directorios se crearán automáticamente al recibir el primer PDF:

```bash
mkdir -p /ruta/a/tmeduca.org/osce/pdfs_osce
mkdir -p /ruta/a/tmeduca.org/osce/html_osce
mkdir -p /ruta/a/tmeduca.org/osce/json_osce
mkdir -p /ruta/a/tmeduca.org/osce/imagenes_osce

chmod 755 /ruta/a/tmeduca.org/osce/pdfs_osce
chmod 755 /ruta/a/tmeduca.org/osce/html_osce
chmod 755 /ruta/a/tmeduca.org/osce/json_osce
chmod 755 /ruta/a/tmeduca.org/osce/imagenes_osce
```

### 2. Configurar PHP (php.ini)

Asegúrate de que estas configuraciones estén habilitadas:

```ini
upload_max_filesize = 50M
post_max_size = 50M
max_execution_time = 300
max_input_time = 300
file_uploads = On
```

Si usas Apache, el archivo `.htaccess` ya incluye estas configuraciones.

### 3. Reiniciar Servidor Web

```bash
# Apache
sudo systemctl restart apache2

# Nginx + PHP-FPM
sudo systemctl restart nginx
sudo systemctl restart php-fpm
```

## Estructura de Directorios Automáticos

Una vez que empieces a recibir PDFs, la estructura será:

```
/osce/
├── index.html
├── listar_pdfs.php
├── recibir_pdf.php
├── .htaccess
├── osce_log.txt                          # Log de todos los envíos
├── pdfs_osce/                            # PDFs recibidos
│   ├── OSCE_PEATC_2021234567_2025-12-01_10-30-15.pdf
│   └── ...
├── html_osce/                            # Reportes HTML (si se envían)
│   ├── OSCE_PEATC_2021234567_2025-12-01_10-30-15.html
│   └── ...
├── json_osce/                            # Metadatos JSON
│   ├── OSCE_PEATC_2021234567_2025-12-01_10-30-15.json
│   └── ...
└── imagenes_osce/                        # Imágenes de curvas ABR
    ├── OSCE_PEATC_2021234567_2025-12-01_10-30-15/
    │   ├── caso1_OD.png
    │   ├── caso1_OI.png
    │   ├── caso1_LatInt.png
    │   └── ...
    └── ...
```

## Prueba de Funcionamiento

### 1. Verificar que el servidor está funcionando

Accede a: `https://tmeduca.org/osce/`

Deberías ver la página de listado vacía.

### 2. Probar el endpoint de recepción

```bash
curl -X POST https://tmeduca.org/osce/recibir_pdf.php
```

Deberías recibir un JSON con error (esperado, porque no enviaste archivo).

### 3. Probar desde la aplicación Python

La aplicación enviará automáticamente al finalizar cada OSCE.

## URLs del Sistema

- **Listado de PDFs:** https://tmeduca.org/osce/
- **Endpoint de recepción:** https://tmeduca.org/osce/recibir_pdf.php
- **API de listado:** https://tmeduca.org/osce/listar_pdfs.php
- **PDFs guardados:** https://tmeduca.org/osce/pdfs_osce/
- **Log de envíos:** https://tmeduca.org/osce/osce_log.txt (protegido por .htaccess)

## Seguridad

- Los archivos `.json` y `.log` están protegidos por `.htaccess`
- El listado de directorios está deshabilitado
- Los PDFs son accesibles públicamente (por ahora)

### Opcional: Proteger con Contraseña

Si quieres proteger el acceso con contraseña:

```bash
cd /ruta/a/tmeduca.org/osce/
htpasswd -c .htpasswd admin

# Agregar al inicio del .htaccess:
AuthType Basic
AuthName "OSCE PEATC - Acceso Restringido"
AuthUserFile /ruta/completa/.htpasswd
Require valid-user
```

## Monitoreo

### Ver log de envíos:

```bash
tail -f /ruta/a/tmeduca.org/osce/osce_log.txt
```

### Contar PDFs recibidos:

```bash
ls -1 /ruta/a/tmeduca.org/osce/pdfs_osce/*.pdf | wc -l
```

### Ver espacio usado:

```bash
du -sh /ruta/a/tmeduca.org/osce/pdfs_osce/
```

## Mantenimiento

### Limpiar PDFs antiguos (más de 30 días):

```bash
find /ruta/a/tmeduca.org/osce/pdfs_osce/ -name "*.pdf" -mtime +30 -delete
find /ruta/a/tmeduca.org/osce/json_osce/ -name "*.json" -mtime +30 -delete
```

### Backup automático:

```bash
# Agregar a crontab (cada día a las 2 AM)
0 2 * * * tar -czf /backups/osce_$(date +\%Y\%m\%d).tar.gz /ruta/a/tmeduca.org/osce/
```

## Solución de Problemas

### Los PDFs no se reciben

1. Verifica permisos: `ls -la /ruta/a/tmeduca.org/osce/pdfs_osce/`
2. Verifica configuración PHP: `php -i | grep upload`
3. Revisa logs: `tail /var/log/apache2/error.log`

### Error de tamaño de archivo

Aumenta `upload_max_filesize` y `post_max_size` en `php.ini`

### Página en blanco

1. Verifica errores PHP: activa `display_errors` en desarrollo
2. Revisa logs del servidor web

## Contacto

Sistema desarrollado para:
**Universidad Austral de Chile - Sede Puerto Montt**
Tecnología Médica - PEATC
