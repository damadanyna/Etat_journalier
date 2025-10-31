import pandas as pd
from sqlalchemy import text
from db.db import DB
from controller.DbGet import DbGet

class ChangeReport:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
    
    from sqlalchemy import text

    def verifTable(self, date_value: str):
        """
        Vérifie si les tables etat_<date>, allocation_devise_<date> et synthese_<date> existent.
        """
        etat_table = f"etat_{date_value}"
        allocation_table = f"allocation_devise_{date_value}"
        synthese_table = f"synthese_{date_value}"
        
        conn = None
        try:
            conn = self.db.connect()

            query = text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME IN (:etat, :allocation, :synthese)
            """)

            results = conn.execute(query, {
                "etat": etat_table,
                "allocation": allocation_table,
                "synthese": synthese_table
            }).fetchall()

            existing_tables = [row[0] for row in results]

            all_tables_exist = (
                etat_table in existing_tables and
                allocation_table in existing_tables and
                synthese_table in existing_tables
            )

            print(f"[INFO] Tables existantes pour {date_value}: {existing_tables}")
            print(f"[INFO] Toutes les tables existent: {'✅ OUI' if all_tables_exist else '❌ NON'}")

            return all_tables_exist

        except Exception as e:
            print(f"[ERREUR] verifTable : {e}")
            return False

        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (verifTable) : {close_err}")

            
            
    def getEtat(self,date_value: str):
        table_name_vrai = f"etat_{date_value}"
        if not table_name_vrai or not table_name_vrai.startswith("change_"):
            raise ValueError("Nom de table invalide")
        conn = None
        try:
            conn = self.db.connect()
            
            query = text(f"SELECT * FROM `{table_name_vrai}`")
            result = conn.execute(query)
            
            rows = conn.execute(query).fetchall()
            columns = list(result.keys())   
            
            data = [dict(zip(columns, row)) for row in rows]
            
            return {
                
                "columns": columns,
                "rows": data
            }
        except Exception as e:
            print(f"[ERREUR] getEtat : {e}")
            return {"columns": [], "rows": []}
        finally:    
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getEtat) : {close_err}")
                    
    def getAllocation(self, date_value:str):
        table_name_vrai = f"allocation_devise_{date_value}"
        if not table_name_vrai or not table_name_vrai.startswith("allocation_devise_"):
            raise ValueError("Nom de table invalide")
        conn = None
        try:
            
            conn = self.db.connect()
            query = text(f"SELECT * FROM `{table_name_vrai}`")
            result = conn.execute(query)
            
            rows = conn.execute(query).fetchall()
            columns = list(result.keys())
            data = [dict(zip(columns, row)) for row in rows]
            return {
                "columns": columns,
                "rows": data
            }
        except Exception as e:
            print(f"[ERREUR] getAllocation : {e}")
            return {"columns": [], "rows": []}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getAllocation) : {close_err}")
    
    def getSynthes(self, date_value:str):
        table_name_vrai = f"synthese_{date_value}"
        if not table_name_vrai or not table_name_vrai.startswith("synthese_"):
            raise ValueError("Nom de table invalide")
        conn = None
        try:
            
            conn = self.db.connect()
            query = text(f"SELECT * FROM `{table_name_vrai}`")
            result = conn.execute(query)
            
            rows = conn.execute(query).fetchall()
            columns = list(result.keys())
            data = [dict(zip(columns, row)) for row in rows]
            return {
                "columns": columns,
                "rows": data
            }
        except Exception as e:
            print(f"[ERREUR] getSynthes : {e}")
            return {"columns": [], "rows": []}
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getSynthes) : {close_err}")