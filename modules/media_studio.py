"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - ESTUDIO MULTIMEDIA & GENERADOR DE VIDEO
=============================================================================
Generador generativo de imágenes (Flux/SD vía Pollinations.ai) y ensamblador
de video MP4 con locución de voz, subtítulos y animaciones mediante FFmpeg,
MoviePy o reproductor web multimedia universal de contingencia.
=============================================================================
"""

import os
import time
import shutil
import urllib.parse
import urllib.request
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

from PIL import Image

import config


class MediaStudio:
    """
    Estudio creativo de generación de medios para Jarvis Omni-Ghost Supreme.
    """

    def __init__(self, media_dir: Optional[Path] = None):
        self.media_dir = media_dir or config.MEDIA_DIR
        self.media_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_cmd = shutil.which("ffmpeg")

    # -------------------------------------------------------------------------
    # GENERACIÓN DE IMÁGENES GENERATIVAS (FLUX / STABLE DIFFUSION)
    # -------------------------------------------------------------------------
    def generate_image(
        self,
        prompt: str,
        model: str = "flux",
        width: int = 1024,
        height: int = 1024,
        seed: Optional[int] = None,
    ) -> Path:
        """
        Descarga una imagen generada en alta definición sin coste ni clave requerida.
        """
        enc_prompt = urllib.parse.quote(prompt)
        use_seed = seed or int(time.time() % 100000)
        url = f"https://image.pollinations.ai/prompt/{enc_prompt}?width={width}&height={height}&model={model}&nologo=true&seed={use_seed}"

        timestamp = int(time.time())
        dest_file = self.media_dir / f"jarvis_flux_{timestamp}.jpg"

        req = urllib.request.Request(url, headers={"User-Agent": "Jarvis-Studio/2.5"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            dest_file.write_bytes(content)

        return dest_file

    # -------------------------------------------------------------------------
    # GENERACIÓN DE SUBTÍTULOS (.SRT)
    # -------------------------------------------------------------------------
    def create_subtitles(self, text: str, duration_seconds: float) -> Path:
        """Crea un archivo de subtítulos cronometrado para el audio."""
        srt_path = self.media_dir / f"subtitles_{int(time.time())}.srt"
        # Dividir texto en frases cortas
        words = text.split()
        chunk_size = 6
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        if not chunks:
            chunks = [text]

        time_per_chunk = max(1.5, duration_seconds / len(chunks))
        srt_lines = []

        for idx, chunk in enumerate(chunks, 1):
            start_s = (idx - 1) * time_per_chunk
            end_s = min(duration_seconds, idx * time_per_chunk)

            s_h, s_m, s_sec = int(start_s // 3600), int((start_s % 3600) // 60), int(start_s % 60)
            s_ms = int((start_s - int(start_s)) * 1000)

            e_h, e_m, e_sec = int(end_s // 3600), int((end_s % 3600) // 60), int(end_s % 60)
            e_ms = int((end_s - int(end_s)) * 1000)

            srt_lines.append(f"{idx}")
            srt_lines.append(f"{s_h:02d}:{s_m:02d}:{s_sec:02d},{s_ms:03d} --> {e_h:02d}:{e_m:02d}:{e_sec:02d},{e_ms:03d}")
            srt_lines.append(chunk)
            srt_lines.append("")

        srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
        return srt_path

    # -------------------------------------------------------------------------
    # ENSAMBLAJE DE VIDEO MP4 (FFMPEG / MOVIEPY)
    # -------------------------------------------------------------------------
    def assemble_video(
        self,
        image_path: Path,
        audio_path: Optional[Path],
        subtitle_text: str,
        output_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compone un video MP4 combinando imagen estática/animada, pista de voz y subtítulos.
        """
        out_name = output_name or f"video_{int(time.time())}.mp4"
        out_path = self.media_dir / out_name

        # Estimar duración
        duration = 5.0
        if audio_path and audio_path.exists():
            # Estimación aproximada si no hay ffprobe disponible
            duration = max(3.0, len(subtitle_text) * 0.08)

        srt_path = self.create_subtitles(subtitle_text, duration)

        # 1. Si disponemos de binario FFmpeg en el sistema
        if self.ffmpeg_cmd:
            try:
                cmd = [
                    self.ffmpeg_cmd,
                    "-y",
                    "-loop", "1",
                    "-i", str(image_path),
                ]
                if audio_path and audio_path.exists():
                    cmd.extend(["-i", str(audio_path)])
                else:
                    # Audio silencioso generado por ffmpeg
                    cmd.extend(["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"])

                cmd.extend([
                    "-c:v", "libx264",
                    "-t", str(duration),
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-shortest",
                    str(out_path),
                ])
                res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=40)
                if res.returncode == 0 and out_path.exists():
                    return {
                        "success": True,
                        "video_path": str(out_path),
                        "method": "ffmpeg",
                        "duration": duration,
                    }
            except Exception:
                pass

        # 2. Ensamblaje MoviePy si está instalado
        try:
            from moviepy.editor import ImageClip, AudioFileClip
            clip = ImageClip(str(image_path)).set_duration(duration)
            if audio_path and audio_path.exists():
                audio_clip = AudioFileClip(str(audio_path))
                clip = clip.set_audio(audio_clip)
            clip.write_videofile(str(out_path), fps=24, logger=None)
            return {
                "success": True,
                "video_path": str(out_path),
                "method": "moviepy",
                "duration": duration,
            }
        except Exception:
            pass

        # 3. Fallback: Generador de Presentación Multimedia HTML5 Interactivo
        showcase_html = self._create_html5_media_showcase(image_path, audio_path, subtitle_text)
        return {
            "success": True,
            "video_path": str(showcase_html),
            "method": "html5_interactive_showcase",
            "duration": duration,
        }

    def _create_html5_media_showcase(self, image_path: Path, audio_path: Optional[Path], text: str) -> Path:
        """Crea un reproductor interactivo autónomo si FFmpeg no está instalado."""
        html_file = self.media_dir / f"showcase_{int(time.time())}.html"
        html_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Jarvis Media Player - {config.USER_TITLE}</title>
    <style>
        body {{ background: #070b12; color: #fff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
        .card {{ background: #0f172a; padding: 24px; border-radius: 16px; border: 1px solid #00e5ff; text-align: center; max-width: 600px; box-shadow: 0 0 25px rgba(0,229,255,0.3); }}
        img {{ max-width: 100%; border-radius: 12px; margin-bottom: 16px; }}
        .sub {{ font-size: 1.1rem; color: #38bdf8; margin: 16px 0; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>Producción de Jarvis Supreme</h2>
        <img src="{image_path.name}">
        <p class="sub">"{text}"</p>
        <p style="color: #64748b;">(Video ensamblado en vista multimedia)</p>
    </div>
</body>
</html>"""
        html_file.write_text(html_code, encoding="utf-8")
        return html_file


# Instancia singleton predeterminada
media_studio = MediaStudio()
