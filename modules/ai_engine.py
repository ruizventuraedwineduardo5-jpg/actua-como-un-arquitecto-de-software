"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - AI ENGINE (GEMINI MULTIMODAL & OFFLINE SLM)
=============================================================================
Motor principal de inteligencia artificial con soporte multimodal nativo
(texto, imágenes de pantalla, audio), grounding con Google Search en tiempo
real y selector inteligente online/offline con motor SLM local de respaldo.
=============================================================================
"""

import os
import io
import re
import json
import base64
import urllib.request
import urllib.error
from typing import Optional, Union, Dict, Any, List
from pathlib import Path

import config

# Intento de carga de SDK oficial google-genai
try:
    from google import genai
    from google.genai import types
    GENAI_SDK_AVAILABLE = True
except ImportError:
    GENAI_SDK_AVAILABLE = False


class OfflineSLMEngine:
    """
    Motor local SLM (Small Language Model / Lógica Cognitiva Offline).
    Garantiza que Jarvis responda con su personalidad cuando no hay internet
    o cuando no se dispone de claves de API activas.
    """

    def __init__(self):
        self.offline_intents = {
            r"(hora|qué hora es)": self._intent_time,
            r"(fecha|qué día es|calendario)": self._intent_date,
            r"(estado|diagnóstico|telemetría|batería|ram)": self._intent_status,
            r"(quién eres|identidad|nombre|presentación)": self._intent_identity,
            r"(crear app|nueva app|desarrollar)": self._intent_app_hint,
            r"(reparar|self healing|error|fallo)": self._intent_healing_hint,
            r"(moto|vehículo|mantenimiento|aceite)": self._intent_mechanics_hint,
            r"(gasto|finanzas|dinero|presupuesto)": self._intent_finance_hint,
        }

    def _intent_time(self, query: str) -> str:
        from datetime import datetime
        now = datetime.now().strftime("%I:%M %p")
        return f"{config.USER_TITLE}, la hora actual en su terminal es {now}."

    def _intent_date(self, query: str) -> str:
        from datetime import datetime
        today = datetime.now().strftime("%A, %d de %B de %Y")
        return f"{config.USER_TITLE}, hoy es {today}."

    def _intent_status(self, query: str) -> str:
        info = config.get_sys_info()
        return (
            f"Diagnóstico Offline de Jarvis Supreme:\n"
            f"- Entorno: {info['platform']}\n"
            f"- Modo: Operación Local Desconectada (SLM)\n"
            f"- Base de Datos: {info['database']}\n"
            f"Todos los sub-sistemas locales continúan plenamente operativos, {config.USER_TITLE}."
        )

    def _intent_identity(self, query: str) -> str:
        return (
            f"Soy Jarvis Omni-Ghost Supreme, su Asistente Personal de Vanguardia, {config.USER_TITLE}. "
            f"Actualmente opero en modo de contingencia local sin requerir conexión externa."
        )

    def _intent_app_hint(self, query: str) -> str:
        return (
            f"{config.USER_TITLE}, el Motor Creador de Apps local está listo. "
            f"Puede solicitar 'crear app <nombre> con <descripción>' y el compilador "
            f"la generará y alojará en http://localhost:{config.WEB_BUILDER_PORT}."
        )

    def _intent_healing_hint(self, query: str) -> str:
        return f"El subsistema de Auto-Reparación (Self-Healing) está vigilando el hilo principal de ejecución."

    def _intent_mechanics_hint(self, query: str) -> str:
        return f"Módulo de Telemetría Mecánica listo. Puede registrar kilometraje o servicios con el comando 'moto'."

    def _intent_finance_hint(self, query: str) -> str:
        return f"Módulo Financiero activo. Puede registrar transacciones diciendo por ejemplo 'gasto 50000 repuestos'."

    def process(self, prompt: str) -> str:
        prompt_clean = prompt.lower().strip()
        for pattern, handler in self.offline_intents.items():
            if re.search(pattern, prompt_clean):
                return handler(prompt)

        # Respuesta general con personalidad Jarvis
        return (
            f"{config.USER_TITLE}, me encuentro operando en modo local SLM fuera de línea. "
            f"He recibido su instrucción: '{prompt}'. Para consultas analíticas complejas o búsqueda "
            f"web en vivo, active su conexión a internet o configure GEMINI_API_KEY. "
            f"No obstante, mis herramientas de automatización, control de apps y meta-IDE "
            f"están a su completa disposición."
        )


class GeminiAIEngine:
    """
    Cliente principal para Google Gemini API (vía SDK google-genai o REST v1beta fallback).
    Incorpora soporte de Google Search Grounding y análisis multimodal (imágenes, pantalla, audio).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = config.DEFAULT_GEMINI_MODEL
        self.offline_slm = OfflineSLMEngine()
        self.client = None
        self._init_sdk_client()

    def _init_sdk_client(self):
        if GENAI_SDK_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                self.client = None

    def is_online_available(self) -> bool:
        """Determina si se dispone de credenciales para procesar en línea."""
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    # -------------------------------------------------------------------------
    # GENERACIÓN DE TEXTO CON BÚSQUEDA WEB EN VIVO (GROUNDING)
    # -------------------------------------------------------------------------
    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        use_search: bool = True,
        temperature: float = 0.7,
    ) -> str:
        """
        Genera una respuesta textual procesada con Gemini.
        Si use_search=True, activa Google Search para obtener información actualizada.
        Si la API no está configurada o falla la red, conmuta transparentemente a OfflineSLM.
        """
        if not self.is_online_available():
            return self.offline_slm.process(prompt)

        system_prompt = system_instruction or config.JARVIS_PERSONA

        # Intento con SDK oficial
        if self.client and GENAI_SDK_AVAILABLE:
            try:
                tools_config = []
                if use_search:
                    try:
                        tools_config.append(types.Tool(google_search=types.GoogleSearch()))
                    except Exception:
                        pass

                cfg = types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                    tools=tools_config if tools_config else None,
                )
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=cfg,
                )
                if response and hasattr(response, "text") and response.text:
                    return response.text.strip()
            except Exception as err:
                # Falla en SDK, intentamos REST fallback antes de saltar a offline
                pass

        # Intento con REST API v1beta
        try:
            return self._generate_rest_fallback(prompt, system_prompt, use_search)
        except Exception:
            return self.offline_slm.process(prompt)

    def _generate_rest_fallback(self, prompt: str, system_prompt: str, use_search: bool) -> str:
        """Fallback directo vía REST HTTP sin dependencias pesadas."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048},
        }
        if use_search:
            payload["tools"] = [{"google_search": {}}]

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                text_result = "".join(p.get("text", "") for p in parts)
                if text_result.strip():
                    return text_result.strip()
        raise RuntimeError("No se obtuvo texto del endpoint REST")

    # -------------------------------------------------------------------------
    # ANÁLISIS MULTIMODAL: IMAGEN Y CAPTURA DE PANTALLA
    # -------------------------------------------------------------------------
    def analyze_image(
        self,
        image_input: Union[str, Path, bytes],
        prompt: str = "¿Qué observas en esta imagen o pantalla? Describe la situación con detalle técnico.",
        mime_type: str = "image/png",
    ) -> str:
        """
        Analiza una imagen en memoria o archivo en disco (frames de pantalla, fotos de cámara).
        """
        # Obtener bytes de la imagen
        image_bytes: bytes = b""
        if isinstance(image_input, (str, Path)):
            p = Path(image_input)
            if p.exists():
                image_bytes = p.read_bytes()
                if p.suffix.lower() in [".jpg", ".jpeg"]:
                    mime_type = "image/jpeg"
                elif p.suffix.lower() == ".webp":
                    mime_type = "image/webp"
            else:
                return f"Error: Archivo de imagen no encontrado en {p}."
        elif isinstance(image_input, bytes):
            image_bytes = image_input

        if not image_bytes:
            return "Error: No se proporcionaron datos de imagen válidos."

        if not self.is_online_available():
            return (
                f"{config.USER_TITLE}, he recibido el fotograma visual ({len(image_bytes)} bytes), "
                f"pero actualmente opero en modo Offline SLM. No es posible ejecutar visión neuronal sin red."
            )

        # Uso con SDK
        if self.client and GENAI_SDK_AVAILABLE:
            try:
                part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt, part],
                    config=types.GenerateContentConfig(
                        system_instruction=config.JARVIS_PERSONA,
                        temperature=0.4,
                    ),
                )
                if response and hasattr(response, "text") and response.text:
                    return response.text.strip()
            except Exception:
                pass

        # Fallback REST v1beta con base64 inline
        try:
            b64_str = base64.b64encode(image_bytes).decode("utf-8")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {"inlineData": {"mimeType": mime_type, "data": b64_str}},
                        ]
                    }
                ],
                "systemInstruction": {"parts": [{"text": config.JARVIS_PERSONA}]},
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    return "".join(p.get("text", "") for p in parts).strip()
        except Exception as e:
            return f"No fue posible procesar la imagen: {e}"

        return "Sin respuesta del motor multimodal."

    # -------------------------------------------------------------------------
    # ANÁLISIS MULTIMODAL: AUDIO
    # -------------------------------------------------------------------------
    def analyze_audio(
        self,
        audio_input: Union[str, Path, bytes],
        prompt: str = "Transcribe y comprende la siguiente locución de voz:",
        mime_type: str = "audio/mp3",
    ) -> str:
        """
        Analiza un archivo o stream de audio y extrae su contenido semántico.
        """
        audio_bytes: bytes = b""
        if isinstance(audio_input, (str, Path)):
            p = Path(audio_input)
            if p.exists():
                audio_bytes = p.read_bytes()
                if p.suffix.lower() == ".wav":
                    mime_type = "audio/wav"
                elif p.suffix.lower() == ".ogg":
                    mime_type = "audio/ogg"
            else:
                return f"Error: Archivo de audio {p} no encontrado."
        elif isinstance(audio_input, bytes):
            audio_bytes = audio_input

        if not self.is_online_available():
            return "Modo Offline: Transcripción de audio neuronal no disponible sin conexión."

        # Fallback REST v1beta
        try:
            b64_str = base64.b64encode(audio_bytes).decode("utf-8")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {"inlineData": {"mimeType": mime_type, "data": b64_str}},
                        ]
                    }
                ]
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    return "".join(p.get("text", "") for p in parts).strip()
        except Exception as e:
            return f"Error procesando audio: {e}"

        return "Sin respuesta de audio."


# Instancia singleton predeterminada
ai_engine = GeminiAIEngine()
