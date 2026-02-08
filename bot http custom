#!/bin/bash
# ================================================
# HTTP CUSTOM BOT - WPPCONNECT + MERCADOPAGO + HWID
# SISTEMA DE AUTENTICACIÓN POR HWID + ARCHIVOS .HC
# ================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

clear
echo -e "${CYAN}${BOLD}"
cat << "BANNER"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  ██╗  ██╗████████╗████████╗██████╗      ██████╗██╗   ██╗    ║
║  ██║  ██║╚══██╔══╝╚══██╔══╝██╔══██╗    ██╔════╝██║   ██║    ║
║  ███████║   ██║      ██║   ██████╔╝    ██║     ██║   ██║    ║
║  ██╔══██║   ██║      ██║   ██╔═══╝     ██║     ██║   ██║    ║
║  ██║  ██║   ██║      ██║   ██║         ╚██████╗╚██████╔╝    ║
║  ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝          ╚═════╝ ╚═════╝     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║          🤖 HTTP CUSTOM BOT - SISTEMA HWID + .HC            ║
║               📱 WhatsApp API + HWID VALIDACIÓN            ║
║               💰 MercadoPago SDK v2.x INTEGRADO            ║
║               📁 Entrega de archivos .hc por HWID          ║
║               🎛️  Panel completo con gestión de .hc       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

echo -e "${GREEN}✅ CARACTERÍSTICAS PRINCIPALES:${NC}"
echo -e "  📱 ${CYAN}WPPConnect${NC} - API WhatsApp funcional"
echo -e "  💰 ${GREEN}MercadoPago SDK v2.x${NC} - Integración completa"
echo -e "  🔐 ${YELLOW}Sistema HWID${NC} - Autenticación por dispositivo"
echo -e "  📁 ${PURPLE}Archivos .hc${NC} - Generación automática por HWID"
echo -e "  🌐 ${BLUE}Servidor web${NC} - Entrega de archivos .hc"
echo -e "  📊 ${GREEN}Estadísticas${NC} - Usuarios, HWIDs, archivos .hc"
echo -e "  ⚡ ${CYAN}Auto-verificación${NC} - Pagos cada 2 minutos"
echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}\n"

# Verificar root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}❌ Debes ejecutar como root${NC}"
    echo -e "${YELLOW}Usa: sudo bash $0${NC}"
    exit 1
fi

# Detectar IP
echo -e "${CYAN}🔍 Detectando IP...${NC}"
SERVER_IP=$(curl -4 -s --max-time 10 ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}' || echo "127.0.0.1")
if [[ -z "$SERVER_IP" || "$SERVER_IP" == "127.0.0.1" ]]; then
    read -p "📝 Ingresa la IP o dominio del servidor: " SERVER_IP
fi

# Puerto para servidor web de archivos .hc
read -p "📝 Puerto para servidor web [8080]: " WEB_PORT
WEB_PORT=${WEB_PORT:-8080}

echo -e "${GREEN}✅ IP: ${CYAN}$SERVER_IP${NC}"
echo -e "${GREEN}✅ Puerto web: ${CYAN}$WEB_PORT${NC}\n"

read -p "$(echo -e "${YELLOW}¿Continuar instalación? (s/N): ${NC}")" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${RED}❌ Cancelado${NC}"
    exit 0
fi

# ================================================
# INSTALAR DEPENDENCIAS
# ================================================
echo -e "\n${CYAN}📦 Instalando dependencias...${NC}"

apt-get update -y
apt-get upgrade -y

# Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs gcc g++ make

# Chrome/Chromium
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update -y
apt-get install -y google-chrome-stable

# Dependencias del sistema
apt-get install -y \
    git curl wget sqlite3 jq nginx \
    build-essential libcairo2-dev \
    libpango1.0-dev libjpeg-dev \
    libgif-dev librsvg2-dev \
    python3 python3-pip ffmpeg \
    unzip cron ufw

# Configurar firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow $WEB_PORT/tcp
ufw allow 3000/tcp
ufw --force enable

# PM2
npm install -g pm2
pm2 update

echo -e "${GREEN}✅ Dependencias instaladas${NC}"

# ================================================
# PREPARAR ESTRUCTURA
# ================================================
echo -e "\n${CYAN}📁 Creando estructura...${NC}"

INSTALL_DIR="/opt/httpcustom-bot"
USER_HOME="/root/httpcustom-bot"
DB_FILE="$INSTALL_DIR/data/users.db"
CONFIG_FILE="$INSTALL_DIR/config/config.json"
HC_FILES_DIR="$INSTALL_DIR/hc_files"

# Limpiar anterior
pm2 delete httpcustom-bot 2>/dev/null || true
rm -rf "$INSTALL_DIR" "$USER_HOME" 2>/dev/null || true
rm -rf /root/.wppconnect 2>/dev/null || true

# Crear directorios
mkdir -p "$INSTALL_DIR"/{data,config,sessions,logs,qr_codes,hwid,hc_files,templates}
mkdir -p "$USER_HOME"
mkdir -p /root/.wppconnect
mkdir -p "$HC_FILES_DIR"
chmod -R 755 "$INSTALL_DIR"
chmod -R 700 /root/.wppconnect

# Plantilla base para archivo .hc
cat > "$INSTALL_DIR/templates/base.hc" << 'HCTEMPLATE'
[General]
loglevel = trace
dns-server = 8.8.8.8, 8.8.4.4
tun-fd = 233
route = 0.0.0.0/0
http-proxy = __SERVER_IP__ __PORT__
http-proxy-auth = __USERNAME__:__PASSWORD__

[Proxy]
Direct = direct
Reject = reject

[Rule]
DOMAIN-KEYWORD,google,Proxy
DOMAIN-KEYWORD,youtube,Proxy
DOMAIN-KEYWORD,netflix,Proxy
DOMAIN-KEYWORD,facebook,Proxy
DOMAIN-KEYWORD,instagram,Proxy
DOMAIN-KEYWORD,twitter,Proxy
DOMAIN-KEYWORD,whatsapp,Proxy
DOMAIN-KEYWORD,tiktok,Proxy
DOMAIN-SUFFIX,ar,Direct
DOMAIN-SUFFIX,com,Proxy
IP-CIDR,192.168.0.0/16,Direct
IP-CIDR,10.0.0.0/8,Direct
IP-CIDR,172.16.0.0/12,Direct
GEOIP,AR,Direct
FINAL,Proxy
HCTEMPLATE

# Configuración principal
cat > "$CONFIG_FILE" << EOF
{
    "bot": {
        "name": "HTTP Custom Bot HWID",
        "version": "2.0-HWID-HC",
        "server_ip": "$SERVER_IP",
        "web_port": $WEB_PORT,
        "proxy_port_start": 10000,
        "proxy_port_end": 20000,
        "default_password": "mgvpn247"
    },
    "prices": {
        "test_hours": 1,
        "price_7d": 3000.00,
        "price_15d": 5000.00,
        "price_30d": 8000.00,
        "price_50d": 12000.00,
        "currency": "ARS"
    },
    "mercadopago": {
        "access_token": "",
        "enabled": false,
        "public_key": ""
    },
    "links": {
        "app_download": "https://play.google.com/store/apps/details?id=xyz.easypro.httpcustom",
        "support": "https://wa.me/543435071016",
        "hc_instructions": "https://example.com/como-usar-hc",
        "web_panel": "http://$SERVER_IP:$WEB_PORT"
    },
    "paths": {
        "database": "$DB_FILE",
        "qr_codes": "$INSTALL_DIR/qr_codes",
        "sessions": "/root/.wppconnect",
        "hwid_dir": "$INSTALL_DIR/hwid",
        "hc_files": "$HC_FILES_DIR",
        "templates": "$INSTALL_DIR/templates"
    },
    "hc_config": {
        "proxy_port": 8080,
        "timeout": 30,
        "enable_udp": true,
        "enable_ipv6": false,
        "dns_cache": 600
    }
}
EOF

# Crear base de datos COMPLETA con HWID y HC
sqlite3 "$DB_FILE" << 'SQL'
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    username TEXT UNIQUE,
    password TEXT DEFAULT 'mgvpn247',
    tipo TEXT DEFAULT 'test',
    expires_at DATETIME,
    status INTEGER DEFAULT 1,
    hwid TEXT DEFAULT NULL,
    device_name TEXT DEFAULT NULL,
    hc_file TEXT DEFAULT NULL,
    proxy_port INTEGER DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE daily_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(phone, date)
);
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id TEXT UNIQUE,
    phone TEXT,
    plan TEXT,
    days INTEGER,
    amount REAL,
    status TEXT DEFAULT 'pending',
    payment_url TEXT,
    qr_code TEXT,
    preference_id TEXT,
    hwid TEXT DEFAULT NULL,
    device_name TEXT DEFAULT NULL,
    hc_file TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME
);
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    message TEXT,
    data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE user_state (
    phone TEXT PRIMARY KEY,
    state TEXT DEFAULT 'main_menu',
    data TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE hwid_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    hwid TEXT UNIQUE,
    device_name TEXT,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME
);
CREATE TABLE hc_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    hwid TEXT,
    device_name TEXT,
    file_path TEXT UNIQUE,
    download_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_download DATETIME
);
CREATE INDEX idx_users_hwid ON users(hwid);
CREATE INDEX idx_users_hc_file ON users(hc_file);
CREATE INDEX idx_payments_hwid ON payments(hwid);
CREATE INDEX idx_hwid_reg_phone ON hwid_registrations(phone);
CREATE INDEX idx_hwid_reg_status ON hwid_registrations(status);
CREATE INDEX idx_hc_files_hwid ON hc_files(hwid);
CREATE INDEX idx_hc_files_username ON hc_files(username);
SQL

echo -e "${GREEN}✅ Estructura creada con sistema HWID + .hc${NC}"

# ================================================
# CREAR SERVIDOR WEB PARA ARCHIVOS .HC
# ================================================
echo -e "\n${CYAN}🌐 Creando servidor web para archivos .hc...${NC}"

cat > "$INSTALL_DIR/hc-server.js" << 'HCSERVEREOF'
const http = require('http');
const fs = require('fs');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const url = require('url');

const config = require('/opt/httpcustom-bot/config/config.json');
const db = new sqlite3.Database(config.paths.database);
const HC_FILES_DIR = config.paths.hc_files;
const PORT = config.bot.web_port;

const server = http.createServer(async (req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    
    console.log(`📥 [HC Server] ${req.method} ${pathname}`);
    
    // Ruta principal
    if (pathname === '/' || pathname === '/index.html') {
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end(`
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>HTTP Custom - Descarga archivos .hc</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                    .container { max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
                    h1 { text-align: center; margin-bottom: 30px; }
                    .form-group { margin-bottom: 20px; }
                    label { display: block; margin-bottom: 8px; font-weight: bold; }
                    input, select { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 16px; }
                    button { background: #4CAF50; color: white; border: none; padding: 15px 30px; border-radius: 8px; cursor: pointer; font-size: 18px; width: 100%; }
                    button:hover { background: #45a049; }
                    .result { margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 8px; display: none; }
                    .qr-container { text-align: center; margin: 20px 0; }
                    .steps { margin: 30px 0; }
                    .step { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; margin-bottom: 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📁 DESCARGAR ARCHIVO HTTP CUSTOM (.hc)</h1>
                    
                    <div class="steps">
                        <div class="step"><strong>Paso 1:</strong> Registra tu HWID en el bot de WhatsApp</div>
                        <div class="step"><strong>Paso 2:</strong> Introduce tu HWID aquí</div>
                        <div class="step"><strong>Paso 3:</strong> Descarga tu archivo .hc personalizado</div>
                    </div>
                    
                    <div class="form-group">
                        <label for="hwid">🔐 Introduce tu HWID:</label>
                        <input type="text" id="hwid" placeholder="Ej: ABC123-DEF456-GHI789" required>
                    </div>
                    
                    <button onclick="downloadHC()">📥 DESCARGAR ARCHIVO .HC</button>
                    
                    <div id="result" class="result"></div>
                    
                    <div class="qr-container" id="qrContainer" style="display:none;">
                        <h3>📱 Escanea para importar directamente</h3>
                        <div id="qrcode"></div>
                    </div>
                    
                    <div style="margin-top: 30px; font-size: 14px; opacity: 0.8;">
                        <p><strong>📋 Instrucciones de uso:</strong></p>
                        <ol>
                            <li>Descarga HTTP Custom desde Play Store</li>
                            <li>Abre la app y ve a "Importar configuración"</li>
                            <li>Selecciona "Desde archivo" y elige el .hc descargado</li>
                            <li>¡Conéctate y disfruta!</li>
                        </ol>
                    </div>
                </div>
                
                <script src="https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js"></script>
                <script>
                    async function downloadHC() {
                        const hwid = document.getElementById('hwid').value.trim();
                        if (!hwid) {
                            showResult('❌ Ingresa tu HWID', 'error');
                            return;
                        }
                        
                        showResult('🔍 Buscando archivo .hc...', 'info');
                        
                        try {
                            const response = await fetch(\`/download/\${encodeURIComponent(hwid)}\`);
                            const data = await response.json();
                            
                            if (data.success) {
                                showResult(\`✅ Archivo encontrado: \${data.filename}\`, 'success');
                                
                                // Crear enlace de descarga
                                const link = document.createElement('a');
                                link.href = data.download_url;
                                link.download = data.filename;
                                link.textContent = '📥 HAZ CLIC AQUÍ PARA DESCARGAR';
                                link.style.display = 'block';
                                link.style.margin = '15px 0';
                                link.style.padding = '10px';
                                link.style.background = '#4CAF50';
                                link.style.color = 'white';
                                link.style.textDecoration = 'none';
                                link.style.borderRadius = '5px';
                                link.style.textAlign = 'center';
                                
                                const resultDiv = document.getElementById('result');
                                resultDiv.appendChild(link);
                                
                                // Generar QR
                                document.getElementById('qrContainer').style.display = 'block';
                                QRCode.toCanvas(document.getElementById('qrcode'), data.download_url, {
                                    width: 200,
                                    margin: 2
                                });
                                
                                // Actualizar estadísticas de descarga
                                fetch(\`/stats/\${encodeURIComponent(hwid)}\`, { method: 'POST' });
                                
                            } else {
                                showResult(\`❌ \${data.error}\`, 'error');
                            }
                        } catch (error) {
                            showResult('❌ Error al conectar con el servidor', 'error');
                            console.error(error);
                        }
                    }
                    
                    function showResult(message, type) {
                        const resultDiv = document.getElementById('result');
                        resultDiv.innerHTML = message;
                        resultDiv.style.display = 'block';
                        resultDiv.style.background = type === 'error' ? 'rgba(255,0,0,0.3)' : 
                                                    type === 'success' ? 'rgba(0,255,0,0.3)' : 
                                                    'rgba(255,255,0,0.3)';
                    }
                </script>
            </body>
            </html>
        `);
        return;
    }
    
    // Descargar archivo .hc por HWID
    if (pathname.startsWith('/download/')) {
        const hwid = decodeURIComponent(pathname.split('/')[2]);
        
        db.get('SELECT hc_file, username FROM users WHERE hwid = ? AND status = 1', [hwid], (err, row) => {
            if (err || !row || !row.hc_file) {
                res.writeHead(404, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ 
                    success: false, 
                    error: 'No se encontró archivo .hc para este HWID o la cuenta está expirada' 
                }));
                return;
            }
            
            const filePath = row.hc_file;
            const filename = `httpcustom-${row.username}.hc`;
            
            if (fs.existsSync(filePath)) {
                // Registrar descarga
                db.run('UPDATE hc_files SET last_download = CURRENT_TIMESTAMP WHERE hwid = ?', [hwid]);
                
                // Servir archivo
                res.writeHead(200, {
                    'Content-Type': 'application/octet-stream',
                    'Content-Disposition': `attachment; filename="${filename}"`,
                    'Cache-Control': 'no-cache'
                });
                
                fs.createReadStream(filePath).pipe(res);
            } else {
                res.writeHead(404, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false, error: 'Archivo no encontrado en el servidor' }));
            }
        });
        return;
    }
    
    // API para obtener info del archivo
    if (pathname.startsWith('/api/hc/')) {
        const hwid = decodeURIComponent(pathname.split('/')[3]);
        
        db.get('SELECT u.username, u.device_name, h.file_path, h.download_url FROM users u LEFT JOIN hc_files h ON u.hwid = h.hwid WHERE u.hwid = ? AND u.status = 1', [hwid], (err, row) => {
            if (err || !row) {
                res.writeHead(404, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false, error: 'HWID no encontrado' }));
                return;
            }
            
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                success: true,
                username: row.username,
                device_name: row.device_name,
                has_file: !!row.file_path,
                download_url: row.download_url || `http://${config.bot.server_ip}:${config.bot.web_port}/download/${hwid}`
            }));
        });
        return;
    }
    
    // Estadísticas de descarga
    if (pathname.startsWith('/stats/') && req.method === 'POST') {
        const hwid = decodeURIComponent(pathname.split('/')[2]);
        db.run('UPDATE hc_files SET last_download = CURRENT_TIMESTAMP WHERE hwid = ?', [hwid]);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true }));
        return;
    }
    
    // 404 - No encontrado
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('404 - No encontrado');
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ Servidor web HC iniciado en puerto ${PORT}`);
    console.log(`🌐 URL: http://${config.bot.server_ip}:${PORT}`);
});

// Manejar cierre
process.on('SIGINT', () => {
    console.log('🛑 Cerrando servidor web HC...');
    server.close();
    process.exit();
});
HCSERVEREOF

echo -e "${GREEN}✅ Servidor web para .hc creado${NC}"

# ================================================
# CREAR BOT COMPLETO CON HWID Y .HC
# ================================================
echo -e "\n${CYAN}🤖 Creando bot con WPPConnect + MercadoPago + HWID + .HC...${NC}"

cd "$USER_HOME"

# package.json
cat > package.json << 'PKGEOF'
{
    "name": "httpcustom-bot",
    "version": "2.0.0",
    "main": "bot.js",
    "dependencies": {
        "@wppconnect-team/wppconnect": "^1.24.0",
        "qrcode-terminal": "^0.12.0",
        "qrcode": "^1.5.3",
        "moment": "^2.30.1",
        "sqlite3": "^5.1.7",
        "chalk": "^4.1.2",
        "node-cron": "^3.0.3",
        "mercadopago": "^2.0.15",
        "axios": "^1.6.5",
        "sharp": "^0.33.2",
        "crypto": "^1.0.1"
    }
}
PKGEOF

echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
npm install --silent 2>&1 | grep -v "npm WARN" || true

# Crear bot.js COMPLETO
echo -e "${YELLOW}📝 Creando bot.js con sistema HWID y .hc...${NC}"

cat > "bot.js" << 'BOTEOF'
const wppconnect = require('@wppconnect-team/wppconnect');
const qrcode = require('qrcode-terminal');
const QRCode = require('qrcode');
const moment = require('moment');
const sqlite3 = require('sqlite3').verbose();
const { exec } = require('child_process');
const util = require('util');
const chalk = require('chalk');
const cron = require('node-cron');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const crypto = require('crypto');

const execPromise = util.promisify(exec);
moment.locale('es');

console.log(chalk.cyan.bold('\n╔══════════════════════════════════════════════════════════════╗'));
console.log(chalk.cyan.bold('║              🤖 HTTP CUSTOM BOT - HWID + .HC                ║'));
console.log(chalk.cyan.bold('╚══════════════════════════════════════════════════════════════╝\n'));

// Cargar configuración
function loadConfig() {
    delete require.cache[require.resolve('/opt/httpcustom-bot/config/config.json')];
    return require('/opt/httpcustom-bot/config/config.json');
}

let config = loadConfig();
const db = new sqlite3.Database('/opt/httpcustom-bot/data/users.db');

// ✅ FUNCIÓN PARA GENERAR ARCHIVO .HC
async function generateHCFile(username, password, hwid, deviceName) {
    try {
        const templatePath = config.paths.templates + '/base.hc';
        let template = fs.readFileSync(templatePath, 'utf8');
        
        // Generar puerto único
        const proxyPort = config.bot.proxy_port_start + Math.floor(Math.random() * 
                     (config.bot.proxy_port_end - config.bot.proxy_port_start));
        
        // Reemplazar variables
        template = template
            .replace(/__SERVER_IP__/g, config.bot.server_ip)
            .replace(/__PORT__/g, proxyPort)
            .replace(/__USERNAME__/g, username)
            .replace(/__PASSWORD__/g, password);
        
        // Crear nombre de archivo único
        const filename = `httpcustom_${username}_${Date.now()}.hc`;
        const filePath = path.join(config.paths.hc_files, filename);
        
        // Guardar archivo
        fs.writeFileSync(filePath, template);
        
        // Generar URL de descarga
        const downloadUrl = `http://${config.bot.server_ip}:${config.bot.web_port}/download/${hwid}`;
        
        // Guardar en base de datos
        db.run(
            `INSERT INTO hc_files (username, hwid, device_name, file_path, download_url) VALUES (?, ?, ?, ?, ?)`,
            [username, hwid, deviceName, filePath, downloadUrl]
        );
        
        console.log(chalk.green(`✅ Archivo .hc generado: ${filename}`));
        console.log(chalk.cyan(`📁 Ruta: ${filePath}`));
        console.log(chalk.cyan(`🌐 URL: ${downloadUrl}`));
        
        return {
            success: true,
            filePath,
            downloadUrl,
            filename,
            proxyPort
        };
        
    } catch (error) {
        console.error(chalk.red('❌ Error generando .hc:'), error.message);
        return { success: false, error: error.message };
    }
}

// ✅ MERCADOPAGO SDK V2.X
let mpEnabled = false;
let mpClient = null;
let mpPreference = null;

function initMercadoPago() {
    config = loadConfig();
    if (config.mercadopago.access_token && config.mercadopago.access_token !== '') {
        try {
            const { MercadoPagoConfig, Preference } = require('mercadopago');
            
            mpClient = new MercadoPagoConfig({ 
                accessToken: config.mercadopago.access_token,
                options: { timeout: 5000, idempotencyKey: true }
            });
            
            mpPreference = new Preference(mpClient);
            mpEnabled = true;
            
            console.log(chalk.green('✅ MercadoPago SDK v2.x ACTIVO'));
            console.log(chalk.cyan(`🔑 Token: ${config.mercadopago.access_token.substring(0, 20)}...`));
            return true;
        } catch (error) {
            console.log(chalk.red('❌ Error inicializando MP:'), error.message);
            mpEnabled = false;
            mpClient = null;
            mpPreference = null;
            return false;
        }
    }
    console.log(chalk.yellow('⚠️ MercadoPago NO configurado'));
    return false;
}

initMercadoPago();

// Variables globales
let client = null;

// ✅ FUNCIONES HWID
function normalizeHWID(hwid) {
    return hwid.trim().toUpperCase().replace(/[^A-Z0-9\-]/g, '');
}

function validateHWID(hwid) {
    const normalized = normalizeHWID(hwid);
    return normalized.length >= 10 && normalized.length <= 64;
}

function hashHWID(hwid) {
    return crypto.createHash('sha256').update(hwid).digest('hex');
}

async function checkHWIDAvailable(hwid) {
    return new Promise((resolve) => {
        const hashed = hashHWID(hwid);
        db.get('SELECT COUNT(*) as count FROM users WHERE hwid = ?', [hashed], (err, row) => {
            if (err) {
                console.error(chalk.red('❌ Error BD HWID:'), err.message);
                resolve(false);
            } else {
                resolve(row.count === 0);
            }
        });
    });
}

async function registerHWID(phone, hwid, deviceName) {
    return new Promise((resolve) => {
        const normalized = normalizeHWID(hwid);
        const hashed = hashHWID(normalized);
        
        db.run(
            `INSERT OR REPLACE INTO hwid_registrations (phone, hwid, device_name, status) VALUES (?, ?, ?, 'pending')`,
            [phone, hashed, deviceName],
            function(err) {
                if (err) {
                    console.error(chalk.red('❌ Error registrando HWID:'), err.message);
                    resolve({ success: false, error: err.message });
                } else {
                    console.log(chalk.green(`✅ HWID registrado para ${phone}: ${deviceName}`));
                    resolve({ success: true, hwid: normalized, hashed: hashed });
                }
            }
        );
    });
}

// ✅ SISTEMA DE ESTADOS
function getUserState(phone) {
    return new Promise((resolve) => {
        db.get('SELECT state, data FROM user_state WHERE phone = ?', [phone], (err, row) => {
            if (err || !row) {
                resolve({ state: 'main_menu', data: null });
            } else {
                resolve({
                    state: row.state || 'main_menu',
                    data: row.data ? JSON.parse(row.data) : null
                });
            }
        });
    });
}

function setUserState(phone, state, data = null) {
    return new Promise((resolve) => {
        const dataStr = data ? JSON.stringify(data) : null;
        db.run(
            `INSERT OR REPLACE INTO user_state (phone, state, data, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)`,
            [phone, state, dataStr],
            (err) => {
                if (err) console.error(chalk.red('❌ Error estado:'), err.message);
                resolve();
            }
        );
    });
}

function clearUserState(phone) {
    db.run('DELETE FROM user_state WHERE phone = ?', [phone]);
}

// Funciones auxiliares
function generateUsername() {
    const chars = 'abcdefghijklmnopqrstuvwxyz';
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    const randomChar = chars.charAt(Math.floor(Math.random() * chars.length));
    return `test${randomChar}${randomNum}`;
}

function generatePremiumUsername() {
    const chars = 'abcdefghijklmnopqrstuvwxyz';
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    const randomChar = chars.charAt(Math.floor(Math.random() * chars.length));
    return `user${randomChar}${randomNum}`;
}

const DEFAULT_PASSWORD = 'mgvpn247';

async function createUser(phone, username, days, hwid = null, deviceName = null) {
    const password = DEFAULT_PASSWORD;
    const expireFull = moment().add(days, 'days').format('YYYY-MM-DD 23:59:59');
    
    try {
        // Generar archivo .hc
        const hcResult = await generateHCFile(username, password, hwid, deviceName);
        
        if (!hcResult.success) {
            return { success: false, error: 'Error generando archivo .hc' };
        }
        
        const hashedHwid = hwid ? hashHWID(hwid) : null;
        
        // Guardar en base de datos
        db.run(`INSERT INTO users (phone, username, password, tipo, expires_at, hwid, device_name, hc_file, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)`,
            [phone, username, password, days === 0 ? 'test' : 'premium', expireFull, hashedHwid, deviceName, hcResult.filePath]);
        
        // Aprobar HWID
        db.run(`UPDATE hwid_registrations SET status = 'approved' WHERE hwid = ?`, [hashedHwid]);
        
        return { 
            success: true, 
            username, 
            password, 
            expires: expireFull, 
            hwid: hashedHwid,
            hcFile: hcResult.filePath,
            downloadUrl: hcResult.downloadUrl,
            proxyPort: hcResult.proxyPort
        };
        
    } catch (error) {
        console.error(chalk.red('❌ Error:'), error.message);
        return { success: false, error: error.message };
    }
}

function canCreateTest(phone) {
    return new Promise((resolve) => {
        const today = moment().format('YYYY-MM-DD');
        db.get('SELECT COUNT(*) as count FROM daily_tests WHERE phone = ? AND date = ?', [phone, today],
            (err, row) => resolve(!err && row && row.count === 0));
    });
}

function registerTest(phone) {
    db.run('INSERT OR IGNORE INTO daily_tests (phone, date) VALUES (?, ?)', [phone, moment().format('YYYY-MM-DD')]);
}

// ✅ MERCADOPAGO - CREAR PAGO CON HWID Y .HC
async function createMercadoPagoPayment(phone, days, amount, planName, hwid = null, deviceName = null) {
    try {
        if (!mpEnabled || !mpPreference) {
            console.log(chalk.red('❌ MercadoPago no inicializado'));
            return { success: false, error: 'MercadoPago no configurado' };
        }
        
        const phoneClean = phone.replace('@c.us', '');
        const paymentId = `HTTPC-${phoneClean}-${days}d-${Date.now()}`;
        
        console.log(chalk.cyan(`🔄 Creando pago MP con HWID y .hc: ${paymentId}`));
        
        const expirationDate = moment().add(24, 'hours');
        const isoDate = expirationDate.toISOString();
        
        const preferenceData = {
            items: [{
                title: `HTTP CUSTOM ${days} DÍAS - HWID`,
                description: `Acceso HTTP Custom Premium por ${days} días - Archivo .hc incluido`,
                quantity: 1,
                currency_id: config.prices.currency || 'ARS',
                unit_price: parseFloat(amount)
            }],
            external_reference: paymentId,
            expires: true,
            expiration_date_from: moment().toISOString(),
            expiration_date_to: isoDate,
            back_urls: {
                success: `http://${config.bot.server_ip}:${config.bot.web_port}/success/${paymentId}`,
                failure: `http://${config.bot.server_ip}:${config.bot.web_port}/failure`,
                pending: `http://${config.bot.server_ip}:${config.bot.web_port}/pending`
            },
            auto_return: 'approved',
            statement_descriptor: 'HTTP CUSTOM PREMIUM'
        };
        
        console.log(chalk.yellow(`📦 Producto: ${preferenceData.items[0].title}`));
        console.log(chalk.yellow(`💰 Monto: $${amount} ${config.prices.currency || 'ARS'}`));
        if (hwid) {
            console.log(chalk.yellow(`🔐 HWID: ${hwid.substring(0, 20)}...`));
        }
        
        const response = await mpPreference.create({ body: preferenceData });
        
        if (response && response.id) {
            const paymentUrl = response.init_point;
            const qrPath = `${config.paths.qr_codes}/${paymentId}.png`;
            
            await QRCode.toFile(qrPath, paymentUrl, { 
                width: 400,
                margin: 2,
                color: {
                    dark: '#000000',
                    light: '#FFFFFF'
                }
            });
            
            const hashedHwid = hwid ? hashHWID(hwid) : null;
            db.run(
                `INSERT INTO payments (payment_id, phone, plan, days, amount, status, payment_url, qr_code, preference_id, hwid, device_name) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?)`,
                [paymentId, phone, `${days}d`, days, amount, paymentUrl, qrPath, response.id, hashedHwid, deviceName],
                (err) => {
                    if (err) console.error(chalk.red('❌ Error BD:'), err.message);
                }
            );
            
            console.log(chalk.green(`✅ Pago creado: ${paymentId}`));
            
            return { 
                success: true, 
                paymentId, 
                paymentUrl, 
                qrPath,
                preferenceId: response.id,
                amount: parseFloat(amount),
                hwid: hashedHwid
            };
        }
        
        throw new Error('Respuesta inválida de MercadoPago');
        
    } catch (error) {
        console.error(chalk.red('❌ Error MercadoPago:'), error.message);
        
        db.run(
            `INSERT INTO logs (type, message, data) VALUES ('mp_error', ?, ?)`,
            [error.message, JSON.stringify({ stack: error.stack })]
        );
        
        return { success: false, error: error.message };
    }
}

// ✅ VERIFICAR PAGOS PENDIENTES Y CREAR .HC
async function checkPendingPayments() {
    if (!mpEnabled) return;
    
    db.all('SELECT * FROM payments WHERE status = "pending" AND created_at > datetime("now", "-48 hours")', async (err, payments) => {
        if (err || !payments || payments.length === 0) return;
        
        console.log(chalk.yellow(`🔍 Verificando ${payments.length} pagos...`));
        
        for (const payment of payments) {
            try {
                const url = `https://api.mercadopago.com/v1/payments/search?external_reference=${payment.payment_id}`;
                const response = await axios.get(url, {
                    headers: { 
                        'Authorization': `Bearer ${config.mercadopago.access_token}`,
                        'Content-Type': 'application/json'
                    },
                    timeout: 15000
                });
                
                if (response.data && response.data.results && response.data.results.length > 0) {
                    const mpPayment = response.data.results[0];
                    
                    console.log(chalk.cyan(`📋 Pago ${payment.payment_id}: ${mpPayment.status}`));
                    
                    if (mpPayment.status === 'approved') {
                        console.log(chalk.green(`✅ PAGO APROBADO: ${payment.payment_id}`));
                        
                        // Crear usuario con .hc
                        const username = generatePremiumUsername();
                        const result = await createUser(payment.phone, username, payment.days, payment.hwid, payment.device_name);
                        
                        if (result.success) {
                            db.run(`UPDATE payments SET status = 'approved', approved_at = CURRENT_TIMESTAMP WHERE payment_id = ?`, [payment.payment_id]);
                            
                            const expireDate = moment().add(payment.days, 'days').format('DD/MM/YYYY');
                            
                            let message = `✅ PAGO CONFIRMADO - HTTP CUSTOM

🎉 Tu compra ha sido aprobada

📋 DATOS DE ACCESO:
👤 Usuario: ${username}
🔑 Contraseña: ${DEFAULT_PASSWORD}
📱 Dispositivo: ${payment.device_name || 'No especificado'}
📁 Archivo .hc: Generado y listo para descargar

⏰ VÁLIDO HASTA: ${expireDate}

🌐 DESCARGAR ARCHIVO .HC:
${result.downloadUrl}

📱 COMO USAR:
1. Descarga HTTP Custom desde Play Store
2. Ve a "Importar configuración"
3. Selecciona "Desde archivo"
4. Usa el archivo .hc descargado
5. ¡Conéctate automáticamente!

🎊 ¡Disfruta del servicio premium!`;
                            
                            if (client) {
                                await client.sendText(payment.phone, message);
                                
                                // Enviar también la URL directa
                                await client.sendText(payment.phone, `📥 Enlace directo de descarga:\n${result.downloadUrl}`);
                            }
                            console.log(chalk.green(`✅ Usuario creado: ${username} con archivo .hc`));
                        }
                    }
                }
            } catch (error) {
                console.error(chalk.red(`❌ Error verificando ${payment.payment_id}:`), error.message);
            }
        }
    });
}

// Inicializar WPPConnect
async function initializeBot() {
    try {
        console.log(chalk.yellow('🚀 Inicializando WPPConnect con HWID y .hc...'));
        
        client = await wppconnect.create({
            session: 'httpcustom-bot-session',
            headless: true,
            devtools: false,
            useChrome: true,
            debug: false,
            logQR: true,
            browserWS: '',
            browserArgs: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=site-per-process',
                '--window-size=1920,1080'
            ],
            puppeteerOptions: {
                executablePath: '/usr/bin/google-chrome',
                headless: 'new',
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage'
                ]
            },
            disableWelcome: true,
            updatesLog: false,
            autoClose: 0,
            tokenStore: 'file',
            folderNameToken: '/root/.wppconnect'
        });
        
        console.log(chalk.green('✅ WPPConnect conectado!'));
        
        // Estado de conexión
        client.onStateChange((state) => {
            console.log(chalk.cyan(`📱 Estado: ${state}`));
            
            if (state === 'CONNECTED') {
                console.log(chalk.green('✅ Conexión establecida con WhatsApp'));
            } else if (state === 'DISCONNECTED') {
                console.log(chalk.yellow('⚠️ Desconectado, reconectando...'));
                setTimeout(initializeBot, 10000);
            }
        });
        
        // Manejar mensajes
        client.onMessage(async (message) => {
            try {
                const text = message.body.toLowerCase().trim();
                const from = message.from;
                
                console.log(chalk.cyan(`📩 [${from}]: ${text.substring(0, 30)}`));
                
                const userState = await getUserState(from);
                
                // MENÚ PRINCIPAL
                if (['menu', 'hola', 'start', 'hi', 'volver', '0'].includes(text)) {
                    await setUserState(from, 'main_menu');
                    
                    await client.sendText(from, `🔐 HTTP CUSTOM BOT - SISTEMA HWID 🚀

🌐 *ACCESO MEDIANTE ARCHIVO .HC*

Elija una opción:

🧾 1 - REGISTRAR HWID Y PRUEBA
💰 2 - COMPRAR USUARIO CON HWID
📁 3 - DESCARGAR MI ARCHIVO .HC
🔄 4 - RENOVAR USUARIO
📱 5 - DESCARGAR HTTP CUSTOM APP
🔍 6 - VER MI HWID REGISTRADO
🌐 7 - ACCEDER AL PANEL WEB`);
                }
                
                // OPCIÓN 1: REGISTRAR HWID Y PRUEBA
                else if (text === '1' && userState.state === 'main_menu') {
                    await setUserState(from, 'registering_hwid');
                    
                    await client.sendText(from, `📝 REGISTRO DE HWID

Para crear una cuenta (prueba o premium) necesitas registrar tu HWID.

📋 *¿Qué es el HWID?*
Es un identificador único de tu dispositivo. La app MG VPN lo genera automáticamente.

📱 *¿Cómo obtenerlo?*
1. Instala MG VPN (Opción 5)
2. Abre la app y ve a "Mi ID" o "HWID"
3. Copia el código que aparece

📤 *Formato para enviar:*
NombreDispositivo + HWID

*Ejemplo:*
MiCelular ABC123-DEF456-GHI789

Envía tu nombre de dispositivo y HWID ahora.`);
                }
                
                // REGISTRANDO HWID
                else if (userState.state === 'registering_hwid') {
                    const parts = text.split(/\s+/);
                    if (parts.length >= 2) {
                        const deviceName = parts.slice(0, -1).join(' ');
                        const hwid = parts[parts.length - 1];
                        
                        if (!validateHWID(hwid)) {
                            await client.sendText(from, `❌ HWID INVÁLIDO

El HWID debe tener entre 10 y 64 caracteres
y contener solo letras, números y guiones.

*Ejemplo válido:* ABC123-DEF456-GHI789

Envía nuevamente:
NombreDispositivo + HWID`);
                            return;
                        }
                        
                        await client.sendText(from, `⏳ Verificando HWID: ${hwid.substring(0, 20)}...`);
                        
                        const isAvailable = await checkHWIDAvailable(hwid);
                        if (!isAvailable) {
                            await client.sendText(from, `❌ HWID YA REGISTRADO

Este HWID ya está registrado en el sistema.
Cada HWID solo puede tener una cuenta activa.

Si es tu dispositivo, contacta soporte:
${config.links.support}

O envía un HWID diferente.`);
                            return;
                        }
                        
                        const registration = await registerHWID(from, hwid, deviceName);
                        
                        if (registration.success) {
                            await setUserState(from, 'hwid_registered', { 
                                hwid: registration.hwid, 
                                deviceName: deviceName 
                            });
                            
                            // Ofrecer prueba inmediata
                            if (await canCreateTest(from)) {
                                await client.sendText(from, `✅ HWID REGISTRADO

📱 Dispositivo: ${deviceName}
🔐 HWID: ${registration.hwid.substring(0, 20)}...

🎁 *PRUEBA DISPONIBLE*

¿Quieres crear una cuenta de prueba de 1 hora ahora?

Envía:
✅ *sí* - Para crear prueba con archivo .hc
⏭️ *no* - Para continuar sin prueba`);
                            } else {
                                await client.sendText(from, `✅ HWID REGISTRADO

📱 Dispositivo: ${deviceName}
🔐 HWID: ${registration.hwid.substring(0, 20)}...

⚠️ Ya usaste tu prueba hoy. Mañana puedes solicitar otra.

Envía *menu* para ver opciones.`);
                                await setUserState(from, 'main_menu');
                            }
                        } else {
                            await client.sendText(from, `❌ ERROR AL REGISTRAR HWID

${registration.error}

Intenta nuevamente o contacta soporte:
${config.links.support}`);
                        }
                    } else {
                        await client.sendText(from, `📝 *FORMATO INCORRECTO*

Envía: *NombreDispositivo + HWID*

*Ejemplo:*
MiCelular ABC123-DEF456-GHI789

Intenta nuevamente.`);
                    }
                }
                
                // CONFIRMAR CREACIÓN DE PRUEBA CON .HC
                else if (userState.state === 'hwid_registered' && ['si', 'sí', 'yes', 'ok'].includes(text)) {
                    const stateData = userState.data;
                    
                    await client.sendText(from, '⏳ Creando cuenta de prueba con archivo .hc...');
                    
                    try {
                        const username = generateUsername();
                        const result = await createUser(from, username, 0, stateData.hwid, stateData.deviceName);
                        
                        if (result.success) {
                            registerTest(from);
                            
                            await client.sendText(from, `✅️ PRUEBA CREADA CON ARCHIVO .HC !

📱 Dispositivo: ${stateData.deviceName}
🔐 HWID: ${stateData.hwid.substring(0, 20)}...
👤 Usuario: ${username}
🔑 Contraseña: ${DEFAULT_PASSWORD}
📁 Archivo .hc: Generado automáticamente
⌛️ Expira en: ${config.prices.test_hours} hora(s)

🌐 DESCARGAR ARCHIVO .HC:
${result.downloadUrl}

📱 COMO USAR:
1. Descarga HTTP Custom desde Play Store
2. Importa el archivo .hc descargado
3. ¡Conéctate automáticamente!

⚠️ *IMPORTANTE:* Solo funciona en el dispositivo registrado.`);
                            
                            console.log(chalk.green(`✅ Test creado con archivo .hc: ${username}`));
                        } else {
                            await client.sendText(from, `❌ Error: ${result.error}`);
                        }
                    } catch (error) {
                        await client.sendText(from, `❌ Error al crear cuenta: ${error.message}`);
                    }
                    
                    await setUserState(from, 'main_menu');
                }
                else if (userState.state === 'hwid_registered' && ['no', 'skip', 'saltar'].includes(text)) {
                    await setUserState(from, 'main_menu');
                    await client.sendText(from, `🔐 HWID REGISTRADO CORRECTAMENTE

Ahora puedes comprar planes premium.

Envía *menu* para ver opciones.`);
                }
                
                // OPCIÓN 2: COMPRAR USUARIO
                else if (text === '2' && userState.state === 'main_menu') {
                    db.get('SELECT hwid, device_name FROM hwid_registrations WHERE phone = ? AND status = "pending"', [from], async (err, row) => {
                        if (err || !row || !row.hwid) {
                            await client.sendText(from, `❌ NECESITAS REGISTRAR HWID

Para comprar un plan premium, primero debes registrar tu HWID.

Usa la opción *1* para registrar tu HWID.

📋 *Instrucciones:*
1. Instala MG VPN (Opción 5)
2. Copia tu HWID de la app
3. Regístralo con la opción 1
4. Luego puedes comprar`);
                        } else {
                            await setUserState(from, 'buying_hwid', {
                                hwid: row.hwid,
                                deviceName: row.device_name
                            });
                            
                            await client.sendText(from, `🔐 COMPRA CON HWID REGISTRADO

📱 Dispositivo: ${row.device_name}
🔐 HWID: ${row.hwid.substring(0, 20)}...

🌐 *PLANES HTTP CUSTOM PREMIUM*

Elija una opción:
🗓 1 - PLANES DIARIOS
🗓 2 - PLANES MENSUALES
⬅️ 0 - VOLVER`);
                        }
                    });
                }
                
                // SUBMENÚ DE COMPRAS
                else if (userState.state === 'buying_hwid') {
                    if (text === '1') {
                        await setUserState(from, 'selecting_daily_plan_hwid');
                        
                        await client.sendText(from, `🌐 PLANES DIARIOS HWID

Elija un plan:
🗓 1 - 7 DIAS - $${config.prices.price_7d}

🗓 2 - 15 DIAS - $${config.prices.price_15d}

⬅️ 0 - VOLVER`);
                    }
                    else if (text === '2') {
                        await setUserState(from, 'selecting_monthly_plan_hwid');
                        
                        await client.sendText(from, `🌐 PLANES MENSUALES HWID

Elija un plan:
🗓 1 - 30 DIAS - $${config.prices.price_30d}

🗓 2 - 50 DIAS - $${config.prices.price_50d}

⬅️ 0 - VOLVER`);
                    }
                    else if (text === '0') {
                        await setUserState(from, 'main_menu');
                        await client.sendText(from, `🔐 HTTP CUSTOM BOT - SISTEMA HWID 🚀

🌐 *ACCESO MEDIANTE ARCHIVO .HC*

Elija una opción:

🧾 1 - REGISTRAR HWID Y PRUEBA
💰 2 - COMPRAR USUARIO CON HWID
📁 3 - DESCARGAR MI ARCHIVO .HC
🔄 4 - RENOVAR USUARIO
📱 5 - DESCARGAR HTTP CUSTOM APP
🔍 6 - VER MI HWID REGISTRADO
🌐 7 - ACCEDER AL PANEL WEB`);
                    }
                }
                
                // SELECCIÓN DE PLAN DIARIO
                else if (userState.state === 'selecting_daily_plan_hwid') {
                    if (['1', '2'].includes(text)) {
                        const planMap = {
                            '1': { days: 7, price: config.prices.price_7d, name: '7 DÍAS' },
                            '2': { days: 15, price: config.prices.price_15d, name: '15 DÍAS' }
                        };
                        
                        const plan = planMap[text];
                        const stateData = userState.data;
                        
                        if (mpEnabled) {
                            await client.sendText(from, '⏳ Procesando tu compra...');
                            
                            const payment = await createMercadoPagoPayment(
                                from, 
                                plan.days, 
                                plan.price, 
                                plan.name,
                                stateData.hwid,
                                stateData.deviceName
                            );
                            
                            if (payment.success) {
                                const message = `🔐 HTTP CUSTOM + HWID + .HC

- 📱 Dispositivo: ${stateData.deviceName}
- 🌐 Plan: ${plan.name}
- 💰 Precio: $${payment.amount}
- 📁 Incluye: Archivo .hc personalizado
- 🕜 Duración: ${plan.days} días

📎 LINK DE PAGO

${payment.paymentUrl}

⏰ Este enlace expira en 24 horas
💳 Pago seguro con MercadoPago
📁 Tras el pago, recibirás tu archivo .hc`;
                                
                                await client.sendText(from, message);
                                
                                // Enviar QR
                                if (fs.existsSync(payment.qrPath)) {
                                    try {
                                        const media = await client.decryptFile(payment.qrPath);
                                        await client.sendImage(from, payment.qrPath, 'qr-pago.jpg', 
                                            `Escanea con MercadoPago\n${plan.name} - $${payment.amount}\nHWID: ${stateData.hwid.substring(0, 10)}...`);
                                    } catch (qrError) {
                                        console.error(chalk.red('⚠️ Error enviando QR:'), qrError.message);
                                    }
                                }
                                
                            } else {
                                await client.sendText(from, `❌ ERROR AL GENERAR PAGO

${payment.error}

Contacta al administrador para otras opciones de pago.`);
                            }
                            
                            await setUserState(from, 'main_menu');
                            
                        } else {
                            await client.sendText(from, `🔐 PLAN SELECCIONADO: ${plan.name}

📱 Dispositivo: ${stateData.deviceName}
🔐 HWID: ${stateData.hwid.substring(0, 20)}...
💰 Precio: $${plan.price} ARS
🕜 Duración: ${plan.days} días
📁 Incluye archivo .hc personalizado

Para continuar con la compra, contacta al administrador:
${config.links.support}

O envía el monto por transferencia bancaria.`);
                            
                            await setUserState(from, 'main_menu');
                        }
                    }
                    else if (text === '0') {
                        await setUserState(from, 'buying_hwid');
                        await client.sendText(from, `🌐 PLANES HWID

Elija una opción:
🗓 1 - PLANES DIARIOS
🗓 2 - PLANES MENSUALES
⬅️ 0 - VOLVER`);
                    }
                }
                
                // SELECCIÓN DE PLAN MENSUAL
                else if (userState.state === 'selecting_monthly_plan_hwid') {
                    if (['1', '2'].includes(text)) {
                        const planMap = {
                            '1': { days: 30, price: config.prices.price_30d, name: '30 DÍAS' },
                            '2': { days: 50, price: config.prices.price_50d, name: '50 DÍAS' }
                        };
                        
                        const plan = planMap[text];
                        const stateData = userState.data;
                        
                        if (mpEnabled) {
                            await client.sendText(from, '⏳ Procesando tu compra...');
                            
                            const payment = await createMercadoPagoPayment(
                                from, 
                                plan.days, 
                                plan.price, 
                                plan.name,
                                stateData.hwid,
                                stateData.deviceName
                            );
                            
                            if (payment.success) {
                                const message = `🔐 HTTP CUSTOM + HWID + .HC

- 📱 Dispositivo: ${stateData.deviceName}
- 🌐 Plan: ${plan.name}
- 💰 Precio: $${payment.amount}
- 📁 Incluye: Archivo .hc personalizado
- 🕜 Duración: ${plan.days} días

📎 LINK DE PAGO

${payment.paymentUrl}

⏰ Este enlace expira en 24 horas
💳 Pago seguro con MercadoPago
📁 Tras el pago, recibirás tu archivo .hc`;
                                
                                await client.sendText(from, message);
                                
                                // Enviar QR
                                if (fs.existsSync(payment.qrPath)) {
                                    try {
                                        const media = await client.decryptFile(payment.qrPath);
                                        await client.sendImage(from, payment.qrPath, 'qr-pago.jpg', 
                                            `Escanea con MercadoPago\n${plan.name} - $${payment.amount}\nHWID: ${stateData.hwid.substring(0, 10)}...`);
                                    } catch (qrError) {
                                        console.error(chalk.red('⚠️ Error enviando QR:'), qrError.message);
                                    }
                                }
                                
                            } else {
                                await client.sendText(from, `❌ ERROR AL GENERAR PAGO

${payment.error}

Contacta al administrador para otras opciones de pago.`);
                            }
                            
                            await setUserState(from, 'main_menu');
                            
                        } else {
                            await client.sendText(from, `🔐 PLAN SELECCIONADO: ${plan.name}

📱 Dispositivo: ${stateData.deviceName}
🔐 HWID: ${stateData.hwid.substring(0, 20)}...
💰 Precio: $${plan.price} ARS
🕜 Duración: ${plan.days} días
📁 Incluye archivo .hc personalizado

Para continuar con la compra, contacta al administrador:
${config.links.support}

O envía el monto por transferencia bancaria.`);
                            
                            await setUserState(from, 'main_menu');
                        }
                    }
                    else if (text === '0') {
                        await setUserState(from, 'buying_hwid');
                        await client.sendText(from, `🌐 PLANES HTTP CUSTOM PREMIUM + HWID

Elija una opción:
🗓 1 - PLANES DIARIOS
🗓 2 - PLANES MENSUALES
⬅️ 0 - VOLVER`);
                    }
                }
                
                // OPCIÓN 3: DESCARGAR MI ARCHIVO .HC
                else if (text === '3' && userState.state === 'main_menu') {
                    db.get('SELECT hwid, device_name FROM hwid_registrations WHERE phone = ? ORDER BY created_at DESC LIMIT 1', [from], async (err, row) => {
                        if (err || !row || !row.hwid) {
                            await client.sendText(from, `❌ NO TIENES HWID REGISTRADO

Usa la opción *1* para registrar tu HWID primero.`);
                        } else {
                            const downloadUrl = `http://${config.bot.server_ip}:${config.bot.web_port}/download/${row.hwid}`;
                            
                            await client.sendText(from, `📁 DESCARGAR ARCHIVO .HC

📱 Dispositivo: ${row.device_name}
🔐 HWID: ${row.hwid.substring(0, 20)}...

🌐 ENLACE DE DESCARGA:
${downloadUrl}

📋 *Instrucciones:*
1. Ve al enlace desde tu dispositivo
2. Introduce tu HWID: ${row.hwid.substring(0, 15)}...
3. Descarga el archivo .hc
4. Importa en HTTP Custom App

O visita directamente:
http://${config.bot.server_ip}:${config.bot.web_port}`);
                        }
                    });
                }
                
                // OPCIÓN 4: RENOVAR
                else if (text === '4' && userState.state === 'main_menu') {
                    await client.sendText(from, `🔄 RENOVAR USUARIO HTTP CUSTOM

Para renovar tu cuenta existente (con HWID), contacta al administrador:
${config.links.support}

Indica tu HWID actual y el plan deseado.`);
                }
                
                // OPCIÓN 5: DESCARGAR APP
                else if (text === '5' && userState.state === 'main_menu') {
                    await client.sendText(from, `📱 DESCARGAR HTTP CUSTOM APP

🔗 Enlace Play Store:
${config.links.app_download}

📋 *Instrucciones:*
1. Descarga e instala "HTTP Custom"
2. Abre la aplicación
3. Ve a "Importar configuración"
4. Selecciona "Desde archivo"
5. Usa el archivo .hc que te proporcionamos

⚠️ *IMPORTANTE:* Necesitas registrar tu HWID primero (Opción 1).`);
                }
                
                // OPCIÓN 6: VER MI HWID REGISTRADO
                else if (text === '6' && userState.state === 'main_menu') {
                    db.get('SELECT hwid, device_name, status FROM hwid_registrations WHERE phone = ? ORDER BY created_at DESC LIMIT 1', [from], async (err, row) => {
                        if (err || !row) {
                            await client.sendText(from, `❌ NO TIENES HWID REGISTRADO

Usa la opción *1* para registrar tu HWID primero.`);
                        } else {
                            await client.sendText(from, `📋 TU HWID REGISTRADO

📱 Dispositivo: ${row.device_name}
🔐 HWID: ${row.hwid.substring(0, 20)}...
📊 Estado: ${row.status === 'pending' ? '🟡 Pendiente' : '🟢 Activo'}

Usa este HWID para:
• Crear cuenta de prueba
• Comprar planes premium
• Descargar archivo .hc
• Identificar tu dispositivo

⚠️ Si cambias de dispositivo, debes registrar el nuevo HWID.`);
                        }
                    });
                }
                
                // OPCIÓN 7: PANEL WEB
                else if (text === '7' && userState.state === 'main_menu') {
                    await client.sendText(from, `🌐 PANEL WEB HTTP CUSTOM

Accede al panel web para:
• Descargar archivos .hc
• Ver tus dispositivos
• Gestionar tu cuenta

🔗 Enlace del panel:
http://${config.bot.server_ip}:${config.bot.web_port}

📱 *Desde tu dispositivo:*
1. Abre el enlace en el navegador
2. Introduce tu HWID
3. Descarga tu archivo .hc
4. Importa en HTTP Custom App`);
                }
                
            } catch (error) {
                console.error(chalk.red('❌ Error procesando mensaje:'), error.message);
            }
        });
        
        // ✅ VERIFICAR PAGOS CADA 2 MINUTOS
        cron.schedule('*/2 * * * *', () => {
            console.log(chalk.yellow('🔄 Verificando pagos pendientes...'));
            checkPendingPayments();
        });
        
        // ✅ LIMPIEZA CADA 15 MINUTOS
        cron.schedule('*/15 * * * *', async () => {
            const now = moment().format('YYYY-MM-DD HH:mm:ss');
            console.log(chalk.yellow(`🧹 Limpiando usuarios expirados...`));
            
            db.all('SELECT username, hwid, hc_file FROM users WHERE expires_at < ? AND status = 1', [now], async (err, rows) => {
                if (err || !rows || rows.length === 0) return;
                
                for (const r of rows) {
                    try {
                        // Eliminar archivo .hc
                        if (r.hc_file && fs.existsSync(r.hc_file)) {
                            fs.unlinkSync(r.hc_file);
                        }
                        
                        db.run('UPDATE users SET status = 0 WHERE username = ?', [r.username]);
                        db.run('DELETE FROM hc_files WHERE hwid = ?', [r.hwid]);
                        db.run(`DELETE FROM hwid_registrations WHERE hwid = ? AND status = 'pending'`, [r.hwid]);
                        
                        console.log(chalk.green(`🗑️ Eliminado: ${r.username} - HWID liberado, .hc eliminado`));
                    } catch (e) {
                        console.error(chalk.red(`Error eliminando ${r.username}:`), e.message);
                    }
                }
            });
        });
        
        // ✅ LIMPIAR ESTADOS ANTIGUOS
        cron.schedule('0 * * * *', () => {
            db.run(`DELETE FROM user_state WHERE updated_at < datetime('now', '-1 hour')`);
        });
        
        // ✅ LIMPIAR HWID PENDIENTES ANTIGUOS
        cron.schedule('0 2 * * *', () => {
            db.run(`DELETE FROM hwid_registrations WHERE status = 'pending' AND created_at < datetime('now', '-7 days')`);
            db.run(`DELETE FROM hc_files WHERE created_at < datetime('now', '-30 days')`);
            console.log(chalk.yellow('🧹 HWID pendientes y archivos .hc antiguos limpiados'));
        });
        
    } catch (error) {
        console.error(chalk.red('❌ Error inicializando WPPConnect:'), error.message);
        console.log(chalk.yellow('🔄 Reintentando en 10 segundos...'));
        setTimeout(initializeBot, 10000);
    }
}

// Iniciar el bot
initializeBot();

// Manejar cierre
process.on('SIGINT', async () => {
    console.log(chalk.yellow('\n🛑 Cerrando bot...'));
    if (client) {
        await client.close();
    }
    process.exit();
});
BOTEOF

echo -e "${GREEN}✅ Bot creado con sistema HWID y .hc${NC}"

# ================================================
# CREAR PANEL DE CONTROL COMPLETO
# ================================================
echo -e "\n${CYAN}🎛️  Creando panel de control completo...${NC}"

cat > /usr/local/bin/hcbot << 'PANELEOF'
#!/bin/bash
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; BLUE='\033[0;34m'; PURPLE='\033[0;35m'; NC='\033[0m'

DB="/opt/httpcustom-bot/data/users.db"
CONFIG="/opt/httpcustom-bot/config/config.json"

get_val() { jq -r "$1" "$CONFIG" 2>/dev/null; }
set_val() { local t=$(mktemp); jq "$1 = $2" "$CONFIG" > "$t" && mv "$t" "$CONFIG"; }

show_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║            🎛️  PANEL HTTP CUSTOM BOT - HWID + .HC         ║${NC}"
    echo -e "${CYAN}║               📁 SISTEMA DE ARCHIVOS .HC                  ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}\n"
}

while true; do
    show_header
    
    TOTAL_USERS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM users" 2>/dev/null || echo "0")
    ACTIVE_USERS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM users WHERE status=1" 2>/dev/null || echo "0")
    TOTAL_HWID=$(sqlite3 "$DB" "SELECT COUNT(DISTINCT hwid) FROM users WHERE hwid IS NOT NULL" 2>/dev/null || echo "0")
    TOTAL_HC_FILES=$(sqlite3 "$DB" "SELECT COUNT(*) FROM hc_files" 2>/dev/null || echo "0")
    PENDING_PAYMENTS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM payments WHERE status='pending'" 2>/dev/null || echo "0")
    
    STATUS=$(pm2 jlist 2>/dev/null | jq -r '.[] | select(.name=="httpcustom-bot") | .pm2_env.status' 2>/dev/null || echo "stopped")
    STATUS_WEB=$(pm2 jlist 2>/dev/null | jq -r '.[] | select(.name=="hc-web-server") | .pm2_env.status' 2>/dev/null || echo "stopped")
    
    if [[ "$STATUS" == "online" ]]; then
        BOT_STATUS="${GREEN}● ACTIVO${NC}"
    else
        BOT_STATUS="${RED}● DETENIDO${NC}"
    fi
    
    if [[ "$STATUS_WEB" == "online" ]]; then
        WEB_STATUS="${GREEN}● ACTIVO${NC}"
    else
        WEB_STATUS="${RED}● DETENIDO${NC}"
    fi
    
    echo -e "${YELLOW}📊 ESTADO DEL SISTEMA HWID + .HC${NC}"
    echo -e "  Bot WhatsApp: $BOT_STATUS"
    echo -e "  Servidor Web: $WEB_STATUS"
    echo -e "  Usuarios: ${CYAN}$ACTIVE_USERS/$TOTAL_USERS${NC} activos/total"
    echo -e "  HWID: ${CYAN}$TOTAL_HWID${NC} únicos"
    echo -e "  Archivos .hc: ${CYAN}$TOTAL_HC_FILES${NC} generados"
    echo -e "  Pagos pendientes: ${CYAN}$PENDING_PAYMENTS${NC}"
    echo -e "  IP: $(get_val '.bot.server_ip')"
    echo -e "  Puerto Web: $(get_val '.bot.web_port')"
    echo -e "  URL Panel: http://$(get_val '.bot.server_ip'):$(get_val '.bot.web_port')"
    echo -e ""
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}[1]${NC} 🚀  Iniciar/Reiniciar todo"
    echo -e "${CYAN}[2]${NC} 🛑  Detener todo"
    echo -e "${CYAN}[3]${NC} 📱  Ver logs del bot"
    echo -e "${CYAN}[4]${NC} 🌐  Ver logs del servidor web"
    echo -e "${CYAN}[5]${NC} 👤  Crear usuario con HWID y .hc"
    echo -e "${CYAN}[6]${NC} 📁  Ver archivos .hc generados"
    echo -e "${CYAN}[7]${NC} 👥  Listar usuarios con HWID"
    echo -e "${CYAN}[8]${NC} 💰  Cambiar precios"
    echo -e "${CYAN}[9]${NC} 🔑  Configurar MercadoPago"
    echo -e "${CYAN}[10]${NC} 🧪 Test MercadoPago"
    echo -e "${CYAN}[11]${NC} 📊 Ver estadísticas .hc"
    echo -e "${CYAN}[12]${NC} 🔄 Limpiar sesión WhatsApp"
    echo -e "${CYAN}[13]${NC} 🗑️  Eliminar archivos .hc antiguos"
    echo -e "${CYAN}[14]${NC} 📝 Ver plantilla .hc"
    echo -e "${CYAN}[15]${NC} 🛠️  Regenerar archivo .hc"
    echo -e "${CYAN}[16]${NC} 🌍 Acceder al panel web"
    echo -e "${CYAN}[0]${NC} 🚪  Salir"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e ""
    
    read -p "👉 Selecciona: " OPTION
    
    case $OPTION in
        1)
            echo -e "\n${YELLOW}🔄 Iniciando todo...${NC}"
            cd /root/httpcustom-bot
            pm2 start bot.js --name httpcustom-bot
            pm2 start /opt/httpcustom-bot/hc-server.js --name hc-web-server
            pm2 save
            echo -e "${GREEN}✅ Bot y servidor web iniciados${NC}"
            sleep 2
            ;;
        2)
            echo -e "\n${YELLOW}🛑 Deteniendo todo...${NC}"
            pm2 stop httpcustom-bot hc-web-server
            echo -e "${GREEN}✅ Todo detenido${NC}"
            sleep 2
            ;;
        3)
            echo -e "\n${YELLOW}📱 Mostrando logs del bot...${NC}"
            pm2 logs httpcustom-bot --lines 100
            ;;
        4)
            echo -e "\n${YELLOW}🌐 Mostrando logs del servidor web...${NC}"
            pm2 logs hc-web-server --lines 100
            ;;
        5)
            clear
            echo -e "${CYAN}👤 CREAR USUARIO CON HWID Y .HC${NC}\n"
            
            read -p "Teléfono (ej: 5491122334455): " PHONE
            read -p "Nombre del dispositivo: " DEVICE
            read -p "HWID (sin espacios): " HWID
            read -p "Usuario (minúsculas, auto=generar): " USERNAME
            read -p "Días (0=test 1h, 7,15,30,50=premium): " DAYS
            
            [[ -z "$DAYS" ]] && DAYS="30"
            if [[ "$USERNAME" == "auto" || -z "$USERNAME" ]]; then
                USERNAME="user$(shuf -i 1000-9999 -n 1)"
            fi
            
            USERNAME=$(echo "$USERNAME" | tr '[:upper:]' '[:lower:]')
            PASSWORD="mgvpn247"
            
            # Hashear HWID
            HWID_HASH=$(echo -n "$HWID" | sha256sum | awk '{print $1}')
            
            # Generar archivo .hc
            cd /root/httpcustom-bot
            node -e "
                const fs = require('fs');
                const path = require('path');
                const config = require('/opt/httpcustom-bot/config/config.json');
                
                const template = fs.readFileSync(config.paths.templates + '/base.hc', 'utf8');
                const proxyPort = config.bot.proxy_port_start + Math.floor(Math.random() * (config.bot.proxy_port_end - config.bot.proxy_port_start));
                
                const hcContent = template
                    .replace(/__SERVER_IP__/g, config.bot.server_ip)
                    .replace(/__PORT__/g, proxyPort)
                    .replace(/__USERNAME__/g, '$USERNAME')
                    .replace(/__PASSWORD__/g, '$PASSWORD');
                
                const filename = \`httpcustom_\${'$USERNAME'}_\${Date.now()}.hc\`;
                const filePath = path.join(config.paths.hc_files, filename);
                const downloadUrl = \`http://\${config.bot.server_ip}:\${config.bot.web_port}/download/\${'$HWID_HASH'}\`;
                
                fs.writeFileSync(filePath, hcContent);
                
                const sqlite3 = require('sqlite3').verbose();
                const db = new sqlite3.Database(config.paths.database);
                
                const expireDate = new Date();
                expireDate.setDate(expireDate.getDate() + parseInt('$DAYS'));
                const expireStr = expireDate.toISOString().split('T')[0] + ' 23:59:59';
                
                db.serialize(() => {
                    db.run(\`INSERT INTO users (phone, username, password, tipo, expires_at, hwid, device_name, hc_file, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)\`,
                        ['$PHONE', '$USERNAME', '$PASSWORD', parseInt('$DAYS') === 0 ? 'test' : 'premium', expireStr, '$HWID_HASH', '$DEVICE', filePath]);
                    
                    db.run(\`INSERT OR REPLACE INTO hwid_registrations (phone, hwid, device_name, status) VALUES (?, ?, ?, 'approved')\`,
                        ['$PHONE', '$HWID_HASH', '$DEVICE']);
                    
                    db.run(\`INSERT INTO hc_files (username, hwid, device_name, file_path, download_url) VALUES (?, ?, ?, ?, ?)\`,
                        ['$USERNAME', '$HWID_HASH', '$DEVICE', filePath, downloadUrl]);
                });
                
                db.close();
                
                console.log('✅ Usuario creado con archivo .hc');
                console.log('👤 Usuario:', '$USERNAME');
                console.log('🔑 Contraseña:', '$PASSWORD');
                console.log('📁 Archivo:', filename);
                console.log('🌐 URL:', downloadUrl);
                console.log('⏰ Expira:', expireStr);
            "
            
            read -p "Presiona Enter..."
            ;;
        6)
            clear
            echo -e "${CYAN}📁 ARCHIVOS .HC GENERADOS${NC}\n"
            
            sqlite3 -column -header "$DB" "SELECT username, device_name, SUBSTR(hwid, 1, 10) as 'HWID', file_path, created_at FROM hc_files ORDER BY created_at DESC LIMIT 20"
            
            echo -e "\n${YELLOW}Ruta de archivos: ${GREEN}$(get_val '.paths.hc_files')${NC}"
            read -p "Presiona Enter..."
            ;;
        7)
            clear
            echo -e "${CYAN}👥 USUARIOS CON HWID Y .HC${NC}\n"
            
            echo -e "${YELLOW}Usuarios activos:${NC}"
            sqlite3 -column -header "$DB" "SELECT username, device_name, SUBSTR(hwid, 1, 10) as 'HWID', tipo, expires_at FROM users WHERE status = 1 ORDER BY expires_at DESC LIMIT 20"
            
            echo -e "\n${YELLOW}Total: ${ACTIVE_USERS} activos${NC}"
            read -p "Presiona Enter..."
            ;;
        8)
            clear
            echo -e "${CYAN}💰 CAMBIAR PRECIOS${NC}\n"
            
            CURRENT_7D=$(get_val '.prices.price_7d')
            CURRENT_15D=$(get_val '.prices.price_15d')
            CURRENT_30D=$(get_val '.prices.price_30d')
            CURRENT_50D=$(get_val '.prices.price_50d')
            
            echo -e "${YELLOW}Precios actuales:${NC}"
            echo -e "  7 días: $${CURRENT_7D} ARS"
            echo -e "  15 días: $${CURRENT_15D} ARS"
            echo -e "  30 días: $${CURRENT_30D} ARS"
            echo -e "  50 días: $${CURRENT_50D} ARS\n"
            
            read -p "Nuevo precio 7d [${CURRENT_7D}]: " NEW_7D
            read -p "Nuevo precio 15d [${CURRENT_15D}]: " NEW_15D
            read -p "Nuevo precio 30d [${CURRENT_30D}]: " NEW_30D
            read -p "Nuevo precio 50d [${CURRENT_50D}]: " NEW_50D
            
            [[ -n "$NEW_7D" ]] && set_val '.prices.price_7d' "$NEW_7D"
            [[ -n "$NEW_15D" ]] && set_val '.prices.price_15d' "$NEW_15D"
            [[ -n "$NEW_30D" ]] && set_val '.prices.price_30d' "$NEW_30D"
            [[ -n "$NEW_50D" ]] && set_val '.prices.price_50d' "$NEW_50D"
            
            echo -e "\n${GREEN}✅ Precios actualizados${NC}"
            read -p "Presiona Enter..."
            ;;
        9)
            clear
            echo -e "${CYAN}🔑 CONFIGURAR MERCADOPAGO${NC}\n"
            
            CURRENT_TOKEN=$(get_val '.mercadopago.access_token')
            
            if [[ -n "$CURRENT_TOKEN" && "$CURRENT_TOKEN" != "null" && "$CURRENT_TOKEN" != "" ]]; then
                echo -e "${GREEN}✅ Token configurado${NC}"
                echo -e "${YELLOW}Preview: ${CURRENT_TOKEN:0:30}...${NC}\n"
            else
                echo -e "${YELLOW}⚠️  Sin token configurado${NC}\n"
            fi
            
            echo -e "${CYAN}📋 Obtener token:${NC}"
            echo -e "  1. https://www.mercadopago.com.ar/developers"
            echo -e "  2. Inicia sesión"
            echo -e "  3. 'Tus credenciales' → Access Token PRODUCCIÓN"
            echo -e "  4. Formato: APP_USR-xxxxxxxxxx\n"
            
            read -p "¿Configurar nuevo token? (s/N): " CONF
            if [[ "$CONF" == "s" ]]; then
                echo ""
                read -p "Pega el Access Token: " NEW_TOKEN
                
                if [[ "$NEW_TOKEN" =~ ^APP_USR- ]] || [[ "$NEW_TOKEN" =~ ^TEST- ]]; then
                    set_val '.mercadopago.access_token' "\"$NEW_TOKEN\""
                    set_val '.mercadopago.enabled' "true"
                    echo -e "\n${GREEN}✅ Token configurado${NC}"
                    echo -e "${YELLOW}🔄 Reiniciando bot...${NC}"
                    cd /root/httpcustom-bot && pm2 restart httpcustom-bot
                    sleep 2
                    echo -e "${GREEN}✅ MercadoPago activado${NC}"
                else
                    echo -e "${RED}❌ Token inválido${NC}"
                    echo -e "${YELLOW}Debe empezar con APP_USR- o TEST-${NC}"
                fi
            fi
            read -p "Presiona Enter..."
            ;;
        10)
            clear
            echo -e "${CYAN}🧪 TEST MERCADOPAGO${NC}\n"
            
            TOKEN=$(get_val '.mercadopago.access_token')
            if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
                echo -e "${RED}❌ Token no configurado${NC}\n"
                read -p "Presiona Enter..."
                continue
            fi
            
            echo -e "${YELLOW}🔑 Token: ${TOKEN:0:30}...${NC}\n"
            echo -e "${YELLOW}🔄 Probando conexión...${NC}"
            
            RESPONSE=$(curl -s -w "\n%{http_code}" \
                -H "Authorization: Bearer $TOKEN" \
                "https://api.mercadopago.com/v1/payment_methods" \
                2>/dev/null)
            
            HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
            
            if [[ "$HTTP_CODE" == "200" ]]; then
                echo -e "${GREEN}✅ CONEXIÓN EXITOSA${NC}"
            else
                echo -e "${RED}❌ ERROR - Código: $HTTP_CODE${NC}"
            fi
            
            read -p "Presiona Enter..."
            ;;
        11)
            clear
            echo -e "${CYAN}📊 ESTADÍSTICAS .HC${NC}\n"
            
            echo -e "${YELLOW}📁 ARCHIVOS .HC:${NC}"
            sqlite3 "$DB" "SELECT 'Total: ' || COUNT(*) || ' | Últimos 7 días: ' || SUM(CASE WHEN created_at > datetime('now', '-7 days') THEN 1 ELSE 0 END) || ' | Hoy: ' || SUM(CASE WHEN date(created_at) = date('now') THEN 1 ELSE 0 END) FROM hc_files"
            
            echo -e "\n${YELLOW}📥 DESCARGAS:${NC}"
            sqlite3 "$DB" "SELECT 'Total descargas: ' || SUM(CASE WHEN last_download IS NOT NULL THEN 1 ELSE 0 END) || ' | Últimas 24h: ' || SUM(CASE WHEN last_download > datetime('now', '-1 day') THEN 1 ELSE 0 END) FROM hc_files"
            
            echo -e "\n${YELLOW}👥 USUARIOS CON .HC:${NC}"
            sqlite3 "$DB" "SELECT 'Activos: ' || SUM(CASE WHEN status=1 AND hc_file IS NOT NULL THEN 1 ELSE 0 END) || ' | Test: ' || SUM(CASE WHEN tipo='test' AND hc_file IS NOT NULL THEN 1 ELSE 0 END) || ' | Premium: ' || SUM(CASE WHEN tipo='premium' AND hc_file IS NOT NULL THEN 1 ELSE 0 END) FROM users"
            
            read -p "Presiona Enter..."
            ;;
        12)
            echo -e "\n${YELLOW}🧹 Limpiando sesión WhatsApp...${NC}"
            pm2 stop httpcustom-bot
            rm -rf /root/.wppconnect/*
            echo -e "${GREEN}✅ Sesión limpiada${NC}"
            echo -e "${YELLOW}📱 Escanea nuevo QR al iniciar${NC}"
            sleep 2
            ;;
        13)
            clear
            echo -e "${CYAN}🗑️  ELIMINAR ARCHIVOS .HC ANTIGUOS${NC}\n"
            
            echo -e "${YELLOW}Archivos .hc >30 días:${NC}"
            sqlite3 "$DB" "SELECT COUNT(*) FROM hc_files WHERE created_at < datetime('now', '-30 days')"
            
            read -p "¿Eliminar automáticamente? (s/N): " CLEAN
            if [[ "$CLEAN" == "s" ]]; then
                echo -e "\n${YELLOW}🧹 Eliminando...${NC}"
                
                # Obtener archivos antiguos
                sqlite3 "$DB" "SELECT file_path FROM hc_files WHERE created_at < datetime('now', '-30 days')" | while read file; do
                    if [[ -f "$file" ]]; then
                        rm -f "$file"
                        echo "Eliminado: $file"
                    fi
                done
                
                # Limpiar BD
                sqlite3 "$DB" "DELETE FROM hc_files WHERE created_at < datetime('now', '-30 days')"
                
                echo -e "${GREEN}✅ Archivos antiguos eliminados${NC}"
            fi
            
            read -p "Presiona Enter..."
            ;;
        14)
            clear
            echo -e "${CYAN}📝 PLANTILLA .HC${NC}\n"
            
            TEMPLATE_FILE="/opt/httpcustom-bot/templates/base.hc"
            if [[ -f "$TEMPLATE_FILE" ]]; then
                echo -e "${YELLOW}Contenido de la plantilla:${NC}\n"
                cat "$TEMPLATE_FILE"
                echo -e "\n\n${YELLOW}Variables disponibles:${NC}"
                echo -e "  __SERVER_IP__ - IP del servidor"
                echo -e "  __PORT__ - Puerto proxy"
                echo -e "  __USERNAME__ - Nombre de usuario"
                echo -e "  __PASSWORD__ - Contraseña"
            else
                echo -e "${RED}❌ Plantilla no encontrada${NC}"
            fi
            
            read -p "Presiona Enter..."
            ;;
        15)
            clear
            echo -e "${CYAN}🛠️  REGENERAR ARCHIVO .HC${NC}\n"
            
            read -p "HWID hash o username: " INPUT
            
            if [[ -n "$INPUT" ]]; then
                echo -e "\n${YELLOW}Buscando usuario...${NC}"
                
                sqlite3 -column -header "$DB" "SELECT username, hwid, device_name, hc_file FROM users WHERE username = '$INPUT' OR hwid LIKE '%$INPUT%' LIMIT 5"
                
                read -p "¿Regenerar archivo .hc? (s/N): " REGEN
                if [[ "$REGEN" == "s" ]]; then
                    echo -e "${YELLOW}🔄 Regenerando...${NC}"
                    
                    # Aquí iría el código para regenerar el archivo .hc
                    echo -e "${GREEN}✅ Función de regeneración (pendiente implementación)${NC}"
                fi
            fi
            
            read -p "Presiona Enter..."
            ;;
        16)
            clear
            SERVER_IP=$(get_val '.bot.server_ip')
            WEB_PORT=$(get_val '.bot.web_port')
            echo -e "${CYAN}🌍 PANEL WEB HTTP CUSTOM${NC}\n"
            echo -e "${YELLOW}Accede desde tu navegador:${NC}"
            echo -e "${GREEN}http://$SERVER_IP:$WEB_PORT${NC}\n"
            echo -e "${YELLOW}O usa estos comandos:${NC}"
            echo -e "  Linux: ${GREEN}xdg-open http://$SERVER_IP:$WEB_PORT${NC}"
            echo -e "  Mac: ${GREEN}open http://$SERVER_IP:$WEB_PORT${NC}"
            echo -e "  Windows: ${GREEN}start http://$SERVER_IP:$WEB_PORT${NC}"
            echo -e "\n${YELLOW}Desde el servidor:${NC}"
            echo -e "  ${GREEN}curl http://localhost:$WEB_PORT${NC}"
            read -p "Presiona Enter..."
            ;;
        0)
            echo -e "\n${GREEN}👋 Hasta pronto${NC}\n"
            exit 0
            ;;
        *)
            echo -e "\n${RED}❌ Opción inválida${NC}"
            sleep 1
            ;;
    esac
done
PANELEOF

chmod +x /usr/local/bin/hcbot
echo -e "${GREEN}✅ Panel de control creado${NC}"

# ================================================
# INICIAR SERVICIOS
# ================================================
echo -e "\n${CYAN}🚀 Iniciando servicios...${NC}"

cd "$USER_HOME"
pm2 start bot.js --name httpcustom-bot
pm2 start "$INSTALL_DIR/hc-server.js" --name hc-web-server
pm2 save
pm2 startup systemd -u root --hp /root > /dev/null 2>&1

sleep 3

# ================================================
# MENSAJE FINAL
# ================================================
clear
echo -e "${GREEN}${BOLD}"
cat << "FINAL"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      🔐 INSTALACIÓN COMPLETADA - HTTP CUSTOM + HWID 🔐      ║
║                                                              ║
║     🤖 HTTP CUSTOM BOT - SISTEMA HWID + ARCHIVOS .HC       ║
║     📱 WhatsApp API + REGISTRO HWID                        ║
║     📁 Generación automática de archivos .hc               ║
║     🌐 Servidor web para descarga de .hc por HWID          ║
║     💰 MercadoPago SDK v2.x COMPLETO                       ║
║     🎛️  Panel completo con gestión de .hc                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
FINAL
echo -e "${NC}"

echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Sistema HTTP Custom completo instalado${NC}"
echo -e "${GREEN}✅ WhatsApp API funcionando${NC}"
echo -e "${GREEN}✅ Servidor web para .hc en puerto $WEB_PORT${NC}"
echo -e "${GREEN}✅ Generación automática de archivos .hc${NC}"
echo -e "${GREEN}✅ Cliente envía: Nombre + HWID${NC}"
echo -e "${GREEN}✅ Descarga de .hc por HWID desde panel web${NC}"
echo -e "${GREEN}✅ MercadoPago SDK v2.x integrado${NC}"
echo -e "${GREEN}✅ Panel de control completo${NC}"
echo -e "${GREEN}✅ Pago automático con QR${NC}"
echo -e "${GREEN}✅ Verificación automática de pagos${NC}"
echo -e "${GREEN}✅ Planes: 7 días, 15 días, 30 días, 50 días${NC}"
echo -e "${GREEN}✅ Contraseña fija: mgvpn247${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}📋 COMANDOS PRINCIPALES:${NC}\n"
echo -e "  ${GREEN}hcbot${NC}           - Panel de control completo"
echo -e "  ${GREEN}pm2 logs httpcustom-bot${NC} - Ver logs del bot"
echo -e "  ${GREEN}pm2 logs hc-web-server${NC} - Ver logs del servidor web"
echo -e "  ${GREEN}pm2 restart all${NC} - Reiniciar todo"
echo -e "\n"

echo -e "${YELLOW}🔐 FLUJO DEL CLIENTE:${NC}\n"
echo -e "  1. Cliente instala MG VPN para obtener HWID"
echo -e "  2. Envía al bot: Nombre + HWID"
echo -e "  3. Bot registra HWID y ofrece prueba/compras"
echo -e "  4. Tras compra/prueba, se genera archivo .hc"
echo -e "  5. Cliente descarga .hc desde panel web con su HWID"
echo -e "  6. Importa .hc en HTTP Custom App"
echo -e "  7. ¡Conectado!"
echo -e "\n"

echo -e "${YELLOW}🌐 PANEL WEB PARA CLIENTES:${NC}\n"
echo -e "  ${GREEN}http://$SERVER_IP:$WEB_PORT${NC}"
echo -e "\n  Funcionalidades:"
echo -e "  • Introducir HWID para descargar .hc"
echo -e "  • Instrucciones de uso"
echo -e "  • QR para importación directa"
echo -e "\n"

echo -e "${YELLOW}📁 ARCHIVOS .HC:${NC}\n"
echo -e "  • Generados automáticamente por usuario"
echo -e "  • Almacenados en: ${GREEN}$HC_FILES_DIR${NC}"
echo -e "  • Descarga por HWID desde panel web"
echo -e "  • Plantilla personalizable en templates/base.hc"
echo -e "\n"

echo -e "${YELLOW}🚀 PRIMEROS PASOS:${NC}\n"
echo -e "  1. Ver logs: ${GREEN}pm2 logs httpcustom-bot${NC}"
echo -e "  2. Escanear QR cuando aparezca"
echo -e "  3. Configurar MercadoPago: ${GREEN}hcbot → Opción 9${NC}"
echo -e "  4. Acceder al panel web: ${GREEN}hcbot → Opción 16${NC}"
echo -e "  5. Enviar 'menu' al bot en WhatsApp"
echo -e "  6. Probar flujo completo con un HWID de prueba"
echo -e "\n"

echo -e "${YELLOW}📱 FORMATO DE REGISTRO HWID:${NC}\n"
echo -e "  *Cliente envía:*"
echo -e "  MiCelular ABC123-DEF456-GHI789"
echo -e "\n  *El bot responde:*"
echo -e "  ✅ HWID registrado para MiCelular"
echo -e "  ¿Crear prueba de 1 hora con .hc? (sí/no)"
echo -e "\n"

echo -e "${GREEN}${BOLD}¡Sistema HTTP Custom con HWID y archivos .hc listo! 🔐📁${NC}\n"

# Ver logs automáticamente
read -p "$(echo -e "${YELLOW}¿Ver logs del bot ahora? (s/N): ${NC}")" -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "\n${CYAN}Mostrando logs del bot...${NC}"
    echo -e "${YELLOW}📱 Espera que aparezca el QR para escanear...${NC}\n"
    sleep 2
    pm2 logs httpcustom-bot
else
    echo -e "\n${YELLOW}💡 Para iniciar: ${GREEN}hcbot${NC}"
    echo -e "${YELLOW}💡 Para logs: ${GREEN}pm2 logs httpcustom-bot${NC}"
    echo -e "${YELLOW}💡 Panel web: ${GREEN}http://$SERVER_IP:$WEB_PORT${NC}"
    echo -e "${YELLOW}💡 Para probar: Envía 'menu' al bot${NC}\n"
fi

exit 0