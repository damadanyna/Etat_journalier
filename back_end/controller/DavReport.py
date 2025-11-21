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
    
    
    def getAllResumeDav(self, type_table: str):
            
        conn = None
        try:
            conn = self.db.connect()

            type_table = type_table.lower().strip()
            if type_table not in ["dav", "dat", "epr", "decaissement"]:
                raise ValueError("Type de table invalide. Valeurs possibles : 'dav', 'dat', 'epr', 'decaissement'.")

            tables_query = text(f"SHOW TABLES LIKE '{type_table}_%'")
            tables_result = conn.execute(tables_query).fetchall()

            if not tables_result:
                print(f"[INFO] Aucune table '{type_table}_' trouvée.")
                return []

            all_summaries = []

            for row in tables_result:
                table_name_vrai = row[0]

                try:
                    if type_table == "dav":
                        query = text(f"""
                            SELECT 
                                COUNT(DISTINCT code_client) AS nb_clients,
                                SUM(solde) AS total_montant_dav,
                                SUM(debit) AS total_debit_dav,
                                SUM(credit) AS total_credit_dav
                            FROM `{table_name_vrai}`
                        """)

                    elif type_table == "dat":
                        query = text(f"""
                            SELECT 
                                COUNT(*) AS nb_lignes,
                                COUNT(DISTINCT code_client) AS nb_clients,
                                SUM(montant_capital) AS total_montant_capital,
                                SUM(montant_pay_total) AS total_montant_pay_total
                            FROM `{table_name_vrai}`
                        """)

                    elif type_table == "epr":
                        query = text(f"""
                            SELECT 
                                COUNT(DISTINCT code_client) AS nb_clients,
                                SUM(solde) AS total_montant_epr,
                                SUM(Debit) AS total_debit_epr,
                                SUM(Credit) AS total_credit_epr
                            FROM `{table_name_vrai}`
                        """)
                    elif type_table == "decaissement":
                        query = text(f"""
                            SELECT 
                                COUNT(DISTINCT code_client) AS nb_clients,
                                 SUM(montant_capital) AS total_montant_capital,
                                 SUM(frais_de_dossier) AS total_frais_de_dossier
                            FROM `{table_name_vrai}`
                        """)
                    result = conn.execute(query).fetchone()
                    
                    if not result:
                        continue

                    if type_table == "dav":
                        summary = {
                            "table_name": table_name_vrai,
                            "nb_clients": int(result[0] or 0),
                            "total_montant_dav": float(result[1] or 0),
                            "total_debit_dav": float(result[2] or 0),
                            "total_credit_dav": float(result[3] or 0)
                        }

                    elif type_table == "dat":
                        summary = {
                            "table_name": table_name_vrai,
                            "nb_lignes": int(result[0] or 0),
                            "nb_clients": int(result[1] or 0),
                            "total_montant_capital": float(result[2] or 0),
                            "total_montant_pay_total": float(result[3] or 0)
                        }

                    elif type_table == "epr":
                        summary = {
                            "table_name": table_name_vrai,
                            "nb_clients": int(result[0] or 0),
                            "total_montant_epr": float(result[1] or 0),
                            "total_debit_epr": float(result[2] or 0),
                            "total_credit_epr": float(result[3] or 0)
                        }
                    elif type_table == "decaissement":
                        summary = {
                            "table_name": table_name_vrai,
                            "nb_clients": int(result[0] or 0),
                            "total_montant_capital": float(result[1] or 0),
                            "total_frais_de_dossier": float(result[2] or 0)
                            
                        }

                    all_summaries.append(summary)

                except Exception as inner_err:
                    print(f"[ERREUR] Résumé échoué pour {table_name_vrai} : {inner_err}")
                    continue

            return all_summaries

        except Exception as e:
            print(f"[ERREUR] getAllResumeDav ({type_table}) : {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as close_err:
                    print(f"[ERREUR] Fermeture connexion (getAllResumeDav) : {close_err}")


    def getTotalResumer(self, type_table: str):
        
        all_summaries = self.getAllResumeDav(type_table)
        if not all_summaries:
            return {}

        type_table = type_table.lower().strip()

        if type_table == "dav":
            total_resumer = {
                "type": "dav",
                "nb_clients_total": sum(item.get("nb_clients", 0) for item in all_summaries),
                "total_montant_dav": sum(item.get("total_montant_dav", 0.0) for item in all_summaries),
                "total_debit_dav": sum(item.get("total_debit_dav", 0.0) for item in all_summaries),
                "total_credit_dav": sum(item.get("total_credit_dav", 0.0) for item in all_summaries),
            }

        elif type_table == "dat":
            total_resumer = {
                "type": "dat",
                "nb_lignes_total": sum(item.get("nb_lignes", 0) for item in all_summaries),
                "nb_clients_total": sum(item.get("nb_clients", 0) for item in all_summaries),
                "total_montant_capital": sum(item.get("total_montant_capital", 0.0) for item in all_summaries),
                "total_montant_pay_total": sum(item.get("total_montant_pay_total", 0.0) for item in all_summaries),
            }

        elif type_table == "epr":
            total_resumer = {
                "type": "epr",
                "nb_clients_total": sum(item.get("nb_clients", 0) for item in all_summaries),
                "total_montant_epr": sum(item.get("total_montant_epr", 0.0) for item in all_summaries),
                "total_debit_epr": sum(item.get("total_debit_epr", 0.0) for item in all_summaries),
                "total_credit_epr": sum(item.get("total_credit_epr", 0.0) for item in all_summaries),
            }
        elif type_table == "decaissement":
            total_resumer = {
                "type": "decaissement",
                "nb_clients_total": sum(item.get("nb_clients", 0) for item in all_summaries),
                "total_montant_capital": sum(item.get("total_montant_capital", 0.0) for item in all_summaries),
                "total_frais_de_dossier": sum(item.get("total_frais_de_dossier", 0.0) for item in all_summaries),
            }

        else:
            raise ValueError("Type de table invalide. Utiliser 'dav', 'dat' ou 'epr', 'decaissement'.")

        return total_resumer


    def getTotalParProduit(self, type_table: str, agence: str = None,
                       date_debut: str = None, date_fin: str = None,
                       single_date_if_all: str = "20251028"):
       
        AGENCES_DISPO = [
            "MG0010009","MG0010004","MG0010024","MG0010052","MG0010011",
            "MG0010012","MG0010010","MG0011001","MG0010003","MG0010022",
            "MG0010053","MG0010013","MG0010041","MG0010023"
        ]

        type_table = type_table.lower().strip()
        if type_table not in ["dav", "dat", "epr"]:
            raise ValueError("Type invalide. Valeurs possibles : 'dav', 'dat', 'epr'.")

        conn = None
        try:
            conn = self.db.connect()

            # Récupérer toutes les tables du type
            tables_query = text(f"SHOW TABLES LIKE '{type_table}_%'")
            all_tables = [row[0] for row in conn.execute(tables_query).fetchall()]
            if not all_tables:
                return []

            results = []

            if agence and agence.lower() == "all":
                # On prend une seule date
                agence = agence.strip()

                table_name = f"{type_table}_{single_date_if_all}"
                if table_name not in all_tables:
                    return {"message": f"Aucune table trouvée pour la date {single_date_if_all}"}

                for ag in AGENCES_DISPO:
                    if type_table == "dav":
                        sql = f"""
                            SELECT 
                                COUNT(DISTINCT code_client) AS nb_clients,
                                SUM(solde) AS total_montant,
                                SUM(debit) AS total_debit,
                                SUM(credit) AS total_credit
                            FROM `{table_name}`
                            WHERE Agence = :agence
                        """
                    elif type_table == "dat":
                        sql = f"""
                            SELECT 
                                COUNT(DISTINCT code_client) AS nb_clients,
                                SUM(montant_capital) AS total_montant,
                                SUM(montant_pay_total) AS total_credit
                            FROM `{table_name}`
                            WHERE Agence = :agence
                        """
                    elif type_table == "epr":
                        sql = f"""
                            SELECT 
                                COUNT(DISTINCT code_client) AS nb_clients,
                                SUM(solde) AS total_montant,
                                SUM(Debit) AS total_debit,
                                SUM(Credit) AS total_credit
                            FROM `{table_name}`
                            WHERE Agence = :agence
                        """
                    result = conn.execute(text(sql), {"agence": ag}).fetchone()
                    if result:
                        date_agence_data = {"date": single_date_if_all}
                        
                        if agence and agence.lower() == "all":
                            date_agence_data["agence"] = ag
                        
                        if type_table == "dav" or type_table == "epr":
                            results.append({
                                "date_agence": date_agence_data,
                                "data": {
                                    "nb_clients": int(result[0] or 0),
                                    "total_montant": float(result[1] or 0),
                                    "total_debit": float(result[2] or 0),
                                    "total_credit": float(result[3] or 0)
                                }
                            })
                        elif type_table == "dat":
                            results.append({
                                "date_agence": date_agence_data,
                                "data": {
                                    "nb_clients": int(result[0] or 0),
                                    "total_montant": float(result[1] or 0),
                                    "total_credit": float(result[2] or 0)
                                }
                            })
            else:
                # Filtrer les tables par plage de dates
                if date_debut and date_fin:
                    filtered_tables = [t for t in all_tables if date_debut <= t.replace(f"{type_table}_", "") <= date_fin]
                else:
                    filtered_tables = all_tables

                if not filtered_tables:
                    return []

                for table_name in sorted(filtered_tables):
                    table_date = table_name.replace(f"{type_table}_", "")
                    where = []
                    params = {}
                    if agence:
                        where.append("Agence = :agence")
                        params["agence"] = agence
                    where_clause = " AND ".join(where)
                    if where_clause:
                        where_clause = "WHERE " + where_clause

                    if type_table == "dav":
                        sql = f"""
                            SELECT 
                                COUNT(DISTINCT code_client) AS nb_clients,
                                SUM(solde) AS total_montant,
                                SUM(debit) AS total_debit,
                                SUM(credit) AS total_credit
                            FROM `{table_name}`
                            {where_clause}
                        """
                    elif type_table == "dat":
                        sql = f"""
                            SELECT 
                                COUNT(DISTINCT code_client) AS nb_clients,
                                SUM(montant_capital) AS total_montant,
                                SUM(montant_pay_total) AS total_credit
                            FROM `{table_name}`
                            {where_clause}
                        """
                    elif type_table == "epr":
                        sql = f"""
                            SELECT 
                                COUNT(DISTINCT code_client) AS nb_clients,
                                SUM(solde) AS total_montant,
                                SUM(Debit) AS total_debit,
                                SUM(Credit) AS total_credit
                            FROM `{table_name}`
                            {where_clause}
                        """
                    result = conn.execute(text(sql), params).fetchone()
                    if result:
                        # Construire l'objet date_agence conditionnellement
                        date_agence_data = {"date": table_date}
                        
                        # Ajouter agence seulement si elle a une valeur
                        if agence:
                            date_agence_data["agence"] = agence
                        
                        if type_table == "dav" or type_table == "epr":
                            results.append({
                                "date_agence": date_agence_data,
                                "data": {
                                    "nb_clients": int(result[0] or 0),
                                    "total_montant": float(result[1] or 0),
                                    "total_debit": float(result[2] or 0),
                                    "total_credit": float(result[3] or 0)
                                }
                            })
                        elif type_table == "dat":
                            results.append({
                                "date_agence": date_agence_data,
                                "data": {
                                    "nb_clients": int(result[0] or 0),
                                    "total_montant": float(result[1] or 0),
                                    "total_credit": float(result[2] or 0)
                                }
                            })

            return results

        except Exception as e:
            print(f"[ERREUR] getTotalParProduit : {e}")
            return {"status": "error", "message": str(e)}

        finally:
            if conn:
                conn.close()





                    
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
