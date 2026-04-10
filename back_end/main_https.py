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

# --- Chemins absolus ---
BASE_DIR    = Path(__file__).resolve().parent   # back_end/
PROJECT_DIR = BASE_DIR.parent                   # racine du projet
DIST_DIR    = PROJECT_DIR / "dist"
CERT_DIR    = PROJECT_DIR / "mkcer"

def _resolve(env_var: str, default: Path) -> Path:
    """Résout un chemin depuis .env : absolu tel quel, relatif → depuis BASE_DIR."""
    raw = os.getenv(env_var)
    if raw:
        p = Path(raw)
        return p if p.is_absolute() else (BASE_DIR / p).resolve()
    return default

SSL_CERT = _resolve("SSL_CERT_FILE", CERT_DIR / "aboaly.sipembanque.local+2.pem")
SSL_KEY  = _resolve("SSL_KEY_FILE",  CERT_DIR / "aboaly.sipembanque.local+2-key.pem")

HOST = os.getenv("PROD_HOST", "0.0.0.0")
PORT = int(os.getenv("PROD_PORT", "443"))

# --- Monter le frontend (SPA) sur "/" --- 
# Les routes /api sont déjà enregistrées sur fastapi_app et ont la priorité.
if DIST_DIR.exists():
    fastapi_app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="static")
else:
    print(f"[WARN] Dossier dist/ introuvable ({DIST_DIR}). Lance d'abord : npm run build")

# --- Vérification des certificats ---
if not SSL_CERT.exists():
    print(f"""
[ERREUR] Certificat SSL introuvable : {SSL_CERT}

Génère-le avec (depuis le dossier mkcer/) :
    mkcert aboaly.sipembanque.local 10.192.1.15 localhost

Ou configure SSL_CERT_FILE / SSL_KEY_FILE dans le fichier .env
""")
    sys.exit(1)

if not SSL_KEY.exists():
    print(f"[ERREUR] Clé SSL introuvable : {SSL_KEY}")
    sys.exit(1)

if __name__ == "__main__":
    print(f"""
[INFO] Démarrage serveur HTTPS
  URL     : https://aboaly.sipembanque.local  (ou https://10.192.1.15)
  Port    : {PORT}
  Dist    : {DIST_DIR}
  Cert    : {SSL_CERT}
""")
    # On passe l'objet asgi_app (déjà configuré avec StaticFiles)
    # et NON la chaîne "app:app" qui réimporterait app.py et perdrait le mount.
    uvicorn.run(
        asgi_app,
        host=HOST,
        port=PORT,
        ssl_certfile=str(SSL_CERT),
        ssl_keyfile=str(SSL_KEY),
        reload=False,
    )
