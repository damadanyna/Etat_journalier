from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from typing import List, Optional
import json
from db.db import DB
from sqlalchemy import text
from controller.DatReport import DatReport 
from controller.DbGet import DbGet
from controller.Operation import Operation
<<<<<<< HEAD
from controller.OperationEsri import OperationEsri
from controller.DavReport import DavReport
from controller.EprReport import EprReport
=======
from controller.OperatioDav import OperatioDav
from controller.Esri import Esri
from controller.OperationEsri import OperationEsri
from controller.OperationEsris import OperationEsris
from controller.DavReport import DavReport
from controller.EprReport import EprReport
from controller.ChangeMande import ChangeMande
>>>>>>> master
from controller.ChangeMandy import ChangeMandy
from controller.DavUnique import DavUnique
from controller.decaissement import DecaissementOptimise

router = APIRouter()
dat_report = DatReport()
db_get = DbGet()
operation = Operation()
<<<<<<< HEAD
dav_unique = DavUnique()
operation_esri = OperationEsri()
dav_report = DavReport()
epr_report = EprReport()
change_mandy = ChangeMandy()
=======
operation_dav = OperatioDav()
dav_unique = DavUnique()
esri = Esri()
operation_esri = OperationEsri()
dav_report = DavReport()
change_mande = ChangeMande()
epr_report = EprReport()
change_mandy = ChangeMandy()
operation_esris = OperationEsris()
>>>>>>> master
decaissement = DecaissementOptimise()
#INITIALISATION COMPTE

@router.post("/compte/compte_init/{name}")
def initialize(name:str):
    try:
        if dav_unique.verifie_statu(name):
            return JSONResponse(
                status_code=200,
                content={
                    "status": "info",
                    "message": f"Le compte {name} est déjà initialisé",
                    "already_initialized": True
                }
            )
        
        table_name_dat = db_get.create_tableDatPreCompute(name)
        table_name_dav = dav_unique.create_table_dav(name)
        table_name_epr = dav_unique.create_table_epr(name)
        
        if not table_name_dat or not table_name_dav or not table_name_epr:
            raise Exception("Erreur lors de la création des tables DAT, DAV et EPR")
        
        operation.calculeAmtCap(table_name_dat)
        db_get.traitement_dat(table_name_dat)
        
        
        dav_unique.add_status_columns()
        dav_unique.create_temp_client()
        dav_unique.create_index()
        dav_unique.create_funct()
        dav_unique.update_status(name)

        return JSONResponse(content={
                    "status": "success",
                    "message": f"Table créée et nettoyée et calculer : {table_name_dav} et {table_name_epr} et {table_name_dat}✅",
                    "table_name_dav": table_name_dav,
                    "table_name_epr": table_name_epr,
                    "table_name_dat": table_name_dat   
        })
        
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
    
    
@router.post("/compte/decaissement/{name}")
def create_decaissement(date_limit:str):
    try:
        
        result = decaissement.generate_decaissement_report(date_limit)        
        
       
        if result:
            print(f"Table créée : {result['table_name']}")
            print(f"Enregistrements : {result['record_count']}")
        
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
    
# ESRI


@router.post("/esri/create_esri_precompute")
def create_esri_precompute( date_debut: str = Query(...), date_fin: str = Query(...)):
    try:
        limit = db_get.getHistoryDate()
        if limit and (date_debut > limit or date_fin > limit):
            raise Exception(f"Les données apres le {limit} ne sont pas encore disponible.")
       
        result_df,columns = operation_esri.process_esri_data_fast(date_debut, date_fin)

        if  result_df.empty:
            return JSONResponse(
                content={
                    "status": "error",
                    "message": f"Aucune donnée trouvée entre {date_debut} et {date_fin}",
                   
                },
                status_code=200
            )

        data_json = json.loads(result_df.to_json(orient="records", force_ascii=False))

        return JSONResponse(
            content={
                "status": "success",
                "message": f"Données ESRI  entre {date_debut} et {date_fin} ",
                
                "columns": columns,
                "rows": data_json,
                "count": len(data_json)
            },
            status_code=200
        )

    except Exception as e:
        import traceback
        print(f"[ERREUR] create_esri_precompute : {e}")
        print(traceback.format_exc())
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


#change
@router.post("/change/generate_report")
def create_change_report(date_debut: str, date_fin: str):
    try:
        limit = db_get.getHistoryDate()
        if limit and (date_debut > limit or date_fin > limit):
            raise Exception(f"Les données apres le {limit} ne sont pas encore disponible.")
        result = change_mandy.generate_tables_report(date_debut, date_fin)
        
        if not result:
            raise Exception("Aucune donnée disponible pour cette période.")
        
        response_data = {
            "status": "success",
            "periode": {"date_debut": date_debut, "date_fin": date_fin},
            "etat": result["etat"],
            "allocation": result["allocation"],
            "synthese": result["synthese"],
        }

        return JSONResponse(status_code=200, content=response_data)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


##"""""""""""""DAT REPORT""""""""""""""##
@router.get("/dat/liste_dat")
def listeDta():
    """
        liste table dat
    """ 
    try:
        listeDta = dat_report.getListeDat()
        if not listeDta:
            raise Exception("Aucune table DAT trouvée")
        
        return {"tables": listeDta}
    
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})

@router.get("/dat/{table_name}")
def get_dat_table(table_name: str):
    """ tablea de dat selectionner
    """
    try:
        data = dat_report.getDat(table_name)
        return {"table": table_name, **data}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})


@router.get("/dat/{table_name}/resume")
def get_dat_resume(table_name: str):

    try:
        summary = dat_report.getResumeDat(table_name)
        if not summary:
            return JSONResponse(status_code=404, content={"error": "Résumé introuvable ou table vide"})

        # Conversion sécurisée en types JSON (int / float)
        safe_summary = {
            "table_name": table_name,
            "nb_lignes": int(summary.get("nb_lignes") or 0),
            "nb_clients": int(summary.get("nb_clients") or 0),
            "total_montant_capital": float(summary.get("total_montant_capital") or 0),
            "total_montant_pay_total": float(summary.get("total_montant_pay_total") or 0)
        }

        return safe_summary

    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    
   

@router.get("/datGraphe/{table_name}")
def get_graphe_dat(
    table_name: str,
    x: str = Query(..., description="Colonne X (ex: kill, agence, produit, numero_compte)"),
    y: str = Query(..., description="Colonne Y (ex: kill, agence, produit, numero_compte)")
):

    try:
        data = dat_report.get_graphe_data(x, y, table_name)
        print(data)
        return data
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})



##"""""""""""HISTORY INSERT""""""""""##
 
@router.get("/history/liste")
def liste_history():

    try:
        history_list = dat_report.getListeHistoryInsert()
        if not history_list:
            return JSONResponse(
                content={"status": "error", "message": "Aucun enregistrement trouvé"},
                status_code=404
            )
        return {"history": history_list}

    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})



#""""""""""""""""""""""DAV REPORT""""""""""""""""""##
@router.get("/dav/liste_dav")
def listeDav():
   
    try:
        listeDav = dav_report.getListeDav()
        if not listeDav:
            raise Exception("Aucune table DAV trouvée")
        
        return {"tables": listeDav}
    
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})

@router.get("/dav/{table_name}")
def get_dav_table(table_name: str):
    """ tablea de dav selectionner
    """
    try:
        data = dav_report.getDav(table_name)
        return {"table": table_name, **data}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    
@router.get("/dav/{table_name}/resume")
def get_dav_resume(table_name: str):

    try:
        summary = dav_report.getResumeDav(table_name)
        if not summary:
            return JSONResponse(status_code=404, content={"error": "Résumé introuvable ou table vide"})

        safe_summary = {
            
            "table_name": table_name,
            "nb_clients": int(summary.get("nb_clients") or 0),
            "total_montant_dav": float(summary.get("total_montant_dav") or 0),
            "total_debit_dav": float(summary.get("total_debit_dav") or 0),
            "total_credit_dav": float(summary.get("total_credit_dav") or 0)
        }

        return safe_summary

    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    


@router.get("/davGraphe/{table_name}")
def get_graphe_dav(
    table_name: str,
    x: str = Query(..., description="Colonne X (ex: client, agence, produit, numero_compte)"),
    y: str = Query(..., description="Colonne Y (ex: kill, agence, produit, numero_compte)")
):

    try:
        data = dav_report.get_graphe_dataDav(x, y, table_name)
       
        return data
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})


#***********EPR**********#
@router.get("/epr/liste_epr")
def listeEpr():
   
    try:
        listeEpr = epr_report.getListeEpr()
        if not listeEpr:
            raise Exception("Aucune table EPR trouvée")
        
        return {"tables": listeEpr}
    
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    
@router.get("/epr/{table_name}")
def get_epr_table(table_name: str):
    try:
        data = epr_report.getEpr(table_name)
        return {"table": table_name, **data}
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})
    
@router.get("/epr/{table_name}/resume")
def get_epr_resume(table_name: str):

    try:
        summary = epr_report.getResumeEpr(table_name)
        if not summary:
            return JSONResponse(status_code=404, content={"error": "Résumé introuvable ou table vide"})

        safe_summary = {
            
            "table_name": table_name,
            "nb_clients": int(summary.get("nb_clients") or 0),
            "total_montant_epr": float(summary.get("total_montant_epr") or 0),
            "total_debit_epr": float(summary.get("total_debit_epr") or 0),
            "total_credit_epr": float(summary.get("total_credit_epr") or 0)
        }

        return safe_summary

    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})

@router.get("/eprGraphe/{table_name}")
def get_graphe_epr(
    table_name: str,
    x: str = Query(..., description="Colonne X (ex: client, agence, produit, numero_compte)"),
    y: str = Query(..., description="Colonne Y (ex: kill, agence, produit, numero_compte)")
):

    try:
        data = epr_report.get_graphe_dataEpr(x, y, table_name)
        
        return data
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Erreur serveur: {e}"})



<<<<<<< HEAD
api_router2 = router
=======
api_router = router
>>>>>>> master
