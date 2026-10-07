"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - ORQUESTADOR MAESTRO Y NÚCLEO OPERATIVO
=============================================================================
Loop principal de eventos asíncrono (asyncio), escucha activa de voz streaming,
orquestador de enjambre de sub-agentes, interfaz CLI/HUD cyberpunk y
enrutamiento dinámico de inteligencia multimodal.
=============================================================================
"""

import os
import sys
import time
import shutil
import asyncio
import traceback
from typing import Optional, Dict, Any

import config
from modules.ai_engine import ai_engine
from modules.omni_ai_router import omni_router, AIContext
from modules.live_screen_vision import screen_vision
from modules.app_controller import app_controller
from modules.app_builder_engine import app_builder
from modules.self_healing import self_healer
from modules.self_evolution import evolution_engine
from modules.agent_swarm import swarm_coordinator
from modules.vector_memory import vector_memory
from modules.media_studio import media_studio
from modules.voice_system import voice_system
from modules.device_telemetry import device_telemetry
from modules.cyber_sentry import cyber_sentry
from modules.mechanics_tracker import mechanics_tracker
from modules.finance_manager import finance_manager
from modules.assistant_tools import assistant_tools


class JarvisSupremeKernel:
    """
    Núcleo de orquestación central de Jarvis Omni-Ghost Supreme.
    """

    def __init__(self):
        self.is_running = True
        self.voice_output_enabled = True
        # Instalar capturador global de auto-reparación
        self_healer.install_global_hook()

    # -------------------------------------------------------------------------
    # INTERFAZ HUD FUTURISTA PARA LA TERMINAL
    # -------------------------------------------------------------------------
    def print_hud_banner(self):
        banner = f"""\033[1;36m
   ╔═══════════════════════════════════════════════════════════════════════════╗
   ║        \033[1;37m░░█ ▄▀█ █▀█ █ █ █▀   █▀█ █▀▄▀█ █▄░█ █   █▀▀ █░█ █▀█ █▀ ▀█▀\033[1;36m         ║
   ║        \033[1;37m█▄█ █▀█ █▀▄ ▀▄▀ █ ▄█   █▄█ █░▀░█ █░▀█ █   █▄█ █▀█ █▄█ ▄█ ░█░\033[1;36m         ║
   ║                       \033[1;33m>>> V2.5.0 SUPREME EDITION <<<\033[1;36m                      ║
   ╚═══════════════════════════════════════════════════════════════════════════╝\033[0m
   \033[1;32m● USUARIO MAESTRO:\033[0m {config.USER_TITLE} ({config.USER_NAME})
   \033[1;32m● ENTORNO ACTIVO:\033[0m {config.CURRENT_PLATFORM} | \033[1;34mTZ:\033[0m {config.TIMEZONE}
   \033[1;32m● META-IDE APPS:\033[0m http://localhost:{app_builder.active_port}/
   \033[1;32m● ENJAMBRE MULTI-AGENTE:\033[0m 4 Sub-Agentes en Concurrencia
   \033[1;32m● ESTADO SLM/ONLINE:\033[0m {'Online (Gemini/Groq/DeepSeek)' if ai_engine.is_online_available() else 'Offline Cognitivo (SLM Activo)'}
   ─────────────────────────────────────────────────────────────────────────────
   \033[1;35mComandos Rápidos:\033[0m 'ayuda' | 'pantalla' | 'crear app <n>' | 'moto' | 'gasto <$>' | 'salir'
   ─────────────────────────────────────────────────────────────────────────────"""
        print(banner)

    # -------------------------------------------------------------------------
    # ENRUTADOR DINÁMICO DE COMANDOS E INSTRUCCIONES
    # -------------------------------------------------------------------------
    async def process_user_command(self, raw_input: str) -> str:
        command = raw_input.strip()
        if not command:
            return ""

        cmd_lower = command.lower()

        # 1. Registrar en memoria episódica
        vector_memory.record_turn(role="user", message=command)

        # 2. Comandos de control directo del sistema
        if cmd_lower in ["salir", "exit", "quit"]:
            self.is_running = False
            return f"Hasta pronto, {config.USER_TITLE}. Poniendo los sistemas de Jarvis en reposo."

        if cmd_lower in ["ayuda", "help", "comandos"]:
            return self._cmd_help()

        if cmd_lower in ["estado", "status", "telemetria", "diagnostico"]:
            return self._cmd_status()

        # 3. Módulo de Percepción de Pantalla
        if any(w in cmd_lower for w in ["pantalla", "screen", "qué hay en la pantalla", "que ves"]):
            return await self._cmd_screen_vision(command)

        # 4. Módulo Meta-Creador de Apps (Mini-Antigravity)
        if cmd_lower.startswith("crear app") or cmd_lower.startswith("build app"):
            return self._cmd_build_app(command)

        if cmd_lower in ["apps", "listar apps", "mis apps"]:
            return self._cmd_list_apps()

        # 5. Módulo de Auto-Evolución (Crear nuevo plugin)
        if cmd_lower.startswith("aprende a") or cmd_lower.startswith("evolve") or cmd_lower.startswith("nuevo plugin"):
            return await self._cmd_evolve(command)

        # 6. Módulo Mecánico de la Moto
        if any(w in cmd_lower for w in ["moto", "mecanica", "kilometraje", "aceite moto"]):
            return self._cmd_mechanics(command)

        # 7. Módulo Financiero
        if any(w in cmd_lower for w in ["gasto", "gasté", "finanzas", "presupuesto", "dinero", "exportar excel"]):
            return self._cmd_finance(command)

        # 8. Módulo de Ciberseguridad y Centinela
        if any(w in cmd_lower for w in ["foto", "camara", "snapshot"]):
            return self._cmd_camera_snapshot()

        if any(w in cmd_lower for w in ["scan wifi", "escanear red", "intrusos", "red"]):
            return self._cmd_wifi_scan()

        if cmd_lower.startswith("p2p"):
            return self._cmd_p2p()

        # 9. Macros del Asistente
        if "modo noche" in cmd_lower:
            return await assistant_tools.run_night_mode()

        if "modo turbo" in cmd_lower:
            return await assistant_tools.run_turbo_mode()

        if "modo guardia" in cmd_lower:
            return await assistant_tools.run_sentry_guard_mode()

        # 10. Comprobación de Plugins Dinámicos (Hot-loaded)
        plugin_output = await evolution_engine.try_execute_plugin(command)
        if plugin_output:
            vector_memory.record_turn(role="jarvis", message=plugin_output)
            return plugin_output

        # 11. Enrutamiento General a IAs (Gemini / Groq / DeepSeek / DuckDuckGo / Pollinations / SLM)
        # Recuperar contexto semántico relevante de la memoria permanente
        memory_ctx = vector_memory.build_memory_context_prompt(command)
        enriched_prompt = f"{memory_ctx}\n\nConsulta actual de {config.USER_TITLE}:\n{command}"

        ai_result = omni_router.route_request(enriched_prompt)
        response_text = ai_result.get("response", "Sin respuesta disponible.")

        # Guardar en memoria de conversación
        vector_memory.record_turn(role="jarvis", message=response_text)
        return response_text

    # -------------------------------------------------------------------------
    # IMPLEMENTACIONES ESPECÍFICAS DE COMANDOS
    # -------------------------------------------------------------------------
    def _cmd_help(self) -> str:
        return (
            f"Manual Operativo de Jarvis Omni-Ghost Supreme:\n"
            f"• 'pantalla': Analiza en tiempo real lo que estás viendo en tu Android o PC.\n"
            f"• 'crear app <nombre> con <descripción>': Genera y aloja una web app en localhost:{app_builder.active_port}.\n"
            f"• 'aprende a <capacidad>': Auto-programa un plugin funcional y lo carga en caliente.\n"
            f"• 'moto' / 'kilometraje <km>': Auditoría técnica y alertas de mantenimiento de tu vehículo.\n"
            f"• 'gasto <monto> <concepto>' / 'exportar excel': Auditoría de gastos y planilla .xlsx.\n"
            f"• 'modo noche' / 'modo turbo' / 'modo guardia': Ejecución de macros de alto nivel.\n"
            f"• 'foto': Captura fotográfica silenciosa de seguridad con la cámara frontal.\n"
            f"• 'scan wifi': Escanea intrusos en la red Wi-Fi local.\n"
            f"• Cualquier otra pregunta: Razonamiento mediante DeepSeek, Groq, Gemini o DuckDuckGo AI."
        )

    def _cmd_status(self) -> str:
        telemetry = device_telemetry.format_hud_summary()
        agents = swarm_coordinator.get_swarm_status()
        agent_lines = "\n".join([f"  - [{a['name']}] ({'ACTIVO' if a['running'] else 'OFF'}): {a['status']}" for a in agents])
        return (
            f"{config.USER_TITLE}, reporte consolidado de sistemas:\n"
            f"{telemetry}\n"
            f"Estado del Enjambre de Sub-Agentes:\n{agent_lines}\n"
            f"Apps Creadas Activas: {len(app_builder.list_apps())}\n"
            f"Plugins Dinámicos: {len(evolution_engine.active_plugins)}"
        )

    async def _cmd_screen_vision(self, command: str) -> str:
        print("\033[1;33m[PERCEPCIÓN VISUAL] Capturando fotograma de pantalla...\033[0m")
        result = screen_vision.inspect_screen(query=command)
        return result["analysis"]

    def _cmd_build_app(self, command: str) -> str:
        parts = command.replace("crear app", "").replace("build app", "").strip()
        name = "App Personalizada"
        desc = "Aplicación interactiva generada a petición"
        if " con " in parts:
            name, desc = parts.split(" con ", 1)
        elif parts:
            name = parts

        print(f"\033[1;33m[META-IDE] Compilando y alojando '{name}'...\033[0m")
        res = app_builder.build_application(name=name, description=desc, auto_launch=True)
        return (
            f"{config.USER_TITLE}, he construido y desplegado la aplicación '{res['name']}'.\n"
            f"URL Local: {res['url']}\n"
            f"Se ha abierto automáticamente en su navegador predeterminado."
        )

    def _cmd_list_apps(self) -> str:
        apps = app_builder.list_apps()
        if not apps:
            return f"{config.USER_TITLE}, aún no ha creado ninguna aplicación personalizada."
        lines = [f"{config.USER_TITLE}, aplicaciones locales disponibles en localhost:{app_builder.active_port}:"]
        for a in apps:
            lines.append(f"• {a.get('name', 'App')}: {a.get('url', '')}")
        return "\n".join(lines)

    async def _cmd_evolve(self, command: str) -> str:
        request_text = command.replace("aprende a", "").replace("evolve", "").replace("nuevo plugin", "").strip()
        print(f"\033[1;35m[AUTO-EVOLUCIÓN] Diseñando, validando y cargando nuevo plugin para: '{request_text}'...\033[0m")
        res = await evolution_engine.evolve_capability(request_text)
        return res.get("message") or str(res)

    def _cmd_mechanics(self, command: str) -> str:
        # Si se solicita actualizar kilometraje
        if "kilometraje" in command or "km" in command:
            import re
            m = re.search(r"(\d{3,6})", command)
            if m:
                new_km = int(m.group(1))
                mechanics_tracker.update_mileage(plate="EDW-001", new_km=new_km)
                return f"{config.USER_TITLE}, kilometraje actualizado a {new_km:,} km.\n" + mechanics_tracker.format_report_speech("EDW-001")

        return mechanics_tracker.format_report_speech("EDW-001")

    def _cmd_finance(self, command: str) -> str:
        if "exportar excel" in command or "excel" in command:
            file_path = finance_manager.export_to_excel()
            return f"{config.USER_TITLE}, he consolidado su auditoría financiera en la hoja de Excel:\n{file_path}"

        if any(w in command for w in ["gasto", "gasté"]):
            res = finance_manager.record_voice_expense(command)
            return res["message"]

        summary = finance_manager.get_summary()
        return (
            f"{config.USER_TITLE}, resumen contable:\n"
            f"• Total Egresos Registrados: ${summary['total_expenses']:,.2f}\n"
            f"• Número de Movimientos: {summary['total_transactions']}\n"
            f"Para exportar la auditoría completa a Excel diga 'exportar excel'."
        )

    def _cmd_camera_snapshot(self) -> str:
        snap = cyber_sentry.take_silent_snapshot()
        if snap:
            return f"{config.USER_TITLE}, captura fotográfica frontal asegurada en: {snap}"
        return f"{config.USER_TITLE}, la cámara no se encuentra disponible en este momento."

    def _cmd_wifi_scan(self) -> str:
        devices = cyber_sentry.scan_network_devices()
        lines = [f"{config.USER_TITLE}, dispositivos identificados en la red Wi-Fi:"]
        for d in devices:
            lines.append(f"• IP: {d['ip']} | MAC: {d.get('mac', 'N/A')} | Estado: {d.get('status', 'OK')}")
        return "\n".join(lines)

    def _cmd_p2p(self) -> str:
        url = cyber_sentry.start_p2p_server()
        return f"{config.USER_TITLE}, servidor P2P local activo para transferencia entre móvil y PC en:\n{url}"

    # -------------------------------------------------------------------------
    # BUCLE DE EVENTOS PRINCIPAL ASÍNCRONO
    # -------------------------------------------------------------------------
    async def run(self):
        self.print_hud_banner()

        # Iniciar Enjambre de Sub-Agentes en segundo plano
        await swarm_coordinator.start_all()

        # Saludo inicial
        greeting = f"Sistemas en línea, {config.USER_TITLE}. Jarvis Omni-Ghost Supreme listo a su orden."
        print(f"\n\033[1;36m[JARVIS]\033[0m {greeting}\n")
        if self.voice_output_enabled:
            voice_system.speak(greeting)

        # Loop interactivo
        while self.is_running:
            try:
                # Entrada de usuario (soporte consola y voz)
                sys.stdout.write(f"\033[1;32m[{config.USER_NAME}@JarvisSupreme]>\033[0m ")
                sys.stdout.flush()

                loop = asyncio.get_event_loop()
                user_input = await loop.run_in_executor(None, sys.stdin.readline)
                if not user_input:
                    break

                text = user_input.strip()
                if not text:
                    continue

                # Procesar comando
                start_t = time.time()
                response = await self.process_user_command(text)
                elapsed = time.time() - start_t

                if response:
                    print(f"\n\033[1;36m[JARVIS SUPREME] ({elapsed:.2f}s)\033[0m")
                    print(f"{response}\n")
                    if self.voice_output_enabled and len(response) < 400:
                        voice_system.speak(response)

            except (KeyboardInterrupt, EOFError):
                print("\nInterrupción detectada. Cerrando sistemas...")
                self.is_running = False
                break
            except Exception as e:
                # Captura por el sistema de auto-reparación (Self-Healing)
                print(f"\n\033[1;31m[ALERTA DE ERROR]: {e}\033[0m")
                repair_info = self_healer.handle_exception(e)
                if repair_info.get("repaired"):
                    print(f"\033[1;32m[SELF-HEALING]: Módulo reparado en caliente exitosamente.\033[0m")

        # Cierre ordenado
        await swarm_coordinator.stop_all()
        app_builder.server.stop()
        cyber_sentry.stop_p2p_server()
        print("\033[1;33m[JARVIS] Sistemas apagados con éxito.\033[0m")


def main():
    kernel = JarvisSupremeKernel()
    try:
        asyncio.run(kernel.run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
