import pandas as pd
from sqlalchemy import text
from db.db import DB
from controller.DbGet import DbGet

db_get = DbGet()

class decaissementReport:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
    
    def getListeDecaissement(self):
        conn = None
        try:
            conn = self.db.connect()

            # Requête pour récupérer les noms des tables commençant par dav_
            query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name LIKE 'decaissement_%'
            """)

            result = conn.execute(query)
            # Transformer en liste Python
            tables = [row[0] for row in result.fetchall()]
            return tables

        except Exception as e:
            print(f"[ERREUR] getListeDecaissement : {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getListeDecaissement) : {close_err}")
                    
    def getDecaissement(self, table_name: str):
        table_name_vrai = f"decaissement_{table_name}"
        if not table_name_vrai or not table_name_vrai.startswith("decaissement_"):
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
            print(f"[ERREUR] getDecaissement : {e}")
            return {
                "columns": [],
                "data": []
            }
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getDecaissement) : {close_err}")
                    
    def getResumeDecaissement(self, table_name: str):
        table_name_vrai = f"decaissement_{table_name}"
        if not table_name_vrai or not table_name_vrai.startswith("decaissement_"):
            raise ValueError("Nom de table invalide")

        conn = None
        try:
            conn = self.db.connect()

            query = text(f"""
                SELECT 
                    COUNT(DISTINCT code_client) AS nb_clients,
                    SUM(montant_capital) AS total_montant_capital,
                    SUM(frai_de_dossier) AS total_frai_de_dossier,
                FROM `{table_name_vrai}`
            """)
            result = conn.execute(query)

            row = result.fetchone()
            return {
                "total_decaissements": row['total_decaissements'],
                "total_montant_decaisse": float(row['total_montant_decaisse']) if row['total_montant_decaisse'] is not None else 0.0
            }

        except Exception as e:
            print(f"[ERREUR] getResumeDecaissement : {e}")
            return {
                "total_decaissements": 0,
                "total_montant_decaisse": 0.0
            }
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getResumeDecaissement) : {close_err}")
                    
                    
    def get_grapheDec(self, x: str, y: str, table_name:str):
        table_name_vrai = f"decaissement_{table_name}"
        if not table_name_vrai or not table_name_vrai.startswith("decaissement"):
                raise ValueError("Nom de table invalide")
        conn = None
        try:
            conn = self.db.connect()
            
            colone_auto= [
                 "Agence", "Produits", "montant_capital", "frais_de_dossier", "taux_interet", "charge_rate","code_client"
            ]
            if x not in colone_auto or y not in colone_auto:
                raise ValueError("Colonnes non autorisées")
            
            numeric_columns = ["montant_capital", "frais_de_dossier", "Debit", "taux_interet", "charge_rate"]
            
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
                group_by = None 
            else: 
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
