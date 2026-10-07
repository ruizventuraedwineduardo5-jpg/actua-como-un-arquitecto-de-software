"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - PERCEPCIÓN DE PANTALLA EN TIEMPO REAL
=============================================================================
Sistema continuo de captura y comprensión visual de pantalla estilo Gemini Live:
- Android (Termux API / ADB / screencap / dumpsys)
- PC (mss / Pillow ImageGrab / X11)
- Detección de cambios por hash visual
- Comprensión contextual de documentos, apps activas y videos
=============================================================================
"""

import os
import io
import time
import hashlib
import asyncio
import threading
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from PIL import Image

import config
from modules.ai_engine import ai_engine

# Intento de importar mss para captura ultrarrápida en PC
try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False


class LiveScreenVision:
    """
    Controlador de visión continua de pantalla para Android y PC.
    """

    def __init__(self, capture_dir: Optional[Path] = None):
        self.capture_dir = capture_dir or (config.STORAGE_DIR / "vision_frames")
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        self.current_frame_path = self.capture_dir / "latest_screen.png"
        self.last_frame_hash: Optional[str] = None
        self.last_analysis_result: str = "Aún no se ha realizado ninguna captura."
        self.last_capture_time: float = 0.0
        self.is_monitoring: bool = False
        self._monitor_task: Optional[asyncio.Task] = None
        self.active_app_cache: str = "Desconocida"

    # -------------------------------------------------------------------------
    # CAPTURA DE PANTALLA ADAPTATIVA (ANDROID VS PC)
    # -------------------------------------------------------------------------
    def capture_frame(self) -> Optional[Path]:
        """
        Captura el fotograma actual de pantalla según la plataforma disponible.
        Guarda el resultado en self.current_frame_path y retorna su ruta.
        """
        captured = False

        # 1. Modo Android / Termux
        if config.IS_ANDROID or config.IS_TERMUX:
            captured = self._capture_android()

        # 2. Modo PC (Linux / Windows / macOS) o fallback de Android
        if not captured:
            captured = self._capture_pc()

        # 3. Fallback Sintético de Contingencia (si el entorno no tiene display gráfico)
        if not captured:
            captured = self._create_synthetic_diagnostic_frame()

        if captured and self.current_frame_path.exists():
            self.last_capture_time = time.time()
            return self.current_frame_path
        return None

    def _capture_android(self) -> bool:
        """Captura en Android vía screencap nativo o ADB."""
        # Intento A: screencap directo en Termux (funciona en muchas ROMs o con root/permisos)
        try:
            res = subprocess.run(
                ["screencap", "-p", str(self.current_frame_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=4,
            )
            if res.returncode == 0 and self.current_frame_path.stat().st_size > 1024:
                return True
        except Exception:
            pass

        # Intento B: ADB local si está habilitado
        if config.ADB_ENABLED:
            try:
                res = subprocess.run(
                    ["adb", "exec-out", "screencap", "-p"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                )
                if res.returncode == 0 and len(res.stdout) > 2048:
                    with open(self.current_frame_path, "wb") as f:
                        f.write(res.stdout)
                    return True
            except Exception:
                pass

        return False

    def _capture_pc(self) -> bool:
        """Captura en PC usando mss o Pillow ImageGrab."""
        # Intento A: mss
        if MSS_AVAILABLE:
            try:
                mss_cls = getattr(mss, "MSS", getattr(mss, "mss", None))
                with mss_cls() as sct:
                    monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                    sct_img = sct.grab(monitor)
                    # Convertir a PIL y guardar PNG
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    img.save(self.current_frame_path, format="PNG")
                    return True
            except Exception:
                pass

        # Intento B: Pillow ImageGrab
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            if screenshot:
                screenshot.save(self.current_frame_path, format="PNG")
                return True
        except Exception:
            pass

        return False

    def _create_synthetic_diagnostic_frame(self) -> bool:
        """Genera un fotograma HUD de telemetría si se ejecuta en servidor sin display X11."""
        try:
            from PIL import ImageDraw
            img = Image.new("RGB", (1280, 720), color=(10, 16, 26))
            draw = ImageDraw.Draw(img)
            # Dibujar marcas cibernéticas HUD
            draw.rectangle([(20, 20), (1260, 700)], outline=(0, 220, 255), width=2)
            draw.text((50, 50), "JARVIS OMNI-GHOST SUPREME - HUD PERCEPTION FEED", fill=(0, 255, 200))
            draw.text((50, 100), f"Plataforma: {config.CURRENT_PLATFORM}", fill=(180, 200, 220))
            draw.text((50, 140), f"Usuario Maestro: {config.USER_TITLE}", fill=(180, 200, 220))
            draw.text((50, 180), f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}", fill=(180, 200, 220))
            draw.text((50, 240), "[ESTADO: Modo Consola / Detección Visual Sintética Activa]", fill=(255, 200, 0))
            img.save(self.current_frame_path, format="PNG")
            return True
        except Exception:
            return False

    # -------------------------------------------------------------------------
    # DETECCIÓN DE APLICACIÓN ACTIVA EN PRIMER PLANO
    # -------------------------------------------------------------------------
    def detect_active_application(self) -> str:
        """Detecta el nombre de la aplicación o ventana activa."""
        if config.IS_ANDROID or config.IS_TERMUX:
            try:
                cmd = "dumpsys window | grep -E 'mCurrentFocus|mFocusedApp' | head -n 1"
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
                if proc.stdout.strip():
                    self.active_app_cache = proc.stdout.strip()
                    return self.active_app_cache
            except Exception:
                pass
        elif config.IS_LINUX:
            try:
                proc = subprocess.run(["xdotool", "getactivewindow", "getwindowname"], capture_output=True, text=True, timeout=2)
                if proc.stdout.strip():
                    self.active_app_cache = proc.stdout.strip()
                    return self.active_app_cache
            except Exception:
                pass
        return "Pantalla Principal / Terminal Activa"

    # -------------------------------------------------------------------------
    # COMPARACIÓN DE CAMBIOS VISUALES (FRAME HASH)
    # -------------------------------------------------------------------------
    def _compute_frame_hash(self, path: Path) -> str:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def has_screen_changed(self) -> bool:
        """Determina si la pantalla ha cambiado de contenido sustancialmente."""
        if not self.current_frame_path.exists():
            return True
        new_hash = self._compute_frame_hash(self.current_frame_path)
        if new_hash != self.last_frame_hash:
            self.last_frame_hash = new_hash
            return True
        return False

    # -------------------------------------------------------------------------
    # ANÁLISIS EN VIVO Y CONSULTA DE PANTALLA
    # -------------------------------------------------------------------------
    def inspect_screen(
        self,
        query: str = "¿Qué hay actualmente en pantalla? Explícame el contexto y datos clave.",
        force_fresh_capture: bool = True,
    ) -> Dict[str, Any]:
        """
        Inspecciona visualmente la pantalla activa y entrega una explicación
        multimodal inteligente en la voz de Jarvis.
        """
        if force_fresh_capture or not self.current_frame_path.exists():
            self.capture_frame()

        active_app = self.detect_active_application()
        prompt = (
            f"Actúa como Jarvis Omni-Ghost Supreme respondiendo a {config.USER_TITLE}.\n"
            f"Aplicación o contexto detectado en primer plano: '{active_app}'.\n"
            f"Instrucción de inspección visual: {query}\n"
            f"Detalla con precisión quirúrgica lo que se ve en la imagen: textos visibles, pestañas, "
            f"código, gráficos, botones y acciones recomendadas."
        )

        analysis = ai_engine.analyze_image(self.current_frame_path, prompt=prompt)
        self.last_analysis_result = analysis

        return {
            "success": True,
            "timestamp": time.time(),
            "active_app": active_app,
            "frame_path": str(self.current_frame_path),
            "analysis": analysis,
        }

    # -------------------------------------------------------------------------
    # BUCLE DE MONITOREO EN SEGUNDO PLANO
    # -------------------------------------------------------------------------
    async def start_background_monitoring(self, interval_seconds: float = 8.0):
        """Inicia un ciclo asíncrono que mantiene actualizados los fotogramas."""
        self.is_monitoring = True
        while self.is_monitoring:
            try:
                self.capture_frame()
                self.detect_active_application()
            except Exception:
                pass
            await asyncio.sleep(interval_seconds)

    def stop_monitoring(self):
        self.is_monitoring = False


# Instancia singleton predeterminada
screen_vision = LiveScreenVision()
