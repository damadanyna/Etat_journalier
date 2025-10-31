import pandas as pd
from sqlalchemy import text
from db.db import DB
from controller.DbGet import DbGet

db_get = DbGet()

class DavReport:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
    
    def getListeDav(self):
        conn = None
        try:
            conn = self.db.connect()

            # Requête pour récupérer les noms des tables commençant par dav_
            query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name LIKE 'dav_%'
            """)

            result = conn.execute(query)
            # Transformer en liste Python
            tables = [row[0] for row in result.fetchall()]
            return tables

        except Exception as e:
            print(f"[ERREUR] getListeDav : {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getListeDav) : {close_err}")

    def getDav(self, table_name: str):
        table_name_vrai = f"dav_{table_name}"
        if not table_name_vrai or not table_name_vrai.startswith("dav_"):
            raise ValueError("Nom de table invalide")

        conn = None
        try:
            conn = self.db.connect()

            query = text(f"SELECT * FROM `{table_name_vrai}`")  
            result = conn.execute(query)

            rows = result.fetchall()
            columns = list(result.keys())   # noms colonnes

            data = [dict(zip(columns, row)) for row in rows]
            return {
                "columns": columns,
                "data": data
            }

        except Exception as e:
            print(f"[ERREUR] getDav : {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getDav) : {close_err}")
                    
    def getResumeDav(self, table_name: str):
        table_name_vrai = f"dav_{table_name}"
        if not table_name_vrai or not table_name_vrai.startswith("dav_"):
            raise ValueError("Nom de table invalide")

        conn = None
        try:
            conn = self.db.connect()

            query = text(f"""
                SELECT 
                   
                    COUNT(DISTINCT code_client) AS nb_clients,
                    SUM(solde) AS total_montant_dav,
                    SUM(debit) AS total_debit_dav,
                    SUM(credit) AS total_credit_dav
                FROM `{table_name_vrai}`
            """)
            result = conn.execute(query).fetchone()

            columns =  result.keys() if hasattr(result, "keys") else [
                
                 "nb_clients", "total_montant_dav", "total_debit_dav", "total_credit_dav"
            ]
            
            summary = {col: result[idx] for idx, col in enumerate(columns)} if result else {}

            return summary

        except Exception as e:
            print(f"[ERREUR] getResumeDav : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getResumeDav) : {close_err}")
                    
                    
    def get_graphe_dataDav(self, x: str, y: str, table_name:str):
        table_name_vrai = f"dav_{table_name}"
        if not table_name_vrai or not table_name_vrai.startswith("dav_"):
                raise ValueError("Nom de table invalide")
        conn = None
        try:
            conn = self.db.connect()
            
            colone_auto= [
                "code_client", "Agence", "Produits", "solde", "Credit", "Debit"
            ]
            if x not in colone_auto or y not in colone_auto:
                raise ValueError("Colonnes non autorisées")
            
            numeric_columns = ["solde", "Credit", "Debit"]
            
            if (x == "Agence" and y == "code_client") or (x == "code_client" and y == "Agence"):
                select = "Agence, COUNT(DISTINCT code_client) AS value"
                group_by = "Agence"
                
            elif x in numeric_columns and y not in numeric_columns:
                select = f"{y}, SUM({x}) AS value"
                group_by = y
            elif y in numeric_columns and x not in numeric_columns:
                select = f"{x}, SUM({y}) AS value"
                group_by = x
            elif x in numeric_columns and y in numeric_columns:
                select = f"SUM({x}) AS value_x, SUM({y}) AS value_y"
                group_by = None  # pas de groupement
            else:  # deux catégorielles
                select = f"{x}, {y}, COUNT(*) AS value"
                group_by = f"{x}, {y}"
                
            if group_by:
                query = f"SELECT {select} FROM {table_name_vrai} GROUP BY {group_by} ORDER BY value DESC;"
            else:
                query = f"SELECT {select} FROM {table_name_vrai} ORDER BY value_x DESC;"

            print("Requête SQL exécutée :", query)
            
            result = conn.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())

            data = [dict(zip(columns, row)) for row in rows]
            return {"query": query, "columns": columns, "rows": data}
        
        except Exception as e:
            print(f"[ERREUR] get_graphe_data : {e}")
            return {"status": "error", "message": str(e)}

        finally:
            if conn:
                conn.close()
