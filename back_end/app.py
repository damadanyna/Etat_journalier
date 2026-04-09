import asyncio
import os

from fastapi import FastAPI
from controller.Credits import Credits
from api.apiCompte import api_router2   
from api.api import api_router
from fastapi.middleware.cors import CORSMiddleware
from socketio import ASGIApp

from socket_manager import socket_manager

fastapi_app = FastAPI()

frontend_port = os.getenv("FRONTEND_PORT", "5173")


# Middleware CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{frontend_port}",
        f"http://127.0.0.1:{frontend_port}",
    ],
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
