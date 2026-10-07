"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - MOTOR DE AUTO-PROGRAMACIÓN (SELF-EVOLUTION)
=============================================================================
Motor autónomo de evolución y expansión de capacidades:
- Escucha solicitudes de nuevas funciones o integraciones ("Quiero que puedas X")
- Diseña y programa nuevos plugins modulares en modules/plugins/plugin_<nombre>.py
- Valida la sintaxis con ast.parse y comprueba seguridad
- Carga e integra los plugins en caliente (hot-plugging)
=============================================================================
"""

import os
import ast
import re
import time
import inspect
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional, Type

import config
from modules.omni_ai_router import omni_router, AIContext

TupleResult = tuple[bool, str]


class BasePlugin:
    """Clase base de la que deben heredar todos los plugins auto-generados."""
    name: str = "Plugin Base"
    description: str = "Descripción del plugin"
    trigger_words: List[str] = []

    def can_handle(self, command: str) -> bool:
        cmd = command.lower()
        return any(trigger.lower() in cmd for trigger in self.trigger_words)

    async def execute(self, command: str, context: Optional[Dict[str, Any]] = None) -> str:
        raise NotImplementedError("El plugin debe implementar el método execute")


class SelfEvolutionEngine:
    """
    Motor central de síntesis, compilación y registro dinámico de nuevas habilidades.
    """

    def __init__(self, plugins_dir: Optional[Path] = None):
        self.plugins_dir = plugins_dir or config.PLUGINS_DIR
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.active_plugins: Dict[str, BasePlugin] = {}
        self.load_all_plugins()

    # -------------------------------------------------------------------------
    # CARGA DINÁMICA DE PLUGINS EXISTENTES
    # -------------------------------------------------------------------------
    def load_all_plugins(self):
        """Descubre e inicializa todos los plugins dentro del directorio."""
        for file in self.plugins_dir.glob("plugin_*.py"):
            self.load_plugin_file(file)

    def load_plugin_file(self, file_path: Path) -> Optional[BasePlugin]:
        """Carga un archivo de plugin individual e instancia su clase principal."""
        try:
            module_name = f"modules.plugins.{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                return None

            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # Buscar clases que hereden de BasePlugin
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (
                    inspect.isclass(attr)
                    and issubclass(attr, BasePlugin)
                    and attr is not BasePlugin
                ):
                    instance = attr()
                    self.active_plugins[instance.name] = instance
                    return instance
        except Exception:
            pass
        return None

    # -------------------------------------------------------------------------
    # SÍNTESIS DE NUEVO CÓDIGO MEDIANTE IA
    # -------------------------------------------------------------------------
    def synthesize_plugin_code(self, capability_description: str, plugin_name: str) -> str:
        """
        Genera el código fuente Python completo y funcional para el nuevo plugin.
        """
        prompt = f"""ERES EL MOTOR DE AUTO-EVOLUCIÓN DE JARVIS OMNI-GHOST SUPREME.
Debes programar un nuevo plugin en Python para añadir la siguiente capacidad solicitada por {config.USER_TITLE}:
DESCRIPCIÓN DE LA CAPACIDAD: {capability_description}
NOMBRE SUGERIDO: {plugin_name}

ESTRUCTURA OBLIGATORIA DEL PLUGIN:
- Debe importar 'from modules.self_evolution import BasePlugin'.
- Debe definir una clase llamada 'SupremePlugin(BasePlugin)'.
- Debe tener atributos: 'name' (str), 'description' (str), 'trigger_words' (lista de str en minúsculas).
- Debe implementar 'async def execute(self, command: str, context: Optional[dict] = None) -> str'.
- La respuesta devuelta por execute DEBE ser respetuosa, completa y con la personalidad de Jarvis.
- El código debe usar bibliotecas estándar de Python o requests/urllib.

Devuelve ÚNICAMENTE el código Python sin explicaciones ni markdown. Debe iniciar con 'import' o comentario."""

        ai_res = omni_router.route_request(prompt, context=AIContext.CODE)
        raw_code = ai_res.get("response", "")

        # Limpiar bloques markdown si existen
        if "```python" in raw_code:
            raw_code = raw_code.split("```python")[1].split("```")[0]
        elif "```" in raw_code:
            raw_code = raw_code.split("```")[1].split("```")[0]

        return raw_code.strip()

    # -------------------------------------------------------------------------
    # VALIDACIÓN DE SEGURIDAD Y SINTAXIS
    # -------------------------------------------------------------------------
    def validate_code_safety(self, code: str) -> TupleResult:
        """Comprueba que el código no contenga errores sintácticos ni operaciones destructivas."""
        # 1. Validación sintáctica con AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Error de sintaxis en el código generado: {e}"

        # 2. Análisis heurístico de seguridad
        dangerous_patterns = ["rm -rf", "shutil.rmtree('/')", "mkfs", ":(){ :|:& };:"]
        for p in dangerous_patterns:
            if p in code:
                return False, f"Patrón de seguridad prohibido detectado: {p}"

        return True, "Código validado correctamente"

    # -------------------------------------------------------------------------
    # PROCESO COMPLETO DE AUTO-EVOLUCIÓN
    # -------------------------------------------------------------------------
    async def evolve_capability(self, user_request: str) -> Dict[str, Any]:
        """
        Interpreta el deseo del usuario, genera el plugin, lo valida y lo activa en caliente.
        """
        # Extraer un identificador limpio
        slug = re.sub(r"[^\w]", "_", user_request.lower())[:25].strip("_") or f"skill_{int(time.time())}"
        file_path = self.plugins_dir / f"plugin_{slug}.py"

        # 1. Síntesis
        code = self.synthesize_plugin_code(user_request, slug)
        if not code or len(code) < 50:
            return {
                "success": False,
                "error": "No se pudo sintetizar código válido para la nueva habilidad.",
            }

        # 2. Validación
        is_safe, msg = self.validate_code_safety(code)
        if not is_safe:
            return {"success": False, "error": msg}

        # 3. Guardado en disco
        file_path.write_text(code, encoding="utf-8")

        # 4. Carga en caliente
        plugin_instance = self.load_plugin_file(file_path)
        if not plugin_instance:
            return {
                "success": False,
                "error": "El archivo se escribió pero falló la instanciación en memoria.",
            }

        return {
            "success": True,
            "plugin_name": plugin_instance.name,
            "description": plugin_instance.description,
            "triggers": plugin_instance.trigger_words,
            "file": str(file_path),
            "message": f"{config.USER_TITLE}, he asimilado con éxito la nueva capacidad '{plugin_instance.name}'. Ya se encuentra activa en el núcleo operativo.",
        }

    # -------------------------------------------------------------------------
    # ENRUTAMIENTO DE COMANDOS A PLUGINS
    # -------------------------------------------------------------------------
    async def try_execute_plugin(self, command: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Verifica si algún plugin activo puede responder a la instrucción."""
        for plugin in self.active_plugins.values():
            if plugin.can_handle(command):
                try:
                    return await plugin.execute(command, context)
                except Exception as e:
                    return f"Error al ejecutar el plugin '{plugin.name}': {e}"
        return None


# Helper tipo
TupleResult = tuple[bool, str]

# Instancia singleton predeterminada
evolution_engine = SelfEvolutionEngine()
