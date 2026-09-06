"""
ApplicationContext para simPEATC.

Resuelve paths a assets (resources/, cache runtime/) sin depender de fbs.

Convenciones:
    context.get_resource('json/ABR.json')        -> resources/json/ABR.json
    context.get_resource('cases/cases.json')     -> resources/cases/cases.json
    context.get_resource('styles/style_base.qss') -> resources/styles/style_base.qss
    context.cache_path('temp/foo.png')           -> ~/.cache/simpeatc/temp/foo.png
    context.app                                  -> QApplication singleton

Modo dev (código fuente):
    BASE_DIR apunta a .../src/main/. Los resources viven al lado.

Modo frozen (PyInstaller):
    sys._MEIPASS contiene los resources; BASE_DIR cae al directorio temporal
    de PyInstaller para que get_resource siga funcionando igual.
"""
import os
import sys
import tempfile
from pathlib import Path

from PySide6.QtWidgets import QApplication


# Raíz del código fuente: .../src/main/
#   base.py vive en .../src/main/python/base.py -> .parent x2 = .../src/main/
if getattr(sys, "frozen", False):
    # Binario PyInstaller: resources están en sys._MEIPASS (unzip temporal).
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

RESOURCES_DIR = BASE_DIR / "resources"
CACHE_DIRNAME = "simpeatc"


class ApplicationContext:
    """Réplica minimal del ApplicationContext de fbs, sin dependencias externas."""

    def __init__(self) -> None:
        # La app la crea main.py -- acá solo guardamos referencia cuando esté.
        self.app = None

    def get_resource(self, path: str) -> str:
        """Path absoluto a un asset dentro de resources/. Acepta path relativo
        con o sin slash inicial."""
        return str(RESOURCES_DIR / path)

    def cache_path(self, *parts: str) -> str:
        """Path absoluto dentro del cache runtime del usuario
        (~/.cache/simpeatc/ en Linux, %LOCALAPPDATA%/simpeatc/Cache en Windows).

        Use para archivos escribibles (temporales, imágenes scratch, PDFs en
        construcción). NUNCA para assets read-only -- esos van por get_resource.

        El directorio se crea lazily al primer uso.
        """
        if sys.platform == "win32":
            base = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / CACHE_DIRNAME / "Cache"
        else:
            base = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / CACHE_DIRNAME
        full = base.joinpath(*parts)
        full.parent.mkdir(parents=True, exist_ok=True)
        return str(full)

    def set_app(self, app: QApplication) -> None:
        """main.py llama esto justo después de crear QApplication para que
        context.app quede apuntando al singleton vivo."""
        self.app = app


context = ApplicationContext()
