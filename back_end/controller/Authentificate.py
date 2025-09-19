import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Response, Request
import mysql.connector  # exemple avec mysql-connector-python

from db.db  import DB

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"

class Authentificate: 
    def __init__(self):
        # Connexion SQLAlchemy
        self.db = DB()  # objet DB qui expose .connect()

        try:
            conn = self.db.connect()
            query = """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            conn.execute(text(query))  # exécute la création
            conn.commit()  # commit pour que ça soit pris en compte
            print("[INFO] Table 'users' créée ou déjà existante")
        except Exception as e:
            print(f"[ERREUR] Impossible de créer la table users : {e}")
            
    # --- SIGN UP ---
    def signup(self, username: str, password: str):
        # Vérifier si l'utilisateur existe déjà
        self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing = self.cursor.fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Utilisateur déjà existant")

        # Hacher le mot de passe
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Enregistrer en base
        self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
        self.db.commit()

        return {"message": "Utilisateur créé avec succès"}

    # --- SIGN IN ---
    def signin(self, username: str, password: str, response: Response):
        self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = self.cursor.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur introuvable")

        # Vérifier le mot de passe
        if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            raise HTTPException(status_code=401, detail="Mot de passe incorrect")

        # Générer un JWT
        token_data = {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        # Définir le cookie
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="Lax"
        )

        return {"message": "Connexion réussie"}

    # --- LOGOUT ---
    def logout(self, response: Response):
        response.delete_cookie("access_token")
        return {"message": "Déconnexion réussie"}

    # --- CURRENT USER ---
    def get_current_user(self, request: Request):
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Non authentifié")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Session expirée")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token invalide")
