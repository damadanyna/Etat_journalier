import pandas as pd
from db.db import DB
from sqlalchemy import text

class Operation:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
        
        
    def calculeAmtCap(self, table_name: str):
       
       
        conn = None
        try:
            conn = self.db.connect()

            # Lire la table entière dans un DataFrame
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)

            # Fonction pour calculer montant_capital
            def extract_balance(row):
                montant_capital_total = 0
                if 'type_sysdate' not in row or 'debit_mvmt' not in row or 'credit_mvmt' not in row or 'open_balance' not in row:
                    return montant_capital_total
                
                type_sysdate_values = str(row['type_sysdate']).split('|')
               
                
                for index, entry in enumerate(type_sysdate_values):
                    if entry == "CURACCOUNT" or entry.startswith("CURACCOUNT-202411") or entry.startswith("CURACCOUNT-202412") or entry.startswith("CURACCOUNT-202501") or entry.startswith("CURACCOUNT-202502") or entry.startswith("CURACCOUNT-202503"):
                        debit_mvmt = row['debit_mvmt'].split('|')[index] if index < len(row['debit_mvmt'].split('|')) else '0'
                        credit_mvmt = row['credit_mvmt'].split('|')[index] if index < len(row['credit_mvmt'].split('|')) else '0'
                        open_balance = row['open_balance'].split('|')[index] if index < len(row['open_balance'].split('|')) else '0'
                  
                        montant_capital_total += float(debit_mvmt.strip() or '0')
                        montant_capital_total += float(credit_mvmt.strip() or '0')
                        montant_capital_total += float(open_balance.strip() or '0')

                return montant_capital_total
            
            def extract_pay_amt(row):
                montant_pay_total = 0
                if 'type_sysdate' not in row or 'debit_mvmt' not in row or 'credit_mvmt' not in row or 'open_balance' not in row:
                     return montant_pay_total

                if isinstance(row['type_sysdate'], str):
                    type_sysdate_values = row['type_sysdate'].split('|')
                    
                    for index, entry in enumerate(type_sysdate_values):
                        # Condition spécifique pour 'montant_pay_total' basée sur 'ACCDEPOSITINT'
                        if entry == "ACCDEPOSITINT" or entry.startswith("ACCDEPOSITINT-2024") or entry.startswith("CURACCOUNT-2025"):
                            debit_mvmt = row['debit_mvmt'].split('|')[index] if index < len(row['debit_mvmt'].split('|')) else '0'
                            credit_mvmt = row['credit_mvmt'].split('|')[index] if index < len(row['credit_mvmt'].split('|')) else '0'
                            open_balance = row['open_balance'].split('|')[index] if index < len(row['open_balance'].split('|')) else '0'
                            
                            # Utilisation de abs() pour s'assurer que les valeurs sont en valeurs absolues avant d'ajouter
                            montant_pay_total += float(debit_mvmt.strip() or '0')
                            montant_pay_total += float(credit_mvmt.strip() or '0')
                            montant_pay_total += float(open_balance.strip() or '0')
                    
                return montant_pay_total
            
            def add_column_if_not_exists(conn, table_name, column_name, column_type="DOUBLE DEFAULT 0"):
                # Vérifie si la colonne existe déjà
                result = conn.execute(text(f"""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table AND COLUMN_NAME = :column
                """), {"table": table_name, "column": column_name}).fetchone()
                
                if not result:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))

   
            # Calculer la nouvelle colonne
            df['montant_capital'] = df.apply(extract_balance, axis=1)

            df['montant_pay_total'] = df.apply(extract_pay_amt, axis=1)

            # Ajouter la colonne à la table si elle n'existe pas encore
            add_column_if_not_exists(conn, table_name, "montant_capital")
            add_column_if_not_exists(conn, table_name, "montant_pay_total")

            

            # Mettre à jour les valeurs dans la table
            for idx, row in df.iterrows():
                update_query_capital = f"""
                    UPDATE {table_name}
                    SET montant_capital = :montant_capital
                    WHERE Numero_compte = :Numero_compte
                """
                
                update_query_amt_pay = f"""
                    UPDATE {table_name}
                    SET montant_pay_total = :montant_pay_total
                    WHERE Numero_compte = :Numero_compte
                """
                conn.execute(text(update_query_amt_pay), {"montant_pay_total": row['montant_pay_total'], "Numero_compte": row['Numero_compte']})
                conn.execute(text(update_query_capital), {"montant_capital": row['montant_capital'], "Numero_compte": row['Numero_compte']})

            conn.commit()
            print(f"[INFO] Colonne montant_capital calculée et mise à jour pour {table_name} ✅")

        except Exception as e:
            print(f"[ERREUR] calculeAmtCap : {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (calculeAmtCap) : {close_err}")

    def exportExcel(self, table_name: str, output_file: str = None):
        """
        Exporte une table MySQL (dat_<label>) dans un fichier Excel.
        """
        if not table_name.startswith("dat_") or table_name.startswith("dav_"):
            print(f"[ERREUR] Table '{table_name}' non autorisée à l'export ❌")
            return None
        conn = None
        try:
            conn = self.db.connect()

            # Lire la table dans un DataFrame
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)

            # Nom de fichier par défaut si non fourni
            if not output_file:
                output_file = f"{table_name}.xlsx"

            # Exporter en Excel
            df.to_excel(output_file, index=False, engine="openpyxl")

            print(f"[INFO] Export terminé ✅ Fichier : {output_file}")
            return output_file

        except Exception as e:
            print(f"[ERREUR] exportExcel : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (exportExcel) : {close_err}")
                    
                    
                    
            