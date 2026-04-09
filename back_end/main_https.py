"""
Serveur de production HTTPS.
Lance FastAPI + Socket.IO + fichiers statiques du frontend (dist/)
sur le port 443 avec les certificats TLS/SSL.

Génération du certificat (une seule fois, depuis le dossier mkcer/) :
    mkcert aboaly.sipembanque.local 10.192.1.15 localhost

Lancement :
    cd back_end
    python main_https.py
Ou via PM2 (ecosystem.config.cjs) :
    pm2 start ecosystem.config.cjs
"""

import os
import sys
import uvicorn
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from app import fastapi_app, app as asgi_app
from config import load_project_env

load_project_env()

# --- Chemins absolus pour les fichiers statiques et les certificats ---
BASE_DIR = Path(__file__).resolve().parent           # back_end/
PROJECT_DIR = BASE_DIR.parent                        # racine du projet

DIST_DIR = PROJECT_DIR / "dist"
CERT_DIR = PROJECT_DIR / "mkcer"

# Certificats (configurable via .env)
SSL_CERT = os.getenv("SSL_CERT_FILE", str(CERT_DIR / "aboaly.sipembanque.local+2.pem"))
SSL_KEY  = os.getenv("SSL_KEY_FILE",  str(CERT_DIR / "aboaly.sipembanque.local+2-key.pem"))

HOST = os.getenv("PROD_HOST", "0.0.0.0")
PORT = int(os.getenv("PROD_PORT", "443"))

# --- Monter le frontend buildé sur "/" (catch-all après les routes /api) ---
if DIST_DIR.exists():
    # html=True → renvoie index.html pour les routes Vue inconnues (SPA)
    fastapi_app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="static")
else:
    print(f"[WARN] Dossier dist/ introuvable ({DIST_DIR}). Lance d'abord : npm run build")

# --- Vérification des certificats ---
if not Path(SSL_CERT).exists():
    print(f"""
[ERREUR] Certificat SSL introuvable : {SSL_CERT}

Pour générer les certificats, exécute :
    cd {CERT_DIR}
    mkcert aboaly.sipembanque.local 10.192.1.15 localhost

Ou configure SSL_CERT_FILE / SSL_KEY_FILE dans le fichier .env
""")
    sys.exit(1)

if not Path(SSL_KEY).exists():
    print(f"[ERREUR] Clé SSL introuvable : {SSL_KEY}")
    sys.exit(1)

if __name__ == "__main__":
    print(f"""
[INFO] Démarrage serveur HTTPS
  URL     : https://aboaly.sipembanque.local (ou https://10.192.1.15)
  Dist    : {DIST_DIR}
  Cert    : {SSL_CERT}
""")
    uvicorn.run(
        "app:app",            # utilise l'app ASGI (FastAPI + Socket.IO)
        host=HOST,
        port=PORT,
        ssl_certfile=SSL_CERT,
        ssl_keyfile=SSL_KEY,
        reload=False,
    )
