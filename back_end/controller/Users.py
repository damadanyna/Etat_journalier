import bcrypt, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Response,Request
from sqlalchemy import text 
import os
from db.db  import DB 
from jose import jwt,JWTError 
 

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600

class Users: 
    def __init__(self): 
            self.db = DB()  # objet DB qui expose .connect()
            self.create_table("users") 

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
                        block_status BOOLEAN DEFAULT FALSE
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

    # --- SIGN UP --- 
    def signupPaie(self, username: str, password: str, immatricule: str):
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
            # Vérifier si l'utilisateur est validé
            if not user["validate_status"]:
                raise HTTPException(status_code=403, detail="Compte en attente de validation par un administrateur")

            # Générer le JWT
            token_data = {
                "sub": username,
                "id": user["id"],

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

    def signinPaie(self, username: str, password: str):
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

    
    def validate_user(self, request: Request, username: str, role: str,admin_password: str):
        conn = None
        try:
            current_user = self.get_current_user(request)
            admin_name = current_user.get("username")
            admin_id = current_user.get("id")

            if current_user.get("privillege") not in ["admin", "superadmin"]:
                raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

            admin_data = self.getUserById(admin_id)["user"]

            if not bcrypt.checkpw(admin_password.encode("utf-8"), admin_data["password"].encode("utf-8")):
                raise HTTPException(status_code=401, detail="Mot de passe administrateur incorrect")

            conn = self.db.connect()
            query = text("""
                UPDATE users
                SET privillege = :role,
                    validate_status = TRUE,
                    validate_by = :admin_name,
                    validate_at = NOW(),
                    block_status = FALSE

                WHERE username = :username
            """)
            result = conn.execute(query, {
            "username": username,
            "admin_name": admin_name,
            "role": role
        })
            conn.commit()

            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Utilisateur introuvable")

            return {"message": f"Utilisateur {username} validé avec succès par {admin_name}"}

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if conn:
                conn.close()
                
                
    def  block_user(self, request: Request, username: str,admin_password: str):
        conn = None
        try:
            current_user = self.get_current_user(request)
            admin_name = current_user.get("username")
            admin_id = current_user.get("id")

            if current_user.get("privillege") not in ["admin", "superadmin"]:
                raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

            admin_data = self.getUserById(admin_id)["user"]

            if not bcrypt.checkpw(admin_password.encode("utf-8"), admin_data["password"].encode("utf-8")):
                raise HTTPException(status_code=401, detail="Mot de passe administrateur incorrect")

            conn = self.db.connect()
            query = text("""
                UPDATE users
                SET 
                    validate_status = FALSE,
                    block_by = :admin_name,
                    block_at = NOW(),
                    block_status = TRUE
                WHERE username = :username
            """)
            result = conn.execute(query, {
            "username": username,
            "admin_name": admin_name,
           
        })
            conn.commit()

            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Utilisateur introuvable")

            return {"message": f"Utilisateur {username} Bloqué avec succès par {admin_name}"}

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if conn:
                conn.close()
                
                
    def update_user_role(self, request: Request, username: str, role: str, admin_password: str):
        conn = None
        try:
            current_user = self.get_current_user(request)
            admin_name = current_user.get("username")
            admin_id = current_user.get("id")

            if current_user.get("privillege") not in ["admin", "superadmin"]:
                raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

            admin_data = self.getUserById(admin_id)["user"]
            if not bcrypt.checkpw(admin_password.encode("utf-8"), admin_data["password"].encode("utf-8")):
                raise HTTPException(status_code=401, detail="Mot de passe administrateur incorrect")

            conn = self.db.connect()
            query = text("""
                UPDATE users
                SET privillege = :role
                WHERE username = :username
            """)
            result = conn.execute(query, {"username": username, "role": role})
            conn.commit()

            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Utilisateur introuvable")

            return {"message": f"Rôle de {username} modifié avec succès par {admin_name}"}

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if conn:
                conn.close()
    
     

    
    def getListeUser(self):
        conn = None
        try:
            conn = self.db.connect()
            query = text("""
                SELECT 
                    id,
                    username,
                    immatricule,
                    privillege,
                    validate_status,
                    validate_by,
                    validate_at,
                    created_at,
                    block_by,
                    block_at,
                    block_status
                FROM users
                ORDER BY created_at DESC
            """)
            result = conn.execute(query)
            users = [dict(row._mapping) for row in result] 
            
            return {"users": users}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des utilisateurs : {e}")
        finally:
            if conn:
                conn.close()
                
                
    def getUserById(self,user_id: int ):
        conn = None
        try:
            conn = self.db.connect()
            query = text("""
                SELECT id, username, password,immatricule, privillege, created_at, validate_by, validate_at,validate_status, block_by, block_at, block_status
                FROM users
                WHERE id = :user_id
            """)
            result = conn.execute(query, {"user_id": user_id}).fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Utilisateur introuvable")

            user_data = dict(result._mapping)

            return {"user": user_data}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
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
            id = payload.get("id")
            app = payload.get("app") 
 
            print("user:", username, "id:", id, "privillege:", privillege   )

            return {"username": username, "id": id, "privillege": privillege, "app": app}
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Session expirée")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Token invalide")

            
    # --- LOGOUT ---
    def logout(self, response: Response):
        response.delete_cookie("access_token")
        return {"message": "Déconnexion réussie"}
    
    #user non valider
    def get_pending_validation_count(self):
        conn = None
        try:
            conn = self.db.connect()
            query = text("SELECT COUNT(*) AS count FROM users WHERE validate_status = FALSE")
            result = conn.execute(query).fetchone()
            return {"count": result[0] if result else 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors du comptage des validations : {e}")
        finally:
            if conn:
                conn.close()
