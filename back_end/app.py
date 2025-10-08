from fastapi import FastAPI
from controller.Credits import Credits
from api.api import api_router   
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # ton frontend en local
        "http://127.0.0.1:5173",  # si tu y accèdes depuis un autre PC
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

 
# Initialiser la classe Credits
credits = Credits()

# Enregistrer les routes de l'API
app.include_router(api_router, prefix="/api")

# Pour lancer : uvicorn app:app --reload --port 8081
