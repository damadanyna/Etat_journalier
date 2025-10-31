import pandas as pd
from sqlalchemy import text
from db.db import DB
from controller.DbGet import DbGet

db_get = DbGet()

class DatReport:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine



  #liste des tables dat disponibles
    def getListeDat(self):
        conn = None
        try:
            conn = self.db.connect()

            # Requête pour récupérer les noms des tables commençant par dat_
            query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_name LIKE 'dat_%'
            """)

            result = conn.execute(query)
            # Transformer en liste Python
            tables = [row[0] for row in result.fetchall()]
            return tables

        except Exception as e:
            print(f"[ERREUR] getListeDat : {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getListeDat) : {close_err}")
                

    def getDat(self, table_name: str):
        table_name_vrai = f"dat_{table_name}"
        if not table_name_vrai or not table_name_vrai.startswith("dat_"):
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
            print(f"[ERREUR] getDat : {e}")
            return {"columns": [], "rows": []}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getDat) : {close_err}")


    def getResumeDat(self, table_name: str):
        table_name_vrai = f"dat_{table_name}"
        if not table_name_vrai or not table_name_vrai.startswith("dat_"):
            raise ValueError("Nom de table invalide")

        conn = None
        try:
           
            conn = self.db.connect()
            query = text(f"""
                SELECT 
                    COUNT(*) AS nb_lignes,
                    COUNT(DISTINCT code_client) AS nb_clients,
                    SUM(montant_capital) AS total_montant_capital,
                    SUM(montant_pay_total) AS total_montant_pay_total
                FROM `{table_name_vrai}`
            """)

            result = conn.execute(query).fetchone()  # tuple
            columns = result.keys() if hasattr(result, "keys") else [
                "nb_lignes",
                "nb_clients",
                "total_montant_capital",
                "total_montant_pay_total"
                ]

            # Convertir en dict
            summary = {col: result[i] for i, col in enumerate(columns)}

            return summary

        except Exception as e:
            print(f"[ERREUR] getResumeDat : {e}")
            return {}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion : {close_err}")

    def getListeHistoryInsert(self):
       
        conn = None
        try:
            conn = self.db.connect()

            query = text("""
                SELECT label, used, dat_status, dav_status, epr_status, stat_compte
                FROM history_insert
                ORDER BY used DESC
            """)

            result = conn.execute(query)
            rows = result.fetchall()
            columns = list(result.keys())

            # Transformer en liste de dictionnaires
            data = [dict(zip(columns, row)) for row in rows]

            return data

        except Exception as e:
            print(f"[ERREUR] getListeHistoryInsert : {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getListeHistoryInsert) : {close_err}")


    def get_graphe_data(self, x: str, y: str, table_name: str):
        
        table_name_vrai = f"dat_{table_name}"
        if not table_name_vrai or not table_name_vrai.startswith("dat_"):
            raise ValueError("Nom de table invalide")
        
        conn = None
        try:
            conn = self.db.connect()

            #colone autorise
            allowed_columns = [
                "code_client", "Agence", "Produits", "Numero_compte",
                "montant_capital", "montant_pay_total"
            ]
            if x not in allowed_columns or y not in allowed_columns:
                raise ValueError("Colonnes non autorisées")

            numeric_columns = ["montant_capital", "montant_pay_total"]

            # particulier : nombre de clients par agence
            if (x == "Agence" and y == "code_client") or (x == "code_client" and y == "Agence"):
                select = "Agence, COUNT(DISTINCT code_client) AS value"
                group_by = "Agence"

            # determiner le type de graphique
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

            # Construire la requête
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
                
