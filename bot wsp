
#!/bin/bash
# ================================================
# SSH BOT PRO - WPPCONNECT + MERCADOPAGO + HWID
# VERSIÓN SIMPLIFICADA: PRIMERO NOMBRE, LUEGO HWID
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
║          🤖 SSH BOT PRO - WPPCONNECT + MERCADOPAGO          ║
║               🔐 VERSIÓN HWID - SIN USUARIO/CONTRASEÑA      ║
║               📱 PRIMERO NOMBRE, LUEGO HWID                 ║
║               💰 MercadoPago SDK v2.x INTEGRADO             ║
║               💳 Pago automático con QR                     ║
║               🎛️  Panel completo con control MP            ║
║               ⏰ NOTIFICACIONES DE VENCIMIENTO              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

echo -e "${GREEN}✅ CARACTERÍSTICAS PRINCIPALES:${NC}"
echo -e "  🔐 ${CYAN}Sistema HWID${NC} - Sin usuario/contraseña"
echo -e "  📱 ${CYAN}WPPConnect${NC} - API WhatsApp que funciona"
echo -e "  💰 ${GREEN}MercadoPago SDK v2.x${NC} - Integrado completo"
echo -e "  💳 ${YELLOW}Pago automático${NC} - QR + Enlace de pago"
echo -e "  📝 ${PURPLE}Flujo mejorado${NC} - Primero nombre, luego HWID"
echo -e "  🎛️  ${PURPLE}Panel completo${NC} - Control total del sistema"
echo -e "  📊 ${BLUE}Estadísticas${NC} - Ventas, HWIDs, ingresos"
echo -e "  ⚡ ${GREEN}Auto-verificación${NC} - Pagos verificados cada 2 min"
echo -e "  ⏱️  ${YELLOW}PRUEBA DE 2 HORAS${NC} - Duración actualizada"
echo -e "  ⏰ ${CYAN}NOTIFICACIONES DE VENCIMIENTO${NC} - Avisos automáticos"
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
DB_FILE="$INSTALL_DIR/data/hwid.db"
CONFIG_FILE="$INSTALL_DIR/config/config.json"

# Limpiar anterior
pm2 delete sshbot-pro 2>/dev/null || true
rm -rf "$INSTALL_DIR" "$USER_HOME" 2>/dev/null || true
rm -rf /root/.wppconnect 2>/dev/null || true

# Crear directorios
mkdir -p "$INSTALL_DIR"/{data,config,sessions,logs,qr_codes}
mkdir -p "$USER_HOME"
mkdir -p /root/.wppconnect
chmod -R 755 "$INSTALL_DIR"
chmod -R 700 /root/.wppconnect

cat > "$CONFIG_FILE" << EOF
{
    "bot": {
        "name": "SSH Bot Pro HWID",
        "version": "3.0-HWID",
        "server_ip": "$SERVER_IP"
    },
    "prices": {
        "test_hours": 2,
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
        "app_download": "https://www.mediafire.com/file/18tnc70qr2771lu/MGVPN.apk/file",
        "support": "https://wa.me/543435071016"
    },
    "paths": {
        "database": "$DB_FILE",
        "qr_codes": "$INSTALL_DIR/qr_codes",
        "sessions": "/root/.wppconnect"
    }
}
EOF

# Crear base de datos para HWID
sqlite3 "$DB_FILE" << 'SQL'
CREATE TABLE hwid_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    nombre TEXT,
    hwid TEXT UNIQUE,
    tipo TEXT DEFAULT 'test',
    expires_at DATETIME,
    status INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE daily_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    nombre TEXT,
    date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(phone, date)
);
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id TEXT UNIQUE,
    phone TEXT,
    nombre TEXT,
    plan TEXT,
    days INTEGER,
    amount REAL,
    status TEXT DEFAULT 'pending',
    payment_url TEXT,
    qr_code TEXT,
    preference_id TEXT,
    hwid TEXT,
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
CREATE TABLE hwid_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hwid TEXT,
    phone TEXT,
    nombre TEXT,
    action TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_hwid_users_hwid ON hwid_users(hwid);
CREATE INDEX idx_hwid_users_status ON hwid_users(status);
CREATE INDEX idx_payments_hwid ON payments(hwid);
CREATE INDEX idx_payments_status ON payments(status);
SQL

echo -e "${GREEN}✅ Estructura HWID creada${NC}"

# ================================================
# CREAR BOT CON HWID (PRIMERO NOMBRE, LUEGO HWID)
# ================================================
echo -e "\n${CYAN}🤖 Creando bot con sistema HWID (primero nombre, luego HWID)...${NC}"

cd "$USER_HOME"

# package.json
cat > package.json << 'PKGEOF'
{
    "name": "sshbot-pro-hwid",
    "version": "3.0.0",
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
        "axios": "^1.6.5"
    }
}
PKGEOF

echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
npm install --silent 2>&1 | grep -v "npm WARN" || true

# Crear bot.js con HWID (flujo nombre -> HWID) - CORREGIDO: prueba 2 HORAS y formato hora
echo -e "${YELLOW}📝 Creando bot.js con flujo nombre -> HWID (prueba 2 horas)...${NC}"

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

const execPromise = util.promisify(exec);
moment.locale('es');

console.log(chalk.cyan.bold('\n╔══════════════════════════════════════════════════════════════╗'));
console.log(chalk.cyan.bold('║           🤖 SSH BOT PRO - HWID + MERCADOPAGO                ║'));
console.log(chalk.cyan.bold('║           📝 FLUJO: PRIMERO NOMBRE, LUEGO HWID                ║'));
console.log(chalk.cyan.bold('║           ⏱️  PRUEBA: 2 HORAS                                 ║'));
console.log(chalk.cyan.bold('║           ⏰ NOTIFICACIONES DE VENCIMIENTO                    ║'));
console.log(chalk.cyan.bold('╚══════════════════════════════════════════════════════════════╝\n'));

// Cargar configuración
function loadConfig() {
    delete require.cache[require.resolve('/opt/sshbot-pro/config/config.json')];
    return require('/opt/sshbot-pro/config/config.json');
}

let config = loadConfig();
const db = new sqlite3.Database('/opt/sshbot-pro/data/hwid.db');

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
            return true;
        } catch (error) {
            console.log(chalk.red('❌ Error inicializando MP:'), error.message);
            mpEnabled = false;
            return false;
        }
    }
    console.log(chalk.yellow('⚠️ MercadoPago NO configurado'));
    return false;
}

initMercadoPago();

let client = null;

// ✅ FUNCIONES PARA HWID
function validateHWID(hwid) {
    // Formato esperado: APP-E3E4D5CBB7636907
    const hwidRegex = /^APP-[A-F0-9]{16}$/;
    return hwidRegex.test(hwid);
}

function normalizeHWID(hwid) {
    // Asegurar formato consistente
    hwid = hwid.trim().toUpperCase();
    if (!hwid.startsWith('APP-')) {
        hwid = 'APP-' + hwid.replace(/[^A-F0-9]/g, '');
    }
    return hwid;
}

function isHWIDActive(hwid) {
    return new Promise((resolve) => {
        db.get('SELECT * FROM hwid_users WHERE hwid = ? AND status = 1 AND expires_at > datetime("now")', 
            [hwid], (err, row) => {
            resolve(!err && row);
        });
    });
}

function getHWIDInfo(hwid) {
    return new Promise((resolve) => {
        db.get('SELECT * FROM hwid_users WHERE hwid = ?', [hwid], (err, row) => {
            if (err || !row) resolve(null);
            else resolve(row);
        });
    });
}

async function registerHWID(phone, nombre, hwid, days, tipo = 'premium') {
    try {
        // Verificar si HWID ya existe
        const existing = await new Promise((resolve) => {
            db.get('SELECT hwid FROM hwid_users WHERE hwid = ?', [hwid], (err, row) => {
                resolve(row);
            });
        });

        if (existing) {
            return { success: false, error: 'HWID ya registrado en el sistema' };
        }

        let expireFull;
        if (days === 0) {
            // Test - 2 horas (CORREGIDO)
            expireFull = moment().add(2, 'hours').format('YYYY-MM-DD HH:mm:ss');
            console.log(chalk.cyan(`⏱️  Prueba 2 horas - Expira: ${expireFull}`));
        } else {
            // Premium
            expireFull = moment().add(days, 'days').format('YYYY-MM-DD 23:59:59');
        }

        // Registrar en BD
        await new Promise((resolve, reject) => {
            db.run(
                `INSERT INTO hwid_users (phone, nombre, hwid, tipo, expires_at, status) VALUES (?, ?, ?, ?, ?, 1)`,
                [phone, nombre, hwid, tipo, expireFull],
                function(err) {
                    if (err) reject(err);
                    else resolve(this.lastID);
                }
            );
        });

        // Registrar intento
        db.run(`INSERT INTO hwid_attempts (hwid, phone, nombre, action) VALUES (?, ?, ?, 'registered')`, 
            [hwid, phone, nombre]);

        return { 
            success: true, 
            hwid,
            nombre,
            expires: expireFull,
            tipo
        };

    } catch (error) {
        console.error(chalk.red('❌ Error registrando HWID:'), error.message);
        return { success: false, error: error.message };
    }
}

function canCreateTest(phone) {
    return new Promise((resolve) => {
        const today = moment().format('YYYY-MM-DD');
        db.get('SELECT COUNT(*) as count FROM daily_tests WHERE phone = ? AND date = ?', 
            [phone, today], (err, row) => resolve(!err && row && row.count === 0));
    });
}

function registerTest(phone, nombre) {
    db.run('INSERT OR IGNORE INTO daily_tests (phone, nombre, date) VALUES (?, ?, ?)', 
        [phone, nombre, moment().format('YYYY-MM-DD')]);
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

// ✅ MERCADOPAGO - CREAR PAGO
async function createMercadoPagoPayment(phone, days, amount, planName) {
    try {
        if (!mpEnabled || !mpPreference) {
            return { success: false, error: 'MercadoPago no configurado' };
        }
        
        const phoneClean = phone.replace('@c.us', '');
        const paymentId = `HWID-${phoneClean}-${days}d-${Date.now()}`;
        
        console.log(chalk.cyan(`🔄 Creando pago MP: ${paymentId}`));
        
        const expirationDate = moment().add(24, 'hours');
        const isoDate = expirationDate.toISOString();
        
        const preferenceData = {
            items: [{
                title: `HWID SSH PREMIUM ${days} DÍAS`,
                description: `Activación HWID SSH por ${days} días - SIN USUARIO/CONTRASEÑA`,
                quantity: 1,
                currency_id: config.prices.currency || 'ARS',
                unit_price: parseFloat(amount)
            }],
            external_reference: paymentId,
            expires: true,
            expiration_date_from: moment().toISOString(),
            expiration_date_to: isoDate,
            back_urls: {
                success: `https://wa.me/${phoneClean}?text=Ya%20pague%20hwid`,
                failure: `https://wa.me/${phoneClean}?text=Pago%20fallido%20hwid`,
                pending: `https://wa.me/${phoneClean}?text=Pago%20pendiente%20hwid`
            },
            auto_return: 'approved',
            statement_descriptor: 'HWID SSH'
        };
        
        const response = await mpPreference.create({ body: preferenceData });
        
        if (response && response.id) {
            const paymentUrl = response.init_point;
            const qrPath = `${config.paths.qr_codes}/${paymentId}.png`;
            
            await QRCode.toFile(qrPath, paymentUrl, { 
                width: 400,
                margin: 2
            });
            
            db.run(
                `INSERT INTO payments (payment_id, phone, plan, days, amount, status, payment_url, qr_code, preference_id) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?, ?)`,
                [paymentId, phone, `${days}d`, days, amount, paymentUrl, qrPath, response.id]
            );
            
            return { 
                success: true, 
                paymentId, 
                paymentUrl, 
                qrPath,
                amount: parseFloat(amount)
            };
        }
        
        throw new Error('Respuesta inválida de MercadoPago');
        
    } catch (error) {
        console.error(chalk.red('❌ Error MercadoPago:'), error.message);
        return { success: false, error: error.message };
    }
}

// ✅ VERIFICAR PAGOS PENDIENTES
async function checkPendingPayments() {
    if (!mpEnabled) return;
    
    db.all('SELECT * FROM payments WHERE status = "pending" AND created_at > datetime("now", "-48 hours")', 
        async (err, payments) => {
        if (err || !payments || payments.length === 0) return;
        
        console.log(chalk.yellow(`🔍 Verificando ${payments.length} pagos...`));
        
        for (const payment of payments) {
            try {
                const url = `https://api.mercadopago.com/v1/payments/search?external_reference=${payment.payment_id}`;
                const response = await axios.get(url, {
                    headers: { 
                        'Authorization': `Bearer ${config.mercadopago.access_token}`
                    },
                    timeout: 15000
                });
                
                if (response.data && response.data.results && response.data.results.length > 0) {
                    const mpPayment = response.data.results[0];
                    
                    console.log(chalk.cyan(`📋 Pago ${payment.payment_id}: ${mpPayment.status}`));
                    
                    if (mpPayment.status === 'approved') {
                        console.log(chalk.green(`✅ PAGO APROBADO: ${payment.payment_id}`));
                        
                        db.run(`UPDATE payments SET status = 'approved', approved_at = CURRENT_TIMESTAMP WHERE payment_id = ?`, 
                            [payment.payment_id]);
                        
                        // Enviar mensaje pidiendo NOMBRE primero
                        const message = `✅ PAGO CONFIRMADO

🎉 Tu pago ha sido aprobado

📝 PRIMERO, ESCRIBE TU NOMBRE:
Para continuar con la activación, dime tu nombre

⏳ Tienes 30 minutos para completar el proceso`;
                        
                        if (client) {
                            await client.sendText(payment.phone, message);
                            await setUserState(payment.phone, 'awaiting_hwid', { 
                                payment_id: payment.payment_id,
                                days: payment.days,
                                plan: payment.plan
                            });
                        }
                    }
                }
            } catch (error) {
                console.error(chalk.red(`❌ Error verificando ${payment.payment_id}:`), error.message);
            }
        }
    });
}

// ✅ NOTIFICACIONES DE VENCIMIENTO (NUEVO)
async function checkExpiringHWIDs() {
    try {
        // Buscar HWIDs que expiran en las próximas 24 horas
        const expiringSoon = await new Promise((resolve, reject) => {
            db.all(`
                SELECT * FROM hwid_users 
                WHERE status = 1 
                AND expires_at > datetime('now') 
                AND expires_at < datetime('now', '+1 day')
                AND tipo = 'premium'
            `, (err, rows) => {
                if (err) reject(err);
                else resolve(rows || []);
            });
        });

        for (const hwid of expiringSoon) {
            const hoursLeft = moment(hwid.expires_at).diff(moment(), 'hours');
            const message = `⏰ RECORDATORIO DE VENCIMIENTO

Hola ${hwid.nombre}, tu acceso expirará en aproximadamente ${hoursLeft} horas.

🔐 HWID: ${hwid.hwid}
⏰ Fecha de vencimiento: ${moment(hwid.expires_at).format('DD/MM/YYYY HH:mm')}

💰 Para renovar, envía 2 y elige tu plan.

¡No te quedes sin servicio!`;
            
            if (client) {
                await client.sendText(hwid.phone, message);
                console.log(chalk.yellow(`📨 Notificación enviada a ${hwid.nombre} - Expira en ${hoursLeft} horas`));
            }
        }

        // Buscar HWIDs que expiraron en las últimas 24 horas (para recordatorio post-vencimiento)
        const expired = await new Promise((resolve, reject) => {
            db.all(`
                SELECT * FROM hwid_users 
                WHERE status = 0 
                AND expires_at > datetime('now', '-1 day')
                AND expires_at < datetime('now')
                AND tipo = 'premium'
            `, (err, rows) => {
                if (err) reject(err);
                else resolve(rows || []);
            });
        });

        for (const hwid of expired) {
            const message = `⏰ SERVICIO EXPIRADO

Hola ${hwid.nombre}, tu acceso ha expirado.

🔐 HWID: ${hwid.hwid}
⏰ Expiró: ${moment(hwid.expires_at).format('DD/MM/YYYY HH:mm')}

💰 Para renovar, envía 2 y elige tu plan.

¡Renueva ahora y sigue disfrutando!`;
            
            if (client) {
                await client.sendText(hwid.phone, message);
                console.log(chalk.yellow(`📨 Notificación post-vencimiento enviada a ${hwid.nombre}`));
            }
        }

    } catch (error) {
        console.error(chalk.red('❌ Error en notificaciones de vencimiento:'), error.message);
    }
}

// Inicializar WPPConnect
async function initializeBot() {
    try {
        console.log(chalk.yellow('🚀 Inicializando WPPConnect...'));
        
        client = await wppconnect.create({
            session: 'sshbot-pro-hwid',
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
                '--window-size=1920,1080'
            ],
            puppeteerOptions: {
                executablePath: '/usr/bin/google-chrome',
                headless: 'new',
                args: ['--no-sandbox', '--disable-setuid-sandbox']
            },
            disableWelcome: true,
            updatesLog: false,
            folderNameToken: '/root/.wppconnect'
        });
        
        console.log(chalk.green('✅ WPPConnect conectado!'));
        
        client.onStateChange((state) => {
            console.log(chalk.cyan(`📱 Estado: ${state}`));
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
                    
                    await client.sendText(from, `HOLA BIENVENIDO BOT MGVPN 🚀

Elija una opción:

 1️⃣ - PROBAR INTERNET (2 horas gratis)
 2️⃣ - COMPRAR INTERNET
 3️⃣ - VERIFICAR MI HWID
 4️⃣ - DESCARGAR APLICACIÓN`);
                }
                
                // OPCIÓN 1: PRUEBA
                else if (text === '1' && userState.state === 'main_menu') {
                    await setUserState(from, 'awaiting_test_nombre');
                    
                    await client.sendText(from, `⏳️ PRUEBA GRATUITA - 2 HORAS

Primero, dime tu nombre:`);
                }
                
                // OPCIÓN 2: COMPRAR
                else if (text === '2' && userState.state === 'main_menu') {
                    await setUserState(from, 'buying_hwid');
                    
                    await client.sendText(from, `💰 PLANES DE INTERNET

Selecciona un plan:

 1️⃣ - 7 DÍAS - $${config.prices.price_7d}
 2️⃣ - 15 DÍAS - $${config.prices.price_15d}
 3️⃣ - 30 DÍAS - $${config.prices.price_30d}
 4️⃣ - 50 DÍAS - $${config.prices.price_50d}

 0️⃣ - VOLVER

💳 Pago con MercadoPago`);
                }
                
                // OPCIÓN 3: VERIFICAR HWID
                else if (text === '3' && userState.state === 'main_menu') {
                    await setUserState(from, 'awaiting_check_hwid');
                    
                    await client.sendText(from, `🔍 VERIFICAR HWID

Envía tu HWID para verificar si está activo:

Ejemplo: APP-E3E4D5CBB7636907`);
                }
                
                // OPCIÓN 4: DESCARGAR APP
                else if (text === '4' && userState.state === 'main_menu') {
                    await client.sendText(from, `📱 DESCARGAR APLICACIÓN

🔗 Enlace:
${config.links.app_download}

💡 Instrucciones:
1. Abre el link Descarga el APK
2. Abre el apk Click en "Más detalles"
3. Click en "Instalar de todas formas"`);
                }
                
                // PROCESAR NOMBRE PARA PRUEBA
                else if (userState.state === 'awaiting_test_nombre') {
                    const nombre = message.body.trim();
                    
                    if (nombre.length < 2) {
                        await client.sendText(from, '❌ El nombre debe tener al menos 2 caracteres. Intenta de nuevo:');
                        return;
                    }
                    
                    // Guardar nombre y pasar a pedir HWID
                    await setUserState(from, 'awaiting_test_hwid', { nombre });
                    
                    await client.sendText(from, `✅ Gracias ${nombre}

Ahora envía tu HWID para activar la prueba (2 horas):

Formato: APP-E3E4D5CBB7636907

📱 ¿CÓMO OBTENER TU HWID?
1. Abre la aplicación
2. Toca el boton de WhatsApp
3. Envia el HWID

⏳ Una prueba por día`);
                }
                
                // PROCESAR HWID PARA PRUEBA
                else if (userState.state === 'awaiting_test_hwid') {
                    const rawHwid = message.body;
                    const hwid = normalizeHWID(rawHwid);
                    const nombre = userState.data.nombre;
                    
                    if (!validateHWID(hwid)) {
                        await client.sendText(from, `❌ HWID INVÁLIDO

Formato correcto: APP-E3E4D5CBB7636907

Envía el HWID nuevamente o escribe MENU para volver`);
                        return;
                    }
                    
                    // Verificar prueba diaria
                    if (!(await canCreateTest(from))) {
                        await client.sendText(from, `❌ YA USASTE TU PRUEBA HOY

⏳ Vuelve mañana o compra un plan`);
                        await setUserState(from, 'main_menu');
                        return;
                    }
                    
                    // Verificar si HWID ya está registrado
                    const active = await isHWIDActive(hwid);
                    if (active) {
                        await client.sendText(from, `❌ Este HWID ya está activo en el sistema

Si crees que es un error, contacta soporte.`);
                        await setUserState(from, 'main_menu');
                        return;
                    }
                    
                    await client.sendText(from, '⏳ Activando prueba (2 horas)...');
                    
                    const result = await registerHWID(from, nombre, hwid, 0, 'test');
                    
                    if (result.success) {
                        registerTest(from, nombre);
                        
                        const expireTime = moment(result.expires).format('HH:mm DD/MM/YYYY');
                        
                        await client.sendText(from, `✅ PRUEBA ACTIVADA ${nombre}

🔐 HWID: ${hwid}
⏰ Expira: ${expireTime}
⚡ Tipo: PRUEBA (2 horas)

📱 Abre la aplicación y ya puedes conectarte

`);
                        
                        console.log(chalk.green(`✅ HWID test: ${hwid} - ${nombre} - Expira: ${result.expires}`));
                    } else {
                        await client.sendText(from, `❌ Error: ${result.error}`);
                    }
                    
                    await setUserState(from, 'main_menu');
                }
                
                // PROCESAR PLAN DE COMPRA
                else if (userState.state === 'buying_hwid' && ['1','2','3','4'].includes(text)) {
                    const planMap = {
                        '1': { days: 7, price: config.prices.price_7d, name: '7 DÍAS' },
                        '2': { days: 15, price: config.prices.price_15d, name: '15 DÍAS' },
                        '3': { days: 30, price: config.prices.price_30d, name: '30 DÍAS' },
                        '4': { days: 50, price: config.prices.price_50d, name: '50 DÍAS' }
                    };
                    
                    const plan = planMap[text];
                    
                    if (mpEnabled) {
                        await client.sendText(from, '⏳ Generando pago...');
                        
                        const payment = await createMercadoPagoPayment(
                            from, 
                            plan.days, 
                            plan.price, 
                            plan.name
                        );
                        
                        if (payment.success) {
                            const message = `💰 PAGO PARA HWID

- 🌐 Plan: ${plan.name}
- 💰 Precio: $${payment.amount}
- 🕜 Duración: ${plan.days} días

LINK DE PAGO:
${payment.paymentUrl}

⏰ Válido por 24 horas

📌 DESPUÉS DE PAGAR:
1. Espera la confirmación
2. Te pediremos tu nombre
3. Luego tu HWID
4. Se activará automáticamente`;
                            
                            await client.sendText(from, message);
                            
                            if (fs.existsSync(payment.qrPath)) {
                                try {
                                    await client.sendImage(from, payment.qrPath, 'qr-pago.jpg', 
                                        `Escanea con MercadoPago\n\n${plan.name} - $${payment.amount}`);
                                } catch (qrError) {
                                    console.error(chalk.red('⚠️ Error QR:'), qrError.message);
                                }
                            }
                        } else {
                            await client.sendText(from, `ERROR AL GENERAR PAGO

${payment.error}

Contacta al administrador para otras opciones de pago.`);
                        }
                        
                        await setUserState(from, 'main_menu');
                    } else {
                        await client.sendText(from, `PLAN SELECCIONADO: ${plan.name}

Precio: $${plan.price} ARS
Duración: ${plan.days} días

Para continuar con la compra, contacta al administrador:
${config.links.support}`);
                        await setUserState(from, 'main_menu');
                    }
                }
                
                else if (text === '0' && userState.state === 'buying_hwid') {
                    await setUserState(from, 'main_menu');
                    await client.sendText(from, `HOLA BIENVENIDO BOT HWID 🚀

Elija una opción:

 1️⃣ - PROBAR INTERNET (2 horas gratis)
 2️⃣ - COMPRAR INTERNET
 3️⃣ - VERIFICAR MI HWID
 4️⃣ - DESCARGAR APLICACIÓN`);
                }
                
                // PROCESAR HWID PARA VERIFICACIÓN
                else if (userState.state === 'awaiting_check_hwid') {
                    const rawHwid = message.body;
                    const hwid = normalizeHWID(rawHwid);
                    
                    if (!validateHWID(hwid)) {
                        await client.sendText(from, `❌ Formato inválido

Ejemplo: APP-E3E4D5CBB7636907

Intenta nuevamente o MENU`);
                        return;
                    }
                    
                    const info = await getHWIDInfo(hwid);
                    
                    if (info && info.status === 1) {
                        const expires = moment(info.expires_at).format('DD/MM/YYYY HH:mm');
                        const now = moment();
                        const expiresMoment = moment(info.expires_at);
                        const nombre = info.nombre || 'Usuario';
                        
                        if (expiresMoment.isAfter(now)) {
                            const remaining = expiresMoment.fromNow();
                            await client.sendText(from, `✅ HWID ACTIVO

👤 Usuario: ${nombre}
🔐 HWID: ${hwid}
📅 Tipo: ${info.tipo === 'test' ? 'PRUEBA' : 'PREMIUM'}
⏰ Válido hasta: ${expires}
⌛ Tiempo restante: ${remaining}`);
                        } else {
                            await client.sendText(from, `❌ HWID EXPIRADO

👤 Usuario: ${nombre}
🔐 HWID: ${hwid}
📅 Expiró: ${expires}

Renueva comprando un nuevo plan`);
                        }
                    } else {
                        await client.sendText(from, `❌ HWID NO REGISTRADO

Este HWID no está en el sistema.

¿Quieres probar el servicio?
Envía 1 para prueba gratis (2 horas)`);
                    }
                    
                    await setUserState(from, 'main_menu');
                }
                
                // ESPERANDO NOMBRE Y HWID DESPUÉS DE PAGO (PRIMERO NOMBRE, LUEGO HWID)
                else if (userState.state === 'awaiting_hwid') {
                    // Si NO tenemos nombre guardado, lo que llega es el nombre
                    if (!userState.data.nombre) {
                        const nombre = message.body.trim();
                        
                        if (nombre.length < 2) {
                            await client.sendText(from, '❌ El nombre debe tener al menos 2 caracteres. Intenta de nuevo:');
                            return;
                        }
                        
                        // Guardar el nombre y pasar a esperar HWID
                        userState.data.nombre = nombre;
                        await setUserState(from, 'awaiting_hwid', userState.data);
                        
                        await client.sendText(from, `✅ Gracias ${nombre}

Ahora envía tu HWID:
Formato: APP-E3E4D5CBB7636907

📱 ¿CÓMO OBTENER TU HWID?
1. Abre la aplicación
2. Toca el botón de WhatsApp
3. Envia el HWID`);
                        
                        return;
                    }
                    
                    // Si ya tenemos nombre, lo que llega es el HWID
                    const rawHwid = message.body;
                    const hwid = normalizeHWID(rawHwid);
                    const nombre = userState.data.nombre;
                    
                    if (!validateHWID(hwid)) {
                        await client.sendText(from, `❌ FORMATO INCORRECTO

Ejemplo: APP-E3E4D5CBB7636907

Envía el HWID nuevamente:`);
                        return;
                    }
                    
                    // Verificar si HWID ya está activo
                    const active = await isHWIDActive(hwid);
                    if (active) {
                        await client.sendText(from, `❌ Este HWID ya está activo

Si es tuyo, contacta soporte.`);
                        return;
                    }
                    
                    await client.sendText(from, '⏳ Activando tu HWID...');
                    
                    // Activar HWID
                    const result = await registerHWID(
                        from, 
                        nombre,
                        hwid, 
                        userState.data.days, 
                        'premium'
                    );
                    
                    if (result.success) {
                        // Actualizar pago con HWID y nombre
                        db.run(`UPDATE payments SET hwid = ?, nombre = ? WHERE payment_id = ?`,
                            [hwid, nombre, userState.data.payment_id]);
                        
                        const expireDate = moment(result.expires).format('DD/MM/YYYY');
                        
                        await client.sendText(from, `✅ ¡ACTIVADO ${nombre}!

🔐 HWID: ${hwid}
⏰ Válido hasta: ${expireDate}

¡Ya puedes usar la aplicación!`);
                        
                        console.log(chalk.green(`✅ HWID premium: ${hwid} - ${nombre}`));
                    } else {
                        await client.sendText(from, `❌ Error: ${result.error}`);
                    }
                    
                    await setUserState(from, 'main_menu');
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
        
        // ✅ NOTIFICACIONES DE VENCIMIENTO CADA HORA (NUEVO)
        cron.schedule('0 * * * *', () => {
            console.log(chalk.yellow('⏰ Verificando HWIDs próximos a vencer...'));
            checkExpiringHWIDs();
        });
        
        // ✅ LIMPIAR HWIDS EXPIRADOS
        cron.schedule('*/15 * * * *', async () => {
            const now = moment().format('YYYY-MM-DD HH:mm:ss');
            console.log(chalk.yellow(`🧹 Limpiando HWIDs expirados...`));
            
            db.run('UPDATE hwid_users SET status = 0 WHERE expires_at < ? AND status = 1', [now]);
        });
        
        // ✅ LIMPIAR ESTADOS
        cron.schedule('0 * * * *', () => {
            db.run(`DELETE FROM user_state WHERE updated_at < datetime('now', '-1 hour')`);
        });
        
    } catch (error) {
        console.error(chalk.red('❌ Error inicializando:'), error.message);
        console.log(chalk.yellow('🔄 Reintentando en 10 segundos...'));
        setTimeout(initializeBot, 10000);
    }
}

// Iniciar
initializeBot();

process.on('SIGINT', async () => {
    console.log(chalk.yellow('\n🛑 Cerrando bot...'));
    if (client) {
        await client.close();
    }
    process.exit();
});
BOTEOF

echo -e "${GREEN}✅ Bot HWID creado con flujo nombre -> HWID (prueba 2 HORAS)${NC}"

# ================================================
# CREAR PANEL DE CONTROL PARA HWID
# ================================================
echo -e "\n${CYAN}🎛️  Creando panel de control HWID...${NC}"

cat > /usr/local/bin/sshbot-hwid << 'PANELEOF'
#!/bin/bash
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; BLUE='\033[0;34m'; PURPLE='\033[0;35m'; NC='\033[0m'

DB="/opt/sshbot-pro/data/hwid.db"
CONFIG="/opt/sshbot-pro/config/config.json"

get_val() { jq -r "$1" "$CONFIG" 2>/dev/null; }
set_val() { local t=$(mktemp); jq "$1 = $2" "$CONFIG" > "$t" && mv "$t" "$CONFIG"; }

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
        return 0
    else
        echo -e "${RED}❌ ERROR - Código: $HTTP_CODE${NC}"
        return 1
    fi
}

show_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           🎛️  PANEL SSH BOT PRO - VERSIÓN HWID              ║${NC}"
    echo -e "${CYAN}║              🔐 SIN USUARIO/CONTRASEÑA                      ║${NC}"
    echo -e "${CYAN}║              ⏱️  PRUEBA: 2 HORAS                            ║${NC}"
    echo -e "${CYAN}║              ⏰ NOTIFICACIONES DE VENCIMIENTO               ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}\n"
}

while true; do
    show_header
    
    TOTAL_HWID=$(sqlite3 "$DB" "SELECT COUNT(*) FROM hwid_users" 2>/dev/null || echo "0")
    ACTIVE_HWID=$(sqlite3 "$DB" "SELECT COUNT(*) FROM hwid_users WHERE status=1" 2>/dev/null || echo "0")
    PENDING_PAYMENTS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM payments WHERE status='pending'" 2>/dev/null || echo "0")
    APPROVED_PAYMENTS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM payments WHERE status='approved'" 2>/dev/null || echo "0")
    TESTS_TODAY=$(sqlite3 "$DB" "SELECT COUNT(*) FROM daily_tests WHERE date = date('now')" 2>/dev/null || echo "0")
    
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
    
    echo -e "${YELLOW}📊 ESTADO DEL SISTEMA${NC}"
    echo -e "  Bot: $BOT_STATUS"
    echo -e "  HWIDs: ${CYAN}$ACTIVE_HWID/$TOTAL_HWID${NC} activos/total"
    echo -e "  Tests hoy: ${CYAN}$TESTS_TODAY${NC}"
    echo -e "  Pagos: ${CYAN}$PENDING_PAYMENTS${NC} pend | ${GREEN}$APPROVED_PAYMENTS${NC} aprob"
    echo -e "  MercadoPago: $MP_STATUS"
    echo -e "  IP: $(get_val '.bot.server_ip')"
    echo -e "  ⏱️  Prueba: ${YELLOW}2 HORAS${NC}"
    echo -e "  ⏰  Notificaciones: ${GREEN}ACTIVAS (cada hora)${NC}"
    echo -e ""
    
    echo -e "${YELLOW}💰 PRECIOS ACTUALES:${NC}"
    echo -e "  7 días: $ $(get_val '.prices.price_7d') ARS"
    echo -e "  15 días: $ $(get_val '.prices.price_15d') ARS"
    echo -e "  30 días: $ $(get_val '.prices.price_30d') ARS"
    echo -e "  50 días: $ $(get_val '.prices.price_50d') ARS"
    echo -e ""
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}[1]${NC} 🚀  Iniciar/Reiniciar bot"
    echo -e "${CYAN}[2]${NC} 🛑  Detener bot"
    echo -e "${CYAN}[3]${NC} 📱  Ver logs y QR"
    echo -e "${CYAN}[4]${NC} 🔐  Registrar HWID manual"
    echo -e "${CYAN}[5]${NC} 👥  Listar HWIDs activos"
    echo -e "${CYAN}[6]${NC} 💰  Cambiar precios"
    echo -e "${CYAN}[7]${NC} 🔑  Configurar MercadoPago"
    echo -e "${CYAN}[8]${NC} 🧪  Test MercadoPago"
    echo -e "${CYAN}[9]${NC} 📊  Estadísticas"
    echo -e "${CYAN}[10]${NC} 🔄 Limpiar sesión"
    echo -e "${CYAN}[11]${NC} 💳 Ver pagos"
    echo -e "${CYAN}[12]${NC} 🔍 Buscar HWID"
    echo -e "${CYAN}[13]${NC} 🧪 Ver tests hoy"
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
            echo -e "${CYAN}🔐 REGISTRAR HWID MANUAL${NC}\n"
            
            read -p "Teléfono (ej: 5491122334455): " PHONE
            read -p "Nombre del usuario: " NOMBRE
            read -p "HWID (formato: APP-E3E4D5CBB7636907): " HWID
            read -p "Tipo (test/premium): " TIPO
            read -p "Días (0=test 2h, 7,15,30,50): " DAYS
            
            [[ -z "$DAYS" ]] && DAYS="30"
            
            # Normalizar HWID
            HWID=$(echo "$HWID" | tr 'a-z' 'A-Z')
            if [[ ! "$HWID" =~ ^APP-[A-F0-9]{16}$ ]]; then
                echo -e "\n${RED}❌ Formato HWID inválido${NC}"
                read -p "Presiona Enter..."
                continue
            fi
            
            if [[ "$TIPO" == "test" ]]; then
                DAYS="0"
                EXPIRE_DATE=$(date -d "+2 hours" +"%Y-%m-%d %H:%M:%S")
            else
                EXPIRE_DATE=$(date -d "+$DAYS days" +"%Y-%m-%d 23:59:59")
            fi
            
            sqlite3 "$DB" "INSERT INTO hwid_users (phone, nombre, hwid, tipo, expires_at, status) VALUES ('$PHONE', '$NOMBRE', '$HWID', '$TIPO', '$EXPIRE_DATE', 1)"
            
            if [[ $? -eq 0 ]]; then
                echo -e "\n${GREEN}✅ HWID REGISTRADO${NC}"
                echo -e "📱 Teléfono: ${PHONE}"
                echo -e "👤 Nombre: ${NOMBRE}"
                echo -e "🔐 HWID: ${HWID}"
                echo -e "⏰ Expira: ${EXPIRE_DATE}"
            else
                echo -e "\n${RED}❌ Error (puede que el HWID ya exista)${NC}"
            fi
            read -p "Presiona Enter..."
            ;;
        5)
            clear
            echo -e "${CYAN}👥 HWIDs ACTIVOS${NC}\n"
            
            sqlite3 -column -header "$DB" "SELECT nombre, hwid, phone, tipo, expires_at FROM hwid_users WHERE status = 1 ORDER BY expires_at DESC LIMIT 20"
            echo -e "\n${YELLOW}Total activos: ${ACTIVE_HWID}${NC}"
            read -p "Presiona Enter..."
            ;;
        6)
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
        7)
            clear
            echo -e "${CYAN}🔑 CONFIGURAR MERCADOPAGO${NC}\n"
            
            CURRENT_TOKEN=$(get_val '.mercadopago.access_token')
            
            if [[ -n "$CURRENT_TOKEN" && "$CURRENT_TOKEN" != "null" && "$CURRENT_TOKEN" != "" ]]; then
                echo -e "${GREEN}✅ Token configurado${NC}"
                echo -e "${YELLOW}Preview: ${CURRENT_TOKEN:0:30}...${NC}\n"
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
                fi
            fi
            read -p "Presiona Enter..."
            ;;
        8)
            clear
            echo -e "${CYAN}🧪 TEST MERCADOPAGO${NC}\n"
            
            TOKEN=$(get_val '.mercadopago.access_token')
            if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
                echo -e "${RED}❌ Token no configurado${NC}\n"
                read -p "Presiona Enter..."
                continue
            fi
            
            test_mercadopago "$TOKEN"
            
            read -p "\nPresiona Enter..."
            ;;
        9)
            clear
            echo -e "${CYAN}📊 ESTADÍSTICAS${NC}\n"
            
            echo -e "${YELLOW}🔐 HWIDs:${NC}"
            sqlite3 "$DB" "SELECT 'Total: ' || COUNT(*) || ' | Activos: ' || SUM(CASE WHEN status=1 THEN 1 ELSE 0 END) || ' | Tests hoy: ' || (SELECT COUNT(*) FROM daily_tests WHERE date = date('now')) FROM hwid_users"
            
            echo -e "\n${YELLOW}💰 PAGOS:${NC}"
            sqlite3 "$DB" "SELECT 'Pendientes: ' || SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) || ' | Aprobados: ' || SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) || ' | Total: $' || printf('%.2f', SUM(CASE WHEN status='approved' THEN amount ELSE 0 END)) FROM payments"
            
            echo -e "\n${YELLOW}📅 PLANES VENDIDOS:${NC}"
            sqlite3 "$DB" "SELECT '7d: ' || SUM(CASE WHEN plan='7d' THEN 1 ELSE 0 END) || ' | 15d: ' || SUM(CASE WHEN plan='15d' THEN 1 ELSE 0 END) || ' | 30d: ' || SUM(CASE WHEN plan='30d' THEN 1 ELSE 0 END) || ' | 50d: ' || SUM(CASE WHEN plan='50d' THEN 1 ELSE 0 END) FROM payments WHERE status='approved'"
            
            echo -e "\n${YELLOW}💸 INGRESOS HOY:${NC}"
            sqlite3 "$DB" "SELECT 'Hoy: $' || printf('%.2f', SUM(CASE WHEN date(created_at) = date('now') THEN amount ELSE 0 END)) FROM payments WHERE status='approved'"
            
            read -p "\nPresiona Enter..."
            ;;
        10)
            echo -e "\n${YELLOW}🧹 Limpiando sesión...${NC}"
            pm2 stop sshbot-pro
            rm -rf /root/.wppconnect/*
            echo -e "${GREEN}✅ Sesión limpiada${NC}"
            sleep 2
            ;;
        11)
            clear
            echo -e "${CYAN}💳 PAGOS${NC}\n"
            
            echo -e "${YELLOW}Pagos pendientes:${NC}"
            sqlite3 -column -header "$DB" "SELECT payment_id, phone, plan, amount, created_at FROM payments WHERE status='pending' ORDER BY created_at DESC LIMIT 10"
            
            echo -e "\n${YELLOW}Pagos aprobados:${NC}"
            sqlite3 -column -header "$DB" "SELECT payment_id, phone, nombre, plan, amount, approved_at, hwid FROM payments WHERE status='approved' ORDER BY approved_at DESC LIMIT 10"
            
            read -p "\nPresiona Enter..."
            ;;
        12)
            clear
            echo -e "${CYAN}🔍 BUSCAR HWID${NC}\n"
            read -p "Ingresa HWID, nombre o teléfono: " SEARCH
            
            echo -e "\n${YELLOW}Resultados:${NC}"
            sqlite3 -column -header "$DB" "SELECT nombre, hwid, phone, tipo, expires_at, status FROM hwid_users WHERE hwid LIKE '%$SEARCH%' OR phone LIKE '%$SEARCH%' OR nombre LIKE '%$SEARCH%'"
            
            read -p "\nPresiona Enter..."
            ;;
        13)
            clear
            echo -e "${CYAN}🧪 TESTS DE HOY${NC}\n"
            
            sqlite3 -column -header "$DB" "SELECT nombre, phone, created_at FROM daily_tests WHERE date = date('now') ORDER BY created_at DESC"
            
            read -p "\nPresiona Enter..."
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

chmod +x /usr/local/bin/sshbot-hwid
ln -sf /usr/local/bin/sshbot-hwid /usr/local/bin/sshbot

# ================================================
# INICIAR BOT
# ================================================
echo -e "\n${CYAN}🚀 Iniciando bot...${NC}"

cd "$USER_HOME"
pm2 start bot.js --name sshbot-pro
pm2 save
pm2 startup systemd -u root --hp /root > /dev/null 2>&1

# ================================================
# MENSAJE FINAL
# ================================================
clear
echo -e "${GREEN}${BOLD}"
cat << "FINAL"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🎉 INSTALACIÓN COMPLETADA - VERSIÓN HWID 🎉        ║
║                                                              ║
║       🔐 SISTEMA SIN USUARIO/CONTRASEÑA                    ║
║       📱 PRIMERO NOMBRE, LUEGO HWID                        ║
║       💰 MercadoPago SDK v2.x INTEGRADO                    ║
║       💳 Pago automático con QR                            ║
║       ⏱️  PRUEBA DE 2 HORAS (ACTUALIZADO)                  ║
║       ⏰ NOTIFICACIONES DE VENCIMIENTO ACTIVAS              ║
║       🎛️  Panel completo con control MP                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
FINAL
echo -e "${NC}"

echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Sistema HWID instalado${NC}"
echo -e "${GREEN}✅ SIN usuario/contraseña${NC}"
echo -e "${GREEN}✅ FLUJO: Primero nombre, luego HWID${NC}"
echo -e "${GREEN}✅ Formato HWID: APP-E3E4D5CBB7636907${NC}"
echo -e "${GREEN}✅ MercadoPago SDK v2.x integrado${NC}"
echo -e "${GREEN}✅ Verificación automática de pagos${NC}"
echo -e "${GREEN}✅ ⏱️  PRUEBA DE 2 HORAS (CORREGIDO)${NC}"
echo -e "${GREEN}✅ ⏰ NOTIFICACIONES DE VENCIMIENTO (cada hora)${NC}"
echo -e "${GREEN}✅ SIN CUPONES DE DESCUENTO - Proceso simplificado${NC}"
echo -e "${GREEN}✅ SIN NÚMEROS AZULES - Texto normal${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}📋 COMANDOS PRINCIPALES:${NC}\n"
echo -e "  ${GREEN}sshbot${NC}         - Panel de control"
echo -e "  ${GREEN}pm2 logs sshbot-pro${NC} - Ver logs y QR"
echo -e "  ${GREEN}pm2 restart sshbot-pro${NC} - Reiniciar"
echo -e "\n"

echo -e "${YELLOW}📱 FLUJO DEL SISTEMA HWID:${NC}\n"
echo -e "  1. Usuario paga o pide prueba"
echo -e "  2. Bot pide: ${CYAN}\"Primero, dime tu nombre\"${NC}"
echo -e "  3. Usuario envía nombre"
echo -e "  4. Bot pide: ${CYAN}\"Ahora envía tu HWID\"${NC}"
echo -e "  5. Usuario envía HWID"
echo -e "  6. Sistema activa automáticamente"
echo -e "\n"

echo -e "${YELLOW}⏱️  PRUEBA GRATUITA: ${GREEN}2 HORAS${NC}\n"

echo -e "${YELLOW}💡 FORMATO HWID VÁLIDO:${NC}"
echo -e "  APP-E3E4D5CBB7636907"
echo -e "  APP- + 16 caracteres hexadecimales"
echo -e "\n"

echo -e "${YELLOW}💰 CONFIGURAR MERCADOPAGO:${NC}\n"
echo -e "  1. Ve a: https://www.mercadopago.com.ar/developers"
echo -e "  2. Inicia sesión"
echo -e "  3. Ve a 'Tus credenciales'"
echo -e "  4. Copia 'Access Token PRODUCCIÓN'"
echo -e "  5. En el panel: Opción 7 → Pegar token"
echo -e "  6. Testear con opción 8"
echo -e "\n"

echo -e "${YELLOW}⏰ NOTIFICACIONES DE VENCIMIENTO:${NC}"
echo -e "  • Se envían automáticamente cada hora"
echo -e "  • Avisan 24 horas antes de vencer"
echo -e "  • También avisan cuando ya venció"
echo -e "  • Solo para usuarios premium"
echo -e "\n"

echo -e "${GREEN}${BOLD}¡Sistema HWID listo! Escanea el QR y ya no necesitas usuario/contraseña 🚀${NC}\n"

read -p "$(echo -e "${YELLOW}¿Ver logs ahora? (s/N): ${NC}")" -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "\n${CYAN}Mostrando logs...${NC}"
    echo -e "${YELLOW}📱 Espera el QR para escanear...${NC}\n"
    sleep 2
    pm2 logs sshbot-pro
else
    echo -e "\n${YELLOW}💡 Para iniciar: ${GREEN}sshbot${NC}"
    echo -e "${YELLOW}💡 Para logs: ${GREEN}pm2 logs sshbot-pro${NC}\n"
fi

exit 0