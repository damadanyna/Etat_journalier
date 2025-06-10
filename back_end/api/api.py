from fastapi import APIRouter, UploadFile, File, Form, Request,HTTPException,Query
from controller.Credits import Credits
from fastapi.responses import StreamingResponse
from typing import List
from typing import Optional
from fastapi.responses import JSONResponse
import json
import time
import asyncio

router = APIRouter()
credits = Credits()



@router.get("/credits")
def get_credits():
    return credits.get_data() 

@router.post("/upload_multiple_files")
async def upload_multiple_files(files: List[UploadFile] = File(...),app: str = Form(...),folder_name: str = Form(...)):
    def generate():
        # 🧪 Premier message immédiat
        yield json.dumps({
            "status": "info",
            "percentage": 0,
            "message": "Début du téléchargement..."
        }) + '\n'

        # 🧪 Petit délai simulé pour observer le streaming
        time.sleep(1)

        # 🧪 Appel à la vraie fonction de traitement
        results = credits.upload_multiple_files(files, app, folder_name)
        for result in results:
            yield json.dumps(result) + '\n'

        # 🧪 Dernier message
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
    data = await request.json()

    if 'files' not in data or 'app' not in data or 'folder' not in data:
        return StreamingResponse(
            content=iter([json.dumps({"error": "Paramètres manquants : files, app et folder requis"})]),
            media_type="application/json"
        )

    filenames: List[str] = data['files']
    app_name: str = data['app']
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
                # Appel à ta méthode (instance de classe contenant `load_file_csv_in_database`)
                generator = credits.load_file_csv_in_database(filename, app_name, folder)
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


api_router = router