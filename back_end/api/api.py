from fastapi import APIRouter, UploadFile, File,FastAPI, Form, Request,HTTPException,Query
from controller.Credits import Credits
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



@router.get("/credits")
def get_credits():
    return credits.get_data() 

@router.post("/upload_multiple_files")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    app: str = Form(...),
    folder_name: str = Form(...)
):
    class NamedBytesIO(io.BytesIO):
        def __init__(self, content, filename):
            super().__init__(content)
            self.filename = filename

    # Étape 1 : lire tous les fichiers en mémoire
    in_memory_files = []

    for file in files:
        try:
            content = await file.read()
            memory_file = NamedBytesIO(content, file.filename)
            in_memory_files.append(memory_file)
        except Exception as e:
            def error_response():
                yield json.dumps({
                    "status": "error",
                    "file": getattr(file, 'filename', 'inconnu'),
                    "message": f"Erreur de lecture du fichier : {str(e)}"
                }) + '\n'
            return StreamingResponse(error_response(), media_type="application/json")

    # Étape 2 : générateur de progression
    def generate():
        yield json.dumps({
            "status": "info",
            "percentage": 0,
            "message": "Début du téléchargement..."
        }) + '\n'

        total = len(in_memory_files)

        for i, memory_file in enumerate(in_memory_files, start=1):
            try:
                for progress in credits.upload_file_manual_in_detail(
                    memory_file, folder_name, i, total
                ):
                    yield json.dumps(progress) + '\n'
            except Exception as e:
                yield json.dumps({
                    "status": "error",
                    "file": memory_file.filename,
                    "current": i,
                    "total": total,
                    "message": f"[ERREUR] Échec du traitement : {str(e)}"
                }) + '\n'

        yield json.dumps({
            "status": "info",
            "percentage": 100,
            "message": "Téléchargement terminé."
        }) + '\n'

    return StreamingResponse(generate(), media_type="application/json")
 
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
async def run_encours():
    gens = [
        {
            "Methode": lambda: credits.run_initialisation_sql(),  # ❗ Appel différé via lambda
            "title": "Initialisation",
            "status": "pending"
        }
    ]

    async def event_generator():
        yield "data: " + json.dumps({"title": "Initialisation", "status": "starting"}) + "\n\n"
        await asyncio.sleep(0.1)

        for gen in gens:
            method_gen = gen["Methode"]()  # ❗ On appelle ici la lambda pour obtenir le générateur
            title = gen["title"]
            status_global = gen["status"]

            for step_status in method_gen:
                data = {
                    "title": title,
                    "status_global": status_global,
                    "step": step_status
                }
                yield "data: " + json.dumps(data) + "\n\n"
                await asyncio.sleep(0.1)

        yield "data: " + json.dumps({"title": "Initialisation", "status": "done"}) + "\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/run_encours")
async def run_encours():
    # Supposons que credits a 6 méthodes génératrices différentes
    gens = [
        credits.run_initialisation_sql()
    ]

    async def event_generator():
        for gen in gens:
            for step_status in gen:
                yield json.dumps(step_status) + "\n"

    return StreamingResponse(event_generator(), media_type="application/json")



api_router = router