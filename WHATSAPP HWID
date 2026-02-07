#!/bin/bash
# ================================================
# SSH BOT PRO - WPPCONNECT + MERCADOPAGO + HWID
# SISTEMA DE AUTENTICACIÓN POR HWID DEL DISPOSITIVO
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
║     ███████╗███████╗██║  ██║    ██████╗  ██████╗ ████████╗  ║
║     ██╔════╝██╔════╝██║  ██║    ██╔══██╗██╔═══██╗╚══██╔══╝  ║
║     ███████╗███████╗███████║    ██████╔╝██║   ██║   ██║     ║
║     ╚════██║╚════██║██╔══██║    ██╔══██╗██║   ██║   ██║     ║
║     ███████║███████║██║  ██║    ██████╔╝╚██████╔╝   ██║     ║
║     ╚══════╝╚══════╝╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║          🤖 SSH BOT PRO - SISTEMA HWID INTEGRADO            ║
║               📱 WhatsApp API + HWID VALIDACIÓN            ║
║               💰 MercadoPago SDK v2.x INTEGRADO            ║
║               🔐 Autenticación por dispositivo HWID         ║
║               🎛️  Panel completo con control MP y HWID     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

echo -e "${GREEN}✅ CARACTERÍSTICAS PRINCIPALES:${NC}"
echo -e "  📱 ${CYAN}WPPConnect${NC} - API WhatsApp que funciona"
echo -e "  💰 ${GREEN}MercadoPago SDK v2.x${NC} - Integrado completo"
echo -e "  🔐 ${YELLOW}Sistema HWID${NC} - Autenticación por dispositivo"
echo -e "  📝 ${PURPLE}Registro de HWID${NC} - Cliente envía nombre + HWID"
echo -e "  🎛️  ${BLUE}Panel completo${NC} - Control total del sistema"
echo -e "  📊 ${GREEN}Estadísticas${NC} - Ventas, usuarios, HWIDs"
echo -e "  ⚡ ${CYAN}Auto-verificación${NC} - Pagos verificados cada 2 min"
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
    read -p "📝 Ingresa la IP del servidor: " SERVER_IP
fi

echo -e "${GREEN}✅ IP: ${CYAN}$SERVER_IP${NC}\n"

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

# Node.js 18.x (compatible con WPPConnect y MercadoPago)
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs gcc g++ make

# Chrome/Chromium
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update -y
apt-get install -y google-chrome-stable

# Dependencias del sistema
apt-get install -y \
    git curl wget sqlite3 jq \
    build-essential libcairo2-dev \
    libpango1.0-dev libjpeg-dev \
    libgif-dev librsvg2-dev \
    python3 python3-pip ffmpeg \
    unzip cron ufw

# Configurar firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8001/tcp
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

INSTALL_DIR="/opt/sshbot-pro"
USER_HOME="/root/sshbot-pro"
DB_FILE="$INSTALL_DIR/data/users.db"
CONFIG_FILE="$INSTALL_DIR/config/config.json"

# Limpiar anterior
pm2 delete sshbot-pro 2>/dev/null || true
rm -rf "$INSTALL_DIR" "$USER_HOME" 2>/dev/null || true
rm -rf /root/.wppconnect 2>/dev/null || true

# Crear directorios
mkdir -p "$INSTALL_DIR"/{data,config,sessions,logs,qr_codes,hwid}
mkdir -p "$USER_HOME"
mkdir -p /root/.wppconnect
chmod -R 755 "$INSTALL_DIR"
chmod -R 700 /root/.wppconnect

cat > "$CONFIG_FILE" << EOF
{
    "bot": {
        "name": "SSH Bot Pro HWID",
        "version": "2.0-HWID-INTEGRADO",
        "server_ip": "$SERVER_IP",
        "default_password": "mgvpn247"
    },
    "prices": {
        "test_hours": 1,
        "price_7d": 3000.00,
        "price_15d": 4000.00,
        "price_30d": 7000.00,
        "price_50d": 9700.00,
        "currency": "ARS"
    },
    "mercadopago": {
        "access_token": "",
        "enabled": false,
        "public_key": ""
    },
    "links": {
        "app_download": "https://www.mediafire.com/file/p8kgthxbsid7xws/MAJ/DNI_AND_FIL",
        "support": "https://wa.me/543435071016",
        "hwid_instructions": "https://example.com/como-obtener-hwid"
    },
    "paths": {
        "database": "$DB_FILE",
        "qr_codes": "$INSTALL_DIR/qr_codes",
        "sessions": "/root/.wppconnect",
        "hwid_dir": "$INSTALL_DIR/hwid"
    }
}
EOF

# Crear base de datos COMPLETA con HWID
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
CREATE INDEX idx_users_hwid ON users(hwid);
CREATE INDEX idx_payments_hwid ON payments(hwid);
CREATE INDEX idx_hwid_reg_phone ON hwid_registrations(phone);
CREATE INDEX idx_hwid_reg_status ON hwid_registrations(status);
SQL

echo -e "${GREEN}✅ Estructura creada con sistema HWID${NC}"

# ================================================
# CREAR BOT COMPLETO CON MERCADOPAGO + HWID
# ================================================
echo -e "\n${CYAN}🤖 Creando bot con WPPConnect + MercadoPago + HWID...${NC}"

cd "$USER_HOME"

# package.json con todas las dependencias
cat > package.json << 'PKGEOF'
{
    "name": "sshbot-pro",
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

# Crear bot.js COMPLETO con MercadoPago + HWID
echo -e "${YELLOW}📝 Creando bot.js con sistema HWID...${NC}"

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
console.log(chalk.cyan.bold('║                🤖 SSH BOT PRO - HWID SYSTEM                  ║'));
console.log(chalk.cyan.bold('╚══════════════════════════════════════════════════════════════╝\n'));

// Cargar configuración
function loadConfig() {
    delete require.cache[require.resolve('/opt/sshbot-pro/config/config.json')];
    return require('/opt/sshbot-pro/config/config.json');
}

let config = loadConfig();
const db = new sqlite3.Database('/opt/sshbot-pro/data/users.db');

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
    // Limpiar y normalizar HWID
    return hwid.trim().toUpperCase().replace(/[^A-Z0-9\-]/g, '');
}

function validateHWID(hwid) {
    // Validar formato básico de HWID
    const normalized = normalizeHWID(hwid);
    return normalized.length >= 10 && normalized.length <= 64;
}

function hashHWID(hwid) {
    // Crear hash del HWID para almacenamiento seguro
    return crypto.createHash('sha256').update(hwid).digest('hex');
}

async function checkHWIDAvailable(hwid) {
    // Verificar si el HWID ya está registrado
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
    // Registrar solicitud de HWID
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

async function createSSHUser(phone, username, days, hwid = null, deviceName = null) {
    const password = DEFAULT_PASSWORD;
    
    if (days === 0) {
        // Test - 1 hora
        const expireFull = moment().add(config.prices.test_hours, 'hours').format('YYYY-MM-DD HH:mm:ss');
        
        try {
            await execPromise(`useradd -m -s /bin/bash ${username} && echo "${username}:${password}" | chpasswd`);
            
            const hashedHwid = hwid ? hashHWID(hwid) : null;
            db.run(`INSERT INTO users (phone, username, password, tipo, expires_at, hwid, device_name) VALUES (?, ?, ?, 'test', ?, ?, ?)`,
                [phone, username, password, expireFull, hashedHwid, deviceName]);
            
            return { success: true, username, password, expires: expireFull, hwid: hashedHwid };
        } catch (error) {
            console.error(chalk.red('❌ Error:'), error.message);
            return { success: false, error: error.message };
        }
    } else {
        // Premium
        const expireFull = moment().add(days, 'days').format('YYYY-MM-DD 23:59:59');
        
        try {
            await execPromise(`useradd -M -s /bin/false -e ${moment().add(days, 'days').format('YYYY-MM-DD')} ${username} && echo "${username}:${password}" | chpasswd`);
            
            const hashedHwid = hwid ? hashHWID(hwid) : null;
            db.run(`INSERT INTO users (phone, username, password, tipo, expires_at, hwid, device_name) VALUES (?, ?, ?, 'premium', ?, ?, ?)`,
                [phone, username, password, expireFull, hashedHwid, deviceName]);
            
            return { success: true, username, password, expires: expireFull, hwid: hashedHwid };
        } catch (error) {
            console.error(chalk.red('❌ Error:'), error.message);
            return { success: false, error: error.message };
        }
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

// ✅ MERCADOPAGO - CREAR PAGO CON HWID
async function createMercadoPagoPayment(phone, days, amount, planName, hwid = null, deviceName = null) {
    try {
        if (!mpEnabled || !mpPreference) {
            console.log(chalk.red('❌ MercadoPago no inicializado'));
            return { success: false, error: 'MercadoPago no configurado' };
        }
        
        const phoneClean = phone.replace('@c.us', '');
        const paymentId = `SSH-${phoneClean}-${days}d-${Date.now()}`;
        
        console.log(chalk.cyan(`🔄 Creando pago MP con HWID: ${paymentId}`));
        
        const expirationDate = moment().add(24, 'hours');
        const isoDate = expirationDate.toISOString();
        
        const preferenceData = {
            items: [{
                title: `SSH PREMIUM ${days} DÍAS - HWID`,
                description: `Acceso SSH Premium por ${days} días - 1 dispositivo`,
                quantity: 1,
                currency_id: config.prices.currency || 'ARS',
                unit_price: parseFloat(amount)
            }],
            external_reference: paymentId,
            expires: true,
            expiration_date_from: moment().toISOString(),
            expiration_date_to: isoDate,
            back_urls: {
                success: `https://wa.me/${phoneClean}?text=Ya%20pague%20mgvpn`,
                failure: `https://wa.me/${phoneClean}?text=Pago%20fallido%20SSH`,
                pending: `https://wa.me/${phoneClean}?text=Pago%20pendiente%20SSH`
            },
            auto_return: 'approved',
            statement_descriptor: 'SSH PREMIUM HWID'
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

// ✅ VERIFICAR PAGOS PENDIENTES CON HWID
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
                        
                        // Crear usuario SSH con HWID
                        const username = generatePremiumUsername();
                        const result = await createSSHUser(payment.phone, username, payment.days, payment.hwid, payment.device_name);
                        
                        if (result.success) {
                            db.run(`UPDATE payments SET status = 'approved', approved_at = CURRENT_TIMESTAMP WHERE payment_id = ?`, [payment.payment_id]);
                            
                            const expireDate = moment().add(payment.days, 'days').format('DD/MM/YYYY');
                            
                            let message = `✅ PAGO CONFIRMADO

🎉 Tu compra ha sido aprobada

📋 DATOS DE ACCESO:
👤 Usuario: ${username}
🔑 Contraseña: ${DEFAULT_PASSWORD}`;

                            if (payment.device_name) {
                                message += `\n📱 Dispositivo: ${payment.device_name}`;
                            }
                            
                            message += `

⏰ VÁLIDO HASTA: ${expireDate}
🔌 DISPOSITIVO: 1 (registrado por HWID)

📱 INSTALACIÓN:
1. Descarga la app (Opción 4)
2. Seleccionar servidor
3. ¡Conéctate automáticamente!

🎊 ¡Disfruta del servicio premium!`;
                            
                            if (client) {
                                await client.sendText(payment.phone, message);
                            }
                            console.log(chalk.green(`✅ Usuario creado: ${username} con HWID`));
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
        console.log(chalk.yellow('🚀 Inicializando WPPConnect con HWID...'));
        
        client = await wppconnect.create({
            session: 'sshbot-pro-session',
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
                    
                    await client.sendText(from, `🔐 BOT SSH CON SISTEMA HWID 🚀

Elija una opción:

🧾 1 - REGISTRAR HWID Y PRUEBA
💰 2 - COMPRAR USUARIO CON HWID
🔄 3 - RENOVAR USUARIO HWID
📱 4 - DESCARGAR APLICACIÓN
🔍 5 - VER MI HWID REGISTRADO`);
                }
                
                // OPCIÓN 1: REGISTRAR HWID Y PRUEBA
                else if (text === '1' && userState.state === 'main_menu') {
                    await setUserState(from, 'registering_hwid');
                    
                    await client.sendText(from, `📝 REGISTRO DE HWID

Para crear una cuenta (prueba o premium) necesitas registrar tu HWID.

📋 *¿Qué es el HWID?*
Es un identificador único de tu dispositivo. La app MG VPN lo genera automáticamente.

📱 *¿Cómo obtenerlo?*
1. Instala la app MG VPN (Opción 4)
2. Abre la app y ve a la sección "Mi ID" o "HWID"
3. Copia el código que aparece

📤 *Formato para enviar:*
NombreDispositivo + HWID

*Ejemplo:*
MiCelular ABC123-DEF456-GHI789

Envía tu nombre de dispositivo y HWID ahora.`);
                }
                
                // REGISTRANDO HWID
                else if (userState.state === 'registering_hwid') {
                    // Esperar nombre + HWID
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
✅ *sí* - Para crear prueba
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
                
                // CONFIRMAR CREACIÓN DE PRUEBA DESPUÉS DE HWID
                else if (userState.state === 'hwid_registered' && ['si', 'sí', 'yes', 'ok'].includes(text)) {
                    const stateData = userState.data;
                    
                    await client.sendText(from, '⏳ Creando cuenta de prueba con tu HWID...');
                    
                    try {
                        const username = generateUsername();
                        const result = await createSSHUser(from, username, 0, stateData.hwid, stateData.deviceName);
                        
                        if (result.success) {
                            registerTest(from);
                            
                            await client.sendText(from, `✅️ PRUEBA CREADA CON HWID !

📱 Dispositivo: ${stateData.deviceName}
🔐 HWID: ${stateData.hwid.substring(0, 20)}...
👤 Usuario: ${username}
🔑 Contraseña: ${DEFAULT_PASSWORD}
🔌 Limite: 1 dispositivo (HWID bloqueado)
⌛️ Expira en: ${config.prices.test_hours} hora(s)

📱APP: ${config.links.app_download}

⚠️ *IMPORTANTE:* Solo funciona en el dispositivo registrado.`);
                            
                            console.log(chalk.green(`✅ Test creado con HWID: ${username}`));
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
                
                // OPCIÓN 2: 💰 COMPRAR USUARIO SSH CON HWID
                else if (text === '2' && userState.state === 'main_menu') {
                    // Verificar si tiene HWID registrado
                    db.get('SELECT hwid, device_name FROM hwid_registrations WHERE phone = ? AND status = "pending"', [from], async (err, row) => {
                        if (err || !row || !row.hwid) {
                            await client.sendText(from, `❌ NECESITAS REGISTRAR HWID

Para comprar un plan premium, primero debes registrar tu HWID.

Usa la opción *1* para registrar tu HWID.

📋 *Instrucciones:*
1. Instala la app (Opción 4)
2. Copia tu HWID de la app
3. Regístralo con la opción 1
4. Luego puedes comprar`);
                        } else {
                            await setUserState(from, 'buying_ssh_hwid', {
                                hwid: row.hwid,
                                deviceName: row.device_name
                            });
                            
                            await client.sendText(from, `🔐 COMPRA CON HWID REGISTRADO

📱 Dispositivo: ${row.device_name}
🔐 HWID: ${row.hwid.substring(0, 20)}...

🌐 *PLANES SSH PREMIUM*

Elija una opción:
🗓 1 - PLANES DIARIOS
🗓 2 - PLANES MENSUALES
⬅️ 0 - VOLVER`);
                        }
                    });
                }
                
                // SUBMENÚ DE COMPRAS CON HWID
                else if (userState.state === 'buying_ssh_hwid') {
                    if (text === '1') {
                        // 🌐 PLANES DIARIOS
                        await setUserState(from, 'selecting_daily_plan_hwid');
                        
                        await client.sendText(from, `🌐 PLANES DIARIOS HWID

Elija un plan:
🗓 1 - 7 DIAS - $${config.prices.price_7d}

🗓 2 - 15 DIAS - $${config.prices.price_15d}

⬅️ 0 - VOLVER`);
                    }
                    else if (text === '2') {
                        // 🌐 PLANES MENSUALES
                        await setUserState(from, 'selecting_monthly_plan_hwid');
                        
                        await client.sendText(from, `🌐 PLANES MENSUALES HWID

Elija un plan:
🗓 1 - 30 DIAS - $${config.prices.price_30d}

🗓 2 - 50 DIAS - $${config.prices.price_50d}

⬅️ 0 - VOLVER`);
                    }
                    else if (text === '0') {
                        await setUserState(from, 'main_menu');
                        await client.sendText(from, `🔐 BOT SSH CON SISTEMA HWID 🚀

Elija una opción:

🧾 1 - REGISTRAR HWID Y PRUEBA
💰 2 - COMPRAR USUARIO CON HWID
🔄 3 - RENOVAR USUARIO HWID
📱 4 - DESCARGAR APLICACIÓN
🔍 5 - VER MI HWID REGISTRADO`);
                    }
                }
                
                // SELECCIÓN DE PLAN DIARIO CON HWID
                else if (userState.state === 'selecting_daily_plan_hwid') {
                    if (['1', '2'].includes(text)) {
                        const planMap = {
                            '1': { days: 7, price: config.prices.price_7d, name: '7 DÍAS' },
                            '2': { days: 15, price: config.prices.price_15d, name: '15 DÍAS' }
                        };
                        
                        const plan = planMap[text];
                        const stateData = userState.data;
                        
                        if (mpEnabled) {
                            // CON MERCADOPAGO - PROCESAR PAGO DIRECTAMENTE
                            await client.sendText(from, '⏳ Procesando tu compra con HWID...');
                            
                            const payment = await createMercadoPagoPayment(
                                from, 
                                plan.days, 
                                plan.price, 
                                plan.name,
                                stateData.hwid,
                                stateData.deviceName
                            );
                            
                            if (payment.success) {
                                const message = `🔐 USUARIO SSH + HWID

- 📱 Dispositivo: ${stateData.deviceName}
- 🌐 Plan: ${plan.name}
- 💰 Precio: $${payment.amount}
- 🔌 Dispositivo: 1 (HWID bloqueado)
- 🕜 Duración: ${plan.days} días

📎 LINK DE PAGO

${payment.paymentUrl}

⏰ Este enlace expira en 24 horas
💳 Pago seguro con MercadoPago
🔐 Solo funciona en el dispositivo registrado`;
                                
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
                            // SIN MERCADOPAGO
                            await client.sendText(from, `🔐 PLAN SELECCIONADO: ${plan.name}

📱 Dispositivo: ${stateData.deviceName}
🔐 HWID: ${stateData.hwid.substring(0, 20)}...
💰 Precio: $${plan.price} ARS
🕜 Duración: ${plan.days} días
🔌 Solo funciona en este dispositivo

Para continuar con la compra, contacta al administrador:
${config.links.support}

O envía el monto por transferencia bancaria.`);
                            
                            await setUserState(from, 'main_menu');
                        }
                    }
                    else if (text === '0') {
                        await setUserState(from, 'buying_ssh_hwid');
                        await client.sendText(from, `🌐 PLANES HWID

Elija una opción:
🗓 1 - PLANES DIARIOS
🗓 2 - PLANES MENSUALES
⬅️ 0 - VOLVER`);
                    }
                }
                
                // SELECCIÓN DE PLAN MENSUAL CON HWID
                else if (userState.state === 'selecting_monthly_plan_hwid') {
                    if (['1', '2'].includes(text)) {
                        const planMap = {
                            '1': { days: 30, price: config.prices.price_30d, name: '30 DÍAS' },
                            '2': { days: 50, price: config.prices.price_50d, name: '50 DÍAS' }
                        };
                        
                        const plan = planMap[text];
                        const stateData = userState.data;
                        
                        if (mpEnabled) {
                            // CON MERCADOPAGO - PROCESAR PAGO DIRECTAMENTE
                            await client.sendText(from, '⏳ Procesando tu compra con HWID...');
                            
                            const payment = await createMercadoPagoPayment(
                                from, 
                                plan.days, 
                                plan.price, 
                                plan.name,
                                stateData.hwid,
                                stateData.deviceName
                            );
                            
                            if (payment.success) {
                                const message = `🔐 USUARIO SSH + HWID

- 📱 Dispositivo: ${stateData.deviceName}
- 🌐 Plan: ${plan.name}
- 💰 Precio: $${payment.amount}
- 🔌 Dispositivo: 1 (HWID bloqueado)
- 🕜 Duración: ${plan.days} días

📎 LINK DE PAGO

${payment.paymentUrl}

⏰ Este enlace expira en 24 horas
💳 Pago seguro con MercadoPago
🔐 Solo funciona en el dispositivo registrado`;
                                
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
                            // SIN MERCADOPAGO
                            await client.sendText(from, `🔐 PLAN SELECCIONADO: ${plan.name}

📱 Dispositivo: ${stateData.deviceName}
🔐 HWID: ${stateData.hwid.substring(0, 20)}...
💰 Precio: $${plan.price} ARS
🕜 Duración: ${plan.days} días
🔌 Solo funciona en este dispositivo

Para continuar con la compra, contacta al administrador:
${config.links.support}

O envía el monto por transferencia bancaria.`);
                            
                            await setUserState(from, 'main_menu');
                        }
                    }
                    else if (text === '0') {
                        await setUserState(from, 'buying_ssh_hwid');
                        await client.sendText(from, `🌐 PLANES SSH PREMIUM + HWID

Elija una opción:
🗓 1 - PLANES DIARIOS
🗓 2 - PLANES MENSUALES
⬅️ 0 - VOLVER`);
                    }
                }
                
                // OPCIÓN 3: RENOVAR
                else if (text === '3' && userState.state === 'main_menu') {
                    await client.sendText(from, `🔄 RENOVAR USUARIO SSH + HWID

Para renovar tu cuenta SSH existente (con HWID), contacta al administrador:
${config.links.support}

Indica tu nombre de usuario actual y si deseas cambiar de dispositivo.`);
                }
                
                // OPCIÓN 4: DESCARGAR APP
                else if (text === '4' && userState.state === 'main_menu') {
                    await client.sendText(from, `📱 DESCARGAR APLICACIÓN MG VPN

🔗 Enlace de descarga:
${config.links.app_download}

💡 *Instrucciones para HWID:*
1. Descarga e instala la app
2. Abre la aplicación
3. Ve a *Configuración* → *Mi ID/HWID*
4. Copia el código que aparece
5. Regístralo con la opción *1* del bot

🔐 *La app mostrará tu HWID único*
Este código identifica tu dispositivo para el sistema SSH

⚠️ *IMPORTANTE:* Cada HWID solo permite una cuenta activa.`);
                }
                
                // OPCIÓN 5: VER MI HWID REGISTRADO
                else if (text === '5' && userState.state === 'main_menu') {
                    db.get('SELECT hwid, device_name, status FROM hwid_registrations WHERE phone = ? ORDER BY created_at DESC LIMIT 1', [from], async (err, row) => {
                        if (err || !row) {
                            await client.sendText(from, `❌ NO TIENES HWID REGISTRADO

Usa la opción *1* para registrar tu HWID primero.

📱 Instala la app (Opción 4)
📋 Copia tu HWID de la app
📤 Regístralo con la opción 1`);
                        } else {
                            await client.sendText(from, `📋 TU HWID REGISTRADO

📱 Dispositivo: ${row.device_name}
🔐 HWID: ${row.hwid.substring(0, 20)}...
📊 Estado: ${row.status === 'pending' ? '🟡 Pendiente' : '🟢 Activo'}

Usa este HWID para:
• Crear cuenta de prueba
• Comprar planes premium
• Identificar tu dispositivo

⚠️ Si cambias de dispositivo, debes registrar el nuevo HWID.`);
                        }
                    });
                }
                
            } catch (error) {
                console.error(chalk.red('❌ Error procesando mensaje:'), error.message);
            }
        });
        
        // ✅ VERIFICAR PAGOS CADA 2 MINUTOS
        cron.schedule('*/2 * * * *', () => {
            console.log(chalk.yellow('🔄 Verificando pagos pendientes con HWID...'));
            checkPendingPayments();
        });
        
        // ✅ LIMPIEZA CADA 15 MINUTOS
        cron.schedule('*/15 * * * *', async () => {
            const now = moment().format('YYYY-MM-DD HH:mm:ss');
            console.log(chalk.yellow(`🧹 Limpiando usuarios expirados...`));
            
            db.all('SELECT username, hwid FROM users WHERE expires_at < ? AND status = 1', [now], async (err, rows) => {
                if (err || !rows || rows.length === 0) return;
                
                for (const r of rows) {
                    try {
                        await execPromise(`pkill -u ${r.username} 2>/dev/null || true`);
                        await execPromise(`userdel -f ${r.username} 2>/dev/null || true`);
                        db.run('UPDATE users SET status = 0 WHERE username = ?', [r.username]);
                        
                        // Liberar HWID si ya no está en uso
                        if (r.hwid) {
                            db.run(`DELETE FROM hwid_registrations WHERE hwid = ? AND status = 'pending'`, [r.hwid]);
                        }
                        
                        console.log(chalk.green(`🗑️ Eliminado: ${r.username} - HWID liberado`));
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
            console.log(chalk.yellow('🧹 HWID pendientes antiguos limpiados'));
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

echo -e "${GREEN}✅ Bot creado con sistema HWID${NC}"

# ================================================
# CREAR PANEL DE CONTROL COMPLETO CON HWID
# ================================================
echo -e "\n${CYAN}🎛️  Creando panel de control completo con HWID...${NC}"

cat > /usr/local/bin/sshbot << 'PANELEOF'
#!/bin/bash
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; BLUE='\033[0;34m'; PURPLE='\033[0;35m'; NC='\033[0m'

DB="/opt/sshbot-pro/data/users.db"
CONFIG="/opt/sshbot-pro/config/config.json"

get_val() { jq -r "$1" "$CONFIG" 2>/dev/null; }
set_val() { local t=$(mktemp); jq "$1 = $2" "$CONFIG" > "$t" && mv "$t" "$CONFIG"; }

show_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                🎛️  PANEL SSH BOT PRO - HWID                ║${NC}"
    echo -e "${CYAN}║               🔐 SISTEMA DE AUTENTICACIÓN HWID             ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}\n"
}

test_mercadopago() {
    local TOKEN="$1"
    echo -e "${YELLOW}🔄 Probando conexión con MercadoPago...${NC}"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        "https://api.mercadopago.com/v1/payment_methods" \
        2>/dev/null)
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [[ "$HTTP_CODE" == "200" ]]; then
        echo -e "${GREEN}✅ CONEXIÓN EXITOSA${NC}"
        echo -e "${CYAN}Métodos disponibles:${NC}"
        echo "$BODY" | jq -r '.[].name' 2>/dev/null | head -3
        return 0
    else
        echo -e "${RED}❌ ERROR - Código: $HTTP_CODE${NC}"
        return 1
    fi
}

while true; do
    show_header
    
    TOTAL_USERS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM users" 2>/dev/null || echo "0")
    ACTIVE_USERS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM users WHERE status=1" 2>/dev/null || echo "0")
    TOTAL_HWID=$(sqlite3 "$DB" "SELECT COUNT(DISTINCT hwid) FROM users WHERE hwid IS NOT NULL" 2>/dev/null || echo "0")
    PENDING_HWID=$(sqlite3 "$DB" "SELECT COUNT(*) FROM hwid_registrations WHERE status='pending'" 2>/dev/null || echo "0")
    PENDING_PAYMENTS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM payments WHERE status='pending'" 2>/dev/null || echo "0")
    APPROVED_PAYMENTS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM payments WHERE status='approved'" 2>/dev/null || echo "0")
    
    STATUS=$(pm2 jlist 2>/dev/null | jq -r '.[] | select(.name=="sshbot-pro") | .pm2_env.status' 2>/dev/null || echo "stopped")
    if [[ "$STATUS" == "online" ]]; then
        BOT_STATUS="${GREEN}● ACTIVO${NC}"
    else
        BOT_STATUS="${RED}● DETENIDO${NC}"
    fi
    
    MP_TOKEN=$(get_val '.mercadopago.access_token')
    if [[ -n "$MP_TOKEN" && "$MP_TOKEN" != "" && "$MP_TOKEN" != "null" ]]; then
        MP_STATUS="${GREEN}✅ CONFIGURADO${NC}"
    else
        MP_STATUS="${RED}❌ NO CONFIGURADO${NC}"
    fi
    
    echo -e "${YELLOW}📊 ESTADO DEL SISTEMA HWID${NC}"
    echo -e "  Bot: $BOT_STATUS"
    echo -e "  Usuarios: ${CYAN}$ACTIVE_USERS/$TOTAL_USERS${NC} activos/total"
    echo -e "  HWID: ${CYAN}$TOTAL_HWID${NC} únicos | ${YELLOW}$PENDING_HWID${NC} pendientes"
    echo -e "  Pagos: ${CYAN}$PENDING_PAYMENTS${NC} pendientes | ${GREEN}$APPROVED_PAYMENTS${NC} aprobados"
    echo -e "  MercadoPago: $MP_STATUS"
    echo -e "  IP: $(get_val '.bot.server_ip')"
    echo -e "  Contraseña: ${GREEN}mgvpn247${NC} (FIJA)"
    echo -e ""
    
    echo -e "${YELLOW}💰 PRECIOS ACTUALES:${NC}"
    echo -e "  ${CYAN}DIARIOS:${NC}"
    echo -e "    7 días: $ $(get_val '.prices.price_7d') ARS"
    echo -e "    15 días: $ $(get_val '.prices.price_15d') ARS"
    echo -e "  ${CYAN}MENSUALES:${NC}"
    echo -e "    30 días: $ $(get_val '.prices.price_30d') ARS"
    echo -e "    50 días: $ $(get_val '.prices.price_50d') ARS"
    echo -e ""
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}[1]${NC} 🚀  Iniciar/Reiniciar bot"
    echo -e "${CYAN}[2]${NC} 🛑  Detener bot"
    echo -e "${CYAN}[3]${NC} 📱  Ver logs y QR"
    echo -e "${CYAN}[4]${NC} 👤  Crear usuario manual con HWID"
    echo -e "${CYAN}[5]${NC} 👥  Listar usuarios y HWID"
    echo -e "${CYAN}[6]${NC} 🔍  Ver HWID registrados"
    echo -e "${CYAN}[7]${NC} 💰  Cambiar precios"
    echo -e "${CYAN}[8]${NC} 🔑  Configurar MercadoPago"
    echo -e "${CYAN}[9]${NC} 🧪  Test MercadoPago"
    echo -e "${CYAN}[10]${NC} 📊 Ver estadísticas HWID"
    echo -e "${CYAN}[11]${NC} 🔄 Limpiar sesión"
    echo -e "${CYAN}[12]${NC} 💳 Ver pagos con HWID"
    echo -e "${CYAN}[13]${NC} ⚙️  Ver configuración HWID"
    echo -e "${CYAN}[14]${NC} 🗑️  Limpiar HWID antiguos"
    echo -e "${CYAN}[15]${NC} 🔓 Liberar HWID específico"
    echo -e "${CYAN}[0]${NC} 🚪  Salir"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e ""
    
    read -p "👉 Selecciona: " OPTION
    
    case $OPTION in
        1)
            echo -e "\n${YELLOW}🔄 Reiniciando...${NC}"
            cd /root/sshbot-pro
            pm2 restart sshbot-pro 2>/dev/null || pm2 start bot.js --name sshbot-pro
            pm2 save
            echo -e "${GREEN}✅ Bot reiniciado${NC}"
            sleep 2
            ;;
        2)
            echo -e "\n${YELLOW}🛑 Deteniendo...${NC}"
            pm2 stop sshbot-pro
            echo -e "${GREEN}✅ Bot detenido${NC}"
            sleep 2
            ;;
        3)
            echo -e "\n${YELLOW}📱 Mostrando logs...${NC}"
            pm2 logs sshbot-pro --lines 100
            ;;
        4)
            clear
            echo -e "${CYAN}👤 CREAR USUARIO CON HWID${NC}\n"
            
            read -p "Teléfono (ej: 5491122334455): " PHONE
            read -p "Nombre del dispositivo: " DEVICE
            read -p "HWID (sin espacios): " HWID
            read -p "Usuario (minúsculas, auto=generar): " USERNAME
            read -p "Tipo (test/premium): " TIPO
            read -p "Días (0=test 1h, 7,15,30,50=premium): " DAYS
            
            [[ -z "$DAYS" ]] && DAYS="30"
            if [[ "$USERNAME" == "auto" || -z "$USERNAME" ]]; then
                if [[ "$TIPO" == "test" ]]; then
                    USERNAME="test$(shuf -i 1000-9999 -n 1)"
                else
                    USERNAME="user$(shuf -i 1000-9999 -n 1)"
                fi
            fi
            
            # Asegurar minúsculas
            USERNAME=$(echo "$USERNAME" | tr '[:upper:]' '[:lower:]')
            PASSWORD="mgvpn247"
            
            # Hashear HWID
            HWID_HASH=$(echo -n "$HWID" | sha256sum | awk '{print $1}')
            
            if [[ "$TIPO" == "test" ]]; then
                DAYS="0"
                EXPIRE_DATE=$(date -d "+1 hour" +"%Y-%m-%d %H:%M:%S")
                useradd -M -s /bin/false "$USERNAME" && echo "$USERNAME:$PASSWORD" | chpasswd
            else
                EXPIRE_DATE=$(date -d "+$DAYS days" +"%Y-%m-%d 23:59:59")
                useradd -M -s /bin/false -e "$(date -d "+$DAYS days" +%Y-%m-%d)" "$USERNAME" && echo "$USERNAME:$PASSWORD" | chpasswd
            fi
            
            if [[ $? -eq 0 ]]; then
                sqlite3 "$DB" "INSERT INTO users (phone, username, password, tipo, expires_at, hwid, device_name, status) VALUES ('$PHONE', '$USERNAME', '$PASSWORD', '$TIPO', '$EXPIRE_DATE', '$HWID_HASH', '$DEVICE', 1)"
                sqlite3 "$DB" "INSERT OR REPLACE INTO hwid_registrations (phone, hwid, device_name, status) VALUES ('$PHONE', '$HWID_HASH', '$DEVICE', 'approved')"
                echo -e "\n${GREEN}✅ USUARIO CREADO CON HWID${NC}"
                echo -e "📱 Teléfono: ${PHONE}"
                echo -e "📱 Dispositivo: ${DEVICE}"
                echo -e "🔐 HWID: ${HWID}"
                echo -e "🔐 HWID Hash: ${HWID_HASH}"
                echo -e "👤 Usuario: ${USERNAME}"
                echo -e "🔑 Contraseña: ${PASSWORD}"
                echo -e "⏰ Expira: ${EXPIRE_DATE}"
                echo -e "🔌 Días: ${DAYS}"
            else
                echo -e "\n${RED}❌ Error${NC}"
            fi
            read -p "Presiona Enter..."
            ;;
        5)
            clear
            echo -e "${CYAN}👥 USUARIOS ACTIVOS CON HWID${NC}\n"
            
            echo -e "${YELLOW}Usuarios premium:${NC}"
            sqlite3 -column -header "$DB" "SELECT username, device_name, SUBSTR(hwid, 1, 10) as 'HWID (10)', expires_at FROM users WHERE status = 1 AND tipo = 'premium' ORDER BY expires_at DESC LIMIT 20"
            
            echo -e "\n${YELLOW}Usuarios test:${NC}"
            sqlite3 -column -header "$DB" "SELECT username, device_name, SUBSTR(hwid, 1, 10) as 'HWID (10)', expires_at FROM users WHERE status = 1 AND tipo = 'test' ORDER BY expires_at DESC LIMIT 10"
            
            echo -e "\n${YELLOW}Total: ${ACTIVE_USERS} activos${NC}"
            read -p "Presiona Enter..."
            ;;
        6)
            clear
            echo -e "${CYAN}🔍 HWID REGISTRADOS${NC}\n"
            
            echo -e "${YELLOW}Pendientes de aprobación:${NC}"
            sqlite3 -column -header "$DB" "SELECT phone, device_name, SUBSTR(hwid, 1, 20) as 'HWID (20)', created_at FROM hwid_registrations WHERE status='pending' ORDER BY created_at DESC LIMIT 15"
            
            echo -e "\n${YELLOW}Aprobados y en uso:${NC}"
            sqlite3 -column -header "$DB" "SELECT u.phone, u.device_name, SUBSTR(u.hwid, 1, 20) as 'HWID (20)', u.expires_at FROM users u WHERE u.status=1 AND u.hwid IS NOT NULL ORDER BY u.expires_at DESC LIMIT 15"
            
            echo -e "\n${YELLOW}Total únicos: ${TOTAL_HWID} | Pendientes: ${PENDING_HWID}${NC}"
            read -p "Presiona Enter..."
            ;;
        7)
            clear
            echo -e "${CYAN}💰 CAMBIAR PRECIOS${NC}\n"
            
            CURRENT_7D=$(get_val '.prices.price_7d')
            CURRENT_15D=$(get_val '.prices.price_15d')
            CURRENT_30D=$(get_val '.prices.price_30d')
            CURRENT_50D=$(get_val '.prices.price_50d')
            
            echo -e "${YELLOW}Precios actuales:${NC}"
            echo -e "  ${CYAN}DIARIOS:${NC}"
            echo -e "  1. 7 días: $${CURRENT_7D} ARS"
            echo -e "  2. 15 días: $${CURRENT_15D} ARS"
            echo -e "  ${CYAN}MENSUALES:${NC}"
            echo -e "  3. 30 días: $${CURRENT_30D} ARS"
            echo -e "  4. 50 días: $${CURRENT_50D} ARS\n"
            
            echo -e "${CYAN}Modificar precios:${NC}"
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
        8)
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
                    cd /root/sshbot-pro && pm2 restart sshbot-pro
                    sleep 2
                    echo -e "${GREEN}✅ MercadoPago activado${NC}"
                else
                    echo -e "${RED}❌ Token inválido${NC}"
                    echo -e "${YELLOW}Debe empezar con APP_USR- o TEST-${NC}"
                fi
            fi
            read -p "Presiona Enter..."
            ;;
        9)
            clear
            echo -e "${CYAN}🧪 TEST MERCADOPAGO${NC}\n"
            
            TOKEN=$(get_val '.mercadopago.access_token')
            if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
                echo -e "${RED}❌ Token no configurado${NC}\n"
                read -p "Presiona Enter..."
                continue
            fi
            
            echo -e "${YELLOW}🔑 Token: ${TOKEN:0:30}...${NC}\n"
            test_mercadopago "$TOKEN"
            
            read -p "\nPresiona Enter..."
            ;;
        10)
            clear
            echo -e "${CYAN}📊 ESTADÍSTICAS HWID${NC}\n"
            
            echo -e "${YELLOW}👥 USUARIOS POR TIPO:${NC}"
            sqlite3 "$DB" "SELECT 'Total: ' || COUNT(*) || ' | Test: ' || SUM(CASE WHEN tipo='test' THEN 1 ELSE 0 END) || ' | Premium: ' || SUM(CASE WHEN tipo='premium' THEN 1 ELSE 0 END) || ' | Con HWID: ' || SUM(CASE WHEN hwid IS NOT NULL THEN 1 ELSE 0 END) FROM users"
            
            echo -e "\n${YELLOW}📱 DISPOSITIVOS (HWID):${NC}"
            sqlite3 "$DB" "SELECT 'Únicos: ' || COUNT(DISTINCT hwid) || ' | Activos: ' || SUM(CASE WHEN status=1 AND hwid IS NOT NULL THEN 1 ELSE 0 END) || ' | Pendientes: ' || (SELECT COUNT(*) FROM hwid_registrations WHERE status='pending') FROM users"
            
            echo -e "\n${YELLOW}💰 PAGOS CON HWID:${NC}"
            sqlite3 "$DB" "SELECT 'Total: ' || COUNT(*) || ' | Con HWID: ' || SUM(CASE WHEN hwid IS NOT NULL THEN 1 ELSE 0 END) || ' | Ingresos: $' || printf('%.2f', SUM(CASE WHEN status='approved' THEN amount ELSE 0 END)) FROM payments"
            
            echo -e "\n${YELLOW}📅 DISTRIBUCIÓN POR PLAN:${NC}"
            sqlite3 "$DB" "SELECT '7 días: ' || SUM(CASE WHEN plan='7d' THEN 1 ELSE 0 END) || ' | 15 días: ' || SUM(CASE WHEN plan='15d' THEN 1 ELSE 0 END) || ' | 30 días: ' || SUM(CASE WHEN plan='30d' THEN 1 ELSE 0 END) || ' | 50 días: ' || SUM(CASE WHEN plan='50d' THEN 1 ELSE 0 END) FROM payments WHERE status='approved'"
            
            echo -e "\n${YELLOW}💸 INGRESOS HOY:${NC}"
            sqlite3 "$DB" "SELECT 'Hoy: $' || printf('%.2f', SUM(CASE WHEN date(created_at) = date('now') THEN amount ELSE 0 END)) FROM payments WHERE status='approved'"
            
            read -p "\nPresiona Enter..."
            ;;
        11)
            echo -e "\n${YELLOW}🧹 Limpiando sesión...${NC}"
            pm2 stop sshbot-pro
            rm -rf /root/.wppconnect/*
            echo -e "${GREEN}✅ Sesión limpiada${NC}"
            echo -e "${YELLOW}📱 Escanea nuevo QR al iniciar${NC}"
            sleep 2
            ;;
        12)
            clear
            echo -e "${CYAN}💳 PAGOS CON HWID${NC}\n"
            
            echo -e "${YELLOW}Pagos pendientes:${NC}"
            sqlite3 -column -header "$DB" "SELECT payment_id, phone, plan, amount, SUBSTR(hwid, 1, 10) as 'HWID', created_at FROM payments WHERE status='pending' ORDER BY created_at DESC LIMIT 10"
            
            echo -e "\n${YELLOW}Pagos aprobados:${NC}"
            sqlite3 -column -header "$DB" "SELECT payment_id, phone, plan, amount, SUBSTR(hwid, 1, 10) as 'HWID', approved_at FROM payments WHERE status='approved' ORDER BY approved_at DESC LIMIT 10"
            
            read -p "\nPresiona Enter..."
            ;;
        13)
            clear
            echo -e "${CYAN}⚙️  CONFIGURACIÓN HWID${NC}\n"
            
            echo -e "${YELLOW}🤖 BOT:${NC}"
            echo -e "  IP: $(get_val '.bot.server_ip')"
            echo -e "  Versión: $(get_val '.bot.version')"
            echo -e "  Contraseña fija: mgvpn247"
            
            echo -e "\n${YELLOW}🔐 SISTEMA HWID:${NC}"
            echo -e "  Validación: SHA-256"
            echo -e "  Almacenamiento: Hash seguro"
            echo -e "  HWID por usuario: 1"
            echo -e "  Prueba: 1 hora con HWID"
            
            echo -e "\n${YELLOW}💰 PRECIOS:${NC}"
            echo -e "  ${CYAN}DIARIOS:${NC}"
            echo -e "  7d: $(get_val '.prices.price_7d') ARS"
            echo -e "  15d: $(get_val '.prices.price_15d') ARS"
            echo -e "  ${CYAN}MENSUALES:${NC}"
            echo -e "  30d: $(get_val '.prices.price_30d') ARS"
            echo -e "  50d: $(get_val '.prices.price_50d') ARS"
            echo -e "  Test: 1 hora con HWID"
            
            echo -e "\n${YELLOW}💳 MERCADOPAGO:${NC}"
            MP_TOKEN=$(get_val '.mercadopago.access_token')
            if [[ -n "$MP_TOKEN" && "$MP_TOKEN" != "null" ]]; then
                echo -e "  Estado: ${GREEN}CONFIGURADO${NC}"
            else
                echo -e "  Estado: ${RED}NO CONFIGURADO${NC}"
            fi
            
            echo -e "\n${YELLOW}⚡ AJUSTES:${NC}"
            echo -e "  Limpieza: cada 15 minutos"
            echo -e "  HWID pendientes: expiran en 7 días"
            echo -e "  Test: 1 hora exacta con HWID"
            
            read -p "\nPresiona Enter..."
            ;;
        14)
            clear
            echo -e "${CYAN}🗑️  LIMPIAR HWID ANTIGUOS${NC}\n"
            
            echo -e "${YELLOW}HWID pendientes >7 días:${NC}"
            sqlite3 "$DB" "SELECT COUNT(*) FROM hwid_registrations WHERE status = 'pending' AND created_at < datetime('now', '-7 days')"
            
            echo -e "${YELLOW}Usuarios expirados:${NC}"
            sqlite3 "$DB" "SELECT COUNT(*) FROM users WHERE status = 1 AND expires_at < datetime('now')"
            
            read -p "¿Limpiar automáticamente? (s/N): " CLEAN
            if [[ "$CLEAN" == "s" ]]; then
                echo -e "\n${YELLOW}🧹 Limpiando...${NC}"
                
                # Limpiar HWID pendientes antiguos
                sqlite3 "$DB" "DELETE FROM hwid_registrations WHERE status = 'pending' AND created_at < datetime('now', '-7 days')"
                CLEANED1=$(sqlite3 "$DB" "SELECT changes();")
                
                # Marcar usuarios expirados como inactivos
                sqlite3 "$DB" "UPDATE users SET status = 0 WHERE status = 1 AND expires_at < datetime('now')"
                CLEANED2=$(sqlite3 "$DB" "SELECT changes();")
                
                echo -e "${GREEN}✅ Limpieza completada${NC}"
                echo -e "HWID pendientes eliminados: ${CLEANED1}"
                echo -e "Usuarios expirados desactivados: ${CLEANED2}"
            fi
            
            read -p "Presiona Enter..."
            ;;
        15)
            clear
            echo -e "${CYAN}🔓 LIBERAR HWID ESPECÍFICO${NC}\n"
            
            read -p "HWID hash (completo o primeros 10 chars): " HWID_INPUT
            
            if [[ -n "$HWID_INPUT" ]]; then
                echo -e "\n${YELLOW}Buscando HWID...${NC}"
                
                if [[ ${#HWID_INPUT} -lt 10 ]]; then
                    echo -e "${RED}❌ Ingresa al menos 10 caracteres${NC}"
                else
                    # Buscar HWID
                    sqlite3 -column -header "$DB" "SELECT phone, device_name, status, expires_at FROM users WHERE hwid LIKE '%${HWID_INPUT}%' OR hwid = '${HWID_INPUT}'"
                    
                    read -p "¿Liberar este HWID? (s/N): " LIBERAR
                    if [[ "$LIBERAR" == "s" ]]; then
                        sqlite3 "$DB" "DELETE FROM hwid_registrations WHERE hwid LIKE '%${HWID_INPUT}%'"
                        sqlite3 "$DB" "UPDATE users SET hwid = NULL, device_name = NULL WHERE hwid LIKE '%${HWID_INPUT}%'"
                        echo -e "${GREEN}✅ HWID liberado${NC}"
                        echo -e "${YELLOW}⚠️  El usuario necesitará registrar nuevo HWID${NC}"
                    fi
                fi
            fi
            
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

chmod +x /usr/local/bin/sshbot
echo -e "${GREEN}✅ Panel creado con control HWID${NC}"

# ================================================
# CREAR SCRIPT PARA VERIFICAR HWID EN CONEXIÓN SSH
# ================================================
echo -e "\n${CYAN}🔐 Creando sistema de verificación HWID...${NC}"

cat > /usr/local/bin/check-hwid.sh << 'HWIDEOF'
#!/bin/bash
# Verificador de HWID para conexiones SSH
# Se ejecuta en el PAM al autenticar

USERNAME="$1"
HWID_PROVIDED="$2"

DB="/opt/sshbot-pro/data/users.db"
LOG="/var/log/hwid-auth.log"

log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG"
}

# Si no hay HWID proporcionado, permitir (para conexiones normales)
if [[ -z "$HWID_PROVIDED" ]]; then
    log_msg "INFO: Sin HWID para $USERNAME - Permitiendo"
    exit 0
fi

# Obtener HWID almacenado para el usuario
STORED_HWID=$(sqlite3 "$DB" "SELECT hwid FROM users WHERE username = '$USERNAME' AND status = 1" 2>/dev/null)

if [[ -z "$STORED_HWID" ]]; then
    log_msg "WARNING: Usuario $USERNAME sin HWID registrado"
    exit 0  # Permitir si no tiene HWID requerido
fi

# Hashear HWID proporcionado
HWID_HASH=$(echo -n "$HWID_PROVIDED" | sha256sum | awk '{print $1}')

if [[ "$HWID_HASH" == "$STORED_HWID" ]]; then
    log_msg "SUCCESS: HWID válido para $USERNAME"
    exit 0
else
    log_msg "DENIED: HWID inválido para $USERNAME (Esperado: ${STORED_HWID:0:10}..., Recibido: ${HWID_HASH:0:10}...)"
    exit 1
fi
HWIDEOF

chmod +x /usr/local/bin/check-hwid.sh

# Crear archivo de configuración PAM (opcional)
cat > /etc/pam.d/sshd-hwid << 'PAMEOF'
# PAM configuration for HWID verification
# Add to /etc/pam.d/sshd if needed
# auth required pam_exec.so quiet /usr/local/bin/check-hwid.sh $USER $HWID
PAMEOF

echo -e "${GREEN}✅ Sistema de verificación HWID creado${NC}"

# ================================================
# INICIAR BOT
# ================================================
echo -e "\n${CYAN}🚀 Iniciando bot con sistema HWID...${NC}"

cd "$USER_HOME"
pm2 start bot.js --name sshbot-pro
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
║        🔐 INSTALACIÓN COMPLETADA - SISTEMA HWID 🔐          ║
║                                                              ║
║       🤖 SSH BOT PRO - AUTENTICACIÓN POR DISPOSITIVO       ║
║       📱 WhatsApp API + REGISTRO HWID                      ║
║       💰 MercadoPago SDK v2.x COMPLETO                     ║
║       🔐 HWID por dispositivo - Seguridad mejorada         ║
║       🎛️  Panel completo con control HWID                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
FINAL
echo -e "${NC}"

echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Sistema completo instalado con HWID${NC}"
echo -e "${GREEN}✅ WhatsApp API funcionando${NC}"
echo -e "${GREEN}✅ MercadoPago SDK v2.x integrado${NC}"
echo -e "${GREEN}✅ Sistema HWID implementado${NC}"
echo -e "${GREEN}✅ Cliente envía: Nombre + HWID${NC}"
echo -e "${GREEN}✅ Autenticación por dispositivo${NC}"
echo -e "${GREEN}✅ Panel de control completo con HWID${NC}"
echo -e "${GREEN}✅ Pago automático con QR${NC}"
echo -e "${GREEN}✅ Verificación automática de pagos${NC}"
echo -e "${GREEN}✅ Estadísticas completas de HWID${NC}"
echo -e "${GREEN}✅ Planes: 7 días, 15 días, 30 días, 50 días${NC}"
echo -e "${GREEN}✅ Contraseña fija: mgvpn247${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}📋 COMANDOS PRINCIPALES:${NC}\n"
echo -e "  ${GREEN}sshbot${NC}         - Panel de control completo con HWID"
echo -e "  ${GREEN}pm2 logs sshbot-pro${NC} - Ver logs y QR"
echo -e "  ${GREEN}pm2 restart sshbot-pro${NC} - Reiniciar bot"
echo -e "\n"

echo -e "${YELLOW}🔐 FLUJO HWID DEL CLIENTE:${NC}\n"
echo -e "  1. Cliente instala app MG VPN"
echo -e "  2. App muestra HWID único del dispositivo"
echo -e "  3. Cliente envía al bot: Nombre + HWID"
echo -e "  4. Bot registra HWID y ofrece prueba/compras"
echo -e "  5. Cuenta vinculada al HWID específico"
echo -e "\n"

echo -e "${YELLOW}🚀 PRIMEROS PASOS:${NC}\n"
echo -e "  1. Ver logs: ${GREEN}pm2 logs sshbot-pro${NC}"
echo -e "  2. Escanear QR cuando aparezca"
echo -e "  3. Configurar MercadoPago en el panel: ${GREEN}sshbot${NC}"
echo -e "  4. Opción [8] - Configurar token de MercadoPago"
echo -e "  5. Opción [9] - Testear conexión"
echo -e "  6. Enviar 'menu' al bot en WhatsApp"
echo -e "  7. Probar flujo HWID: Cliente envía 'Nombre MiCelular + HWID123'"
echo -e "\n"

echo -e "${YELLOW}📱 FORMATO DE REGISTRO HWID:${NC}\n"
echo -e "  *Cliente envía:*"
echo -e "  MiCelular ABC123-DEF456-GHI789"
echo -e "\n  *El bot responde:*"
echo -e "  ✅ HWID registrado para MiCelular"
echo -e "  ¿Crear prueba de 1 hora? (sí/no)"
echo -e "\n"

echo -e "${YELLOW}💰 MERCADOPAGO CON HWID:${NC}\n"
echo -e "  1. Ve a: https://www.mercadopago.com.ar/developers"
echo -e "  2. Inicia sesión"
echo -e "  3. Ve a 'Tus credenciales'"
echo -e "  4. Copia 'Access Token PRODUCCIÓN'"
echo -e "  5. En el panel: Opción 8 → Pegar token"
echo -e "  6. Testear con opción 9"
echo -e "\n"

echo -e "${YELLOW}🔐 CARACTERÍSTICAS HWID:${NC}\n"
echo -e "  • Cada HWID = 1 dispositivo"
echo -e "  • Cliente envía nombre + HWID"
echo -e "  • HWID se almacena con hash SHA-256"
echo -e "  • Prueba de 1 hora vinculada al HWID"
echo -e "  • Compras premium vinculadas al HWID"
echo -e "  • Panel administra HWIDs pendientes/activos"
echo -e "  • Sistema evita múltiples cuentas por dispositivo"
echo -e "\n"

echo -e "${GREEN}${BOLD}¡Sistema HWID listo! Los clientes ahora envían Nombre + HWID 🔐${NC}\n"

# Ver logs automáticamente
read -p "$(echo -e "${YELLOW}¿Ver logs ahora? (s/N): ${NC}")" -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "\n${CYAN}Mostrando logs...${NC}"
    echo -e "${YELLOW}📱 Espera que aparezca el QR para escanear...${NC}\n"
    sleep 2
    pm2 logs sshbot-pro
else
    echo -e "\n${YELLOW}💡 Para iniciar: ${GREEN}sshbot${NC}"
    echo -e "${YELLOW}💡 Para logs: ${GREEN}pm2 logs sshbot-pro${NC}"
    echo -e "${YELLOW}💡 Para probar HWID: Envía 'menu' al bot${NC}\n"
fi

exit 0