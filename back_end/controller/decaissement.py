from sqlalchemy import text
from db.db import DB
import pandas as pd

class DecaissementOptimise:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
        
    def create_capital_function(self):
        """Crée une fonction MySQL pour calculer le montant capital"""
        try:
            query = """
            
CREATE FUNCTION calcul_montant_capital(
                type_sysdate TEXT,
                debit_mvmt TEXT,
                credit_mvmt TEXT,
                open_balance TEXT,
                date_limite INT
            )
            RETURNS DECIMAL(20,2)
            DETERMINISTIC
            BEGIN
                DECLARE token TEXT;
                DECLARE remaining_type TEXT;
                DECLARE remaining_debit TEXT;
                DECLARE remaining_credit TEXT;
                DECLARE remaining_open TEXT;
                DECLARE date_part INT;
                
                DECLARE sep_pos INT;
                DECLARE debit_val DECIMAL(20,2);
                DECLARE credit_val DECIMAL(20,2);
                DECLARE open_val DECIMAL(20,2);
                DECLARE montant_total DECIMAL(20,2) DEFAULT 0;

                -- Initialisation des chaînes
                SET remaining_type = type_sysdate;
                SET remaining_debit = debit_mvmt;
                SET remaining_credit = credit_mvmt;
                SET remaining_open = open_balance;

                -- Boucle principale
                WHILE LENGTH(remaining_type) > 0 DO
                    -- Extraction du token type_sysdate
                    SET sep_pos = LOCATE('|', remaining_type);
                    IF sep_pos = 0 THEN
                        SET token = remaining_type;
                        SET remaining_type = '';
                    ELSE
                        SET token = LEFT(remaining_type, sep_pos - 1);
                        SET remaining_type = SUBSTRING(remaining_type, sep_pos + 1);
                    END IF;

                    -- Extraction debit_mvmt
                    SET sep_pos = LOCATE('|', remaining_debit);
                    IF sep_pos = 0 THEN
                        SET debit_val = IF(remaining_debit = '' OR remaining_debit IS NULL, 0, 
                                         CAST(remaining_debit AS DECIMAL(20,2)));
                        SET remaining_debit = '';
                    ELSE
                        SET debit_val = IF(LEFT(remaining_debit, sep_pos - 1) = '' OR LEFT(remaining_debit, sep_pos - 1) IS NULL,
                                        0, CAST(LEFT(remaining_debit, sep_pos - 1) AS DECIMAL(20,2)));
                        SET remaining_debit = SUBSTRING(remaining_debit, sep_pos + 1);
                    END IF;

                    -- Extraction credit_mvmt
                    SET sep_pos = LOCATE('|', remaining_credit);
                    IF sep_pos = 0 THEN
                        SET credit_val = IF(remaining_credit = '' OR remaining_credit IS NULL, 0, 
                                          CAST(remaining_credit AS DECIMAL(20,2)));
                        SET remaining_credit = '';
                    ELSE
                        SET credit_val = IF(LEFT(remaining_credit, sep_pos - 1) = '' OR LEFT(remaining_credit, sep_pos - 1) IS NULL,
                                         0, CAST(LEFT(remaining_credit, sep_pos - 1) AS DECIMAL(20,2)));
                        SET remaining_credit = SUBSTRING(remaining_credit, sep_pos + 1);
                    END IF;

                    -- Extraction open_balance
                    SET sep_pos = LOCATE('|', remaining_open);
                    IF sep_pos = 0 THEN
                        SET open_val = IF(remaining_open = '' OR remaining_open IS NULL, 0, 
                                        CAST(remaining_open AS DECIMAL(20,2)));
                        SET remaining_open = '';
                    ELSE
                        SET open_val = IF(LEFT(remaining_open, sep_pos - 1) = '' OR LEFT(remaining_open, sep_pos - 1) IS NULL,
                                        0, CAST(LEFT(remaining_open, sep_pos - 1) AS DECIMAL(20,2)));
                        SET remaining_open = SUBSTRING(remaining_open, sep_pos + 1);
                    END IF;

                    -- Calcul pour TOTCOMMITMENT
                    IF token = 'TOTCOMMITMENT' THEN
                        SET montant_total = montant_total + open_val + credit_val + debit_val;

                    ELSEIF token LIKE 'TOTCOMMITMENT-%%' THEN
                        SET date_part = CAST(SUBSTRING(token, LOCATE('-', token) + 1) AS UNSIGNED);

                        IF date_part <= date_limite THEN
                            SET montant_total = montant_total + open_val + credit_val + debit_val;
                        END IF;
                    END IF;

                END WHILE;

                RETURN montant_total;
                
                END
            """

            with self.db.connect() as conn:
                drop_query = "DROP FUNCTION IF EXISTS calcul_montant_capital"
                conn.execute(text(drop_query))
                conn.commit()
                
                conn.execute(text(query))
                conn.commit()
            
            print("[INFO] Function calcul_montant_capital créée avec succès ✅")
            return True

        except Exception as e:
            print(f"[ERREUR] création function calcul_montant_capital : {e}")
            return False

    def create_frais_dossier_function(self):
        try:
            query = """
            CREATE FUNCTION calcul_frais_dossier(
                montant_capital DECIMAL(20,2),
                charge_rate DECIMAL(10,4)
            )
            RETURNS DECIMAL(20,2)
            DETERMINISTIC
            BEGIN
                DECLARE frais DECIMAL(20,2);
                
                IF montant_capital IS NULL OR charge_rate IS NULL THEN
                    RETURN NULL;
                END IF;
                
                SET frais = montant_capital * (charge_rate / 100);
                RETURN frais;
            END
            """

            with self.db.connect() as conn:
                drop_query = "DROP FUNCTION IF EXISTS calcul_frais_dossier"
                conn.execute(text(drop_query))
                conn.commit()
                
                conn.execute(text(query))
                conn.commit()
            
            print("[INFO] Function calcul_frais_dossier créée avec succès ✅")
            return True

        except Exception as e:
            print(f"[ERREUR] création function calcul_frais_dossier : {e}")
            return False


    def create_indexes(self):
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_arrangement_id ON aa_arrangement_mcbc_live_full (id(255))",
            "CREATE INDEX IF NOT EXISTS idx_arrangement_customer ON aa_arrangement_mcbc_live_full (customer(255))",
            "CREATE INDEX IF NOT EXISTS idx_arrangement_linked_appl ON aa_arrangement_mcbc_live_full (linked_appl_id(255))",
            "CREATE INDEX IF NOT EXISTS idx_account_opening_date ON account_mcbc_live_full (opening_date)",
            "CREATE INDEX IF NOT EXISTS idx_em_arrangement ON em_lo_application_mcbc_live_full (arrangement_id(255))",
            "CREATE INDEX IF NOT EXISTS idx_charge_id_prefix ON aa_arr_charge_mcbc_live_full (id)",
            "CREATE INDEX IF NOT EXISTS idx_charge_rate ON aa_arr_charge_mcbc_live_full (charge_rate)"

        ]
        
        try:
            with self.db.connect() as conn:
                for index_query in indexes:
                    conn.execute(text(index_query))
                conn.commit()
            
            print("[INFO] Index créés avec succès ✅")
            return True
            
        except Exception as e:
            print(f"[ERREUR] create_indexes : {e}")
            return False

    def create_decaissement_table(self, date_limite: str):
        try:
            table_name = f"decaissement_{date_limite}"
            
            query = f"""
                CREATE TABLE {table_name} AS
                SELECT
                    arr.co_code AS Agence, 
                    SUBSTRING_INDEX(arr.customer, '|', 1) AS code_client,
                    arr.linked_appl_id AS Numero_compte,
                    acc_det.id as Numero_pret,
                    CASE 
                        WHEN cust.sector != 1000 AND cust.nom_complet IS NOT NULL THEN
                            CASE 
                                WHEN cust.nom_complet LIKE '% % %' THEN 
                                    SUBSTRING_INDEX(cust.nom_complet, ' ', 
                                        (LENGTH(cust.nom_complet) - LENGTH(REPLACE(cust.nom_complet, ' ', '')) + 1) DIV 2)
                                ELSE cust.nom_complet
                            END
                        ELSE cust.nom_complet
                    END AS Nom_compte,
                    cust.industry AS Secteur_Activite,
                    cust.gender AS Titre,
                    acc.opening_date AS date_decaissement,  
                    TIMESTAMPDIFF(MONTH, acc.opening_date, acc_det.maturity_date) AS Duree,
                    arr.product AS Produits,
                    (
                        SELECT effective_rate  
                        FROM aa_arr_interest_mcbc_live_full 
                        WHERE id_comp_1 = arr.id 
                        AND id_comp_2 = 'PRINCIPALINT' 
                        LIMIT 1
                    ) AS taux_d_interet,
                    -- Calcul du montant capital avec la fonction
                    calcul_montant_capital(
                        cb.type_sysdate, 
                        cb.debit_mvmt,  
                        cb.credit_mvmt,  
                        cb.open_balance,
                        {date_limite}
                    ) AS montant_capital,
                    chg.charge_rate,
                    -- Calcul des frais de dossier avec la fonction
                    calcul_frais_dossier(
                        calcul_montant_capital(cb.type_sysdate, cb.debit_mvmt, cb.credit_mvmt, cb.open_balance,{date_limite}),
                        chg.charge_rate
                    ) AS frais_de_dossier,
                    CASE
                        WHEN cust.sector = 1000 THEN 'Particulier'
                        ELSE 'Morale'
                    END AS categorie
                FROM 
                    aa_arrangement_mcbc_live_full AS arr
                INNER JOIN 
                    aa_account_details_mcbc_live_full AS acc_det
                    ON acc_det.id = arr.id
                LEFT JOIN 
                    temp_clients AS cust
                    ON cust.id = SUBSTRING_INDEX(arr.customer, '|', 1)
                LEFT JOIN 
                    eb_cont_bal_mcbc_live_full AS cb
                    ON cb.id = arr.linked_appl_id
                LEFT JOIN 
                    account_mcbc_live_full AS acc
                    ON acc.id = arr.linked_appl_id 
                LEFT JOIN 
                    aa_arr_charge_mcbc_live_full AS chg
                    ON SUBSTRING_INDEX(chg.id, '-', 1) = arr.id  
                INNER JOIN
                    em_lo_application_mcbc_live_full AS em
                    ON em.arrangement_id = arr.id   
                WHERE 
                    arr.product_line = 'LENDING'
                    AND arr.arr_status IN ('AUTH', 'CURRENT')
                    AND acc.opening_date >= '20241125'
                    AND em.proc_status = 'DISBURSED' limit 100; 
                
            """
            
            with self.db.connect() as conn:
                # Supprimer la table si elle existe
                drop_query = f"DROP TABLE IF EXISTS {table_name}"
                conn.execute(text(drop_query))
                conn.commit()
                
                # Créer la nouvelle table
                conn.execute(text(query))
                conn.commit()
            
            print(f"[INFO] Table {table_name} créée avec succès ✅")
            return table_name
            
        except Exception as e:
            print(f"[ERREUR] create_decaissement_table : {e}")
            return False

    def generate_decaissement_report(self, date_limite: str):
        """Génère le rapport complet de décaissement"""
        try:
            # Créer les fonctions
            if not self.create_capital_function():
                return False
                
            if not self.create_frais_dossier_function():
                return False
            
            # Créer les index
            if not self.create_indexes():
                print("[ATTENTION] Problème avec les index, continuation...")
                        
            # Créer la table finale
            table_name = self.create_decaissement_table(date_limite)
            
            if not table_name:
                return False
            
            # Fonction pour supprimer les doublons dans les noms
            def remove_duplicate_name(name):
                if pd.isnull(name):
                    return name
                words = name.strip().split()
                half = len(words) // 2
                if len(words) % 2 == 0 and words[:half] == words[half:]:
                    return ' '.join(words[:half])
                return name

            # Vérifier et traiter les doublons avec pandas
            with self.db.connect() as conn:
                # Charger les données dans un DataFrame pandas
                df_query = f"SELECT * FROM {table_name}"
                df = pd.read_sql(df_query, conn)
                
                # Afficher le nombre initial d'enregistrements
                initial_count = len(df)
                print(f"[INFO] Nombre initial d'enregistrements : {initial_count}")
                
                # Vérifier les doublons avant traitement
                duplicates_before = df.duplicated(subset=['Numero_compte']).sum()
                if duplicates_before > 0:
                    print(f"[INFO] {duplicates_before} doublons détectés dans Numero_compte avant traitement")
                
                # Appliquer le nettoyage seulement aux clients Morale (categorie != 'Particulier')
                if 'categorie' in df.columns and 'Nom_compte' in df.columns:
                    df.loc[df['categorie'] != 'Particulier', 'Nom_compte'] = (
                        df.loc[df['categorie'] != 'Particulier', 'Nom_compte']
                        .apply(remove_duplicate_name)
                    )
                    print("[INFO] Nettoyage des noms en double appliqué aux clients Morale")
                
                # Supprimer les doublons basés sur Numero_compte
                df = df.drop_duplicates(subset=['Numero_compte'], keep='first')
                
                # Afficher le nombre d'enregistrements après suppression des doublons
                final_count = len(df)
                duplicates_removed = initial_count - final_count
                print(f"[INFO] {duplicates_removed} doublons supprimés")
                print(f"[INFO] Nombre final d'enregistrements : {final_count}")
                
                # Vérifier les doublons après traitement
                duplicates_after = df.duplicated(subset=['Numero_compte']).sum()
                if duplicates_after == 0:
                    print("[INFO] Aucun doublon restant dans Numero_compte ✅")
                else:
                    print(f"[ATTENTION] {duplicates_after} doublons restants après traitement")
                
                # Recréer la table avec les données nettoyées
                # Supprimer l'ancienne table
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                
                # Créer une nouvelle table avec les données nettoyées
                df.to_sql(table_name, conn, index=False, if_exists='replace')
                conn.commit()
                
                # Compter les enregistrements finaux dans la base de données
                count_query = f"SELECT COUNT(*) FROM {table_name}"
                result = conn.execute(text(count_query))
                db_count = result.fetchone()[0]
            
            print(f"[INFO] Rapport généré avec succès : {db_count} enregistrements uniques")
            
            return {
                "status": "success",
                "table_name": table_name,
                "record_count": db_count,
                "duplicates_count": duplicates_before,
                "duplicates_removed": duplicates_removed,
                "initial_count": initial_count,
                "final_count": final_count
            }
            
        except Exception as e:
            print(f"[ERREUR] generate_decaissement_report : {e}")
            return False

    # def cleanup(self, table_name: str = None):
    #     """Nettoie les ressources temporaires"""
    #     try:
    #         with self.db.connect() as conn:
    #             # Supprimer les fonctions
    #             functions_to_drop = [
    #                 "calcul_montant_capital",
    #                 "calcul_frais_dossier"
    #             ]
                
    #             for function in functions_to_drop:
    #                 try:
    #                     conn.execute(text(f"DROP FUNCTION IF EXISTS {function}"))
    #                 except Exception as e:
    #                     print(f"[ATTENTION] Impossible de supprimer {function} : {e}")
                
    #             # Supprimer les tables temporaires
    #             temp_tables = [
    #                 "temp_clients_decaissement"
    #             ]
                
    #             if table_name:
    #                 temp_tables.append(table_name)
                
    #             for table in temp_tables:
    #                 try:
    #                     conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
    #                 except Exception as e:
    #                     print(f"[ATTENTION] Impossible de supprimer {table} : {e}")
                
    #             conn.commit()
    #             print("[INFO] Nettoyage effectué avec succès ✅")
                
    #     except Exception as e:
    #         print(f"[ERREUR] cleanup : {e}")