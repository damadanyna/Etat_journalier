import bcrypt, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Response,Request
from sqlalchemy import text 
import os,io,sys,json,re,string
from config import load_project_env
from db.db  import DB 
from jose import jwt,JWTError 
from werkzeug.utils import secure_filename 
import shutil 
from datetime import date, datetime
from socket_manager import socket_manager


load_project_env()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 360

class UsersPaie: 
    def __init__(self): 
            self.db = DB()  
            self.create_table("usersPaie")
            self.create_table_log("user_activity_log")
            self.upload_folder = 'load_file_paie' 
            self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.trash_folder = os.path.join(self.upload_folder, 'corbeil')
            if not os.path.exists(self.upload_folder):
                os.makedirs(self.upload_folder) 
            if not os.path.exists(self.trash_folder):
                os.makedirs(self.trash_folder)

    def normalize_payroll_period_key(self, value: str):
        raw_value = str(value or '').strip()
        if not raw_value:
            return None

        if re.fullmatch(r"\d{2}-\d{4}", raw_value):
            month, year = raw_value.split('-')
            return f"{month}{year}"

        if re.fullmatch(r"\d{6}", raw_value):
            month = raw_value[:2]
            year = raw_value[2:]
            return f"{month}{year}" if 1 <= int(month) <= 12 else None

        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_value):
            year, month, _day = raw_value.split('-')
            return f"{month}{year}"

        if re.fullmatch(r"\d{4}-\d{2}", raw_value):
            year, month = raw_value.split('-')
            return f"{month}{year}"

        if re.fullmatch(r"\d{8}", raw_value):
            year = raw_value[:4]
            month = raw_value[4:6]
            return f"{month}{year}" if 1 <= int(month) <= 12 else None

        return None

    def format_payroll_period_label(self, value: str):
        normalized_key = self.normalize_payroll_period_key(value)
        if not normalized_key:
            return str(value or '').strip()
        return f"{normalized_key[:2]}-{normalized_key[2:]}"

    def prepare_upload_folder(self, folder_name: str):
        normalized_folder_name = self.format_payroll_period_label(folder_name)
        if not normalized_folder_name:
            raise ValueError("Nom de dossier de paie invalide")

        folder_path = os.path.join(self.upload_folder, normalized_folder_name)
        if os.path.exists(folder_path):
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            trash_target = os.path.join(self.trash_folder, f"{normalized_folder_name}_{timestamp}")
            shutil.move(folder_path, trash_target)

        os.makedirs(folder_path, exist_ok=True)
        return normalized_folder_name

    def create_table(self, table_name: str):
        try:
            with self.db.connect() as conn:
                # Création table si non existante  
                
                query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
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

                immatricule_exists = conn.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM information_schema.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE()
                          AND TABLE_NAME = :table_name
                          AND COLUMN_NAME = 'immatricule'
                        """
                    ),
                    {"table_name": table_name}
                ).scalar()

                matricule_exists = conn.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM information_schema.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE()
                          AND TABLE_NAME = :table_name
                          AND COLUMN_NAME = 'matricule'
                        """
                    ),
                    {"table_name": table_name}
                ).scalar()

                if not immatricule_exists:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN immatricule VARCHAR(50) NULL AFTER email"))

                if matricule_exists:
                    conn.execute(
                        text(
                            f"""
                            UPDATE {table_name}
                            SET immatricule = matricule
                            WHERE immatricule IS NULL OR immatricule = ''
                            """
                        )
                    )

                conn.commit()
                print(f"[INFO] Table '{table_name}' créée ou déjà existante")
        except Exception as e:
            print(f"[ERREUR] Impossible de créer la table {table_name} : {e}")
    
   
    def create_table_log(self, table_name: str):
        try:
            with self.db.connect() as conn:
                # Création table si non existante  
                
                query = f"""
                   CREATE TABLE IF NOT EXISTS {table_name} (
                        id INT AUTO_INCREMENT PRIMARY KEY, 
                        user_id VARCHAR(100) NOT NULL, 
                        action VARCHAR(100) NOT NULL,
                        entity_type VARCHAR(100) NOT NULL, 
                        description TEXT NULL,    
                        old_value JSON NULL,                    
                        new_value JSON NULL,   
                        ip_address VARCHAR(45) NULL,
                        user_agent TEXT NULL, 
                        status TEXT DEFAULT 'SUCCESS', 
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ) 
                """
                conn.execute(text(query))
                conn.commit()
                print(f"[INFO] Table '{table_name}' créée ou déjà existante")
        except Exception as e:
            print(f"[ERREUR] Impossible de créer la table {table_name} : {e}")
    
   
    # --- SIGN UP --- 
    def signup(self, username: str,email:str, password: str, immatricule: str, ip_address: str):
        conn = None
        try:
            conn = self.db.connect() 
            
            # Vérifier si l'utilisateur existe déjà
            query_check = text("SELECT * FROM usersPaie WHERE username = :username OR email = :email OR immatricule = :immatricule")
            result = conn.execute(query_check, {"username": username, "email": email, "immatricule": immatricule})
            existing = result.mappings().first()
            if existing:
                raise HTTPException(status_code=400, detail="Utilisateur déjà existant")

            # Hacher le mot de passe
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            # Insérer l'utilisateur
            query_insert = text("""
                INSERT INTO usersPaie (username, password, email, immatricule, privillege)
                VALUES (:username, :password, :email, :immatricule, '')
            """)
            conn.execute(query_insert, {
                "username": username,
                "email": email,
                "password": hashed_pw,
                "immatricule": immatricule
            })
            conn.commit()
            
            self.saveEvent(user_id= immatricule, action="signup", entity_type="user", description=f"Inscription de l'utilisateur {username} (immatricule : {immatricule})", old_value=None, new_value=json.dumps({"username": username, "email": email, "immatricule": immatricule}), ip_address=ip_address, user_agent=None)
            pending_count = self.get_pending_validation_count().get("count", 0)
            socket_manager.emit_pending_validation_update_sync(pending_count)
        

            return {"message": "Utilisateur créé avec succès"}

        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur serveur: {e}")
        finally:
            if conn:
                conn.close()
 
    def saveEvent(self,user_id:str,action:str,entity_type:str,description:str,old_value:str,new_value:str,ip_address:str,user_agent:str,status:str = "SUCCESS"):
        conn = None
        try:
            conn = self.db.connect() 
            query_insert = text("""
                INSERT INTO user_activity_log ( user_id,action,entity_type,description,old_value,new_value,ip_address,user_agent,status)
                VALUES (:user_id,:action,:entity_type,:description,:old_value,:new_value,:ip_address,:user_agent,:status)
            """)
            conn.execute(query_insert, {
                "user_id": user_id,
                "action": action,
                "entity_type": entity_type,
                "description": description,
                "old_value": old_value,
                "new_value": new_value,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "status": status
            })
            conn.commit()
            socket_manager.emit_user_activity_update_sync({
                "app": "paie",
                "user_id": user_id,
                "action": action,
                "entity_type": entity_type,
                "description": description,
                "old_value": old_value,
                "new_value": new_value,
                "ip_address": ip_address,
                "status": status,
                "created_at": datetime.utcnow().isoformat(),
            })
        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur serveur: {e}")
        finally:
            if conn:
                conn.close()
 

    def signin(self, immatricule: str, password: str, ip_address: str = None):
        conn = None
        try:
            conn = self.db.connect()

            # Vérifier si l'utilisateur existe
            query = text("SELECT * FROM usersPaie WHERE immatricule = :immatricule")
            result = conn.execute(query, {"immatricule": immatricule})
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
                "sub": immatricule,
                "id": user["id"],
                "app": "paie",
                "privillege": user["privillege"],
                "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            }
            token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
            
            self.saveEvent(user_id= immatricule, action="signin", entity_type="user", description=f"Connexion de l'utilisateur {immatricule}", old_value=None, new_value=json.dumps({"username": user["username"], "email": user["email"], "immatricule": immatricule}), ip_address=ip_address, user_agent=None)

            return {
                "message": "Connexion réussie",
                "access_token": token,
                "id": user["id"],
                "token_type": "bearer",
                "user": {"immatricule": immatricule},
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
        
    
    # --- LOGOUT ---
    def logout(self, response: Response, ip_address: str = None,matricule:str = None):
        response.delete_cookie("access_token")
        self.saveEvent(user_id=matricule, action="logout", entity_type="user", description=f"Déconnexion de l'utilisateur {matricule}", old_value=None, new_value=None, ip_address=ip_address, user_agent=None)
        return {"message": "Déconnexion réussie"}

    def change_own_password(self, request: Request, current_password: str, new_password: str, ip_address: str = None):
        conn = None
        try:
            current_user = self.get_current_user(request)
            immatricule = current_user.get("username")

            conn = self.db.connect()
            query = text("SELECT * FROM usersPaie WHERE immatricule = :immatricule")
            result = conn.execute(query, {"immatricule": immatricule})
            user = result.mappings().first()

            if not user:
                raise HTTPException(status_code=404, detail="Utilisateur introuvable")

            if not bcrypt.checkpw(current_password.encode("utf-8"), user["password"].encode("utf-8")):
                raise HTTPException(status_code=401, detail="Ancien mot de passe incorrect")

            hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            conn.execute(
                text("UPDATE usersPaie SET password = :password WHERE immatricule = :immatricule"),
                {"password": hashed_pw, "immatricule": immatricule}
            )
            conn.commit()

            self.saveEvent(
                user_id=immatricule,
                action="change_own_password",
                entity_type="user",
                description=f"Mot de passe modifié par l'utilisateur {immatricule}",
                old_value=None,
                new_value=None,
                ip_address=ip_address,
                user_agent=request.headers.get("user-agent"),
            )

            return {"message": "Mot de passe mis à jour avec succès"}
        except HTTPException as http_err:
            raise http_err
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if conn:
                conn.close()
    
    # --- LOGOUT ---
    def downloadpaie(self, response: Response, ip_address: str = None,matricule:str = None, file_id:str = None):
        response.delete_cookie("access_token")
        self.saveEvent(user_id=matricule, action="download_paie", entity_type="fichier_paie", description=f"Téléchargement de la fiche de paie de {matricule} (fichier : {file_id})", old_value=None, new_value=None, ip_address=ip_address, user_agent=None)
        return {"message": "Téléchargement réussie"}
    
                
    def upload_file_manual_in_detail(self, file, folder_name=None, current=None, total=None):
        original_filename = getattr(file, 'filename', None)
        if not file or not original_filename or not self.allowed_file(original_filename):
            yield {"status": "error", "file": str(file), "message": "Format invalide"}
            return

        original_filename = secure_filename(original_filename)

        # 📌 Forcer le nom du fichier
        _, ext = os.path.splitext(original_filename)
        filename = f"etat_detaille{ext}"

        normalized_folder_name = self.format_payroll_period_label(folder_name) if folder_name else None
        folder_path = os.path.join(self.upload_folder, normalized_folder_name) if normalized_folder_name else self.upload_folder
        os.makedirs(folder_path, exist_ok=True)

        final_filepath = os.path.join(folder_path, filename)
        backup_filepath = None

        try:
            yield {
                "status": "info",
                "file": filename,
                "message": "Lecture du fichier en cours..."
            }

            # 🔍 Lecture du fichier
            if hasattr(file, 'read'):
                file_content = file.read()
            elif hasattr(file, 'file') and hasattr(file.file, 'read'):
                file_content = file.file.read()
            else:
                raise IOError(f"Type de fichier non supporté: {type(file)}")

            if not isinstance(file_content, bytes):
                file_content = (
                    file_content.encode("utf-8")
                    if isinstance(file_content, str)
                    else bytes(file_content)
                )

            total_size = len(file_content)

            yield {
                "status": "info",
                "file": filename,
                "message": f"Fichier lu: {total_size / (1024 * 1024):.2f} MB. Écriture en cours..."
            }

            # Déplacer l'ancien fichier vers la corbeille avant écriture
            if os.path.exists(final_filepath):
                trash_target_folder = os.path.join(self.trash_folder, normalized_folder_name or 'sans_dossier')
                os.makedirs(trash_target_folder, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                backup_filepath = os.path.join(trash_target_folder, f"{timestamp}_{filename}")
                shutil.move(final_filepath, backup_filepath)

            chunk_size = 1024 * 1024  # 1 MB
            written_size = 0

            with open(final_filepath, "wb") as f:
                content_buffer = io.BytesIO(file_content)

                while chunk := content_buffer.read(chunk_size):
                    f.write(chunk)
                    f.flush()
                    written_size += len(chunk)

                    yield {
                        "status": "progress",
                        "file": filename,
                        "current": current,
                        "total": total,
                        "received_mb": round(written_size / (1024 * 1024), 2),
                        "total_mb": round(total_size / (1024 * 1024), 2),
                        "percentage_file": round((written_size / total_size) * 100, 2),
                        "message": (
                            f"[Serveur] Écrit {written_size / (1024 * 1024):.2f} / "
                            f"{total_size / (1024 * 1024):.2f} MB"
                        )
                    }

                f.flush()
                os.fsync(f.fileno())

            # ❌ Vérification taille
            if written_size != total_size:
                if backup_filepath and os.path.exists(backup_filepath):
                    shutil.move(backup_filepath, final_filepath)

                yield {
                    "status": "error",
                    "file": filename,
                    "message": f"Erreur d'écriture: {written_size} / {total_size} octets"
                }
                return

            yield {
                "status": "success",
                "file": filename,
                "received_mb": round(total_size / (1024 * 1024), 2),
                "message": (
                    f"✅ Fichier {filename} transféré avec succès "
                    f"({total_size / (1024 * 1024):.2f} MB)"
                )
            }

        except Exception as e:
            if backup_filepath and os.path.exists(backup_filepath):
                try:
                    shutil.move(backup_filepath, final_filepath)
                except Exception as restore_error:
                    yield {
                        "status": "warning",
                        "file": filename,
                        "message": f"Erreur et impossible de restaurer le backup: {restore_error}"
                    }

            yield {
                "status": "error",
                "file": filename,
                "message": f"Erreur lors de l'upload: {e}"
            }

        finally:
            pass


    
    # def upload_file_manual_in_detail(self, file, folder_name=None, current=None, total=None):
    #     filename = getattr(file, 'filename', None)
    #     if not file or not filename or not self.allowed_file(filename):
    #         yield {"status": "error", "file": str(file), "message": "Format invalide"}
    #         return

    #     filename = secure_filename(filename)
    #     folder_path = os.path.join(self.upload_folder, folder_name) if folder_name else self.upload_folder
    #     os.makedirs(folder_path, exist_ok=True)

    #     final_filepath = os.path.join(folder_path, filename)
    #     backup_filepath = None

    #     try:
    #         yield {"status": "info", "file": filename, "message": "Lecture du fichier en cours..."}
    #         # Lecture du contenu - méthode synchrone (suppose que file.read() est synchrone)
    #         if hasattr(file, 'read'):
    #             file_content = file.read()
    #         elif hasattr(file, 'file') and hasattr(file.file, 'read'):
    #             file_content = file.file.read()
    #         else:
    #             raise IOError(f"Type de fichier non supporté: {type(file)}")

    #         if not isinstance(file_content, bytes):
    #             file_content = file_content.encode('utf-8') if isinstance(file_content, str) else bytes(file_content)

    #         total_size = len(file_content)
    #         yield {
    #             "status": "info",
    #             "file": filename,
    #             "message": f"Fichier lu: {total_size / (1024 * 1024):.2f} MB. Écriture en cours..."
    #         }

    #         if os.path.exists(final_filepath):
    #             backup_filepath = final_filepath + '.backup'
    #             shutil.copy2(final_filepath, backup_filepath)

    #         chunk_size = 1024 * 1024  # 1 MB
    #         written_size = 0

    #         with open(final_filepath, 'wb') as f:
    #             content_buffer = io.BytesIO(file_content)
    #             while chunk := content_buffer.read(chunk_size):
    #                 f.write(chunk)
    #                 f.flush()
    #                 written_size += len(chunk)

    #                 yield {
    #                     "status": "progress",
    #                     "file": filename,
    #                     "current": current,
    #                     "total": total,
    #                     "received_mb": round(written_size / (1024 * 1024), 2),
    #                     "total_mb": round(total_size / (1024 * 1024), 2),
    #                     "percentage_file": round((written_size / total_size) * 100, 2),
    #                     "message": f"[Serveur] Écrit {written_size / (1024 * 1024):.2f} / {total_size / (1024 * 1024):.2f} MB"
    #                 }

    #             f.flush()
    #             os.fsync(f.fileno())

    #         if written_size != total_size:
    #             if backup_filepath and os.path.exists(backup_filepath):
    #                 shutil.move(backup_filepath, final_filepath)
    #             yield {
    #                 "status": "error",
    #                 "file": filename,
    #                 "message": f"Erreur d'écriture: {written_size} / {total_size} octets"
    #             }
    #             return

    #         if backup_filepath and os.path.exists(backup_filepath):
    #             os.remove(backup_filepath)

    #         yield {
    #             "status": "success",
    #             "file": filename,
    #             "received_mb": round(total_size / (1024 * 1024), 2),
    #             "message": f"✅ Fichier {filename} transféré avec succès ({total_size / (1024 * 1024):.2f} MB)"
    #         }

    #     except Exception as e:
    #         if backup_filepath and os.path.exists(backup_filepath):
    #             try:
    #                 shutil.move(backup_filepath, final_filepath)
    #             except Exception as restore_error:
    #                 yield {
    #                     "status": "warning",
    #                     "file": filename,
    #                     "message": f"Erreur et impossible de restaurer le backup: {str(restore_error)}"
    #                 }

    #         yield {
    #             "status": "error",
    #             "file": filename,
    #             "message": f"Erreur lors de l'upload: {str(e)}"
    #         }

    #     finally:
    #         if backup_filepath and os.path.exists(backup_filepath):
    #             try:
    #                 os.remove(backup_filepath)
    #             except:
    #                 pass
    
    
    def allowed_file(self, filename):
        """
        Vérifie si l'extension du fichier est autorisée
        """
        ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
        if '.' in filename:
            ext = filename.rsplit('.', 1)[1].lower()
            print("Extension détectée:", ext)
            return ext in ALLOWED_EXTENSIONS
        return False
       
       
    def show_files(self, app=None):
        """
        Renvoie une structure arborescente des sous-dossiers de `upload_folder/app`
        compatible avec Vuetify <v-treeview>, sans inclure le dossier racine.
        """

        base_folder = self.upload_folder
        if not os.path.exists(base_folder):
            return []

        tree = []

        for root, dirs, files in os.walk(base_folder):
            dirs[:] = [directory for directory in dirs if directory.lower() != 'corbeil']
            # On saute la racine : on ne veut afficher que les sous-dossiers
            if root == base_folder:
                continue
            relative_path = os.path.relpath(root, base_folder).replace("\\", "/")
            path_parts = relative_path.split('/') if relative_path != '.' else []
            # Liste des fichiers CSV
            csv_files = [
                {"title": f, "file": True}
                for f in files
                if f.lower().endswith('.xlsx')
            ]

            if not csv_files:
                continue  # On ignore les dossiers sans fichiers CSV
            # Construction arborescente
            current_level = tree
            for part in path_parts:
                folder = next((item for item in current_level if item.get("folder_name") == part and not item.get("file")), None)
                if not folder:
                    folder = {
                        "title": self.format_payroll_period_label(part),
                        "folder_name": part,
                        "children": []
                    }
                    current_level.append(folder)
                current_level = folder["children"]

            current_level.extend(csv_files)

        return tree
       
       
    def create_history_table(self):
        conn = self.db.connect()
        """
        Crée la table `history_insert_paie` si elle n'existe pas déjà.
        """
        create_query = """
        CREATE TABLE IF NOT EXISTS `history_insert_paie` ( 
            `label` VARCHAR(255) NOT NULL PRIMARY KEY,
            `stat_of` VARCHAR(100),
            `used` TINYINT(1) DEFAULT 0,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `dav_status` Boolean DEFAULT FALSE,
            `dat_status` Boolean DEFAULT FALSE,
            `epr_status`  Boolean DEFAULT FALSE,
            `stat_compte` Boolean DEFAULT FALSE
        );
        """
        conn.execute(text(create_query))
    
    
    def getListeUser(self): 
        conn = None
        try:
            conn = self.db.connect()
            query = text("""
                SELECT 
                   *
                FROM usersPaie
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
    
    def get_pending_validation_count(self):
        conn = None
        try:
            conn = self.db.connect()
            query = text("SELECT COUNT(*) AS count FROM usersPaie WHERE validate_status = FALSE")
            result = conn.execute(query).fetchone()
            return {"count": result[0] if result else 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors du comptage des validations : {e}")
        finally:
            if conn:
                conn.close()
                
                
    def getUserById(self,user_id: int ):
        conn = None
        try:
            conn = self.db.connect()
            query = text("""
                SELECT *
                FROM usersPaie
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
                UPDATE usersPaie
                SET privillege = :role,
                    validate_status = TRUE,
                    validate_by = :admin_name,
                    validate_at = NOW(),
                    block_status = FALSE 
                WHERE username = :username
                """)
            result = conn.execute(query, {"username": username,"admin_name": admin_name,"role": role})
            conn.commit()

            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Utilisateur introuvable")

            pending_count = self.get_pending_validation_count().get("count", 0)
            socket_manager.emit_pending_validation_update_sync(pending_count)

            self.saveEvent(
                user_id=admin_name,
                action="validate_user",
                entity_type="user",
                description=f"Validation de l'utilisateur {username} avec le rôle '{role}' par {admin_name}",
                old_value=None,
                new_value=json.dumps({"username": username, "role": role}),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )

            return {"message": f"Utilisateur {username} validé avec succès par {admin_name}"}

        except HTTPException as e:
            print("[ERREUR] ", e)
            raise e
        except Exception as e:
            print("[ERREUR] ICI ", e)
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if conn:
                conn.close()
                
                                       
    def update_user_role(self, request: Request, colab_lastname:str, colab_immatricule:str, user_id: str, role: str, admin_password: str):
        conn = None
        try:
            current_user = self.get_current_user(request)
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
                UPDATE usersPaie
                SET privillege = :role, 
                    username = :colab_lastname,
                    immatricule = :colab_immatricule
                WHERE id = :user_id
            """)
            result = conn.execute(query, {"colab_lastname": colab_lastname,"colab_immatricule": colab_immatricule,"user_id": user_id, "role": role})
            conn.commit()

            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Utilisateur introuvable")

            self.saveEvent(
                user_id=admin_name,
                action="update_user_role",
                entity_type="user",
                description=f"Modification du rôle de {colab_lastname} (immatricule : {colab_immatricule}) en '{role}' par {admin_name}",
                old_value=None,
                new_value=json.dumps({"user_id": user_id, "colab_immatricule": colab_immatricule, "role": role}),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )

            return {"message": f"Rôle de {user_id} modifié avec succès par {admin_name}"}

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if conn:
                conn.close()

    def update_user_pwd_paie(self, request: Request, colab_pwd:str, colab_immatricule:str, user_id: str,   admin_password: str,matricule: str, ip_address: str,immatricule:str):
        conn = None
        try:
            current_user = self.get_current_user(request)
            current_user = self.get_current_user(request)
            admin_name = current_user.get("username")
            admin_id = current_user.get("id")

            if current_user.get("privillege") not in ["admin", "superadmin"]:
                raise HTTPException(status_code=403, detail="Accès refusé : privilège insuffisant")

            admin_data = self.getUserById(admin_id)["user"]
            if not bcrypt.checkpw(admin_password.encode("utf-8"), admin_data["password"].encode("utf-8")):
                raise HTTPException(status_code=401, detail="Mot de passe administrateur incorrect")
    
            hashed_pw = bcrypt.hashpw(colab_pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            conn = self.db.connect()
            query = text("""
                UPDATE usersPaie
                SET password = :password
                WHERE id = :user_id
            """)
            
            result = conn.execute(query, {"password": hashed_pw,"user_id": user_id})
            conn.commit()
            
            
            self.saveEvent(user_id= matricule, action="update_password", entity_type=immatricule, description=f"Mot de passe mis à jour pour {colab_immatricule} par {matricule}", old_value=None, new_value=None, ip_address=ip_address, user_agent=None)

          
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Utilisateur introuvable")

            return {"message": f"Rôle de {user_id} modifié avec succès par {admin_name}"}

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
                UPDATE usersPaie
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

            pending_count = self.get_pending_validation_count().get("count", 0)
            socket_manager.emit_pending_validation_update_sync(pending_count)

            self.saveEvent(
                user_id=admin_name,
                action="block_user",
                entity_type="user",
                description=f"Blocage de l'utilisateur {username} par {admin_name}",
                old_value=None,
                new_value=json.dumps({"username": username}),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )

            return {"message": f"Utilisateur {username} Bloqué avec succès par {admin_name}"}

        except HTTPException as e:
            raise e
        except Exception as e:
            print("error -----------> ", e)
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



    def insert_into_history_table(self, label_value: str, used: int = 1, stat_of=None):
        try:
            conn = self.db.connect()
            raw_label = str(label_value or '').strip()
            normalized_label = self.format_payroll_period_label(label_value)

            # Étape 1 : mettre tous les used = 0
            reset_query = "UPDATE `history_insert_paie` SET `used` = 0"
            conn.execute(text(reset_query))

            if raw_label and raw_label != normalized_label:
                conn.execute(
                    text("DELETE FROM `history_insert_paie` WHERE `label` = :legacy_label"),
                    {"legacy_label": raw_label}
                )

            # Étape 2 : insérer ou mettre à jour la ligne ciblée
            upsert_query = """
                INSERT INTO `history_insert_paie` (`label`, `stat_of`, `used`)
                VALUES (:label, :stat_of, :used)
                ON DUPLICATE KEY UPDATE
                    stat_of = VALUES(stat_of),
                    used = VALUES(used),
                    created_at = CURRENT_TIMESTAMP
            """
            conn.execute(text(upsert_query), {
                "label": normalized_label,
                "stat_of": stat_of,
                "used": used
            })

            conn.commit()
            print(f"[INFO] Mise à jour réussie de history_insert_paie, actif: {normalized_label}")
            socket_manager.emit_payroll_date_update_sync(normalized_label, stat_of, used)

        except Exception as e:
            print(f"[ERREUR] Erreur lors de la mise à jour de history_insert_paie : {e}")
            try:
                conn.rollback()
            except:
                pass
        finally:
            try:
                if conn:
                    conn.close()
            except Exception as close_err:
                print(f"[ERREUR] Fermeture de la connexion échouée : {close_err}")
                
    
    def nettoyer_nom_fichier(self,filename):
            # Enlever l'extension
            nom_sans_ext = os.path.splitext(filename)[0] 
            # Remplacer les ponctuations par '_'
            nom_remplace = re.sub(f"[{re.escape(string.punctuation)}]", "_", nom_sans_ext)
            # Enlever les chiffres
            nom_sans_chiffres = re.sub(r"\d+", "", nom_remplace)
            # Tout en minuscules
            nom_final = nom_sans_chiffres.lower()
            # Nettoyage double underscore éventuel
            nom_final = re.sub(r"_+", "_", nom_final).strip("_")
            return nom_final
        
        
    
    def load_file_excel_in_database(self, filename: str, folder: str, str_date: str):
        """
        Charge un fichier Excel (.xlsx) depuis './load_file/{folder}/{filename}'
        et l'insère dans la base MySQL avec progression en temps réel.
        La table créée sera : {folder}_{nomFichierSansExtension}_{str_date}
        """

        import openpyxl
        import os
        import json
        import re
        from sqlalchemy import text

        def progress_generator(): 
            conn = None
            workbook = None

            # Fonction locale pour nettoyer le nom de fichier
            def nettoyer_nom_fichier(nom):
                """Nettoie le nom de fichier pour créer un nom de table SQL valide"""
                # Remplacer les espaces et caractères spéciaux par des underscores
                nom = re.sub(r'[^\w]', '_', nom)
                # Supprimer les underscores multiples
                nom = re.sub(r'_+', '_', nom)
                # Supprimer les underscores au début et à la fin
                nom = nom.strip('_')
                # Convertir en minuscules
                nom = nom.lower()
                # Limiter la longueur (MySQL max 64 caractères)
                if len(nom) > 50:
                    nom = nom[:50]
                # S'assurer que ça ne commence pas par un chiffre
                if nom and nom[0].isdigit():
                    nom = 'tbl_' + nom
                return "ETAT_DETAILLE" 

            # Nom de table
            normalized_period_key = self.normalize_payroll_period_key(str_date)
            if not normalized_period_key:
                yield json.dumps({
                    "status": "error",
                    "message": f"Période invalide : {str_date}",
                    "filename": filename
                })
                return

            table_name = f"etat_detaille_{normalized_period_key}"
            # table_name = nettoyer_nom_fichier(table_name)
            header_table=[]
            
            # print(f"[INFO]---------------> {f"{filename_clean}_{str_date}"} en cours...")
            # print(f"[INFO]---------------> {table_name} en cours...")

            try:
                # 1) Vérification fichier
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                folder_path = os.path.join(project_root, self.upload_folder, folder)
            
                if not os.path.exists(folder_path):
                    yield json.dumps({
                        "status": "error",
                        "message": f"[ERREUR] Le répertoire {folder_path} n'existe pas",
                        "filename": filename
                    })
                    return

                filepath = os.path.join(folder_path, filename)

                if not os.path.exists(filepath):
                    yield json.dumps({
                        "status": "error",
                        "message": f"[ERREUR] Fichier {filename} introuvable dans {folder_path}",
                        "filename": filename
                    })
                    return

                yield json.dumps({
                    "status": "info", 
                    "message": f"Fichier détecté : {filepath}",
                    "filename": filename
                })

                # 2) Lecture Excel
                yield json.dumps({
                    "status": "info", 
                    "message": "Lecture du fichier Excel...",
                    "filename": filename
                })

                try:
                    workbook = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
                    sheet = workbook.active
                except Exception as e:
                    yield json.dumps({
                        "status": "error",
                        "message": f"Impossible de lire Excel : {str(e)}",
                        "filename": filename
                    })
                    return

                # Lecture headers
                try:
                    rows_iter = sheet.iter_rows(values_only=True)
                    headers_raw = next(rows_iter)
                                        
                    # Ignorer les 7 premières lignes
                    for _ in range(6):
                        next(rows_iter)

                    # Récupérer la 8ème ligne
                    header_table=next(rows_iter)
                    # ligne_8 = next(rows_iter)
                    print("8ème ligne :", header_table)
                    # print('[INFO] En-tetes detectees :', headers_raw)
                except StopIteration:
                    if workbook:
                        workbook.close()
                    yield json.dumps({
                        "status": "error",
                        "message": "[ERREUR] Feuille Excel vide : aucune ligne détectée",
                        "filename": filename
                    })
                    return
                except Exception as e:
                    if workbook:
                        workbook.close()
                    yield json.dumps({
                        "status": "error",
                        "message": f"[ERREUR] Impossible de lire les en-têtes : {str(e)}",
                        "filename": filename
                    })
                    return

                # Nettoyage des headers
                headers = []
                for i, col in enumerate(header_table):
                    col = str(col).strip() if col not in (None, "") else f"colonne_{i+1}"
                    col = col.replace('.', '_').replace(' ', '_').lower().replace('  ', '_').lower().replace('__', '_')
                    col = ''.join(c if c.isalnum() or c == '_' else '_' for c in col)
                    # Sécurité : si vide ou commence par chiffre
                    if not col or col[0].isdigit():
                        col = f"col_{i+1}"
                    headers.append(col)
                # print('----------------------------------')
                # print('[INFO] En-tetes nettoyes :', headers)
                # Gestion des headers dupliqués
                new_headers = []
                count_map = {}
                for h in headers:
                    if h not in count_map:
                        count_map[h] = 0
                        new_headers.append(h)
                    else:
                        count_map[h] += 1
                        new_headers.append(f"{h}_{count_map[h]}")
                headers = new_headers
                # print('------------------------------------')
                # print("[INFO] En-tetes nettoyes : ", headers)
                # Lecture des lignes de données
                data_rows = []
                row_count = 0
                # Commencer à la ligne 9 (après les 7 lignes de métadonnées + 1 ligne d'en-têtes)
                for row in sheet.iter_rows(min_row=9, values_only=True):
                    cleaned_row = ["" if v is None else str(v).strip() for v in row]
                    data_rows.append(cleaned_row)
                    row_count += 1
                    if row_count % 1000 == 0:
                        yield json.dumps({
                            "status": "reading",
                            "task": "Lecture Excel",
                            "row_count": row_count,
                            "message": f"Lecture Excel : {row_count} lignes",
                            "filename": filename
                        })

                if workbook:
                    workbook.close()

                yield json.dumps({
                    "status": "info",
                    "task": "Lecture terminée",
                    "row_count": row_count,
                    "total": row_count,
                    "message": f"Lecture terminée : {row_count} lignes.",
                    "filename": filename
                })

                # Merge colonnes si méthode disponible
                if hasattr(self, 'merge_duplicate_columns'):
                    headers, data_rows = self.merge_duplicate_columns(headers, data_rows)

                # 3) Connexion DB
                try:
                    conn = self.db.connect()
                except Exception as e:
                    yield json.dumps({
                        "status": "error",
                        "message": f"Connexion DB impossible : {str(e)}",
                        "filename": filename
                    })
                    return

                # 4) Drop + create table
                yield json.dumps({
                    "status": "info",
                    "task": "Création table",
                    "message": f"Suppression ancienne table {table_name}",
                    "filename": filename
                })

                conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`;"))

                cols_sql = ", ".join([f"`{h}` TEXT" for h in headers])
                conn.execute(text(f"CREATE TABLE `{table_name}` ({cols_sql});"))
                conn.commit()

                yield json.dumps({
                    "status": "info",
                    "task": "Table créée",
                    "message": f"Table {table_name} créée avec succès.",
                    "table_name": table_name,
                    "filename": filename
                })

                # 5) Insert par batch
                total_rows = len(data_rows)
                if total_rows == 0:
                    yield json.dumps({
                        "status": "success",
                        "task": "Terminé",
                        "message": f"Table `{table_name}` créée mais aucune ligne à insérer.",
                        "table_name": table_name,
                        "total": 0,
                        "total_inserted": 0,
                        "filename": filename,
                        "fait": True
                    })
                    conn.commit()
                    return

                batch_size = 5000
                placeholders = ", ".join([f":val{j}" for j in range(len(headers))])
                insert_query = text(f"INSERT INTO `{table_name}` VALUES ({placeholders})")

                inserted_count = 0
                for start in range(0, total_rows, batch_size):
                    end = min(start + batch_size, total_rows)
                    batch = data_rows[start:end]

                    # Normalisation des lignes
                    cleaned_batch = []
                    for row in batch:
                        if len(row) < len(headers):
                            row = row + [""] * (len(headers) - len(row))
                        elif len(row) > len(headers):
                            row = row[:len(headers)]
                        cleaned_batch.append(row)

                    # Création des paramètres
                    params = [
                        {f"val{j}": cleaned_batch[i][j] for j in range(len(headers))}
                        for i in range(len(cleaned_batch))
                    ]

                    conn.execute(insert_query, params)
                    conn.commit()
                    
                    inserted_count = end
                    percentage = round((end / total_rows) * 100, 2)
                    yield json.dumps({
                        "status": "inserting",
                        "task": "Insertion en cours",
                        "current": end,
                        "total": total_rows,
                        "percentage": percentage,
                        "message": f"Insertion : {end}/{total_rows} ({percentage}%)",
                        "filename": filename
                    })

                yield json.dumps({
                    "status": "success",
                    "task": "Terminé",
                    "message": f"{total_rows} lignes insérées dans `{table_name}`.",
                    "table_name": table_name,
                    "total": total_rows,
                    "total_inserted": total_rows,
                    "filename": filename,
                    "fait": True
                })

            except Exception as e:
                if conn:
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                yield json.dumps({
                    "status": "critical_error",
                    "message": f"Erreur inattendue : {str(e)}",
                    "filename": filename
                })
            finally:
                if conn:
                    try:
                        conn.close()
                    except Exception:
                        pass
                if workbook:
                    try:
                        workbook.close()
                    except Exception:
                        pass

        return progress_generator()
    
    
      
    def get_history_insert(self):
        conn = None 
        try:  
            query = text("""  SELECT * FROM `history_insert_paie` ORDER BY `created_at` DESC, `label` DESC """) 
            conn = self.db.connect()
            result = conn.execute(query )
            columns = result.keys()
            data = [dict(zip(columns, row)) for row in result.fetchall()]

            for item in data:
                item["label"] = self.format_payroll_period_label(item.get("label"))

            return {"data": data}

        except Exception as e:
            print(f"[ERREUR] Impossible d’exécuter la requête : {e}")
            return None

        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture de connexion échouée : {close_err}")
    
    def get_users(self, matricule: str = None, dateStr: str = None):
        """
        Récupère les utilisateurs depuis une table dynamique selon dateStr.
        Exemple : dateStr='20251101' → table = etat_detaille_20251101
        """
        if not dateStr:
            raise ValueError("Le paramètre dateStr est requis pour déterminer la table.")

        normalized_period_key = self.normalize_payroll_period_key(dateStr)
        if not normalized_period_key:
            raise ValueError("dateStr doit être un format de période valide (MM-AAAA, MMAAAA, YYYY-MM-DD ou YYYYMMDD)")

        table_name = f"etat_detaille_{normalized_period_key}"

        conn = None
        try:
            conn = self.db.connect()

            table_exists = conn.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = :table_name
                    """
                ),
                {"table_name": table_name}
            ).scalar()

            if not table_exists:
                return {
                    "count": 0,
                    "users": []
                }

            # Construire la requête dynamiquement
            if matricule:
                query = text(f"SELECT * FROM {table_name} WHERE matricule = :mat")
                print(query)
                result = conn.execute(query, {"mat": matricule})
            else:
                query = text(f"SELECT * FROM {table_name}")
                result = conn.execute(query)

            columns = result.keys()
            data = []

            for row in result.fetchall():
                row_dict = {}
                for col, val in zip(columns, row):
                    if isinstance(val, (datetime, date)):
                        row_dict[col] = val.isoformat()
                    else:
                        row_dict[col] = val
                data.append(row_dict)

            return {
                "count": len(data),
                "users": data
            }

        except Exception as e:
            print(f"[ERREUR] Impossible de récupérer les données : {e}")
            return None

        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture de connexion échouée : {close_err}")

    def get_users_activity(self): 

        table_name = f"user_activity_log"

        conn = None
        try:
            conn = self.db.connect()

          
            query = text(f"SELECT * FROM {table_name} ORDER BY created_at DESC, id DESC")
            result = conn.execute(query)

            columns = result.keys()
            data = []

            for row in result.fetchall():
                row_dict = {}
                for col, val in zip(columns, row):
                    if isinstance(val, (datetime, date)):
                        row_dict[col] = val.isoformat()
                    else:
                        row_dict[col] = val
                data.append(row_dict)

            return {
                "count": len(data),
                "users": data
            }

        except Exception as e:
            print(f"[ERREUR] Impossible de récupérer les données : {e}")
            return None

        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture de connexion échouée : {close_err}")

    def insert_user_activity_log(self, request: Request, current_user: dict, action: str, entity_type: str, entity_id: str = None, description: str = None, status: str = "SUCCESS"):
        try:
            user_identifier = current_user.get("username") or current_user.get("sub") or "inconnu"
            payload = {
                "entity_id": entity_id,
                "app": current_user.get("app"),
                "path": str(request.url.path),
            }

            action_labels = {
                "page_view": "Consultation de la page",
                "load_folder": "Chargement du dossier",
                "upload_file": "Import de fichier dans le dossier",
                "show_files": "Ouverture de l'explorateur des fichiers",
                "auto_logout": "Déconnexion automatique de l'utilisateur",
                "select_payroll_date": "Sélection de la date de paie",
                "export_multi": "Export de données",
                "import_multi": "Import multiple de fichiers",
                "download": "Téléchargement",
            }
            if not description:
                label = action_labels.get(action, f"Action : {action}")
                description = f"{label} {entity_id or entity_type}".strip()

            self.saveEvent(
                user_id=user_identifier,
                action=action,
                entity_type=entity_type,
                description=description,
                old_value=None,
                new_value=json.dumps(payload, ensure_ascii=False),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                status=status,
            )

            return {"message": "Activité enregistrée avec succès"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement de l'activité : {e}")

                                        
