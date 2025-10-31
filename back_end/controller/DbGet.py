from sqlalchemy import text
from db.db import DB

class DbGet:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
        
    
    def create_indexes(self):
      
        indexes = [
            # Table aa_arrangement_mcbc_live_full
            "CREATE INDEX IF NOT EXISTS idx_arrangement_id ON aa_arrangement_mcbc_live_full(id(255))",
            "CREATE INDEX IF NOT EXISTS idx_co_code ON aa_arrangement_mcbc_live_full(co_code(255))",
            "CREATE INDEX IF NOT EXISTS idx_customer ON aa_arrangement_mcbc_live_full(customer(255))",
            "CREATE INDEX IF NOT EXISTS idx_linked_appl_id ON aa_arrangement_mcbc_live_full(linked_appl_id(255))",
            "CREATE INDEX IF NOT EXISTS idx_product_line ON aa_arrangement_mcbc_live_full(product_line(255))",
            "CREATE INDEX IF NOT EXISTS idx_arr_status ON aa_arrangement_mcbc_live_full(arr_status(255))",
            "CREATE INDEX IF NOT EXISTS idx_product_group ON aa_arrangement_mcbc_live_full(product_group(255))",
            "CREATE INDEX IF NOT EXISTS idx_start_date ON aa_arrangement_mcbc_live_full(start_date(255))",

            # Table customer_mcbc_live_full_partie_1
            "CREATE INDEX IF NOT EXISTS idx_customer_id ON customer_mcbc_live_full(id(255))",
            "CREATE INDEX IF NOT EXISTS idx_customer_sector ON customer_mcbc_live_full(sector(255))",
            "CREATE INDEX IF NOT EXISTS idx_customer_short_name_name_1 ON customer_mcbc_live_full(short_name(255), name_1(255))",
            "CREATE INDEX IF NOT EXISTS idx_customer_street ON customer_mcbc_live_full(street(255))",
            "CREATE INDEX IF NOT EXISTS idx_customer_sms_1 ON customer_mcbc_live_full(sms_1(255))",
            "CREATE INDEX IF NOT EXISTS idx_customer_gender ON customer_mcbc_live_full(gender(255))",
            "CREATE INDEX IF NOT EXISTS idx_customer_industry ON customer_mcbc_live_full(industry(255))",
            "CREATE INDEX IF NOT EXISTS idx_customer_target ON customer_mcbc_live_full(target(255))",
            "CREATE INDEX IF NOT EXISTS idx_customer_legal_id ON customer_mcbc_live_full(legal_id(255))",
            "CREATE INDEX IF NOT EXISTS idx_customer_account_officer ON customer_mcbc_live_full(account_officer(255))",

            # Table aa_account_details_mcbc_live_full
            "CREATE INDEX IF NOT EXISTS idx_account_details_id ON aa_account_details_mcbc_live_full(id(255))",
            "CREATE INDEX IF NOT EXISTS idx_account_details_maturity_date ON aa_account_details_mcbc_live_full(maturity_date(255))",

            # Table eb_cont_bal_mcbc_live_full
            "CREATE INDEX IF NOT EXISTS idx_contract_balance_id ON eb_cont_bal_mcbc_live_full(id(255))",
            "CREATE INDEX IF NOT EXISTS idx_balance_columns ON eb_cont_bal_mcbc_live_full(open_balance(255))",
            "CREATE INDEX IF NOT EXISTS idx_debit_mvmt ON eb_cont_bal_mcbc_live_full(debit_mvmt(255))",
            "CREATE INDEX IF NOT EXISTS idx_credit_mvmt ON eb_cont_bal_mcbc_live_full(credit_mvmt(255))",
            "CREATE INDEX IF NOT EXISTS idx_contract_balance_type_sysdate ON eb_cont_bal_mcbc_live_full(type_sysdate(255))",

            # Table aa_arr_interest_mcbc_live_full
            "CREATE INDEX idx_interest_id ON aa_arr_interest_mcbc_live_full (id(255))",
            "CREATE INDEX IF NOT EXISTS idx_interest_id_comp_1 ON aa_arr_interest_mcbc_live_full(id_comp_1(255))",
            "CREATE INDEX IF NOT EXISTS idx_interest_id_comp_2 ON aa_arr_interest_mcbc_live_full(id_comp_2(255))",
            "CREATE INDEX IF NOT EXISTS idx_interest_effective_rate ON aa_arr_interest_mcbc_live_full(effective_rate(255))",

            # Table account_mcbc_live_full
            "CREATE INDEX IF NOT EXISTS idx_account_id ON account_mcbc_live_full(id(255))",
            "CREATE INDEX IF NOT EXISTS idx_account_opening_date ON account_mcbc_live_full(opening_date(255))",

            # Table em_lo_application_mcbc_live_full
            "CREATE INDEX IF NOT EXISTS idx_em_arrangement_id ON em_lo_application_mcbc_live_full (arrangement_id)",

            "CREATE INDEX IF NOT EXISTS idx_em_proc_status ON em_lo_application_mcbc_live_full(proc_status(255))",
            
            # Table teller_mcbc_his_full
            "CREATE INDEX idx_teller_value_date ON teller_mcbc_his_full(value_date_1)",
            "CREATE INDEX idx_teller_transaction_code ON teller_mcbc_his_full(transaction_code)",
            "CREATE INDEX idx_teller_currency ON teller_mcbc_his_full(currency_1)"  
        ]

        conn = None
        try:
            conn = self.db.connect()
            for idx_query in indexes:
                conn.execute(text(idx_query))
            conn.commit()
            print("[INFO] Tous les index ont été créés avec succès ✅")
        except Exception as e:
            print(f"[ERREUR] create_indexes : {e}")
        finally:
            if conn:
                conn.close()
            
            

    def getHistoryDate(self):
       
        conn = None
        try:
            conn = self.db.connect()
            query = text("""
                SELECT label 
                FROM history_insert
                WHERE used = 1 
                LIMIT 1
            """)
            result = conn.execute(query).fetchone()
            if result:
                return str(result[0])
            return None
        except Exception as e:
            print(f"[ERREUR] getHistory : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getHistory) : {close_err}")
                    
                    

    def create_tableDatPreCompute(self, name: str):
       
        conn = None
        try:
            # # recuperation historydate
            # label = self.getHistoryDate()
            # # Récupération du label dynamique
            
            table_name = f"dat_{name}"

            query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} AS
            SELECT 
                arrangement.co_code AS Agence, 
                arrangement.customer AS code_client,
                arrangement.linked_appl_id AS Numero_compte,
                arrangement.product AS Produits,

                -- Nom du compte optimisé avec une jointure
                CASE 
                    WHEN cust.sector = 1000 
                        THEN CONCAT(cust.short_name, ' ', cust.name_1)
                    ELSE cust.name_1
                END AS Nom_compte,

                cust.street AS Adresse,
                cust.sms_1 AS Contact,
                cust.gender AS Titre,
                cust.industry,
                cust.target,
                cust.legal_id AS Identification_Personne,

                -- Jointure directe pour le taux d’intérêt
                interet.effective_rate AS taux_d_interet, 

                arrangement.product_group AS Type_Produit,
                cb.open_balance,
                cb.debit_mvmt,
                cb.credit_mvmt,
                acc.opening_date AS Date_effet,

                TIMESTAMPDIFF(MONTH, arrangement.start_date, details.maturity_date) AS Durée_en_mois,
                DATEDIFF(details.maturity_date, arrangement.start_date) AS Durée_en_jours, 
                details.maturity_date AS date_echeance,

                cust.account_officer AS chargé_clientele,
                CASE
                    WHEN cust.sector = 1000 THEN 'Particulier'
                    ELSE 'Morale'
                END AS categorie,

                cb.type_sysdate,
                interet.id AS id_comp_2

            FROM 
                aa_arrangement_mcbc_live_full AS arrangement

            INNER JOIN 
                aa_account_details_mcbc_live_full AS details
                    ON details.id = arrangement.id

            LEFT JOIN 
                customer_mcbc_live_full AS cust
                    ON cust.id = SUBSTRING_INDEX(arrangement.customer, '|', 1)  
                    

            LEFT JOIN 
                eb_cont_bal_mcbc_live_full AS cb
                    ON cb.id = arrangement.linked_appl_id

            LEFT JOIN 
                account_mcbc_live_full AS acc
                    ON acc.id = arrangement.linked_appl_id 

            LEFT JOIN 
                aa_arr_interest_mcbc_live_full AS interet
                    ON interet.id_comp_1 = arrangement.id
                AND interet.id_comp_2 = 'DEPOSITINT' 

            WHERE 
                arrangement.product_line = 'DEPOSITS'
                AND arrangement.arr_status IN ('AUTH', 'CURRENT')
                AND arrangement.product_group = 'DAT.SP.MG';

           
            """

            conn = self.db.connect()
            drop_query = f"DROP TABLE IF EXISTS {table_name}"
            conn.execute(text(drop_query))
            conn.execute(text(query))
            conn.commit() 

            print(f"[INFO] Table {table_name} créée avec succès ✅")
            return table_name

        except Exception as e:
            print(f"[ERREUR] create_tableDatPreCompute : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (create_tableDatPreCompute) : {close_err}")


            
            
    def traitement_dat(self, table_name: str):
       
        conn = None
        try:
            conn = self.db.connect()

            
            query_nulls = f"""
            UPDATE {table_name}
            SET 
                debit_mvmt   = COALESCE(debit_mvmt, 0),
                credit_mvmt  = COALESCE(credit_mvmt, 0),
                open_balance = COALESCE(open_balance, 0);
            """
            conn.execute(text(query_nulls))

            
            query_code_client = f"""
            UPDATE {table_name}
            SET code_client = SUBSTRING_INDEX(code_client, '|', 1);
            """
            conn.execute(text(query_code_client))
            
            query_dedup = f"""
                DELETE t1 FROM {table_name} t1
                INNER JOIN {table_name} t2
                ON t1.Agence = t2.Agence
                AND t1.Numero_compte = t2.Numero_compte
                AND t1.Produits = t2.Produits
                AND t1.id_comp_2 < t2.id_comp_2;
                """
            conn.execute(text(query_dedup))

           
            query_drop_cols = f"""
            ALTER TABLE {table_name}
            DROP COLUMN type_sysdate,
            DROP COLUMN debit_mvmt,
            DROP COLUMN open_balance,
            DROP COLUMN credit_mvmt;
            """
            conn.execute(text(query_drop_cols))
            conn.commit()
            print(f"[INFO] Nettoyage terminé pour {table_name} ✅")

        except Exception as e:
            print(f"[ERREUR] clean_tableDatPreCompute : {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (clean_tableDatPreCompute) : {close_err}")
    
    