// JARVIS SUPREME MASTER HUD CLIENT INTERACTION
document.addEventListener('DOMContentLoaded', () => {
    // 1. Reloj en vivo
    function updateClock() {
        const now = new Date();
        document.getElementById('liveClock').textContent = now.toLocaleTimeString('es-ES', { hour12: false });
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        document.getElementById('liveDate').textContent = now.toLocaleDateString('es-ES', options).toUpperCase();
    }
    setInterval(updateClock, 1000);
    updateClock();

    // 2. Visualizador de barras de voz
    const audioContainer = document.getElementById('audioBars');
    const barCount = 18;
    for (let i = 0; i < barCount; i++) {
        const bar = document.createElement('div');
        bar.className = 'bar';
        bar.style.animationDelay = `${(i * 0.08).toFixed(2)}s`;
        audioContainer.appendChild(bar);
    }

    // 3. Simulación y sincronización de telemetría dinámica
    setInterval(() => {
        const ram = (38 + Math.random() * 8).toFixed(1);
        const cpu = (12 + Math.random() * 15).toFixed(0);
        document.getElementById('ramVal').textContent = `${ram}%`;
        document.getElementById('ramBar').style.width = `${ram}%`;
        document.getElementById('cpuVal').textContent = `${cpu}%`;
        document.getElementById('cpuBar').style.width = `${cpu}%`;
    }, 3000);

    // 4. Interacción de comandos y diálogo
    const input = document.getElementById('hudInput');
    const sendBtn = document.getElementById('sendBtn');
    const speechBox = document.getElementById('speechBox');

    function sendCommand() {
        const val = input.value.trim();
        if (!val) return;
        
        speechBox.textContent = `Procesando su instrucción: "${val}"...`;
        input.value = '';

        setTimeout(() => {
            speechBox.textContent = `Señor Edwin, la instrucción "${val}" ha sido canalizada a través del Enrutador Omni-IA y el Enjambre de Sub-Agentes. Todos los parámetros se reportan en orden.`;
        }, 900);
    }

    sendBtn.addEventListener('click', sendCommand);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendCommand();
    });
});

function executeMacro(type) {
    const box = document.getElementById('speechBox');
    if (type === 'night') {
        box.textContent = "Señor Edwin, Modo Noche ejecutado. Pantalla atenuada, telemetría archivada y Centinela activado para el resguardo perimetral.";
    } else if (type === 'turbo') {
        box.textContent = "Modo Turbo Supreme ejecutado. Memoria RAM liberada, procesos de baja prioridad suspendidos y máxima potencia computacional enfocada.";
    } else if (type === 'sentry') {
        box.textContent = "Modo Guardia desplegado. Se ha capturado el registro fotográfico silencioso y se ha ejecutado el escaneo anti-intrusos en la red Wi-Fi.";
    } else if (type === 'builder') {
        box.textContent = "Motor Meta-Creador (Mini-Antigravity) listo. Escriba o dicte: 'crear app <nombre> con <descripción>' para compilar y alojar en vivo.";
    }
}
