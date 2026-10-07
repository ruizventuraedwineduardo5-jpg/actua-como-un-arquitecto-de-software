#!/data/data/com.termux/files/usr/bin/bash
# =============================================================================
# JARVIS OMNI-GHOST SUPREME - INSTALADOR MAESTRO PARA ANDROID (TERMUX)
# =============================================================================
# Arquitectura: Instalación autónoma de entorno Python 3, FFmpeg, compiladores C++,
# dependencias de imágenes, herramientas ADB y configuración de Termux:API.
# =============================================================================

set -e

CYAN='\033[1;36m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═════════════════════════════════════════════════════════════════════════╗"
echo "║          JARVIS OMNI-GHOST SUPREME - INSTALADOR TERMUX V2.5.0           ║"
echo "║                      EDICIÓN ESPECIAL PARA EDWIN                        ║"
echo "╚═════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}[1/6] Configurando permisos de almacenamiento en Android...${NC}"
if command -v termux-setup-storage >/dev/null 2>&1; then
    termux-setup-storage
    sleep 2
else
    echo "Aviso: termux-setup-storage no detectado en este sistema (probablemente no es Android nativo)."
fi

echo -e "${YELLOW}[2/6] Actualizando repositorios oficiales de paquetes (pkg)...${NC}"
pkg update -y || apt-get update -y
pkg upgrade -y || apt-get upgrade -y

echo -e "${YELLOW}[3/6] Instalando dependencias de bajo nivel, multimedia y C++...${NC}"
pkg install -y \
    python \
    python-pip \
    ffmpeg \
    termux-api \
    git \
    clang \
    libjpeg-turbo \
    libpng \
    openssl \
    libffi \
    android-tools \
    binutils \
    rust \
    make \
    curl \
    jq || true

echo -e "${YELLOW}[4/6] Actualizando gestor de paquetes Python (pip)...${NC}"
python3 -m pip install --upgrade pip setuptools wheel --break-system-packages || true

echo -e "${YELLOW}[5/6] Instalando librerías científicas y de Inteligencia Artificial...${NC}"
# Instalación de librerías esenciales
python3 -m pip install --break-system-packages \
    requests \
    pillow \
    openpyxl \
    flask \
    aiohttp \
    edge-tts \
    psutil \
    google-genai || true

# Intento de librerías opcionales
python3 -m pip install --break-system-packages \
    mss \
    scapy \
    SpeechRecognition || true

echo -e "${YELLOW}[6/6] Ajustando permisos de ejecución y creando acceso directo...${NC}"
chmod +x main.py
cat << 'EOF' > run_jarvis.sh
#!/data/data/com.termux/files/usr/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
python3 main.py
EOF
chmod +x run_jarvis.sh

echo -e "${GREEN}"
echo "========================================================================="
echo " ¡INSTALACIÓN COMPLETADA CON ÉXITO!                                      "
echo "========================================================================="
echo -e "${NC}"
echo -e "Para iniciar el asistente en cualquier momento ejecute:"
echo -e "  ${CYAN}./run_jarvis.sh${NC}  o  ${CYAN}python3 main.py${NC}"
echo ""
echo -e "${YELLOW}RECOMENDACIONES PARA ANDROID:${NC}"
echo "1. Asegúrate de tener instalada la aplicación complementaria 'Termux:API' de F-Droid."
echo "2. Concede los permisos de micrófono, cámara y ubicación a Termux:API en los ajustes de tu teléfono."
echo "3. Las aplicaciones web creadas por Jarvis se alojarán en http://localhost:8080/"
echo ""
echo -e "${GREEN}Jarvis Omni-Ghost Supreme está listo para servirle, Señor Edwin.${NC}"
