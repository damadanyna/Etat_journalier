from fastapi import APIRouter, UploadFile, File,FastAPI,Response,Depends, Form, Request,HTTPException,Query
from controller.Credits import Credits
from controller.Credit_outstanding_report import Credit_outstanding_report
from fastapi.responses import StreamingResponse
from typing import List
from typing import Optional
from fastapi.responses import JSONResponse
from controller.Authentificate import Authentificate
from decimal import Decimal
import json
import time
import asyncio 
import io  
   
 
 
 
 
router = APIRouter()
credits = Credits()
credit_outstanding_report = Credit_outstanding_report()
auth= Authentificate()

credit_outstanding_report = Credit_outstanding_report()



@router.get("/credits")
def get_credits():
    return credits.get_data() 


#  ------------  LOGIN  -----------

@router.post("/signup")
def signup(username: str, password: str):
    return auth.signup(username, password)

@router.post("/signin")
def signin(username: str, password: str, response: Response):
    return auth.signin(username, password, response)

@router.post("/logout")
def logout(response: Response):
    return auth.logout(response)

@router.get("/protected")
def protected(request: Request, user=Depends(auth.get_current_user)):
    return {"message": f"Bienvenue {user} !" }



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

@router.get("/show_files")
async def show_files(app: Optional[str] = Query(None)):
    files = credits.show_files(app=app)
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


api_router = router