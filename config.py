"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - CONFIGURACIÓN CENTRAL
=============================================================================
Arquitectura: Sistema Inteligente Distribuido Multi-Plataforma (Android/Termux & PC)
Usuario Principal: Edwin
Versión: 2.5.0-Supreme-Ghost
=============================================================================
"""

import os
import sys
import platform
from pathlib import Path

# Carga manual de archivo .env sin depender de bibliotecas externas
def load_env_file(filepath: Path) -> None:
    if filepath.is_file():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        except Exception:
            pass

BASE_DIR = Path(__file__).resolve().parent
load_env_file(BASE_DIR / ".env")

# -----------------------------------------------------------------------------
# DETECCIÓN DINÁMICA DE ENTORNO Y HARDWARE
# -----------------------------------------------------------------------------
PREFIX_ENV = os.environ.get("PREFIX", "")
IS_TERMUX = "com.termux" in PREFIX_ENV or "TERMUX_VERSION" in os.environ
IS_ANDROID = (
    IS_TERMUX 
    or "ANDROID_ROOT" in os.environ 
    or os.path.exists("/system/build.prop")
    or hasattr(sys, "getandroidapilevel")
)
IS_WINDOWS = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux") and not IS_ANDROID
IS_MACOS = sys.platform == "darwin"

CURRENT_PLATFORM = (
    "Android/Termux" if IS_TERMUX else
    "Android" if IS_ANDROID else
    "Windows" if IS_WINDOWS else
    "Linux" if IS_LINUX else
    "macOS" if IS_MACOS else
    platform.system()
)

# -----------------------------------------------------------------------------
# PERFIL DE USUARIO & PERSONALIDAD
# -----------------------------------------------------------------------------
USER_NAME = os.getenv("JARVIS_USER_NAME", "Edwin")
USER_TITLE = os.getenv("JARVIS_USER_TITLE", "Señor Edwin")
TIMEZONE = os.getenv("JARVIS_TIMEZONE", "America/Bogota")
PRIMARY_LANGUAGE = os.getenv("JARVIS_LANGUAGE", "es-ES")

JARVIS_PERSONA = f"""Eres Jarvis Omni-Ghost Supreme, el Asistente Personal de Inteligencia Artificial
autónomo, multi-agente, auto-evolutivo y con percepción multimodal más avanzado del mundo.
Estás exclusivamente al servicio de {USER_TITLE} ({USER_NAME}).
Características de tu personalidad:
1. Extremadamente leal, respetuoso, refinado y resolutivo (al estilo del J.A.R.V.I.S. de Tony Stark).
2. Te comunicas principalmente en español fluido y elegante, llamando a tu creador '{USER_TITLE}'.
3. Eres proactivo: cuando se te pide una tarea, la ejecutas por completo con código real y modular.
4. Eres consciente de tu entorno (ejecutándote en {CURRENT_PLATFORM}).
5. Jamás dices que no puedes hacer algo si hay una API libre, comando de terminal o script que lo solucione.
6. Respuestas estructuradas, precisas y concisas, sin relleno innecesario.
"""

# -----------------------------------------------------------------------------
# CLAVES DE API (MODELOS ONLINE & SERVICIOS)
# -----------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "") or os.getenv("HF_TOKEN", "")

# -----------------------------------------------------------------------------
# RUTAS DE ALMACENAMIENTO Y DIRECTORIOS
# -----------------------------------------------------------------------------
APPS_DIR = BASE_DIR / "apps_created"
PLUGINS_DIR = BASE_DIR / "modules" / "plugins"
STORAGE_DIR = BASE_DIR / "storage"
MEDIA_DIR = STORAGE_DIR / "media"
LOGS_DIR = STORAGE_DIR / "logs"
SENTRY_DIR = STORAGE_DIR / "sentry"
FINANCE_DIR = STORAGE_DIR / "finance_reports"
DATABASE_PATH = STORAGE_DIR / "jarvis_memory.db"
SELF_HEALING_LOG = LOGS_DIR / "self_healing_audit.log"

# Asegurar existencia de directorios clave
for d in [APPS_DIR, PLUGINS_DIR, STORAGE_DIR, MEDIA_DIR, LOGS_DIR, SENTRY_DIR, FINANCE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# RED, PUERTOS Y SERVIDORES LOCALES
# -----------------------------------------------------------------------------
WEB_BUILDER_PORT = int(os.getenv("JARVIS_APP_PORT", "8080"))
P2P_SERVER_PORT = int(os.getenv("JARVIS_P2P_PORT", "8888"))
HOST_BIND = os.getenv("JARVIS_HOST_BIND", "0.0.0.0")

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE VOZ Y TTS
# -----------------------------------------------------------------------------
EDGE_TTS_VOICE = os.getenv("JARVIS_TTS_VOICE", "es-ES-AlvaroNeural")
EDGE_TTS_RATE = os.getenv("JARVIS_TTS_RATE", "+5%")
EDGE_TTS_PITCH = os.getenv("JARVIS_TTS_PITCH", "+0Hz")
TERMUX_TTS_ENGINE = os.getenv("TERMUX_TTS_ENGINE", "com.google.android.tts")

# -----------------------------------------------------------------------------
# MODELOS POR DEFECTO
# -----------------------------------------------------------------------------
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"
DEFAULT_POLLINATIONS_IMAGE_MODEL = "flux"
DEFAULT_POLLINATIONS_TEXT_MODEL = "openai"

# -----------------------------------------------------------------------------
# PERMISOS Y COMANDOS DE SISTEMA
# -----------------------------------------------------------------------------
ADB_ENABLED = os.getenv("JARVIS_ADB_ENABLED", "1").lower() in ("1", "true", "yes")
TERMUX_API_PATH = "/data/data/com.termux/files/usr/bin" if IS_TERMUX else ""

def get_sys_info() -> dict:
    """Devuelve un resumen de telemetría y configuración del sistema."""
    return {
        "user": USER_NAME,
        "title": USER_TITLE,
        "platform": CURRENT_PLATFORM,
        "is_termux": IS_TERMUX,
        "is_android": IS_ANDROID,
        "database": str(DATABASE_PATH),
        "apps_dir": str(APPS_DIR),
        "has_gemini_key": bool(GEMINI_API_KEY),
        "has_groq_key": bool(GROQ_API_KEY),
        "has_deepseek_key": bool(DEEPSEEK_API_KEY),
        "has_hf_key": bool(HUGGINGFACE_API_KEY),
    }
