"""
Plugin dinámico: Radar Meteorológico Global (Open-Meteo API Libre)
"""

import json
import urllib.request
from typing import Optional, Dict, Any

from modules.self_evolution import BasePlugin
import config


class SupremePlugin(BasePlugin):
    name = "WeatherRadar Supreme"
    description = "Consulta condiciones climáticas satelitales en vivo."
    trigger_words = ["clima", "temperatura", "lluvia", "pronóstico", "tiempo hoy"]

    async def execute(self, command: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Consulta default para Bogotá (o coordenadas configurables)
        lat, lon = 4.7110, -74.0721
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        headers = {"User-Agent": "Jarvis-Weather/1.0"}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            cw = data.get("current_weather", {})
            temp = cw.get("temperature", "N/A")
            wind = cw.get("windspeed", "N/A")

            return (
                f"{config.USER_TITLE}, reporte meteorológico satelital en tiempo real:\n"
                f"• Temperatura actual: {temp} °C\n"
                f"• Velocidad del viento: {wind} km/h\n"
                f"Condiciones operativas estables en su sector."
            )
        except Exception as e:
            return f"{config.USER_TITLE}, no fue posible consultar la telemetría climática: {e}"
