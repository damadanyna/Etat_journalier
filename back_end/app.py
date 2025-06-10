from fastapi import FastAPI
from controller.Credits import Credits
from api.api import api_router   
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://192.168.1.212:5173",  # URL de ton frontend
    # Tu peux aussi ajouter d'autres origines ou "*" pour tout autoriser (pas recommandé en prod)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # liste des URLs autorisées
    allow_credentials=True,
    allow_methods=["*"],        # méthodes HTTP autorisées (GET, POST, etc.)
    allow_headers=["*"],        # headers autorisés
)
# Initialiser la classe Credits
credits = Credits()

# Enregistrer les routes de l'API
app.include_router(api_router, prefix="/api")

# Pour lancer : uvicorn app:app --reload --port 8081
