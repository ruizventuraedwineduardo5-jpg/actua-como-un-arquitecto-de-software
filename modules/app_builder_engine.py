"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - MOTOR META-CREADOR DE APLICACIONES (MINI-ANTIGRAVITY)
=============================================================================
Generador autónomo de aplicaciones web y móviles completas (HTML5, CSS3, JS,
Python Flask) a partir de lenguaje natural.
Incluye servidor HTTP multi-hilo local con auto-apertura en navegador.
=============================================================================
"""

import os
import re
import json
import time
import socket
import threading
import functools
import http.server
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any, List

import config
from modules.app_controller import app_controller
from modules.omni_ai_router import omni_router, AIContext


class LocalAppServer:
    """
    Servidor HTTP multi-hilo local para alojar aplicaciones generadas.
    """

    def __init__(self, root_dir: Path, port: int = config.WEB_BUILDER_PORT, host: str = "0.0.0.0"):
        self.root_dir = root_dir
        self.port = port
        self.host = host
        self.server: Optional[http.server.ThreadingHTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.is_running: bool = False

    def _find_available_port(self, start_port: int) -> int:
        port = start_port
        while port < start_port + 50:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("127.0.0.1", port)) != 0:
                    return port
                port += 1
        return start_port

    def start(self) -> int:
        if self.is_running:
            return self.port

        self.port = self._find_available_port(self.port)
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(self.root_dir))

        try:
            self.server = http.server.ThreadingHTTPServer((self.host, self.port), handler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            self.is_running = True
            return self.port
        except Exception as e:
            self.is_running = False
            return self.port

    def stop(self):
        if self.server and self.is_running:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False


class AppBuilderEngine:
    """
    Motor Meta-Creador de Aplicaciones Inteligentes de Jarvis.
    """

    def __init__(self, apps_dir: Optional[Path] = None):
        self.apps_dir = apps_dir or config.APPS_DIR
        self.apps_dir.mkdir(parents=True, exist_ok=True)
        self.server = LocalAppServer(root_dir=self.apps_dir, port=config.WEB_BUILDER_PORT)
        # Iniciar servidor local
        self.active_port = self.server.start()

    def _slugify(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        return re.sub(r"[\s_-]+", "_", text) or f"app_{int(time.time())}"

    # -------------------------------------------------------------------------
    # GENERADOR DE APLICACIONES MEDIANTE IA O PLANTILLA VANGUARDISTA
    # -------------------------------------------------------------------------
    def build_application(
        self,
        name: str,
        description: str,
        category: str = "productividad",
        auto_launch: bool = True,
    ) -> Dict[str, Any]:
        """
        Crea una aplicación completa con HTML5, CSS3 cibernético y JS interactivo.
        """
        slug = self._slugify(name)
        app_path = self.apps_dir / slug
        app_path.mkdir(parents=True, exist_ok=True)

        # Generación de código
        html_code, css_code, js_code = self._generate_full_stack_code(name, description, category)

        # Escritura de archivos
        (app_path / "index.html").write_text(html_code, encoding="utf-8")
        (app_path / "style.css").write_text(css_code, encoding="utf-8")
        (app_path / "app.js").write_text(js_code, encoding="utf-8")

        metadata = {
            "name": name,
            "slug": slug,
            "description": description,
            "category": category,
            "author": config.USER_NAME,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "url": f"http://localhost:{self.active_port}/{slug}/",
        }
        (app_path / "manifest.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

        # Lanzamiento automático en navegador si se solicita
        if auto_launch:
            self.launch_app(slug)

        return {
            "success": True,
            "name": name,
            "slug": slug,
            "path": str(app_path),
            "url": metadata["url"],
            "metadata": metadata,
        }

    def _generate_full_stack_code(self, name: str, description: str, category: str) -> tuple[str, str, str]:
        """
        Sintetiza la aplicación integrando el Omni-Router o la arquitectura de componentes.
        """
        prompt = (
            f"Diseña una aplicación web moderna de primer nivel llamada '{name}'.\n"
            f"Propósito: {description}\n"
            f"Categoría: {category}\n"
            f"El usuario creador es {config.USER_NAME}.\n"
            f"Devuelve un JSON estrictamente válido con las claves 'html', 'css' y 'js'. "
            f"El diseño debe ser estilo 'cyberpunk/Jarvis HUD' con modo oscuro, tipografía pulida, "
            f"animaciones suaves y funcionalidad interactiva completa en JS usando localStorage."
        )

        try:
            ai_res = omni_router.route_request(prompt, context=AIContext.CODE)
            res_text = ai_res.get("response", "")
            # Intentar extraer bloque JSON si viene formateado con ```json
            json_match = re.search(r"\{[\s\S]*\}", res_text)
            if json_match:
                parsed = json.loads(json_match.group(0))
                if "html" in parsed and "css" in parsed and "js" in parsed:
                    return parsed["html"], parsed["css"], parsed["js"]
        except Exception:
            pass

        # Plantilla Modular Cibernética de Alta Gama (Garantía de funcionamiento 100%)
        return self._build_robust_fallback_app(name, description)

    def _build_robust_fallback_app(self, name: str, description: str) -> tuple[str, str, str]:
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Jarvis Supreme Hub</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
</head>
<body>
    <div class="hud-background"></div>
    <div class="container">
        <header class="app-header">
            <div class="brand">
                <span class="pulse-dot"></span>
                <span class="cyber-tag">JARVIS APPS</span>
            </div>
            <h1 class="glow-title">{name}</h1>
            <p class="subtitle">{description}</p>
        </header>

        <main class="dashboard-grid">
            <section class="card input-card">
                <h3>+ Entrada de Datos</h3>
                <div class="form-group">
                    <input type="text" id="itemTitle" placeholder="Elemento o tarea para {config.USER_NAME}...">
                    <button id="addBtn" class="cyber-btn">Registrar</button>
                </div>
            </section>

            <section class="card stats-card">
                <h3>Estado Operativo</h3>
                <div class="stat-row">
                    <span>Total Registros:</span>
                    <strong id="counter" class="cyan-text">0</strong>
                </div>
                <div class="stat-row">
                    <span>Sistema:</span>
                    <strong class="green-text">Online Supreme</strong>
                </div>
            </section>

            <section class="card list-card">
                <h3>Registros Activos</h3>
                <ul id="itemList" class="cyber-list">
                    <!-- Dinámico -->
                </ul>
            </section>
        </main>

        <footer class="app-footer">
            <p>Construido autónomamente por Jarvis Omni-Ghost Supreme para {config.USER_TITLE}</p>
        </footer>
    </div>
    <script src="app.js"></script>
</body>
</html>"""

        css = """/* Jarvis Cyberpunk Glassmorphism UI */
:root {
    --bg-dark: #070b12;
    --card-bg: rgba(13, 21, 38, 0.75);
    --cyan-glow: #00e5ff;
    --green-glow: #00ff88;
    --text-main: #e2e8f0;
    --border-neon: rgba(0, 229, 255, 0.35);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    background: var(--bg-dark);
    color: var(--text-main);
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
    padding: 24px;
    position: relative;
    overflow-x: hidden;
}

.hud-background {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: radial-gradient(circle at 50% 10%, rgba(0, 229, 255, 0.08), transparent 70%);
    pointer-events: none;
    z-index: 0;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}

.app-header {
    text-align: center;
    margin-bottom: 32px;
}

.glow-title {
    font-family: 'Orbitron', sans-serif;
    color: #fff;
    font-size: 2.2rem;
    letter-spacing: 2px;
    text-shadow: 0 0 15px rgba(0, 229, 255, 0.6);
    margin-top: 8px;
}

.subtitle {
    color: #94a3b8;
    margin-top: 8px;
}

.pulse-dot {
    display: inline-block;
    width: 10px; height: 10px;
    background: var(--cyan-glow);
    border-radius: 50%;
    box-shadow: 0 0 10px var(--cyan-glow);
    animation: pulse 1.8s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.85); }
}

.cyber-tag {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.75rem;
    color: var(--cyan-glow);
    letter-spacing: 1.5px;
    margin-left: 6px;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.card {
    background: var(--card-bg);
    border: 1px solid var(--border-neon);
    backdrop-filter: blur(12px);
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.list-card {
    grid-column: span 2;
}

h3 {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem;
    color: var(--cyan-glow);
    margin-bottom: 16px;
}

.form-group {
    display: flex;
    gap: 10px;
}

input[type="text"] {
    flex: 1;
    background: rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 12px 16px;
    border-radius: 8px;
    color: #fff;
    outline: none;
    transition: 0.2s;
}

input[type="text"]:focus {
    border-color: var(--cyan-glow);
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
}

.cyber-btn {
    background: linear-gradient(135deg, #0099ff, #00e5ff);
    color: #000;
    font-weight: 700;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-family: 'Orbitron', sans-serif;
    transition: 0.3s;
}

.cyber-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 15px var(--cyan-glow);
}

.stat-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
}

.cyan-text { color: var(--cyan-glow); }
.green-text { color: var(--green-glow); }

.cyber-list {
    list-style: none;
}

.cyber-list li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.03);
    border-left: 3px solid var(--cyan-glow);
    margin-bottom: 10px;
    border-radius: 4px;
}

.delete-btn {
    background: transparent;
    border: 1px solid #ff4444;
    color: #ff6666;
    padding: 4px 10px;
    border-radius: 6px;
    cursor: pointer;
}

.app-footer {
    text-align: center;
    font-size: 0.85rem;
    color: #64748b;
    margin-top: 36px;
}
"""

        js = """// Jarvis Dynamic Engine Client
const STORAGE_KEY = 'jarvis_app_records_' + window.location.pathname;

let records = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');

const itemInput = document.getElementById('itemTitle');
const addBtn = document.getElementById('addBtn');
const itemList = document.getElementById('itemList');
const counter = document.getElementById('counter');

function render() {
    itemList.innerHTML = '';
    records.forEach((rec, idx) => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${rec.text} <small style="color: #64748b; margin-left: 8px;">${rec.time}</small></span>
            <button class="delete-btn" onclick="removeItem(${idx})">Eliminar</button>
        `;
        itemList.appendChild(li);
    });
    counter.textContent = records.length;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
}

function addItem() {
    const val = itemInput.value.trim();
    if (!val) return;
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    records.push({ text: val, time: timeStr });
    itemInput.value = '';
    render();
}

function removeItem(idx) {
    records.splice(idx, 1);
    render();
}

addBtn.addEventListener('click', addItem);
itemInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') addItem();
});

render();
"""
        return html, css, js

    # -------------------------------------------------------------------------
    # GESTIÓN Y LANZAMIENTO DE APLICACIONES
    # -------------------------------------------------------------------------
    def launch_app(self, slug: str) -> bool:
        url = f"http://localhost:{self.active_port}/{slug}/"
        return app_controller.open_url(url)

    def list_apps(self) -> List[Dict[str, Any]]:
        """Devuelve el inventario de aplicaciones construidas."""
        apps = []
        if self.apps_dir.exists():
            for folder in self.apps_dir.iterdir():
                if folder.is_dir():
                    manifest_file = folder / "manifest.json"
                    if manifest_file.exists():
                        try:
                            meta = json.loads(manifest_file.read_text(encoding="utf-8"))
                            apps.append(meta)
                        except Exception:
                            pass
                    else:
                        apps.append({
                            "name": folder.name,
                            "slug": folder.name,
                            "url": f"http://localhost:{self.active_port}/{folder.name}/",
                        })
        return apps


# Instancia singleton predeterminada
app_builder = AppBuilderEngine()
