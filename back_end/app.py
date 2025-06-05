from fastapi import FastAPI
from controller.Credits import Credits
from api.api import api_router  

app = FastAPI()

# Initialiser la classe Credits
credits = Credits()

# Enregistrer les routes de l'API
app.include_router(api_router, prefix="/api")

# Pour lancer : uvicorn app:app --reload --port 8081
