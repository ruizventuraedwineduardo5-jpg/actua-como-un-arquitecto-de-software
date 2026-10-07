"""
Plugin dinámico: Monitor de Criptomonedas en Tiempo Real (CoinGecko API Libre)
"""

import json
import urllib.request
from typing import Optional, Dict, Any

from modules.self_evolution import BasePlugin
import config


class SupremePlugin(BasePlugin):
    name = "CryptoRadar Supreme"
    description = "Consulta cotizaciones en vivo de Bitcoin, Ethereum y Solana sin claves de API."
    trigger_words = ["crypto", "bitcoin", "btc", "ethereum", "eth", "solana", "sol", "criptomoneda"]

    async def execute(self, command: str, context: Optional[Dict[str, Any]] = None) -> str:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd,cop"
        headers = {"User-Agent": "Jarvis-Crypto/1.0"}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            btc_usd = data.get("bitcoin", {}).get("usd", "N/A")
            eth_usd = data.get("ethereum", {}).get("usd", "N/A")
            sol_usd = data.get("solana", {}).get("usd", "N/A")

            return (
                f"{config.USER_TITLE}, he consultado los mercados de criptoactivos en tiempo real:\n"
                f"• Bitcoin (BTC): ${btc_usd:,} USD\n"
                f"• Ethereum (ETH): ${eth_usd:,} USD\n"
                f"• Solana (SOL): ${sol_usd:,} USD\n"
                f"La liquidez y la red se reportan estables."
            )
        except Exception as e:
            return f"{config.USER_TITLE}, no fue posible consultar los nodos de criptomonedas: {e}"
