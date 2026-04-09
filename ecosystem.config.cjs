/**
 * PM2 ecosystem configuration
 *
 * Premie démarrage :
 *   npm run build          ← génère dist/
 *   pm2 start ecosystem.config.cjs
 *   pm2 save
 *   pm2 startup            ← optionnel : démarrage automatique au boot
 *
 * Certificats (une seule fois) :
 *   cd mkcer
 *   mkcert aboaly.sipembanque.local 10.192.1.15 localhost
 *
 * Rechargement après un build :
 *   npm run build && pm2 restart prod-backend
 */

const path = require('path')
const ROOT = __dirname

module.exports = {
  apps: [
    {
      name: 'prod-backend',
      script: path.join(ROOT, 'back_end', 'main_https.py'),
      interpreter: 'python',
      cwd: path.join(ROOT, 'back_end'),
      env: {
        // Le .env est chargé par config.py au démarrage
      },
      // Redémarre automatiquement si le process crash
      autorestart: true,
      watch: false,
      max_memory_restart: '400M',
      // Logs
      out_file: path.join(ROOT, 'logs', 'backend-out.log'),
      error_file: path.join(ROOT, 'logs', 'backend-err.log'),
      merge_logs: true,
      time: true,
    },
  ],
}
