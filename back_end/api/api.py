from fastapi import APIRouter, UploadFile, File,FastAPI, Form, Request,HTTPException,Query
from controller.Credits import Credits
from controller.Credit_outstanding_report import Credit_outstanding_report
from fastapi.responses import StreamingResponse
from typing import List
from typing import Optional
from fastapi.responses import JSONResponse
import json
import time
import asyncio 
import io  
   
 
 
 
 
router = APIRouter()
credits = Credits()
credit_outstanding_report = Credit_outstanding_report()



@router.get("/credits")
def get_credits():
    return credits.get_data() 

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

    if not isinstance(filenames, list) or not filenames:
        return StreamingResponse(
            content=iter([json.dumps({"error": "files doit être une liste non vide"})]),
            media_type="application/json"
        )

    def generate_all():
        for filename in filenames:
            yield json.dumps({
                "status": "start",
                "message": f"[INFO] Début du traitement du fichier : {filename}",
                "filename": filename
            }) + "\n"

            try:
                print("File name",filename)
                print("Folder",folder)
                # Appel à ta méthode (instance de classe contenant `load_file_csv_in_database`)
                generator = credits.load_file_csv_in_database(filename, folder)
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

    return StreamingResponse(generate_all(), media_type="application/json")

@router.get("/show_files")
async def show_files(app: Optional[str] = Query(None)):
    files = credits.show_files(app=app)
    return JSONResponse(content={"files": files})





@router.get("/run_encours")
def run_encours():
    gens = [
        {
            "Methode": credits.run_initialisation_sql,
            # "Methode": credits.run_init,
            "title": "Initialisation",
            "status": "pending"
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
            status_global = gen['status']

            yield f"data: {json.dumps({'title_parent': title, 'status_parent': status_global, 'step': i})}\n\n"

            method_gen = gen["Methode"]()

            for step_status in method_gen:
                data = {
                    "title": title,
                    "status_global": status_global,
                    "step": step_status
                }
                yield "data: " + json.dumps(data) + "\n\n"
                time.sleep(0.1)
            
            yield f"data: {json.dumps({'title_parent': title, 'status_parent': 'done', 'step': i})}\n\n"
        yield "data: " + json.dumps({"title": "Initialisation", "status_final": "done"}) + "\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")




api_router = router