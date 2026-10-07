"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - SISTEMA DE AUTO-REPARACIÓN EN CALIENTE (SELF-HEALING)
=============================================================================
Capturador proactivo de excepciones en tiempo de ejecución, diagnóstico autónomo,
corrección de código fuente en modules/ con validación AST y hot-reload
en caliente (importlib.reload) sin detener el asistente.
=============================================================================
"""

import os
import sys
import ast
import time
import shutil
import logging
import traceback
import importlib
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

import config
from modules.omni_ai_router import omni_router, AIContext

# Configuración de logging de auto-reparación
logger = logging.getLogger("JarvisSelfHealing")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(config.SELF_HEALING_LOG, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
logger.addHandler(file_handler)


class SelfHealingSystem:
    """
    Sistema autónomo de diagnóstico, parcheo y recarga de módulos en caliente.
    """

    def __init__(self):
        self.active = True
        self.repair_history: list = []

    # -------------------------------------------------------------------------
    # ANÁLISIS DE EXCEPCIONES Y EXTRACCIÓN DE CONTEXTO
    # -------------------------------------------------------------------------
    def parse_traceback(self, exc: Exception, tb_obj=None) -> Optional[Dict[str, Any]]:
        """Extrae el archivo, línea y contexto del error."""
        tb = tb_obj or exc.__traceback__
        if not tb:
            return None

        # Obtener el último frame perteneciente al proyecto
        extracted = traceback.extract_tb(tb)
        project_frames = []
        for frame in extracted:
            frame_path = Path(frame.filename).resolve()
            if str(config.BASE_DIR) in str(frame_path) and "venv" not in str(frame_path):
                project_frames.append(frame)

        target_frame = project_frames[-1] if project_frames else extracted[-1]
        target_path = Path(target_frame.filename).resolve()

        if not target_path.exists():
            return None

        return {
            "file_path": target_path,
            "line_no": target_frame.lineno,
            "func_name": target_frame.name,
            "exc_type": type(exc).__name__,
            "exc_msg": str(exc),
            "traceback_str": "".join(traceback.format_exception(type(exc), exc, tb)),
        }

    # -------------------------------------------------------------------------
    # DIAGNÓSTICO Y GENERACIÓN DE PARCHE AUTÓNOMO
    # -------------------------------------------------------------------------
    def generate_fix(self, error_details: Dict[str, Any]) -> Optional[str]:
        """
        Consulta al Omni-Router para que genere la versión corregida del código fuente.
        """
        file_path = error_details["file_path"]
        try:
            current_code = file_path.read_text(encoding="utf-8")
        except Exception:
            return None

        prompt = (
            f"ERES EL SUBSISTEMA DE AUTO-REPARACIÓN DE JARVIS OMNI-GHOST SUPREME.\n"
            f"El archivo '{file_path.name}' ha producido una excepción en tiempo de ejecución:\n"
            f"Tipo de Error: {error_details['exc_type']}\n"
            f"Mensaje: {error_details['exc_msg']}\n"
            f"Línea de falla: {error_details['line_no']} en la función {error_details['func_name']}\n\n"
            f"TRACEBACK COMPLETO:\n{error_details['traceback_str']}\n\n"
            f"CÓDIGO FUENTE ACTUAL DEL ARCHIVO:\n```python\n{current_code}\n```\n\n"
            f"INSTRUCCIONES CRÍTICAS:\n"
            f"1. Analiza y repara el fallo de forma definitiva.\n"
            f"2. Devuelve ÚNICAMENTE el código Python completo y funcional del archivo sin explicaciones adicionales.\n"
            f"3. Asegúrate de que el código sea 100% sintácticamente válido para Python 3.10+."
        )

        try:
            ai_res = omni_router.route_request(prompt, context=AIContext.CODE)
            resp_text = ai_res.get("response", "")
            # Limpiar bloques markdown si la IA los incluye
            if "```python" in resp_text:
                resp_text = resp_text.split("```python")[1].split("```")[0]
            elif "```" in resp_text:
                resp_text = resp_text.split("```")[1].split("```")[0]

            cleaned_code = resp_text.strip()
            # Validación AST obligatoria antes de autorizar
            ast.parse(cleaned_code)
            return cleaned_code
        except Exception as e:
            logger.error(f"Fallo en la síntesis o validación AST del parche: {e}")
            return None

    # -------------------------------------------------------------------------
    # APLICACIÓN DE PARCHE Y HOT-RELOAD
    # -------------------------------------------------------------------------
    def apply_patch_and_reload(self, file_path: Path, new_code: str) -> bool:
        """
        Crea backup (.bak), escribe el código corregido y recarga el módulo en memoria.
        """
        try:
            # 1. Copia de seguridad
            backup_path = file_path.with_suffix(f".bak_{int(time.time())}")
            shutil.copy2(file_path, backup_path)

            # 2. Sobrescribir archivo con código saneado
            file_path.write_text(new_code, encoding="utf-8")
            logger.info(f"Parche aplicado con éxito en {file_path}. Backup guardado en {backup_path.name}")

            # 3. Identificar nombre de módulo en sys.modules
            module_name = None
            for mod_name, mod_obj in list(sys.modules.items()):
                if hasattr(mod_obj, "__file__") and mod_obj.__file__:
                    if Path(mod_obj.__file__).resolve() == file_path:
                        module_name = mod_name
                        break

            # 4. Hot-reload si el módulo ya estaba cargado
            if module_name and module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                logger.info(f"Módulo '{module_name}' recargado en caliente (hot-reload) exitosamente.")

            return True
        except Exception as e:
            logger.error(f"Error durante el proceso de aplicación de parche: {e}")
            return False

    # -------------------------------------------------------------------------
    # CONTROLADOR MAESTRO DE AUTO-SANACIÓN
    # -------------------------------------------------------------------------
    def handle_exception(self, exc: Exception, tb_obj=None) -> Dict[str, Any]:
        """
        Punto de entrada para interceptar y resolver fallos en tiempo de ejecución.
        """
        details = self.parse_traceback(exc, tb_obj)
        if not details:
            return {"repaired": False, "reason": "No se pudo determinar el archivo origen"}

        logger.warning(f"Interceptada anomalía en {details['file_path'].name}:{details['line_no']} -> {details['exc_msg']}")

        new_code = self.generate_fix(details)
        if not new_code:
            return {"repaired": False, "reason": "La IA no pudo sintetizar un parche con sintaxis válida"}

        success = self.apply_patch_and_reload(details["file_path"], new_code)
        event = {
            "timestamp": time.time(),
            "file": str(details["file_path"]),
            "line": details["line_no"],
            "error": details["exc_msg"],
            "repaired": success,
        }
        self.repair_history.append(event)
        return event

    def install_global_hook(self):
        """Instala el capturador global de excepciones en el proceso."""
        def _excepthook(exc_type, exc_val, exc_tb):
            self.handle_exception(exc_val, exc_tb)
            sys.__excepthook__(exc_type, exc_val, exc_tb)

        sys.excepthook = _excepthook


# Instancia singleton predeterminada
self_healer = SelfHealingSystem()
