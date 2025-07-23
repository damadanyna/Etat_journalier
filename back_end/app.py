from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware  # ✅ Compression gzip

from controller.Credits import Credits
from api.api import api_router

app = FastAPI()

# ✅ Middleware GZip pour compresser les grandes réponses JSON (ex: 5 Mo)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ✅ Middleware CORS pour accepter les requêtes cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Initialiser la classe Credits
credits = Credits()

# ✅ Enregistrer les routes de l'API
app.include_router(api_router, prefix="/api")

# ✅ Pour lancer :
# uvicorn app:app --reload --host 0.0.0.0 --port 8000
