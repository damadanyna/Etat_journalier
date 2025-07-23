import pymysql  # Assurez-vous que pymysql est importé correctement
import pandas as pd
import pymysql.cursors
import os
import time
from fastapi import Request
from fastapi.responses import StreamingResponse
import json
from typing import List
import os
from datetime import datetime 
import re  
import string
import openpyxl 
import sys   
import pandas as pd
from db.db  import DB
from werkzeug.utils import secure_filename 
import aiofiles
import io
from sqlalchemy import text


 

class Credit_outstanding_report:
    def __init__(self):
        
        self.db = DB()  # au cas où tu veux utiliser la BDD 

    def fetch_data_from_table(self, conn, query):
        """Fetch data from the database based on the query and return as list of dicts."""
        try:
            # cursor = conn.cursor()
            cursor = conn.connection.cursor()
            print(f"Executing query in progress...")
            cursor.execute(query)
            
            columns = [col[0] for col in cursor.description]  # Récupérer les noms des colonnes
            results = cursor.fetchall()
            
            print(f"Query executed successfully. Fetched {len(results)} rows.")
            
            # Transformation des tuples en dictionnaires
            data = [dict(zip(columns, row)) for row in results]
            
            return data
        except pymysql.MySQLError as err:
            print(f"Error: Unable to execute query. Query: {query} | Error: {err}")
            return None
        finally:
            cursor.close()


    def split_value(self,value, index, default=None):
        """Helper function to split values by '|' and return the part at the given index."""
        if value:
            parts = value.split('|')
            return parts[index] if len(parts) > index else  default
        return  default 

    def modify_column_data(self,data):
        """Modify the 'contract_balance.open_balance' column to keep only the first value before the pipe (|)."""
        new_data=[] 
        return data
  
    def safe_float(self,value):
        try:
            return round(float(value),2) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def data_base_query(self):
        return """ 
                    SELECT 
                            arrangement.id,
                            arrangement.co_code AS Agence,
                            arrangement.customer AS identification_client,
                            arrangement.customer,
                            arrangement.id AS Numero_pret,
                            tmp_CLT.nom_complet AS Nom_client,
                            arrangement.linked_appl_id AS linked_appl_id,
                            COALESCE(arrangement.orig_contract_date, arrangement.start_date) AS Date_pret, 
                            tmp_int.Date_fin_pret AS Date_fin_pret,
                            arrangement.product AS Produits,
                            tmp_amnt.amount AS Amount,
                            tmp_int.`Duree_Remboursement` as Duree_Remboursement,
                            tmp_int.taux_d_interet as taux_d_interet,
                            tmp_Nombre_de_jour_retard.Nombre_de_jour_retard AS Nombre_de_jour_retard,
                            tmp_payment_date.payment_date AS payment_date,
                            calculate_all_capitals(
                                eb_cont.type_sysdate, 
                                eb_cont.open_balance, 
                                eb_cont.credit_mvmt, 
                                eb_cont.debit_mvmt
                            ) AS Capital_,
                            calculate_total_interet_echus(cont_bal.type_sysdate,cont_bal.open_balance,'|') as Total_interet_echus,
                            '' as "OD Pen",
                            tmp_od_pen.OD_PEN as "OD & PEN",  
                            tmp_CLT.gender AS Genre, 
                            industry.description AS Secteur_d_activité,
                            tmp_CLT.industry AS CODE,
                            arrangement.arr_status
                    FROM aa_arrangement_mcbc_live_full AS arrangement
                    INNER JOIN eb_cont_bal_mcbc_live_full as eb_cont
                        ON eb_cont.id = arrangement.linked_appl_id
                    LEFT JOIN temp_AMOUNT as tmp_amnt
                        ON tmp_amnt.id_comp_1 = arrangement.id 
                    LEFT JOIN temp_INTEREST as tmp_int
                        ON tmp_int.id_comp_1 = arrangement.id
                    LEFT JOIN eb_cont_bal_mcbc_live_full as cont_bal
                        ON cont_bal.id = arrangement.linked_appl_id
                    LEFT JOIN temp_payment_date as tmp_payment_date
                        ON tmp_payment_date.arrangement_id = arrangement.id
                    LEFT JOIN temp_Nombre_de_jour_retard as tmp_Nombre_de_jour_retard
                        ON tmp_Nombre_de_jour_retard.arrangement_id = arrangement.id
                    LEFT JOIN temp_od_pen as tmp_od_pen
                        ON tmp_od_pen.arrangement_id = arrangement.id
                    LEFT JOIN temp_clients as tmp_CLT
                        ON tmp_CLT.id = get_customer(arrangement.customer) 
                    LEFT JOIN industry_mcbc_live_full AS industry 
                        ON industry.id = tmp_CLT.industry
                    WHERE arrangement.product_line = 'LENDING' 
                        AND arrangement.arr_status IN ('CURRENT', 'EXPIRED', 'AUTH','CLOSE')
                        AND NOT (tmp_od_pen.OD_PEN  = 0.0 AND (arrangement.arr_status = 'EXPIRED' OR arrangement.arr_status = 'CLOSE'))
                        HAVING NOT (Capital_ = 0.00|0.00|0.00 AND (tmp_od_pen.OD_PEN=0.00 OR tmp_od_pen.OD_PEN =''))

                """      
                
    def export_to_excel(self,data, file_name):
        """Export data to an Excel file."""
        if not data:
            print("No data to export!")
            return

        try:
            df = pd.DataFrame(data)
            df.to_excel(file_name, index=False, engine='openpyxl')
            print(f"Data has been exported to {file_name} successfully!")
        except Exception as e:
            print(f"Error while exporting to Excel: {e}")


    def get_all_outstanding(self):
        output_file_template = "../ALL_OUT_PUT/credit_outstanding/credit_outstanding_reppor_FINAL.xlsx"
        output_dir = os.path.dirname(output_file_template)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with self.db.connect() as conn:
            start_time = time.time()
            query = self.data_base_query()  # Appel sans offset

            result = conn.execute(text(query))
            data = [dict(row._mapping) for row in result]  # convertir en liste de dict

            if data:
                yield {"status": "running", "message": "En cours..."} 
                modified_data = self.modify_column_data(data)
                output_file = output_file_template.format(offset="final")  # ou un nom fixe si tu préfères
                self.export_to_excel(modified_data, output_file) 
                elapsed_time = time.time() - start_time
                yield {"status": "done", "message": "Terminé."}
            else:
                yield {"status": "error", "message": "Aucune donnée trouvée."}

    def get_last_import_file(self): 
        try:
            conn = self.db.connect()
            query = """
            SELECT label,stat_of
            FROM history_insert
            WHERE used = 1
            LIMIT 1
            """
            result = conn.execute(text(query)).mappings().fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"[ERREUR] Impossible de récupérer le dernier fichier importé : {e}")
            return None
        finally:
            try:
                if conn:
                    conn.close()
            except Exception as close_err:
                print(f"[ERREUR] Fermeture de connexion échouée : {close_err}")
                
    def get_capital_sums(self):
        conn = None
        try:
            conn = self.db.connect()
            capital_result = conn.execute(text("SELECT * FROM total_capital_encours_credit;"))
            columns = capital_result.keys()
            capital_data = [dict(zip(columns, row)) for row in capital_result.fetchall()]
            print("Capital sums data:", capital_data)
            return {"capital_sums": capital_data}
        except Exception as e:
            print(f"[ERREUR] Impossible de récupérer les données : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture de connexion échouée : {close_err}")
                     
                    

    def get_encours_credit_by_date(self, date: str):
        conn = None
        try:
            # Validation simple du format AAAAMMJJ
            if not date.isdigit() or len(date) != 8:
                raise ValueError(f"Format de date invalide : {date}")

            table_name = f"encours_credit_{date}"
            query = text(f"SELECT * FROM `{table_name}`")  # les backticks évitent des erreurs si le nom a des caractères spéciaux

            conn = self.db.connect()
            result = conn.execute(query)
            columns = result.keys()
            data = [dict(zip(columns, row)) for row in result.fetchall()]

            print(f"✅ Données extraites depuis la table {table_name} :", data)
            return {"data": data}

        except Exception as e:
            print(f"[ERREUR] Impossible d’exécuter la requête : {e}")
            return None

        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture de connexion échouée : {close_err}")

                        