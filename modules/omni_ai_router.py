"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - ENRUTADOR UNIFICADO MULTI-IA
=============================================================================
Enrutador de IA gratuito y multi-proveedor sin requerimiento obligatorio
de tarjeta de crédito:
- Groq (Llama 3.3 70B, Mixtral 8x7B)
- DeepSeek (V3 & R1 Reasoner)
- DuckDuckGo AI (GPT-4o-mini, Llama 3 70B libre sin API key)
- Hugging Face Inference API
- Pollinations.ai (Texto libre & Generación de Imágenes Flux/SD)
- Google Gemini API (Grounding y Visión)
- Offline SLM Fallback
=============================================================================
"""

import os
import json
import enum
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

import config
from modules.ai_engine import ai_engine


class AIContext(enum.Enum):
    GENERAL = "general"
    CODE = "code"
    FAST_VOICE = "fast_voice"
    LOGIC_REASONING = "logic_reasoning"
    WEB_SEARCH = "web_search"
    CREATIVE = "creative"
    FREE_TIER = "free_tier"


class BaseAIProvider:
    name: str = "base"

    def is_available(self) -> bool:
        return False

    def complete(self, prompt: str, system_prompt: str, model: Optional[str] = None) -> str:
        raise NotImplementedError


class GroqProvider(BaseAIProvider):
    name = "Groq"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.GROQ_API_KEY
        self.default_model = config.DEFAULT_GROQ_MODEL

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def complete(self, prompt: str, system_prompt: str, model: Optional[str] = None) -> str:
        target_model = model or self.default_model
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.5,
            "max_tokens": 3000,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Jarvis-Omni-Supreme/2.5",
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()


class DeepSeekProvider(BaseAIProvider):
    name = "DeepSeek"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.DEEPSEEK_API_KEY
        self.default_model = config.DEFAULT_DEEPSEEK_MODEL

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def complete(self, prompt: str, system_prompt: str, model: Optional[str] = None) -> str:
        target_model = model or self.default_model
        url = "https://api.deepseek.com/chat/completions"
        payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 4096,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Jarvis-Omni-Supreme/2.5",
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()


class PollinationsAIProvider(BaseAIProvider):
    """
    Proveedor completamente gratuito y sin clave de API.
    Ofrece modelos de lenguaje (OpenAI, Claude, Mistral) y generación de imágenes.
    """
    name = "Pollinations.ai"

    def is_available(self) -> bool:
        # Siempre disponible si hay conexión a internet
        return True

    def complete(self, prompt: str, system_prompt: str, model: Optional[str] = None) -> str:
        target_model = model or config.DEFAULT_POLLINATIONS_TEXT_MODEL
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "model": target_model,
            "seed": int(time.time()),
            "jsonMode": False,
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Jarvis-Omni-Supreme/2.5",
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=18) as resp:
            res_text = resp.read().decode("utf-8")
            return res_text.strip()


class DuckDuckGoAIProvider(BaseAIProvider):
    """
    Proveedor DuckDuckGo AI (acceso gratuito a modelos de última generación sin tarjetas ni cuentas).
    """
    name = "DuckDuckGo AI"

    def is_available(self) -> bool:
        return True

    def complete(self, prompt: str, system_prompt: str, model: Optional[str] = None) -> str:
        # Protocolo DuckDuckGo AI vqd token
        target_model = model or "gpt-4o-mini"
        # 1. Obtener token VQD
        status_url = "https://duckduckgo.com/duckchat/v1/status"
        headers_init = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "x-vqd-accept": "1",
        }
        req_vqd = urllib.request.Request(status_url, headers=headers_init)
        with urllib.request.urlopen(req_vqd, timeout=8) as r_vqd:
            vqd = r_vqd.headers.get("x-vqd-4")

        if not vqd:
            raise RuntimeError("No se pudo obtener token de DuckDuckGo AI")

        # 2. Consultar chat
        chat_url = "https://duckduckgo.com/duckchat/v1/chat"
        combined_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
        payload = {
            "model": target_model,
            "messages": [{"role": "user", "content": combined_prompt}],
        }
        headers_chat = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "x-vqd-4": vqd,
        }
        req_chat = urllib.request.Request(
            chat_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers_chat,
            method="POST",
        )
        result_text = []
        with urllib.request.urlopen(req_chat, timeout=15) as r_chat:
            for line in r_chat:
                line_str = line.decode("utf-8").strip()
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        if "message" in chunk:
                            result_text.append(chunk["message"])
                    except Exception:
                        pass
        full_res = "".join(result_text).strip()
        if full_res:
            return full_res
        raise RuntimeError("Respuesta vacía de DuckDuckGo AI")


class HuggingFaceProvider(BaseAIProvider):
    name = "HuggingFace"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.HUGGINGFACE_API_KEY
        self.default_model = "meta-llama/Meta-Llama-3-8B-Instruct"

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def complete(self, prompt: str, system_prompt: str, model: Optional[str] = None) -> str:
        target_model = model or self.default_model
        url = f"https://api-inference.huggingface.co/models/{target_model}"
        payload = {
            "inputs": f"<|system|>\n{system_prompt}</s>\n<|user|>\n{prompt}</s>\n<|assistant|>",
            "parameters": {"max_new_tokens": 1024, "return_full_text": False},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            return str(data)


class GeminiProvider(BaseAIProvider):
    name = "Gemini"

    def is_available(self) -> bool:
        return ai_engine.is_online_available()

    def complete(self, prompt: str, system_prompt: str, model: Optional[str] = None) -> str:
        return ai_engine.generate_text(
            prompt=prompt,
            system_instruction=system_prompt,
            use_search=True,
        )


class OmniAIRouter:
    """
    Enrutador dinámico que selecciona inteligentemente el mejor motor
    según el contexto de la solicitud y garantiza la personalidad de Jarvis.
    """

    def __init__(self):
        self.groq = GroqProvider()
        self.deepseek = DeepSeekProvider()
        self.gemini = GeminiProvider()
        self.pollinations = PollinationsAIProvider()
        self.duckduckgo = DuckDuckGoAIProvider()
        self.hf = HuggingFaceProvider()

        # Cadena de prioridad por contexto
        self.context_routes = {
            AIContext.CODE: [self.deepseek, self.groq, self.gemini, self.duckduckgo, self.pollinations],
            AIContext.FAST_VOICE: [self.groq, self.gemini, self.pollinations, self.duckduckgo],
            AIContext.LOGIC_REASONING: [self.deepseek, self.gemini, self.groq, self.duckduckgo],
            AIContext.WEB_SEARCH: [self.gemini, self.duckduckgo, self.groq],
            AIContext.CREATIVE: [self.pollinations, self.gemini, self.groq],
            AIContext.FREE_TIER: [self.duckduckgo, self.pollinations, self.groq],
            AIContext.GENERAL: [self.gemini, self.groq, self.deepseek, self.duckduckgo, self.pollinations],
        }

    def detect_context(self, prompt: str) -> AIContext:
        """Determina automáticamente el contexto idóneo a partir del texto."""
        prompt_lower = prompt.lower()
        if any(w in prompt_lower for w in ["código", "python", "script", "función", "bug", "refactor", "html", "css", "javascript"]):
            return AIContext.CODE
        if any(w in prompt_lower for w in ["rápido", "voz", "habla", "dime ya", "eco"]):
            return AIContext.FAST_VOICE
        if any(w in prompt_lower for w in ["por qué", "demuestra", "lógica", "matemática", "algoritmo", "raciocinio"]):
            return AIContext.LOGIC_REASONING
        if any(w in prompt_lower for w in ["noticias", "precio hoy", "clima hoy", "busca en internet", "investiga", "quién ganó"]):
            return AIContext.WEB_SEARCH
        if any(w in prompt_lower for w in ["historia", "poema", "cuento", "crea un personaje", "imaginativo"]):
            return AIContext.CREATIVE
        return AIContext.GENERAL

    def harmonize_response(self, raw_text: str) -> str:
        """
        Unifica la respuesta para asegurar que encaje con la personalidad de Jarvis Supreme
        y respete la identidad hacia Edwin.
        """
        cleaned = raw_text.strip()
        # Si la respuesta parece fría o no menciona al usuario en respuestas largas
        if not any(t in cleaned for t in [config.USER_TITLE, config.USER_NAME, "Señor"]):
            # Prefijo sutil y natural si no es un bloque puro de código
            if not cleaned.startswith("```"):
                cleaned = f"{config.USER_TITLE}, {cleaned[0].lower() + cleaned[1:] if len(cleaned) > 1 else cleaned}"
        return cleaned

    def route_request(
        self,
        prompt: str,
        context: Optional[AIContext] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Enruta la petición al proveedor óptimo. Si uno falla, pasa en cascada al siguiente.
        """
        ctx = context or self.detect_context(prompt)
        sys_prompt = system_prompt or config.JARVIS_PERSONA
        providers = self.context_routes.get(ctx, self.context_routes[AIContext.GENERAL])

        errors = []
        for provider in providers:
            try:
                # Comprobamos si tiene claves si el proveedor las requiere
                if isinstance(provider, (GroqProvider, DeepSeekProvider, HuggingFaceProvider)):
                    if not provider.is_available():
                        continue
                response = provider.complete(prompt, sys_prompt)
                if response and len(response.strip()) > 0:
                    harmonized = self.harmonize_response(response)
                    return {
                        "success": True,
                        "provider": provider.name,
                        "context": ctx.value,
                        "response": harmonized,
                        "errors": errors,
                    }
            except Exception as e:
                errors.append(f"{provider.name}: {str(e)}")
                continue

        # Último recurso: Motor Offline SLM
        offline_resp = ai_engine.offline_slm.process(prompt)
        return {
            "success": True,
            "provider": "Offline-SLM",
            "context": ctx.value,
            "response": offline_resp,
            "errors": errors,
        }


# Instancia singleton predeterminada
omni_router = OmniAIRouter()
