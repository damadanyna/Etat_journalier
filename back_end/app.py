import asyncio
import os

from fastapi import FastAPI
from controller.Credits import Credits
from api.apiCompte import api_router2   
from api.api import api_router
from fastapi.middleware.cors import CORSMiddleware
from socketio import ASGIApp

from config import load_project_env
from socket_manager import socket_manager


load_project_env()

fastapi_app = FastAPI()

frontend_port = os.getenv("FRONTEND_PORT", "5173")
configured_origins = os.getenv("CORS_ALLOW_ORIGINS", "")

default_allowed_origins = [
    f"http://localhost:{frontend_port}", 
    f"http://127.0.0.1:{frontend_port}", 
    "http://10.192.1.15",
    f"http://10.192.1.15:{frontend_port}", 
    "https://aboaly.sipembanque.local",
]

allow_origins = [
    origin.strip()
    for origin in (configured_origins.split(",") if configured_origins else default_allowed_origins)
    if origin.strip()
]


# Middleware CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

 
# Initialiser la classe Credits
credits = Credits()

# Enregistrer les routes de l'API
fastapi_app.include_router(api_router, prefix="/api")

fastapi_app.include_router(api_router2, prefix="/api")


@fastapi_app.on_event("startup")
async def startup_event():
    socket_manager.set_loop(asyncio.get_running_loop())


app = ASGIApp(socket_manager.sio, other_asgi_app=fastapi_app, socketio_path="socket.io")

# Pour lancer : uvicorn app:app --reload --port 8081
