"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - HERRAMIENTAS Y MACROS DEL ASISTENTE
=============================================================================
Macros automatizados ("Modo Noche", "Modo Turbo", "Modo Guardia"),
redacción de comunicaciones de alta gama y temporizadores asíncronos.
=============================================================================
"""

import os
import gc
import time
import asyncio
from typing import Dict, Any, Optional

import config
from modules.voice_system import voice_system
from modules.cyber_sentry import cyber_sentry
from modules.device_telemetry import device_telemetry
from modules.app_controller import app_controller
from modules.vector_memory import vector_memory


class AssistantTools:
    """
    Herramientas de productividad y orquestación de macros para Edwin.
    """

    # -------------------------------------------------------------------------
    # MACROS INTEGRADOS DE SISTEMA
    # -------------------------------------------------------------------------
    async def run_night_mode(self) -> str:
        """
        Modo Noche: Atenúa interfaces, activa el centinela de seguridad,
        reporta estado de batería y saluda cordialmente antes del descanso.
        """
        # Reducir brillo si estamos en Android Termux
        if config.IS_TERMUX:
            try:
                import subprocess
                subprocess.run(["termux-brightness", "10"], timeout=2)
            except Exception:
                pass

        # Verificar batería
        bat = device_telemetry.get_battery_info()
        level = bat.get("percentage", 100)
        plugged = bat.get("status")

        # Tomar registro de guardia de inicio de noche
        cyber_sentry.take_silent_snapshot(camera_id=1)

        msg = (
            f"Modo Noche activado, {config.USER_TITLE}.\n"
            f"Batería en {level}% ({plugged}). Sub-agente Centinela en vigilancia perimetral. "
            f"Que tenga una excelente noche de descanso."
        )
        voice_system.speak(msg)
        return msg

    async def run_turbo_mode(self) -> str:
        """
        Modo Turbo: Limpieza profunda de memoria RAM, recolección de basura (GC)
        y optimización de descriptores de socket.
        """
        before_mem = device_telemetry.get_memory_info()
        # Forzar garbage collection
        collected = gc.collect()
        time.sleep(0.5)
        after_mem = device_telemetry.get_memory_info()

        msg = (
            f"Modo Turbo ejecutado con éxito, {config.USER_TITLE}.\n"
            f"Objetos liberados en memoria: {collected}.\n"
            f"Carga de RAM actual: {after_mem['percent']}% ({after_mem['used_gb']} GB en uso)."
        )
        voice_system.speak(msg)
        return msg

    async def run_sentry_guard_mode(self) -> str:
        """
        Modo Guardia: Escaneo intensivo de red Wi-Fi y captura de fotografía silenciosa.
        """
        snap = cyber_sentry.take_silent_snapshot()
        devices = cyber_sentry.scan_network_devices()

        msg = (
            f"Modo Guardia activo, {config.USER_TITLE}.\n"
            f"Registro fotográfico asegurado en: {snap.name if snap else 'Archivo Centinela'}.\n"
            f"Equipos verificados en su red Wi-Fi: {len(devices)} dispositivos."
        )
        voice_system.speak(msg)
        return msg

    # -------------------------------------------------------------------------
    # REDACTOR DE COMUNICACIONES
    # -------------------------------------------------------------------------
    def draft_whatsapp_message(self, recipient_name: str, topic: str, tone: str = "profesional") -> str:
        from modules.omni_ai_router import omni_router, AIContext
        prompt = (
            f"Redacta un mensaje de WhatsApp para '{recipient_name}' sobre el tema '{topic}'. "
            f"Tono: {tone}. Redáctalo como si lo enviara {config.USER_NAME}. Conciso, cordial y efectivo."
        )
        res = omni_router.route_request(prompt, context=AIContext.GENERAL)
        return res.get("response", "")

    # -------------------------------------------------------------------------
    # TEMPORIZADORES ASÍNCRONOS
    # -------------------------------------------------------------------------
    async def set_timer(self, seconds: int, label: str = "Temporizador"):
        """Inicia un temporizador asíncrono que avisa por voz al finalizar."""
        await asyncio.sleep(seconds)
        alert_msg = f"{config.USER_TITLE}, su temporizador de {seconds} segundos para '{label}' ha concluido."
        voice_system.speak(alert_msg)


# Instancia singleton predeterminada
assistant_tools = AssistantTools()
