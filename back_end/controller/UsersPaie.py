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

class UsersPaie: 
    def __init__(self): 
            self.db = DB()  
            self.create_table("usersPaie")

    def create_table(self, table_name: str):
        try:
            with self.db.connect() as conn:
                # Création table si non existante
                query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        immatricule VARCHAR(50) NOT NULL,
                        privillege VARCHAR(50) NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        validate_at TIMESTAMP NULL,
                        validate_by VARCHAR(255) NULL,
                        validate_status BOOLEAN DEFAULT FALSE,
                        block_by VARCHAR(255) NULL,
                        block_at TIMESTAMP NULL,
                        is_blocked BOOLEAN DEFAULT FALSE
                    )
                """
                conn.execute(text(query))
                conn.commit()
                print(f"[INFO] Table '{table_name}' créée ou déjà existante")
        except Exception as e:
            print(f"[ERREUR] Impossible de créer la table {table_name} : {e}")
    
  
    # --- SIGN UP --- 
    def signup(self, username: str, password: str, immatricule: str):
        conn = None
        try:
            conn = self.db.connect() 
            
            # Vérifier si l'utilisateur existe déjà
            query_check = text("SELECT * FROM usersPaie WHERE username = :username")
            result = conn.execute(query_check, {"username": username})
            existing = result.mappings().first()
            if existing:
                raise HTTPException(status_code=400, detail="Utilisateur déjà existant")

            # Hacher le mot de passe
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            # Insérer l'utilisateur
            query_insert = text("""
                INSERT INTO usersPaie (username, password, immatricule, privillege)
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
            raise HTTPException(status_code=500, detail="Erreur serveur",error=e)
        finally:
            if conn:
                conn.close()
 

    def signin(self, username: str, password: str):
        conn = None
        try:
            conn = self.db.connect()

            # Vérifier si l'utilisateur existe
            query = text("SELECT * FROM usersPaie WHERE username = :username")
            result = conn.execute(query, {"username": username})
            user = result.mappings().first()

            if not user:
                raise HTTPException(status_code=401, detail="Utilisateur introuvable")

            # Vérifier le mot de passe
            if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
                raise HTTPException(status_code=401, detail="Mot de passe incorrect")
            # Vérifier si l'utilisateur est validé
            if not user["validate_status"]:
                raise HTTPException(status_code=403, detail="Compte en attente de validation par un administrateur")

            # Générer le JWT
            token_data = {
                "sub": username,
                "id": user["id"],
                "app": "paie",
                "privillege": user["privillege"],
                "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            }
            token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

            return {
                "message": "Connexion réussie",
                "access_token": token,
                "id": user["id"],
                "token_type": "bearer",
                "user": {"username": username},
                "privilege": user["privillege"]
            }

        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Erreur serveur")
        finally:
            if conn:
                conn.close()

    