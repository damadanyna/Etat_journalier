import bcrypt, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Response,Request
from sqlalchemy import text 
import os
from db.db  import DB 
from jose import jwt,JWTError 
 

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 360

class Users: 
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
                    immatricule VARCHAR(50) NOT NULL,
                    privillege VARCHAR(50) NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            conn.execute(text(query))  # exécute la création
            conn.commit()  # commit pour que ça soit pris en compte
            print("[INFO] Table 'users' créée ou déjà existante")
        except Exception as e:
            print(f"[ERREUR] Impossible de créer la table users : {e}")
    
            
    # --- SIGN UP --- 
    def signup(self, username: str, password: str, immatricule: str):
        conn = None
        try:
            conn = self.db.connect()

            # Vérifier si l'utilisateur existe déjà
            query_check = text("SELECT * FROM users WHERE username = :username")
            result = conn.execute(query_check, {"username": username})
            existing = result.mappings().first()
            if existing:
                raise HTTPException(status_code=400, detail="Utilisateur déjà existant")

            # Hacher le mot de passe
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            # Insérer l'utilisateur
            query_insert = text("""
                INSERT INTO users (username, password, immatricule, privillege)
                VALUES (:username, :password, :immatricule, '')
            """)
            conn.execute(query_insert, {
                "username": username,
                "password": hashed_pw,
                "immatricule": immatricule
            })
            conn.commit()

            return {"message": "Utilisateur créé avec succès"}

        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            raise HTTPException(status_code=500, detail="Erreur serveur")
        finally:
            if conn:
                conn.close()

    # --- SIGN IN ---
    
    def signin(self, username: str, password: str):
        conn = None
        try:
            conn = self.db.connect()

            # Vérifier si l'utilisateur existe
            query = text("SELECT * FROM users WHERE username = :username")
            result = conn.execute(query, {"username": username})
            user = result.mappings().first()

            if not user:
                raise HTTPException(status_code=401, detail="Utilisateur introuvable")

            # Vérifier le mot de passe
            if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
                raise HTTPException(status_code=401, detail="Mot de passe incorrect")

            # Générer le JWT
            token_data = {
                "sub": username,
                "privillege": user["privillege"],
                "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            }
            token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

            return {
                "message": "Connexion réussie",
                "access_token": token,
                "token_type": "bearer",
                "user": {"username": username}
            }

        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Erreur serveur")
        finally:
            if conn:
                conn.close()

    
    
    

    def get_current_user(self, request: Request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Non authentifié")

        token = auth_header.split(" ")[1]

        try:
           
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            privillege = payload.get("privillege")
 

            return {"username": username, "privillege": privillege}

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Session expirée")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Token invalide")

            
    # --- LOGOUT ---
    def logout(self, response: Response):
        response.delete_cookie("access_token")
        return {"message": "Déconnexion réussie"}
