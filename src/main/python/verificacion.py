import requests
from PySide6.QtWidgets import QMessageBox

def verificar_activacion(parent=None) -> bool:
    """
    Verifica si la aplicación está activada consultando el servidor
    
    Args:
        parent: Widget padre para el diálogo de error
        
    Returns:
        bool: True si está activada, False si está deshabilitada
    """
    try:
        # Timeout de 5 segundos para no bloquear mucho
        response = requests.get(
            'https://tmeduca.org/abr_activate.php',
            timeout=5
        )
        
        # Verificar respuesta
        if response.status_code == 200 and response.text.strip().lower() == 'true':
            return True
        else:
            mostrar_error_desactivado(parent)
            return False
            
    except requests.exceptions.ConnectionError:
        mostrar_error_sin_internet(parent)
        return False
    except requests.exceptions.Timeout:
        mostrar_error_sin_internet(parent, timeout=True)
        return False
    except Exception as e:
        mostrar_error_generico(parent, str(e))
        return False


def mostrar_error_desactivado(parent=None):
    """Muestra mensaje cuando la versión está deshabilitada"""
    QMessageBox.critical(
        parent,
        "Versión Deshabilitada",
        "Esta versión del software ha sido deshabilitada.\n\n"
        "Esta era una versión de desarrollo y ya no está disponible.\n"
        "Por favor contacte al administrador para obtener la versión actual.",
        QMessageBox.Ok
    )


def mostrar_error_sin_internet(parent=None, timeout=False):
    """Muestra mensaje cuando no hay conexión"""
    mensaje = (
        "No se pudo verificar la activación del software.\n\n"
        "Por favor verifique su conexión a internet y intente nuevamente."
    )
    if timeout:
        mensaje = (
            "El servidor no responde (timeout).\n\n"
            "Por favor verifique su conexión a internet y intente nuevamente."
        )
    
    QMessageBox.warning(
        parent,
        "Sin Conexión a Internet",
        mensaje,
        QMessageBox.Ok
    )


def mostrar_error_generico(parent=None, error_msg=""):
    """Muestra mensaje de error genérico"""
    QMessageBox.critical(
        parent,
        "Error de Activación",
        f"Ocurrió un error al verificar la activación:\n\n{error_msg}\n\n"
        "Por favor contacte al soporte técnico.",
        QMessageBox.Ok
    )