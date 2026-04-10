from fastapi import APIRouter, UploadFile, Body,File,FastAPI,Response,Depends, Form, Request,HTTPException,Query
from controller.Credits import Credits
from controller.Credit_outstanding_report import Credit_outstanding_report
from controller.Users import Users
from controller.UsersPaie import UsersPaie
from fastapi.responses import StreamingResponse
from typing import List
from typing import Optional
from fastapi.responses import JSONResponse
from decimal import Decimal
import json
import time
import asyncio 

from fastapi.responses import FileResponse
import io  ,os
from controller.DavUnique import DavUnique
dav_unique = DavUnique()   
 
 
 
 
router = APIRouter()
credits = Credits()
user= Users()
usersPaie= UsersPaie()
credit_outstanding_report = Credit_outstanding_report()

credit_outstanding_report = Credit_outstanding_report()



@router.get("/credits")
def get_credits():
    return credits.get_data() 


#  ------------  LOGIN  -----------  


# --- SIGNUP ---
@router.post("/signup")
def signup(username: str = Form(...), password: str = Form(...), immatricule: str = Form(...)):
    return user.signup(username, password, immatricule)
# --- SIGNUP ---

# --- SIGNIN ---
@router.post("/signin")
def signin(username: str = Form(...), password: str = Form(...)):
    result = user.signin(username, password)

    # Si connexion réussie, on ajoute les colonnes manquantes
    try:
        success = dav_unique.add_status_columns()
        if success:
            print("[INFO] Vérification des colonnes de status terminée ✅")
        else:
            print("[WARN] Échec de la vérification/ajout des colonnes ⚠️")
    except Exception as e:
        print(f"[ERREUR] lors de la vérification des colonnes : {e}")

    return result


@router.post("/signupPaie")
def signupPaie(request: Request,username: str = Form(...),email: str = Form(...), password: str = Form(...), immatricule: str = Form(...)):
    client_ip = request.client.host
    return usersPaie.signup(username,email, password, immatricule, ip_address=client_ip)

# --- SIGNINPAIE ---
@router.post("/signinPaie")
def signinPaie(request: Request,immatricule: str = Form(...), password: str = Form(...)):
    client_ip = request.client.host
    result = usersPaie.signin(immatricule, password, ip_address=client_ip)

    # Si connexion réussie, on ajoute les colonnes manquantes
    try:
        success = dav_unique.add_status_columns()
        if success:
            print("[INFO] Vérification des colonnes de status terminée ✅")
        else:
            print("[WARN] Échec de la vérification/ajout des colonnes ⚠️")
    except Exception as e:
        print(f"[ERREUR] lors de la vérification des colonnes : {e}")

    return result
# --- GET CURRENT USER ---
def get_user_from_request(request: Request):
    return user.get_current_user(request)

# --- ROUTE PROTÉGÉE ---
@router.get("/protected")
def protected(user_: str = Depends(get_user_from_request)):
    return user_

@router.post("/validate_user")
def validate_user(
    request: Request,
    username: str = Form(...),
    role: str = Form(...),
    admin_password: str = Form(...)
):
    current_user = user.get_current_user(request)

    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    return user.validate_user(request, username,role,admin_password)

@router.post("/validate_user_paie")
def validate_user( request: Request, username: str = Form(...), role: str = Form(...), admin_password: str = Form(...)):
    current_user = user.get_current_user(request) 
    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    return usersPaie.validate_user(request, username,role,admin_password)


@router.post("/block_user")
def block_user(
    request: Request,
    username: str = Form(...),
    admin_password: str = Form(...)
):
    
    current_user = user.get_current_user(request)
    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    return user.block_user(request, username, admin_password)


@router.post("/block_user_paie")
def block_user(
    request: Request,
    username: str = Form(...),
    admin_password: str = Form(...)
):
    
    current_user = user.get_current_user(request)
    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    return usersPaie.block_user(request, username, admin_password)


@router.post("/update_user_role")
def update_user_role(
    request: Request,
    username: str = Form(...),
    role: str = Form(...),
    admin_password: str = Form(...)
):
    current_user = user.get_current_user(request)

    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return user.update_user_role(request, username, role, admin_password)

@router.post("/update_user_role_paie")
def update_user_role(
    request: Request, 
    colab_lastname: str = Form(...),
    colab_immatricule: str = Form(...),
    user_id: str = Form(...),
    role: str = Form(...),
    admin_password: str = Form(...)
):
    current_user = user.get_current_user(request)

    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return usersPaie.update_user_role(request,  colab_lastname, colab_immatricule, user_id, role, admin_password)


@router.post("/update_user_pwd_paie")
def update_user_pwd_paie(
    request: Request,  
    colab_pwd: str = Form(...),
    colab_immatricule: str = Form(...),
    user_id: str = Form(...), 
    admin_password: str = Form(...),
    matricule: str = Form(...),
    immatricule: str = Form(...)
):
    client_ip = request.client.host
    current_user = user.get_current_user(request)

    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return usersPaie.update_user_pwd_paie(request, colab_pwd,colab_immatricule, user_id, admin_password,matricule, ip_address=client_ip,immatricule=immatricule)


@router.post("/change_password")
def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...)
):
    user.get_current_user(request)
    return user.change_own_password(request, current_password, new_password)


@router.post("/change_password_paie")
def change_password_paie(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...)
):
    client_ip = request.client.host
    user.get_current_user(request)
    return usersPaie.change_own_password(request, current_password, new_password, ip_address=client_ip)


@router.post("/log_user_activity")
def log_user_activity(
    request: Request,
    action: str = Form(...),
    entity_type: str = Form(...),
    entity_id: str = Form(None),
    description: str = Form(None),
    status: str = Form("SUCCESS")
):
    current_user = user.get_current_user(request)

    if not current_user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")

    return usersPaie.insert_user_activity_log(
        request=request,
        current_user=current_user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        status=status
    )


@router.get("/users")
def get_users(request: Request):
    current_user = user.get_current_user(request)

    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    return user.getListeUser()

@router.get("/usersPaie")
def get_usersPaie(request: Request):
    current_user = user.get_current_user(request)

    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    return usersPaie.getListeUser() 

@router.get("/users/pending_count")
def get_pending_count():
    return user.get_pending_validation_count()

@router.get("/usersPaie/pending_count")
def get_pending_count():
    return usersPaie.get_pending_validation_count()

@router.get("/user/{user_id}")
def get_users(request: Request, user_id: int):
    current_user = user.get_current_user(request)

    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    return user.getUserById(user_id)


@router.get("/userPaie/{user_id}")
def get_users(request: Request, user_id: int):
    current_user = user.get_current_user(request)

    if current_user.get("privillege") not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    return usersPaie.getUserById(user_id)


# --- LOGOUT ---

@router.post("/logout")
def logout(response: Response):
    return user.logout(response) 

def extract_matricule(data):
    """
    Extrait la valeur du matricule et optionnellement file_id depuis un dict ou une string JSON
    Retourne :
      - [matricule, file_id] si file_id présent
      - matricule seul si file_id absent
      - None si matricule absent ou invalide
    """
    # Si c'est une string, essayer de la parser en dict
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return None
    
    # Si c'est un dict, extraire la valeur
    if isinstance(data, dict):
        matricule_value = data.get("matricule")
        file_id_value = data.get("file_id")

        # Nettoyer les strings et gérer les absents
        matricule_value = matricule_value.strip() if isinstance(matricule_value, str) else None
        file_id_value = file_id_value.strip() if isinstance(file_id_value, str) else None

        if matricule_value and file_id_value:
            return [matricule_value, file_id_value]
        return matricule_value  # retourne juste le matricule si file_id absent
    
    return None

@router.post("/logoutpaie")
def logoutpaie(
    request: Request,
    response: Response,
    matricule: str = Body(...)
):
    # print(client_ip,matricule)
    matricule_value =extract_matricule (matricule)
    client_ip = request.client.host  
    return usersPaie.logout(response,ip_address=client_ip,matricule=matricule_value)

@router.post("/downloadpaie")
def downloadpaie(request: Request,response: Response,matricule: str = Body(...)):
    # print(client_ip,matricule)
    matricule_value =extract_matricule (matricule)[0]
    file_id_value =extract_matricule (matricule)[1]
    client_ip = request.client.host  
    return usersPaie.downloadpaie(response,ip_address=client_ip,matricule=matricule_value,file_id=file_id_value)

@router.post("/upload_multiple_files")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    app: str = Form(...),
    folder_name: str = Form(...)
):
    import io, json
    from fastapi.responses import StreamingResponse

    class NamedBytesIO(io.BytesIO):
        def __init__(self, content, filename):
            super().__init__(content)
            self.filename = filename

    # 🔥 Étape 1 : lire tous les fichiers **immédiatement**
    in_memory_files = []
    for file in files:
        try:
            content = await file.read()  # doit être fait ici
            memory_file = NamedBytesIO(content, file.filename)
            in_memory_files.append(memory_file)
        except Exception as e:
            return StreamingResponse(
                iter([json.dumps({
                    "status": "error",
                    "file": getattr(file, 'filename', 'inconnu'),
                    "message": f"Erreur de lecture du fichier : {str(e)}"
                }) + '\n']),
                media_type="application/json"
            )

    # ✅ Étape 2 : générateur avec les fichiers déjà chargés en mémoire
    def main_process():
        total_files = len(in_memory_files)

        yield json.dumps({
            "status": "info",
            "message": f"{total_files} fichiers chargés pour l'application '{app}', dossier '{folder_name}'.",
            "total_files": total_files
        }) + '\n'

        for i, memory_file in enumerate(in_memory_files, start=1):
            filename = memory_file.filename
            try:
                yield json.dumps({
                    "status": "info",
                    "file": filename,
                    "current": i,
                    "total_files": total_files,
                    "message": f"Traitement du fichier {i}/{total_files} : {filename}..."
                }) + '\n'

                for progress in credits.upload_file_manual_in_detail(
                    memory_file, folder_name, i, total_files
                ):
                    print(f"[Progression] {filename}: {progress.get('percentage', '?')}% - {progress.get('message', '')}")
                    yield json.dumps(progress) + '\n'

            except Exception as e:
                print(f"[Erreur] {filename} : {e}")
                yield json.dumps({
                    "status": "error",
                    "file": filename,
                    "message": f"Erreur pendant le traitement : {str(e)}"
                }) + '\n'

        yield json.dumps({
            "status": "success",
            "message": "Tous les fichiers ont été importés avec succès.",
            "percentage": 100
        }) + '\n'

    return StreamingResponse(main_process(), media_type="application/json")


@router.post("/upload_multiple_files_paie")
async def upload_multiple_files_paie(request: Request, files: List[UploadFile] = File(...),app: str = Form(...),folder_name: str = Form(...)):
    import io, json
    from fastapi.responses import StreamingResponse

    current_user = usersPaie.get_current_user(request)
    file_names = [file.filename for file in files]

    class NamedBytesIO(io.BytesIO):
        def __init__(self, content, filename):
            super().__init__(content)
            self.filename = filename

    # 🔥 Étape 1 : lire tous les fichiers **immédiatement**
    in_memory_files = []
    for file in files:
        try:
            content = await file.read()  # doit être fait ici
            memory_file = NamedBytesIO(content, file.filename)
            in_memory_files.append(memory_file)
        except Exception as e:
            return StreamingResponse(iter([json.dumps({"status": "error","file": getattr(file, 'filename', 'inconnu'),
                "message": f"Erreur de lecture du fichier : {str(e)}"}) + '\n']),
                media_type="application/json"
            )

    # ✅ Étape 2 : générateur avec les fichiers déjà chargés en mémoire
    def main_process():
        total_files = len(in_memory_files)

        yield json.dumps({
            "status": "info",
            "message": f"{total_files} fichiers chargés pour l'application '{app}', dossier '{folder_name}'.",
            "total_files": total_files
        }) + '\n'

        for i, memory_file in enumerate(in_memory_files, start=1):
            filename = memory_file.filename
            try:
                yield json.dumps({
                    "status": "info",
                    "file": filename,
                    "current": i,
                    "total_files": total_files,
                    "message": f"Traitement du fichier {i}/{total_files} : {filename}..."
                }) + '\n'

                for progress in usersPaie.upload_file_manual_in_detail(
                    memory_file, folder_name, i, total_files
                ):
                    print(f"[Progression] {filename}: {progress.get('percentage', '?')}% - {progress.get('message', '')}")
                    yield json.dumps(progress) + '\n'

            except Exception as e:
                print(f"[Erreur] {filename} : {e}")
                yield json.dumps({
                    "status": "error",
                    "file": filename,
                    "message": f"Erreur pendant le traitement : {str(e)}"
                }) + '\n'

        yield json.dumps({
            "status": "success",
            "message": "Tous les fichiers ont été importés avec succès.",
            "percentage": 100
        }) + '\n'

    usersPaie.saveEvent(
        user_id=current_user.get("username"),
        action="upload_multiple_files_paie",
        entity_type="folder",
        description=f"Appel API upload_multiple_files_paie sur le dossier {folder_name} avec {len(file_names)} fichier(s)",
        old_value=None,
        new_value=json.dumps({"folder_name": folder_name, "files": file_names}, ensure_ascii=False),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return StreamingResponse(main_process(), media_type="application/json")

@router.post("/create_multiple_table")
async def create_multiple_table(request: Request):
    """
    Endpoint pour créer plusieurs tables à partir de fichiers CSV dans un sous-dossier
    spécifique à une application. La réponse est streamée.
    """
    
    print("Endpoint appelé")
    
    data = await request.json()

    if 'files' not in data or 'folder' not in data:
        return StreamingResponse(
            content=iter([json.dumps({"error": "Paramètres manquants : files et folder requis"})]),
            media_type="application/json"
        )

    filenames: List[str] = data['files'] 
    folder: str = data['folder']
    str_date: str = data['str_date']
     

    if not isinstance(filenames, list) or not filenames:
        return StreamingResponse(
            content=iter([json.dumps({"error": "files doit être une liste non vide"})]),
            media_type="application/json"
        )

    def generate_all():
        credits.create_history_table()
        for filename in filenames:
            # continue
            yield json.dumps({
                "status": "start",
                "message": f"[INFO] Début du traitement du fichier : {filename}",
                "filename": filename
            }) + "\n"

            try:
                print("File name",filename)
                print("Folder",folder)
                # Appel à ta méthode (instance de classe contenant `load_file_csv_in_database`)
                generator = credits.load_file_csv_in_database(filename, folder, str_date)
                if generator is None:
                    yield json.dumps({
                        "status": "critical_error",
                        "message": f"[ERREUR] Aucun message retourné pour {filename} (retour = None)"
                    }) + "\n"
                    continue

                for message in generator:
                    yield message + "\n"

            except Exception as e:
                yield json.dumps({
                    "status": "critical_error",
                    "message": f"[ERREUR] Problème lors du traitement de {filename} : {str(e)}"
                }) + "\n"

            yield json.dumps({
                "status": "end",
                "message": f"[INFO] Fin du traitement du fichier : {filename}"
            }) + "\n"
        credits.insert_into_history_table(label_value=str_date, used=1,stat_of=None)
    return StreamingResponse(generate_all(), media_type="application/json")


@router.post("/create_multiple_table_paie")
async def create_multiple_table(request: Request):
    """
    Endpoint pour créer plusieurs tables à partir de fichiers Excel
    avec streaming en temps réel de la progression
    """
    try:
        data = await request.json()
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"JSON invalide : {str(e)}"}
        )

    # Validation des paramètres requis
    if 'files' not in data or 'folder' not in data or 'str_date' not in data:
        return JSONResponse(
            status_code=400,
            content={"error": "Paramètres manquants : files, folder et str_date requis"}
        )

    filenames: List[str] = data['files']
    folder: str = data['folder']
    str_date: str = data['str_date']
    current_user = usersPaie.get_current_user(request)

    # Validation des données
    if not isinstance(filenames, list) or len(filenames) == 0:
        return JSONResponse(
            status_code=400,
            content={"error": "Le paramètre 'files' doit être une liste non vide"}
        )

    usersPaie.saveEvent(
        user_id=current_user.get("username"),
        action="create_multiple_table_paie",
        entity_type="folder",
        description=f"Chargement du dossier {folder} dans la base pour la date {str_date}",
        old_value=None,
        new_value=json.dumps({"folder": folder, "str_date": str_date, "files": filenames}, ensure_ascii=False),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    def generate_all():
        """Générateur pour le streaming des messages de progression"""
        
        # Message d'initialisation IMMÉDIAT
        yield json.dumps({
            "status": "init",
            "message": "[INFO] Initialisation du processus...",
            "total_files": len(filenames)
        }) + "\n"
        
        # IMPORTANT: yield vide pour forcer le flush
        yield ""

        # Création de la table historique
        try:
            yield json.dumps({
                "status": "info",
                "message": "[INFO] Création/vérification de la table historique..."
            }) + "\n"
            
            usersPaie.create_history_table()
            
            yield json.dumps({
                "status": "info",
                "message": "[INFO] Table historique vérifiée/créée"
            }) + "\n"
        except Exception as e:
            yield json.dumps({
                "status": "warning",
                "message": f"[AVERTISSEMENT] Problème table historique : {str(e)}"
            }) + "\n"

        # Compteurs pour le résumé final
        success_count = 0
        error_count = 0
        processed_tables = []

        # Traitement de chaque fichier
        for idx, filename in enumerate(filenames, 1):
            
            yield json.dumps({
                "status": "start",
                "message": f"[INFO] Début du traitement du fichier {idx}/{len(filenames)} : {filename}",
                "filename": filename,
                "file_index": idx,
                "total_files": len(filenames)
            }) + "\n"

            try:
                # Appel de la fonction de chargement
                generator = usersPaie.load_file_excel_in_database(filename, folder, str_date)

                if generator is None:
                    error_count += 1
                    yield json.dumps({
                        "status": "error",
                        "message": f"[ERREUR] Aucun générateur retourné pour {filename}",
                        "filename": filename
                    }) + "\n"
                    continue

                # Stream des messages de progression
                file_success = False
                table_name = None
                for message in generator:
                    try:
                        msg_data = json.loads(message)
                        if msg_data.get("status") == "success":
                            file_success = True
                            table_name = msg_data.get("table_name")
                        yield message + "\n"
                    except json.JSONDecodeError:
                        yield message + "\n"

                if file_success:
                    success_count += 1
                    if table_name:
                        processed_tables.append(table_name)
                else:
                    error_count += 1

            except Exception as e:
                error_count += 1
                yield json.dumps({
                    "status": "critical_error",
                    "message": f"[ERREUR CRITIQUE] Problème sur {filename} : {str(e)}",
                    "filename": filename
                }) + "\n"

            # Message de fin pour ce fichier
            yield json.dumps({
                "status": "end",
                "message": f"[INFO] Fin du traitement du fichier {idx}/{len(filenames)} : {filename}",
                "filename": filename,
                "file_index": idx,
                "total_files": len(filenames)
            }) + "\n"

        # Mise à jour de l'historique
        try:
            usersPaie.insert_into_history_table(
                label_value=str_date,
                used=1,
                stat_of=None
            )
            yield json.dumps({
                "status": "info",
                "message": "[INFO] Historique mis à jour"
            }) + "\n"
        except Exception as e:
            yield json.dumps({
                "status": "warning",
                "message": f"[AVERTISSEMENT] Erreur mise à jour historique : {str(e)}"
            }) + "\n"

        # Message final avec résumé
        yield json.dumps({
            "status": "done",
            "message": "[INFO] Tous les fichiers ont été traités.",
            "summary": {
                "total_files": len(filenames),
                "success": success_count,
                "errors": error_count,
                "tables_created": processed_tables
            }
        }) + "\n"

    # Retour du StreamingResponse
    return StreamingResponse(
        generate_all(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
    
    
    
    
@router.get("/show_files")
async def show_files(app: Optional[str] = Query(None)):
    files = credits.show_files(app=app)
    return JSONResponse(content={"files": files})

@router.get("/show_files_paie")
async def show_files_paie(request: Request, app: Optional[str] = Query(None)):
    current_user = usersPaie.get_current_user(request)
    files = usersPaie.show_files(app=app)
    usersPaie.saveEvent(
        user_id=current_user.get("username"),
        action="show_files_paie",
        entity_type="file_explorer",
        description="Consultation de l'explorateur des fichiers paie via API",
        old_value=None,
        new_value=json.dumps({"app": app}, ensure_ascii=False),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return JSONResponse(content={"files": files})



@router.get("/get_last_import_file")
async def show_files(app: Optional[str] = Query(None)):
    response = credit_outstanding_report.get_last_import_file()
    print(response)
    return JSONResponse(content={"response": response})

 

@router.get("/run_encours")
async def run_encours(request: Request, str_date: str = Query(None)):
    # print("DATE",str_date)
    
    gens = [
        {
            "Methode": credits.run_initialisation_sql,
            # "Methode": credits.run_init,
            "title": "Initialisation",
            "status": "pending",
            "params": {"str_date": str_date} 
        },
        {
            # "Methode": credit_outstanding_report.get_all_outstanding,
            "Methode": credits.run_init,
            "title": "États des encours",
            "status": "pending"
        },
        # {
        #     "Methode": credits.run_etat_remboursement,
        #     "title": "État des run_etat_remboursement",
        #     "status": "pending"
        # }, 
        {
            "Methode": credits.run_remboursement,
            "title": "État des remboursements",
            "status": "pending"
        },
        {
            "Methode": credits.run_previsionnel,
            "title": "État prévisionnel de remboursement",
            "status": "pending"
        },
        {
            "Methode": credits.run_limit_avm,
            "title": "Limit AVM",
            "status": "pending"
        },
        {
            "Methode": credits.run_limit_caution,
            "title": "Limit Caution",
            "status": "pending"
        }
    ]

    
    def event_generator():
        yield "data: " + json.dumps({"title": "Initialisation", "status": "starting"}) + "\n\n"
        time.sleep(0.1)

        for i, gen in enumerate(gens):
            title = gen["title"]
            status_global = gen["status"]

            # Message de début d'étape
            yield f"data: {json.dumps({'title_parent': title, 'status_parent': status_global, 'step': i})}\n\n"
            time.sleep(0.1)

            # Appel de la méthode avec ou sans paramètres
            methode = gen["Methode"]
            if "params" in gen:
                method_gen = methode(**gen["params"])
            else:
                method_gen = methode()

            # Itération sur le générateur retourné par la méthode
            for step_status in method_gen:
                data = {
                    "title": title,
                    "status_global": status_global,
                    "step": step_status
                }
                yield "data: " + json.dumps(data) + "\n\n"
                time.sleep(0.1)

            # Message de fin d'étape
            yield f"data: {json.dumps({'title_parent': title, 'status_parent': 'done', 'step': i})}\n\n"

        # Fin de l'initialisation
        yield "data: " + json.dumps({"title": "Initialisation", "status_final": "done"}) + "\n\n"
        
    credits.insert_into_history_table(label_value=str_date, used=1,stat_of='init')
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/get_capital_sums")
def get_capital_sums():
    try:
        data = credit_outstanding_report.get_capital_sums()
        if data is None:
            return JSONResponse(status_code=500, content={"status": "error", "detail": "Erreur lors de la récupération des données."})

        data_serializable = convert_decimals(data)
        return JSONResponse(content={"status": "success", "data": data_serializable})

    except Exception as e:
        print("Erreur dans get_capital_sums:", e)
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})
    


@router.get("/get_paie_list")
def get_capital_sums(
    matricule: str | None = Query(default=None),
    dateStr: str | None = Query(default=None)
):
    print( "matricule: ", matricule, "dateStr: ", {dateStr} )
    try:
        # Appel de la fonction avec les paramètres
        data = usersPaie.get_users(matricule=matricule, dateStr=dateStr)

        if data is None:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "detail": "Erreur lors de la récupération des données."}
            )

        # Convertir les types non JSON serializable
        data_serializable = convert_decimals(data)

        return JSONResponse(
            content={
                "status": "success",
                "matricule": matricule,
                "dateStr": dateStr,
                "data": data_serializable
            }
        )

    except Exception as e:
        print("Erreur dans get_capital_sums:", e)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

    
@router.get("/get_activite_list")
def get_capital_sums(request: Request): 
    try:
        current_user = user.get_current_user(request)

        if current_user.get("privillege") not in ["admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Accès refusé")

        # Appel de la fonction avec les paramètres
        data = usersPaie.get_users_activity()

        if data is None:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "detail": "Erreur lors de la récupération des données."}
            )

        # Convertir les types non JSON serializable
        data_serializable = convert_decimals(data)
        
        return JSONResponse(
            content={
                "status": "success", 
                "matricule": "",
                "data": data_serializable
            }
        )

    except Exception as e:
        print("Erreur dans get_capital_sums:", e)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

    
    
def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)  # ou str(obj) si tu préfères garder la précision
    else:
        return obj





@router.get("/get_encours_credits")
async def get_encours_credits(date: str = Query(...)):  # obligatoire (not None)
    try:
        response = credit_outstanding_report.get_encours_credit_by_date(date)
        if response is None or len(response) == 0:
            raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour la date donnée.")
        return {"response": response}
    except Exception as e:
        print(f"[ERREUR route get_encours_credits] {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.get("/encours_remboursement")
async def encours_remboursement(date: str = Query(...)): 
    try:
        response = credit_outstanding_report.get_encours_etat_remboursement(date)

        if response is None or len(response.get("data", [])) == 0:
            raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour la date donnée.")

        return {"response": response}

    except Exception as e:
        print(f"[ERREUR route get_encours_credits] {e}")
        raise HTTPException(status_code=500, detail=str(e))

    
@router.get("/encours_limit")
async def encours_limit(limit_type: str = Query(...)): 
    try:
        response = credit_outstanding_report.get_limit(limit_type)

        if response is None or len(response.get("data", [])) == 0:
            raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour la limit_type donnée.")

        return {"response": response}

    except Exception as e:
        print(f"[ERREUR route get_encours_credits] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history_insert")
async def history_insert( ): 
    try:
        response = credit_outstanding_report.get_history_insert()

        if response is None or len(response.get("data", [])) == 0:
            raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour la limit_type donnée.")

        return {"response": response}

    except Exception as e:
        print(f"[ERREUR route get_encours_credits] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history_insert_paie")
async def history_insert( ): 
    try:
        response = usersPaie.get_history_insert()

        if response is None or len(response.get("data", [])) == 0:
            raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour la limit_type donnée.")

        return {"response": response}

    except Exception as e:
        print(f"[ERREUR route get_encours_credits] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_local_ref")
async def get_local_ref(date: str = Query(...)): 
    try:
        response = credit_outstanding_report.get_local_reference(date)

        if response is None or len(response.get("data", [])) == 0:
            raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour la limit_type donnée.")

        return {"response": response}

    except Exception as e:
        print(f"[ERREUR route get_encours_credits] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_pa_class")
async def get_pa_class(date: str = Query(...)): 
    try:
        response = credit_outstanding_report.get_pa_class(date)

        if response is None or len(response.get("data", [])) == 0:
            raise HTTPException(status_code=404, detail="Aucune donnée trouvée pour la limit_type donnée.")

        return {"response": response}

    except Exception as e:
        print(f"[ERREUR route get_encours_credits] {e}")
        raise HTTPException(status_code=500, detail=str(e))

 




BASE_DIR = os.path.join(os.path.dirname(__file__), "..")  # remonte d'un niveau pour enlever api

@router.get("/download-file")
def download_file(filename: str, date: str):
    path = os.path.join(BASE_DIR, "load_file", date, filename)
    print(">>> Chemin construit :", path)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Fichier introuvable")

    file_size = os.path.getsize(path)

    def iter_file():
        with open(path, "rb") as f:
            while chunk := f.read(1024 * 1024):  # 1 Mo par chunk
                yield chunk

    return StreamingResponse(
        iter_file(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(file_size)
        }
    )


@router.get("/download-file-paie")
def download_file(request: Request, filename: str, date: str):
    current_user = usersPaie.get_current_user(request)
    path = os.path.join(BASE_DIR, "load_file_paie", date, filename)
    print(">>> Chemin construit :", path)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Fichier introuvable")

    usersPaie.saveEvent(
        user_id=current_user.get("username"),
        action="download_file_paie",
        entity_type="file",
        description=f"Téléchargement du fichier {filename} pour la date {date} via API",
        old_value=None,
        new_value=json.dumps({"filename": filename, "date": date}, ensure_ascii=False),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    file_size = os.path.getsize(path)

    def iter_file():
        with open(path, "rb") as f:
            while chunk := f.read(1024 * 1024):  # 1 Mo par chunk
                yield chunk

    return StreamingResponse(
        iter_file(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(file_size)
        }
    )


api_router = router