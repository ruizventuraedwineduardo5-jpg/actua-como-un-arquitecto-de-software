"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - ENJAMBRE MULTI-AGENTE EN PARALELO (AGENT SWARM)
=============================================================================
Arquitectura multi-agente asíncrona concurrente:
- SentinelAgent: Telemetría, batería, memoria y seguridad perimetral
- VisionScreenAgent: Ojo vigilante continuo de pantalla
- CoderAgent: Análisis de sintaxis, diagnóstico y auxilio a Self-Healing
- AppBuilderAgent: Construcción y despliegue autónomo de mini-aplicaciones
- SwarmCoordinator: Bus de eventos, balanceo de carga y prioridades
=============================================================================
"""

import time
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable

import config
from modules.live_screen_vision import screen_vision
from modules.app_builder_engine import app_builder

logger = logging.getLogger("JarvisSwarm")


@dataclass
class SwarmMessage:
    sender: str
    recipient: str
    topic: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


class BaseAgent:
    def __init__(self, name: str, role: str, coordinator: "SwarmCoordinator"):
        self.name = name
        self.role = role
        self.coordinator = coordinator
        self.inbox: asyncio.Queue[SwarmMessage] = asyncio.Queue()
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.status_message = "Iniciando"

    async def start(self):
        self.is_running = True
        self._task = asyncio.create_task(self.run_loop())
        logger.info(f"Agente [{self.name}] iniciado ({self.role}).")

    async def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
        logger.info(f"Agente [{self.name}] detenido.")

    async def run_loop(self):
        """Bucle principal de trabajo del agente."""
        while self.is_running:
            try:
                # Procesar mensajes pendientes si existen
                while not self.inbox.empty():
                    msg = await self.inbox.get()
                    await self.handle_message(msg)

                await self.perform_work()
                await asyncio.sleep(2.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en agente [{self.name}]: {e}")
                await asyncio.sleep(4.0)

    async def handle_message(self, message: SwarmMessage):
        pass

    async def perform_work(self):
        pass


class SentinelAgent(BaseAgent):
    """Agente Centinela: Monitorea batería, RAM, temperatura y seguridad en segundo plano."""
    def __init__(self, coordinator: "SwarmCoordinator"):
        super().__init__("Sentinel", "Vigilancia de Telemetría y Ciberseguridad", coordinator)
        self.battery_low_alerted = False

    async def perform_work(self):
        from modules.device_telemetry import device_telemetry
        metrics = device_telemetry.get_metrics()
        bat = metrics.get("battery", {})
        level = bat.get("percentage")

        if level is not None and isinstance(level, (int, float)):
            if level <= 15 and not self.battery_low_alerted:
                self.battery_low_alerted = True
                await self.coordinator.broadcast(
                    sender=self.name,
                    topic="ALERT_BATTERY_LOW",
                    payload={"level": level, "msg": f"{config.USER_TITLE}, nivel crítico de batería ({level}%). Conecte el cargador."},
                )
            elif level > 25:
                self.battery_low_alerted = False

        self.status_message = f"Monitoreo OK | Batería: {level or 'N/A'}% | RAM: {metrics.get('memory', {}).get('percent', 0)}%"
        await asyncio.sleep(6.0)


class VisionScreenAgent(BaseAgent):
    """Agente de Visión: Monitorea la actividad visual en pantalla de forma continua."""
    def __init__(self, coordinator: "SwarmCoordinator"):
        super().__init__("VisionScreen", "Percepción Visual de Pantalla en Tiempo Real", coordinator)
        self.last_app = "Desconocida"

    async def perform_work(self):
        # Actualiza fotograma y detecta app activa
        screen_vision.capture_frame()
        app = screen_vision.detect_active_application()
        if app != self.last_app:
            self.last_app = app
            await self.coordinator.broadcast(
                sender=self.name,
                topic="SCREEN_APP_CHANGED",
                payload={"active_app": app},
            )
        self.status_message = f"App activa: {self.last_app[:30]}..."
        await asyncio.sleep(5.0)


class CoderAgent(BaseAgent):
    """Agente Programador: Se encarga de refactorización, verificación de código y apoyo al self-healing."""
    def __init__(self, coordinator: "SwarmCoordinator"):
        super().__init__("Coder", "Ingeniería de Software y Parcheo en Tiempo Real", coordinator)
        self.tasks_completed = 0

    async def handle_message(self, message: SwarmMessage):
        if message.topic == "AUDIT_CODE":
            code = message.payload.get("code", "")
            # Verificación sintáctica
            import ast
            try:
                ast.parse(code)
                res = "Código válido sintácticamente."
            except Exception as e:
                res = f"Error sintáctico: {e}"

            await self.coordinator.send_direct(
                sender=self.name,
                recipient=message.sender,
                topic="AUDIT_RESULT",
                payload={"result": res},
            )
            self.tasks_completed += 1

    async def perform_work(self):
        self.status_message = f"Listo | Tareas completadas: {self.tasks_completed}"
        await asyncio.sleep(4.0)


class AppBuilderAgent(BaseAgent):
    """Agente Creador de Apps: Coordina la generación y alojamiento de aplicaciones."""
    def __init__(self, coordinator: "SwarmCoordinator"):
        super().__init__("AppBuilder", "Meta-IDE y Despliegue de Aplicaciones Locales", coordinator)

    async def handle_message(self, message: SwarmMessage):
        if message.topic == "CREATE_APP":
            name = message.payload.get("name", "App Nueva")
            desc = message.payload.get("desc", "Generada por Jarvis")
            res = app_builder.build_application(name, desc)
            await self.coordinator.send_direct(
                sender=self.name,
                recipient=message.sender,
                topic="APP_CREATED",
                payload=res,
            )

    async def perform_work(self):
        total_apps = len(app_builder.list_apps())
        self.status_message = f"Apps activas en localhost:{app_builder.active_port}: {total_apps}"
        await asyncio.sleep(5.0)


class SwarmCoordinator:
    """
    Coordinador maestro del Enjambre de Sub-Agentes.
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.is_running = False

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent

    def init_default_agents(self):
        self.register_agent(SentinelAgent(self))
        self.register_agent(VisionScreenAgent(self))
        self.register_agent(CoderAgent(self))
        self.register_agent(AppBuilderAgent(self))

    async def start_all(self):
        self.is_running = True
        for agent in self.agents.values():
            await agent.start()
        logger.info(f"Enjambre Jarvis iniciado con {len(self.agents)} agentes activos.")

    async def stop_all(self):
        self.is_running = False
        for agent in self.agents.values():
            await agent.stop()

    async def broadcast(self, sender: str, topic: str, payload: Dict[str, Any]):
        """Envía un mensaje a todos los agentes excepto al emisor."""
        msg = SwarmMessage(sender=sender, recipient="ALL", topic=topic, payload=payload)
        for name, agent in self.agents.items():
            if name != sender:
                await agent.inbox.put(msg)

    async def send_direct(self, sender: str, recipient: str, topic: str, payload: Dict[str, Any]):
        """Envía un mensaje a un agente específico."""
        if recipient in self.agents:
            msg = SwarmMessage(sender=sender, recipient=recipient, topic=topic, payload=payload)
            await self.agents[recipient].inbox.put(msg)

    def get_swarm_status(self) -> List[Dict[str, Any]]:
        """Devuelve un resumen de estado de todos los agentes para el HUD de Jarvis."""
        status = []
        for name, agent in self.agents.items():
            status.append({
                "name": name,
                "role": agent.role,
                "running": agent.is_running,
                "status": agent.status_message,
            })
        return status


# Instancia singleton predeterminada
swarm_coordinator = SwarmCoordinator()
swarm_coordinator.init_default_agents()
