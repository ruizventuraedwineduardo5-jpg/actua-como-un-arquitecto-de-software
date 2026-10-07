"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - SISTEMA DE VOZ BIDIRECCIONAL STREAMING
=============================================================================
Detección de entorno (Android/Termux vs PC), captura continua de voz (STT)
y salida de audio fluida ultra-realista con Edge-TTS, Termux-TTS o Pyttsx3.
=============================================================================
"""

import os
import sys
import time
import shutil
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

import config

# Intento de cargar edge-tts
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Intento de cargar pyttsx3
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


class VoiceSystem:
    """
    Controlador universal de entrada y salida de voz para Jarvis Supreme.
    """

    def __init__(self, media_dir: Optional[Path] = None):
        self.media_dir = media_dir or config.MEDIA_DIR
        self.media_dir.mkdir(parents=True, exist_ok=True)
        self.termux_tts_cmd = shutil.which("termux-tts-speak")
        self.termux_stt_cmd = shutil.which("termux-speech-to-text")
        self.termux_player_cmd = shutil.which("termux-media-player")

        self.offline_engine = None
        if PYTTSX3_AVAILABLE:
            try:
                self.offline_engine = pyttsx3.init()
                self.offline_engine.setProperty("rate", 160)
            except Exception:
                self.offline_engine = None

    # -------------------------------------------------------------------------
    # SÍNTESIS DE VOZ (TEXT-TO-SPEECH)
    # -------------------------------------------------------------------------
    def speak(self, text: str, wait: bool = False) -> bool:
        """
        Sintetiza la voz de Jarvis utilizando el motor óptimo según la plataforma.
        """
        clean_text = text.replace('"', '\\"').replace("`", "")

        # 1. Android con Termux API nativo (Respuesta inmediata sin latencia de red)
        if (config.IS_ANDROID or config.IS_TERMUX) and self.termux_tts_cmd:
            try:
                cmd = [
                    self.termux_tts_cmd,
                    "-e", config.TERMUX_TTS_ENGINE,
                    "-l", "es",
                    clean_text,
                ]
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                pass

        # 2. Edge-TTS con voz neuronal humana de alta definición
        if EDGE_TTS_AVAILABLE:
            try:
                loop = None
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    pass

                if loop and loop.is_running():
                    loop.create_task(self._async_speak_edge(clean_text, wait=wait))
                    return True
                else:
                    mp3_file = self.media_dir / f"tts_{int(time.time() * 1000)}.mp3"
                    asyncio.run(self._generate_edge_tts(clean_text, mp3_file))
                    if mp3_file.exists() and mp3_file.stat().st_size > 500:
                        self._play_audio(mp3_file, wait=wait)
                        return True
            except Exception:
                pass

        # 3. Offline Pyttsx3 (SAPI5 en Windows / espeak en Linux)
        if self.offline_engine:
            try:
                self.offline_engine.say(clean_text)
                if wait:
                    self.offline_engine.runAndWait()
                return True
            except Exception:
                pass

        # Fallback visual en HUD de consola
        return False

    async def _async_speak_edge(self, text: str, wait: bool = False):
        try:
            mp3_file = self.media_dir / f"tts_{int(time.time() * 1000)}.mp3"
            await self._generate_edge_tts(text, mp3_file)
            if mp3_file.exists() and mp3_file.stat().st_size > 500:
                self._play_audio(mp3_file, wait=wait)
        except Exception:
            pass

    async def _generate_edge_tts(self, text: str, output_file: Path):
        communicate = edge_tts.Communicate(
            text=text,
            voice=config.EDGE_TTS_VOICE,
            rate=config.EDGE_TTS_RATE,
            pitch=config.EDGE_TTS_PITCH,
        )
        await communicate.save(str(output_file))

    async def generate_speech_file(self, text: str, output_file: Optional[Path] = None) -> Optional[Path]:
        """Genera un archivo MP3 con la locución de voz (útil para el ensamblador de video)."""
        dest = output_file or (self.media_dir / f"speech_{int(time.time())}.mp3")
        if EDGE_TTS_AVAILABLE:
            try:
                await self._generate_edge_tts(text, dest)
                if dest.exists():
                    return dest
            except Exception:
                pass
        return None

    def _play_audio(self, audio_file: Path, wait: bool = False):
        """Reproduce un archivo de audio según los reproductores del sistema."""
        players = []
        if config.IS_TERMUX and self.termux_player_cmd:
            players.append([self.termux_player_cmd, "play", str(audio_file)])

        for cmd_name in ["ffplay", "mpv", "play", "aplay", "paplay"]:
            cmd_path = shutil.which(cmd_name)
            if cmd_path:
                if cmd_name == "ffplay":
                    players.append([cmd_path, "-nodisp", "-autoexit", "-loglevel", "quiet", str(audio_file)])
                elif cmd_name == "mpv":
                    players.append([cmd_path, "--no-video", "--really-quiet", str(audio_file)])
                else:
                    players.append([cmd_path, str(audio_file)])

        for player_args in players:
            try:
                if wait:
                    subprocess.run(player_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=25)
                else:
                    subprocess.Popen(player_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except Exception:
                continue

    # -------------------------------------------------------------------------
    # RECONOCIMIENTO DE VOZ CONTINUO (SPEECH-TO-TEXT)
    # -------------------------------------------------------------------------
    def listen_voice(self, prompt_text: str = "Escuchando a Edwin...") -> Optional[str]:
        """
        Escucha una locución de voz y la transcribe a texto.
        """
        # 1. Android Termux API
        if (config.IS_ANDROID or config.IS_TERMUX) and self.termux_stt_cmd:
            try:
                res = subprocess.run(
                    [self.termux_stt_cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10,
                )
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip()
            except Exception:
                pass

        # 2. Reconocedor PC vía SpeechRecognition si está presente
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.6)
                audio = r.listen(source, timeout=6, phrase_time_limit=12)
                text = r.recognize_google(audio, language="es-ES")
                return text
        except Exception:
            pass

        return None


# Instancia singleton predeterminada
voice_system = VoiceSystem()
