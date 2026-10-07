"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - CONTROLADOR DE APLICACIONES ANDROID & PC
=============================================================================
Control de bajo nivel y automatización de interfaz para Android
(Termux API, Activity Manager `am`, `pm`, ADB, input tap/text/keyevent)
con fallbacks para entornos PC (Windows/Linux).
=============================================================================
"""

import os
import sys
import shlex
import urllib.parse
import webbrowser
import subprocess
from typing import Optional, List, Dict, Any

import config

TupleResult = tuple[bool, str, str]


class AppController:
    """
    Controlador universal de aplicaciones y simulación de interacción táctil/teclado.
    """

    KNOWN_PACKAGES: Dict[str, str] = {
        "whatsapp": "com.whatsapp",
        "chrome": "com.android.chrome",
        "youtube": "com.google.android.youtube",
        "telegram": "org.telegram.messenger",
        "spotify": "com.spotify.music",
        "ajustes": "com.android.settings",
        "configuracion": "com.android.settings",
        "camara": "com.android.camera2",
        "calculadora": "com.google.android.calculator",
        "gmail": "com.google.android.gm",
        "maps": "com.google.android.apps.maps",
        "archivos": "com.google.android.documentsui",
        "termux": "com.termux",
    }

    KEY_CODES: Dict[str, int] = {
        "home": 3,
        "back": 4,
        "call": 5,
        "endcall": 6,
        "power": 26,
        "volume_up": 24,
        "volume_down": 25,
        "camera": 27,
        "enter": 66,
        "del": 67,
        "backspace": 67,
        "tab": 61,
        "space": 62,
        "menu": 82,
        "search": 84,
        "media_play_pause": 85,
        "media_next": 87,
        "media_prev": 88,
    }

    def __init__(self):
        self.is_android = config.IS_ANDROID or config.IS_TERMUX

    # -------------------------------------------------------------------------
    # EJECUTOR DE COMANDOS DE SISTEMA
    # -------------------------------------------------------------------------
    def _run_cmd(self, cmd_args: List[str], timeout: int = 5) -> TupleResult:
        try:
            res = subprocess.run(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
            return res.returncode == 0, res.stdout.strip(), res.stderr.strip()
        except Exception as e:
            return False, "", str(e)

    # -------------------------------------------------------------------------
    # LISTADO Y DESCUBRIMIENTO DE APLICACIONES
    # -------------------------------------------------------------------------
    def list_installed_apps(self) -> List[str]:
        """Obtiene una lista de paquetes instalados en el sistema."""
        if self.is_android:
            # Intentar pm list packages
            success, out, _ = self._run_cmd(["pm", "list", "packages", "-3"])
            if not success and config.ADB_ENABLED:
                success, out, _ = self._run_cmd(["adb", "shell", "pm", "list", "packages", "-3"])

            if success and out:
                packages = [line.replace("package:", "").strip() for line in out.splitlines() if line]
                return packages

        # Fallback PC / Android sin acceso a pm
        return list(self.KNOWN_PACKAGES.keys())

    # -------------------------------------------------------------------------
    # LANZAMIENTO DE APLICACIONES
    # -------------------------------------------------------------------------
    def launch_app(self, app_name_or_package: str) -> Dict[str, Any]:
        """
        Abre una aplicación por nombre común o nombre de paquete.
        """
        target = app_name_or_package.lower().strip()
        pkg = self.KNOWN_PACKAGES.get(target, target)

        if self.is_android:
            # Intento 1: monkey launcher
            cmd = ["monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"]
            success, stdout, stderr = self._run_cmd(cmd)
            if success:
                return {"success": True, "method": "android_monkey", "app": pkg}

            # Intento 2: am start vía ADB si está disponible
            if config.ADB_ENABLED:
                cmd_adb = ["adb", "shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"]
                s_adb, _, _ = self._run_cmd(cmd_adb)
                if s_adb:
                    return {"success": True, "method": "adb_monkey", "app": pkg}

            # Intento 3: Intent directo con am start
            cmd_am = ["am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER", "-p", pkg]
            s_am, _, _ = self._run_cmd(cmd_am)
            if s_am:
                return {"success": True, "method": "android_am_start", "app": pkg}

        # Fallback PC
        return self._launch_pc_fallback(target)

    def _launch_pc_fallback(self, target: str) -> Dict[str, Any]:
        """Lanza aplicaciones o equivalentes en entorno PC."""
        pc_apps = {
            "chrome": ["google-chrome", "chrome", "chromium"],
            "calculadora": ["gnome-calculator", "calc.exe", "kcalc"],
            "whatsapp": ["https://web.whatsapp.com"],
            "youtube": ["https://www.youtube.com"],
            "spotify": ["spotify", "https://open.spotify.com"],
        }

        candidates = pc_apps.get(target, [target])
        for cand in candidates:
            if cand.startswith("http://") or cand.startswith("https://"):
                webbrowser.open(cand)
                return {"success": True, "method": "pc_browser", "target": cand}
            else:
                try:
                    subprocess.Popen([cand], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return {"success": True, "method": "pc_subprocess", "target": cand}
                except Exception:
                    continue

        return {"success": False, "method": "pc_fallback_failed", "target": target}

    # -------------------------------------------------------------------------
    # INTERACCIÓN TÁCTIL Y AUTOMATIZACIÓN DE PANTALLA (ADB / INPUT)
    # -------------------------------------------------------------------------
    def tap(self, x: int, y: int) -> bool:
        """Simula un toque en las coordenadas (x, y)."""
        if self.is_android:
            success, _, _ = self._run_cmd(["input", "tap", str(x), str(y)])
            if success:
                return True
            if config.ADB_ENABLED:
                s, _, _ = self._run_cmd(["adb", "shell", "input", "tap", str(x), str(y)])
                return s
        return False

    def type_text(self, text: str) -> bool:
        """Escribe texto en el campo activo de Android o PC."""
        if self.is_android:
            # Reemplazar espacios para el binario 'input' de Android
            escaped_text = text.replace(" ", "%s").replace("'", "\\'").replace('"', '\\"')
            success, _, _ = self._run_cmd(["input", "text", escaped_text])
            if success:
                return True
            if config.ADB_ENABLED:
                s, _, _ = self._run_cmd(["adb", "shell", "input", "text", escaped_text])
                return s
        return False

    def press_key(self, key_name: str) -> bool:
        """Presiona una tecla de hardware (home, back, enter, power, etc.)."""
        key_lower = key_name.lower().strip()
        code = self.KEY_CODES.get(key_lower)
        if code is None:
            try:
                code = int(key_lower)
            except ValueError:
                return False

        if self.is_android:
            success, _, _ = self._run_cmd(["input", "keyevent", str(code)])
            if success:
                return True
            if config.ADB_ENABLED:
                s, _, _ = self._run_cmd(["adb", "shell", "input", "keyevent", str(code)])
                return s
        return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> bool:
        """Realiza un deslizamiento táctil de (x1, y1) a (x2, y2)."""
        if self.is_android:
            args = ["input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)]
            success, _, _ = self._run_cmd(args)
            if success:
                return True
            if config.ADB_ENABLED:
                s, _, _ = self._run_cmd(["adb", "shell"] + args)
                return s
        return False

    # -------------------------------------------------------------------------
    # INTENTS DE ALTO NIVEL (URL, WHATSAPP, LLAMADAS)
    # -------------------------------------------------------------------------
    def open_url(self, url: str) -> bool:
        """Abre un enlace en el navegador predeterminado."""
        if self.is_android:
            # Intentar termux-open-url primero
            s_t, _, _ = self._run_cmd(["termux-open-url", url])
            if s_t:
                return True
            # Intentar am start
            s_am, _, _ = self._run_cmd(["am", "start", "-a", "android.intent.action.VIEW", "-d", url])
            if s_am:
                return True

        # Fallback estándar con webbrowser
        try:
            return webbrowser.open(url)
        except Exception:
            return False

    def send_whatsapp(self, phone: str, message: str) -> bool:
        """Prepara y envía un mensaje de WhatsApp directo a un número telefónico."""
        clean_phone = "".join(c for c in phone if c.isdigit() or c == "+")
        encoded_msg = urllib.parse.quote(message)
        wa_url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_msg}"
        return self.open_url(wa_url)

    def make_call(self, phone: str) -> bool:
        """Inicia una llamada telefónica."""
        clean_phone = "".join(c for c in phone if c.isdigit() or c == "+")
        if self.is_android:
            # Intentar termux-telephony-call
            s, _, _ = self._run_cmd(["termux-telephony-call", clean_phone])
            if s:
                return True
            # Intentar am start con acción CALL o DIAL
            s_am, _, _ = self._run_cmd(["am", "start", "-a", "android.intent.action.CALL", "-d", f"tel:{clean_phone}"])
            if s_am:
                return True
            s_dial, _, _ = self._run_cmd(["am", "start", "-a", "android.intent.action.DIAL", "-d", f"tel:{clean_phone}"])
            return s_dial
        return False


# Helper tipo resultado
TupleResult = tuple[bool, str, str]

# Instancia singleton predeterminada
app_controller = AppController()
