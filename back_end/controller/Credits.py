from fastapi import Request
from fastapi.responses import StreamingResponse
import json
from typing import List
import os
from datetime import datetime
import re 
import random
import string
import openpyxl
import csv 
import sys  
import shutil 
import pandas as pd
from db.db  import DB
from werkzeug.utils import secure_filename
import asyncio
import aiofiles
import io




class Credits:

    def __init__(self):
        
        self.db = DB()  # au cas où tu veux utiliser la BDD
        self.upload_folder = 'load_file' 
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder) 

    def get_data(self):
        return {"message": "Données Credit"}
    
    def nettoyer_nom_fichier(self,filename):
            # Enlever l'extension
            nom_sans_ext = os.path.splitext(filename)[0] 
            # Remplacer les ponctuations par '_'
            nom_remplace = re.sub(f"[{re.escape(string.punctuation)}]", "_", nom_sans_ext)
            # Enlever les chiffres
            nom_sans_chiffres = re.sub(r"\d+", "", nom_remplace)
            # Tout en minuscules
            nom_final = nom_sans_chiffres.lower()
            # Nettoyage double underscore éventuel
            nom_final = re.sub(r"_+", "_", nom_final).strip("_")
            return nom_final
        
    def merge_duplicate_columns(self, headers, data):
        from collections import defaultdict
        column_indices = defaultdict(list)

        for idx, col in enumerate(headers):
            column_indices[col].append(idx)

        unique_headers = list(column_indices.keys())
        merged_data = []
        for row in data[1:]:
            merged_row = []
            for col in unique_headers:
                indices = column_indices[col]
                merged_values = [str(row[i]).strip() for i in indices if i < len(row) and row[i] not in [None, '']]
                merged_row.append(','.join(merged_values))
            merged_data.append(merged_row)

        return unique_headers, merged_data
    
    def load_file_csv_in_database(self, filename: str,  folder: str):
        """
        Charge un fichier CSV depuis './load_file/{filename}' avec séparateur '^' 
        et insère les données dans la base avec progression en temps réel.
        """ 
        def progress_generator():  
            table_name = self.nettoyer_nom_fichier(filename)
            try:
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                folder_path = os.path.join(project_root, 'load_file', folder)

                if not os.path.exists(folder_path):
                    yield json.dumps({"status": "error", "message": f"[ERREUR] Le répertoire {folder_path} n'existe pas",
                                    "task": f"Le répertoire {folder_path} n'existe pas"})
                    return

                files_in_dir = os.listdir(folder_path)
                yield json.dumps({"status": "info", "message": f"[INFO] Fichiers disponibles dans le répertoire : {files_in_dir}"})
 
                found_file = next((file for file in files_in_dir if file == filename), None)


                if not found_file:
                    yield json.dumps({"status": "error", "message": f"[ERREUR] Fichier {filename} introuvable dans {folder_path}",
                                    "task": f"Fichier {filename} introuvable dans"})
                    return

                filepath = os.path.join(folder_path, found_file)
                yield json.dumps({"status": "info", "message": f"[INFO] Fichier trouvé : {found_file}"})
                yield json.dumps({"status": "info", "message": f"[INFO] Chemin complet du fichier : {filepath}"})

                try:
                    data = []
                    yield json.dumps({"status": "info", "message": "[INFO] Début de la lecture du fichier CSV...",
                                    "task": "Début de la lecture du fichier CSV."})

                    with open(filepath, 'r', encoding='utf-8', newline='') as csvfile:
                        csv_reader = csv.reader(csvfile, delimiter='^')
                        is_header = True
                        row_count = 0

                        for row in csv_reader:
                            if is_header:
                                cleaned_row = []
                                for i, cell in enumerate(row):
                                    cleaned_cell = cell.strip().replace('.', '_').lower()
                                    if not cleaned_cell:
                                        cleaned_cell = f'colonne_{i+1}'
                                    cleaned_cell = ''.join(c if c.isalnum() or c == '_' else '_' for c in cleaned_cell)
                                    if cleaned_cell and cleaned_cell[0].isdigit():
                                        cleaned_cell = f'col_{cleaned_cell}'
                                    cleaned_row.append(cleaned_cell)
                                is_header = False
                            else:
                                cleaned_row = [cell.strip() for cell in row]
                                row_count += 1
                                if row_count % 1000 == 0:
                                    yield json.dumps({
                                        "status": "reading",
                                        "task": "Lecture encours",
                                        "row_count": row_count
                                    })
                                    yield json.dumps({
                                        "status": "info",
                                        "message": f"[INFO] Lecture en cours. Ligne : {row_count}"
                                    })
                            data.append(cleaned_row)

                    if data:
                        yield json.dumps({
                            "status": "info",
                            "message": f"[INFO] Lecture réussie. Nombre de lignes : {len(data)}"
                        })
                        yield json.dumps({
                            "status": "info",
                            "message": f"[INFO] Entêtes détectées : {data[0] if data else 'Aucune'}"
                        })
                    else:
                        yield json.dumps({"status": "error", "message": "[ERREUR] Le fichier a été lu mais ne contient pas de données"})
                        return

                except Exception as read_error:
                    yield json.dumps({
                        "status": "error",
                        "message": f"[ERREUR] Lecture du fichier CSV échouée : {str(read_error)}"
                    })
                    return

                try:
                    yield json.dumps({"status": "info", "message": "[INFO] Tentative de connexion à la base de données"})
                    conn = self.db.connect()
                    yield json.dumps({"status": "info", "message": "[INFO] Connexion à la base de données établie"})
                    cursor = conn.cursor()
                    yield json.dumps({"status": "info", "message": "[INFO] Curseur créé avec succès"})
                except Exception as db_error:
                    yield json.dumps({
                        "status": "error",
                        "message": f"[ERREUR] Échec de connexion à la base de données : {str(db_error)}"
                    })
                    return

                try:
                    headers = data[0]
                    yield json.dumps({
                        "status": "debug",
                        "message": f"[DEBUG] En-têtes avant traitement : {headers}"
                    })

                    for i, header in enumerate(headers):
                        if not header or header.strip() == '':
                            headers[i] = f'colonne_{i+1}'
                            yield json.dumps({
                                "status": "warning",
                                "message": f"[WARNING] En-tête vide détecté à la position {i}, remplacé par 'colonne_{i+1}'"
                            })

                    seen_headers = {}
                    for i, header in enumerate(headers):
                        if header in seen_headers:
                            counter = 1
                            original_header = header
                            while f"{original_header}_{counter}" in seen_headers:
                                counter += 1
                            headers[i] = f"{original_header}_{counter}"
                            yield json.dumps({
                                "status": "warning",
                                "message": f"[WARNING] En-tête dupliqué '{original_header}' renommé en '{headers[i]}'"
                            })
                        seen_headers[headers[i]] = i

                    yield json.dumps({
                        "status": "debug",
                        "message": f"[DEBUG] En-têtes après nettoyage : {headers}",
                        "task": "En-têtes après nettoyage"
                    })

                    yield json.dumps({"status": "info", "message": f"[INFO] Suppression de la table existante {table_name}...",
                                    "task": "Suppression de la table existante"})
                    cursor.execute(f'DROP TABLE IF EXISTS `{table_name}`;')
                    yield json.dumps({"status": "info", "message": "[INFO] Traitement des colonnes dupliquées..."})
                    headers, data_rows = self.merge_duplicate_columns(headers, data[1:])
                    columns = ', '.join([f'`{col}` TEXT' for col in headers])
                    create_query = f'CREATE TABLE IF NOT EXISTS `{table_name}` ({columns});'
                    cursor.execute(create_query)
                    yield json.dumps({"status": "info", "message": f"[INFO] Table `{table_name}` créée avec succès"})
                    total_rows = len(data_rows)
                    yield json.dumps({
                        "status": "start_insert",
                        "task": "Debut de l'insertion",
                        "total_rows": total_rows,
                        "message": f"[INFO] Début de l'insertion de {total_rows} lignes..."
                    })
                    for i, row in enumerate(data_rows, 1):
                        try:
                            while len(row) < len(headers):
                                row.append('')
                            if len(row) > len(headers):
                                row = row[:len(headers)]
                            placeholders = ', '.join(['%s'] * len(headers))
                            insert_query = f'INSERT INTO `{table_name}` VALUES ({placeholders})'
                            if i % 100 == 0 or i == 1:
                                yield json.dumps({
                                    "status": "inserting",
                                    "current": i,
                                    "total": total_rows,
                                    "percentage": round((i / total_rows) * 100, 2),
                                    "row_count": i,
                                    "task": "insertion",
                                    "message": f"[INFO] Insertion de la ligne {i}/{total_rows}",
                                    "debug": f"[DEBUG] Longueur de l'entête: {len(headers)}, Longueur de la ligne: {len(row)}"
                                })
                                sys.stdout.flush()
                            cursor.execute(insert_query, row)
                        except Exception as insert_error:
                            yield json.dumps({
                                "status": "error",
                                "message": f"[ERREUR] Échec à l'insertion de la ligne {i} : {str(insert_error)}",
                                "row_content": str(row[:5])
                            })
                            conn.rollback()
                            return
                    yield json.dumps({"status": "info", "message": "[INFO] Validation des modifications (commit)..."})
                    conn.commit()
                    yield json.dumps({
                        "status": "success",
                        "total_inserted": total_rows,
                        "table_name": table_name,
                        "message": f"[SUCCESS] {total_rows} lignes insérées avec succès dans la table `{table_name}`"
                    })
                except Exception as e:
                    yield json.dumps({
                        "status": "error",
                        "message": f"[ERREUR] Exception non gérée : {str(e)}"
                    })
                    try:
                        conn.rollback()
                        yield json.dumps({"status": "info", "message": "[INFO] Rollback effectué"})
                    except Exception as rollback_error:
                        yield json.dumps({
                            "status": "error",
                            "message": f"[ERREUR] Échec du rollback : {str(rollback_error)}"
                        })
                finally:
                    try:
                        if 'conn' in locals() and conn:
                            conn.close()
                            yield json.dumps({"status": "info", "message": "[INFO] Connexion à la base de données fermée"})
                    except Exception as close_error:
                        yield json.dumps({
                            "status": "error",
                            "message": f"[ERREUR] Problème lors de la fermeture de la connexion : {str(close_error)}"
                        })
            except Exception as global_error:
                yield json.dumps({
                    "status": "critical_error",
                    "message": f"[ERREUR CRITIQUE] Exception non gérée dans la fonction principale : {str(global_error)}"
                })
                return
            yield json.dumps({"fait": "true", "message": "insertion fait"})
        return progress_generator()

    def upload_multiple_files(self, files, folder_name=None):
        total = len(files)
        for i, file in enumerate(files, 1):
            try:
                for progress in self.upload_file_manual_in_detail(file, folder_name, i, total):
                    yield progress
            except Exception as e:
                yield {
                    "status": "error",
                    "file": getattr(file, "filename", str(file)),
                    "current": i,
                    "total": total,
                    "percentage": round((i / total) * 100, 2),
                    "message": f"[ERREUR] Échec du téléchargement de {getattr(file, 'filename', str(file))} : {str(e)}"
                }


    def show_files(self, app=None):
        """
        Renvoie une structure arborescente des sous-dossiers de `upload_folder/app`
        compatible avec Vuetify <v-treeview>, sans inclure le dossier racine.
        """

        base_folder = self.upload_folder
        if not os.path.exists(base_folder):
            return []

        tree = []

        for root, dirs, files in os.walk(base_folder):
            # On saute la racine : on ne veut afficher que les sous-dossiers
            if root == base_folder:
                continue

            relative_path = os.path.relpath(root, base_folder).replace("\\", "/")
            path_parts = relative_path.split('/') if relative_path != '.' else []

            # Liste des fichiers CSV
            csv_files = [
                {"title": f, "file": True}
                for f in files
                if f.lower().endswith('.csv')
            ]

            if not csv_files:
                continue  # On ignore les dossiers sans fichiers CSV

            # Construction arborescente
            current_level = tree
            for part in path_parts:
                folder = next((item for item in current_level if item["title"] == part and not item.get("file")), None)
                if not folder:
                    folder = {"title": part, "children": []}
                    current_level.append(folder)
                current_level = folder["children"]

            current_level.extend(csv_files)

        return tree
    
    def allowed_file(self, filename):
        """
        Vérifie si l'extension du fichier est autorisée
        """
        ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
        if '.' in filename:
            ext = filename.rsplit('.', 1)[1].lower()
            print("Extension détectée:", ext)
            return ext in ALLOWED_EXTENSIONS
        return False
    
    
        
    def upload_file_manual_in_detail(self, file, folder_name=None, current=None, total=None):
        filename = getattr(file, 'filename', None)
        if not file or not filename or not self.allowed_file(filename):
            yield {"status": "error", "file": str(file), "message": "Format invalide"}
            return

        filename = secure_filename(filename)
        folder_path = os.path.join(self.upload_folder, folder_name) if folder_name else self.upload_folder
        os.makedirs(folder_path, exist_ok=True)

        final_filepath = os.path.join(folder_path, filename)
        backup_filepath = None

        try:
            yield {"status": "info", "file": filename, "message": "Lecture du fichier en cours..."}

            # Lecture du contenu - méthode synchrone (suppose que file.read() est synchrone)
            if hasattr(file, 'read'):
                file_content = file.read()
            elif hasattr(file, 'file') and hasattr(file.file, 'read'):
                file_content = file.file.read()
            else:
                raise IOError(f"Type de fichier non supporté: {type(file)}")

            if not isinstance(file_content, bytes):
                file_content = file_content.encode('utf-8') if isinstance(file_content, str) else bytes(file_content)

            total_size = len(file_content)
            yield {
                "status": "info",
                "file": filename,
                "message": f"Fichier lu: {total_size / (1024 * 1024):.2f} MB. Écriture en cours..."
            }

            if os.path.exists(final_filepath):
                backup_filepath = final_filepath + '.backup'
                shutil.copy2(final_filepath, backup_filepath)

            chunk_size = 1024 * 1024  # 1 MB
            written_size = 0

            with open(final_filepath, 'wb') as f:
                content_buffer = io.BytesIO(file_content)
                while chunk := content_buffer.read(chunk_size):
                    f.write(chunk)
                    f.flush()
                    written_size += len(chunk)

                    yield {
                        "status": "progress",
                        "file": filename,
                        "current": current,
                        "total": total,
                        "received_mb": round(written_size / (1024 * 1024), 2),
                        "total_mb": round(total_size / (1024 * 1024), 2),
                        "percentage_file": round((written_size / total_size) * 100, 2),
                        "message": f"[Serveur] Écrit {written_size / (1024 * 1024):.2f} / {total_size / (1024 * 1024):.2f} MB"
                    }

                f.flush()
                os.fsync(f.fileno())

            if written_size != total_size:
                if backup_filepath and os.path.exists(backup_filepath):
                    shutil.move(backup_filepath, final_filepath)
                yield {
                    "status": "error",
                    "file": filename,
                    "message": f"Erreur d'écriture: {written_size} / {total_size} octets"
                }
                return

            if backup_filepath and os.path.exists(backup_filepath):
                os.remove(backup_filepath)

            yield {
                "status": "success",
                "file": filename,
                "received_mb": round(total_size / (1024 * 1024), 2),
                "message": f"✅ Fichier {filename} transféré avec succès ({total_size / (1024 * 1024):.2f} MB)"
            }

        except Exception as e:
            if backup_filepath and os.path.exists(backup_filepath):
                try:
                    shutil.move(backup_filepath, final_filepath)
                except Exception as restore_error:
                    yield {
                        "status": "warning",
                        "file": filename,
                        "message": f"Erreur et impossible de restaurer le backup: {str(restore_error)}"
                    }

            yield {
                "status": "error",
                "file": filename,
                "message": f"Erreur lors de l'upload: {str(e)}"
            }

        finally:
            if backup_filepath and os.path.exists(backup_filepath):
                try:
                    os.remove(backup_filepath)
                except:
                    pass
    
                  
    def run_initialisation_sql(self):
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            create_table_query ="""
                CREATE TABLE IF NOT EXISTS init_status (
                    name VARCHAR(255) PRIMARY KEY,  
                    status VARCHAR(20) NOT NULL,   
                    message TEXT,                  
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );"""
            cursor.execute(create_table_query)
            
            steps = [ 
                        {
                            "name": "Modifier colonnes - aa_arrangement_mcbc_live_full",
                            "sql": """
                            ALTER TABLE aa_arrangement_mcbc_live_full 
                            MODIFY COLUMN product_line VARCHAR(100),
                            MODIFY COLUMN arr_status VARCHAR(100),
                            MODIFY COLUMN id VARCHAR(100),
                            MODIFY COLUMN customer VARCHAR(100),
                            MODIFY COLUMN linked_appl_id VARCHAR(100);
                            """
                        },
                        {
                            "name": "Modifier colonne - account_mcbc_live_full",
                            "sql": "ALTER TABLE account_mcbc_live_full MODIFY COLUMN id VARCHAR(100);"
                        },
                        {
                            "name": "Modifier colonne - customer_mcbc_live_full",
                            "sql": "ALTER TABLE customer_mcbc_live_full MODIFY COLUMN id VARCHAR(100);"
                        },
                        {
                            "name": "Modifier colonne - industry_mcbc_live_full",
                            "sql": "ALTER TABLE industry_mcbc_live_full MODIFY COLUMN id VARCHAR(100);"
                        },
                        {
                            "name": "Modifier colonne - collateral_right_mcbc_live_full",
                            "sql": "ALTER TABLE collateral_right_mcbc_live_full MODIFY COLUMN id VARCHAR(100);"
                        },
                        {
                            "name": "Modifier colonne - collateral_mcbc_live_full",
                            "sql": "ALTER TABLE collateral_mcbc_live_full MODIFY COLUMN id VARCHAR(100);"
                        },
                        {
                            "name": "Modifier colonnes - aa_arr_term_mcbc_live_full",
                            "sql": """
                            ALTER TABLE aa_arr_term_mcbc_live_full 
                            MODIFY COLUMN id_comp_1 VARCHAR(100),
                            MODIFY COLUMN activity VARCHAR(100);
                            """
                        },
                        {
                            "name": "Modifier colonnes - em_lo_application_mcbc_live_full",
                            "sql": """
                            ALTER TABLE em_lo_application_mcbc_live_full 
                            MODIFY COLUMN arrangement_id VARCHAR(100),
                            MODIFY COLUMN co_coll_id VARCHAR(100);
                            """
                        },
                        {
                            "name": "Modifier colonne - aa_account_details_mcbc_live_full",
                            "sql": "ALTER TABLE aa_account_details_mcbc_live_full MODIFY COLUMN id VARCHAR(100);"
                        },
                        {
                            "name": "Modifier colonnes - aa_bill_details_mcbc_live_full",
                            "sql": """
                            ALTER TABLE aa_bill_details_mcbc_live_full 
                            MODIFY COLUMN arrangement_id VARCHAR(100),
                            MODIFY COLUMN bill_date VARCHAR(100),
                            MODIFY COLUMN payment_date VARCHAR(100),
                            MODIFY COLUMN settle_status VARCHAR(100);
                            """
                        },
                        {
                            "name": "Modifier colonnes - eb_cont_bal_mcbc_live_full",
                            "sql": """
                            ALTER TABLE eb_cont_bal_mcbc_live_full 
                            MODIFY COLUMN id VARCHAR(100),
                            MODIFY COLUMN last_ac_bal_upd VARCHAR(100);
                            """
                        },
                        # Bloc "Créer index principaux - aa_arrangement_mcbc_live_full"
                        {
                            "name": "Créer index idx_product_line sur aa_arrangement_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_product_line ON aa_arrangement_mcbc_live_full(product_line);"
                        },
                        {
                            "name": "Créer index idx_arr_status sur aa_arrangement_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_arr_status ON aa_arrangement_mcbc_live_full(arr_status);"
                        },
                        {
                            "name": "Créer index idx_arrangement_id sur aa_arrangement_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_arrangement_id ON aa_arrangement_mcbc_live_full(id);"
                        },
                        {
                            "name": "Créer index idx_customer sur aa_arrangement_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_customer ON aa_arrangement_mcbc_live_full(customer);"
                        },
                        {
                            "name": "Créer index idx_linked_appl_id sur aa_arrangement_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_linked_appl_id ON aa_arrangement_mcbc_live_full(linked_appl_id);"
                        },

                        # Bloc "Créer index - sous-requêtes"
                        {
                            "name": "Créer index idx_account_id sur account_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_account_id ON account_mcbc_live_full(id);"
                        },
                        {
                            "name": "Créer index idx_customer_id sur customer_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_customer_id ON customer_mcbc_live_full(id);"
                        },
                        {
                            "name": "Créer index idx_industry_id sur industry_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_industry_id ON industry_mcbc_live_full(id);"
                        },
                        {
                            "name": "Créer index idx_collateral_id sur collateral_right_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_collateral_id ON collateral_right_mcbc_live_full(id);"
                        },
                        {
                            "name": "Créer index idx_collateral__id sur collateral_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_collateral__id ON collateral_mcbc_live_full(id);"
                        },
                        {
                            "name": "Créer index idx_collateral__type sur collateral_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_collateral__type ON collateral_mcbc_live_full(collateral_type);"
                        },
                        {
                            "name": "Créer index idx_em_lo_arr_co sur em_lo_application_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_em_lo_arr_co ON em_lo_application_mcbc_live_full(arrangement_id, co_coll_id);"
                        },

                        # Bloc "Créer index - autres tables"
                        {
                            "name": "Créer index idx_id_comp_1 sur AA_ARR_TERM_MCBC_LIVE_FULL",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_id_comp_1 ON AA_ARR_TERM_MCBC_LIVE_FULL(id_comp_1);"
                        },
                        {
                            "name": "Créer index idx_activity sur AA_ARR_TERM_MCBC_LIVE_FULL",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_activity ON AA_ARR_TERM_MCBC_LIVE_FULL(activity);"
                        },
                        {
                            "name": "Créer index idx_account_details_id sur aa_account_details_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_account_details_id ON aa_account_details_mcbc_live_full(id);"
                        },
                        {
                            "name": "Créer index idx_bill_details_arrangement_id sur aa_bill_details_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_bill_details_arrangement_id ON aa_bill_details_mcbc_live_full(arrangement_id);"
                        },
                        {
                            "name": "Créer index idx_bill_details_bill_date sur aa_bill_details_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_bill_details_bill_date ON aa_bill_details_mcbc_live_full(bill_date);"
                        },
                        {
                            "name": "Créer index idx_bill_details_payment_date sur aa_bill_details_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_bill_details_payment_date ON aa_bill_details_mcbc_live_full(payment_date);"
                        },
                        {
                            "name": "Créer index idx_bill_details_settle_status sur aa_bill_details_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_bill_details_settle_status ON aa_bill_details_mcbc_live_full(settle_status);"
                        },
                        {
                            "name": "Créer index idx_eb_cont_bal_id sur eb_cont_bal_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_eb_cont_bal_id ON eb_cont_bal_mcbc_live_full(id);"
                        },
                        {
                            "name": "Créer index idx_last_ac_bal_upd sur eb_cont_bal_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_last_ac_bal_upd ON eb_cont_bal_mcbc_live_full(last_ac_bal_upd);"
                        },
                        {
                            "name": "Créer index idx_bill_details_property sur aa_bill_details_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_bill_details_property ON aa_bill_details_mcbc_live_full(property(100));"
                        },
                        {
                            "name": "Créer index idx_bill_details_bill_status sur aa_bill_details_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_bill_details_bill_status ON aa_bill_details_mcbc_live_full(bill_status(20));"
                        },
                        {
                            "name": "Créer index idx_bill_details_os_prop_amount sur aa_bill_details_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_bill_details_os_prop_amount ON aa_bill_details_mcbc_live_full(os_prop_amount);"
                        },
                        {
                            "name": "Créer index idx_arrangement_linked_co_code sur aa_arrangement_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_arrangement_linked_co_code ON aa_arrangement_mcbc_live_full(linked_appl_id, co_code(20));"
                        },
                        {
                            "name": "Créer index idx_eb_cont_bal_type_sysdate sur eb_cont_bal_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_eb_cont_bal_type_sysdate ON eb_cont_bal_mcbc_live_full(id, type_sysdate(30));"
                        },
                        {
                            "name": "Créer index idx_eb_cont_bal_open_balance sur eb_cont_bal_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_eb_cont_bal_open_balance ON eb_cont_bal_mcbc_live_full(id, open_balance(100));"
                        },
                        {
                            "name": "Créer index idx_account_opening_date sur account_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_account_opening_date ON account_mcbc_live_full(id, opening_date(100));"
                        },
                        {
                            "name": "Créer index idx_bill_payment_arr_id sur aa_bill_details_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_bill_payment_arr_id ON aa_bill_details_mcbc_live_full(arrangement_id, payment_date(100));"
                        },
                        {
                            "name": "Créer index idx_bill_details_combined sur aa_bill_details_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_bill_details_combined ON aa_bill_details_mcbc_live_full(bill_date, os_prop_amount(100), bill_status(20), property(100));"
                        },
                        {
                            "name": "Créer index idx_customer_short_name_name sur customer_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_customer_short_name_name ON customer_mcbc_live_full(short_name(50), name_1(50), id);"
                        },
                        {
                            "name": "Créer index idx_arrangement_customer sur aa_arrangement_mcbc_live_full",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_arrangement_customer ON aa_arrangement_mcbc_live_full(customer);"
                        },
                        {
                            "name": "Drop table temporaire - temp_arrangement_customers",
                            "sql": """
                            DROP TABLE IF EXISTS temp_arrangement_customers; 
                            """
                        },
                        {
                            "name": "Créer table temporaire - temp_arrangement_customers",
                            "sql": """ 
                            CREATE TABLE temp_arrangement_customers AS
                            SELECT 
                                id AS arrangement_id, 
                                CASE 
                                    WHEN LOCATE('|', customer) > 0 
                                    THEN SUBSTRING_INDEX(customer, '|', 1) 
                                    ELSE customer 
                                END AS customer_id
                            FROM aa_arrangement_mcbc_live_full;
                            """
                        },
                        {
                            "name": "Drop table temporaire - temp_clients",
                            "sql": """
                            DROP TABLE IF EXISTS temp_clients; 
                            """
                        },
                        {
                            "name": "Créer table temporaire - temp_clients",
                            "sql": """ 
                            CREATE TABLE temp_clients AS 
                            SELECT id, CONCAT(short_name, ' ', name_1) AS nom_complet ,phone_1
                            FROM customer_mcbc_live_full;
                            """
                        },
                        {
                            "name": "Drop table temporaire - temp_accounts",
                            "sql": """
                            DROP TABLE IF EXISTS temp_accounts; 
                            """
                        },
                        {
                            "name": "Créer table temporaire - temp_accounts",
                            "sql": """ 
                            CREATE TABLE temp_accounts AS 
                            SELECT id, opening_date
                            FROM account_mcbc_live_full
                            WHERE opening_date IS NOT NULL;
                            """
                        },
                        {
                            "name": "Drop table temporaire - temp_balances",
                            "sql": """
                            DROP TABLE IF EXISTS temp_balances; 
                            """
                        },
                        {
                            "name": "Créer table temporaire - temp_balances",
                            "sql": """ 
                            CREATE TABLE temp_balances AS 
                            SELECT id, type_sysdate, open_balance
                            FROM eb_cont_bal_mcbc_live_full;
                            """
                        },
                        {
                            "name": "Drop table temporaire - temp_echeances",
                            "sql": """
                            DROP TABLE IF EXISTS temp_echeances; 
                            """
                        },
                        {
                            "name": "Créer table temporaire - temp_echeances",
                            "sql": """ 
                            CREATE TABLE temp_echeances AS 
                            SELECT arrangement_id, COUNT(*) as echeance
                            FROM aa_bill_details_mcbc_live_full
                            WHERE  (property NOT LIKE '%DISBURSEMENTFEE%' 
                                    OR property NOT LIKE '%NEWARRANGEMENTFEE%')
                            AND bill_date <= '{current_date}'
                            AND os_prop_amount >= 0
                            AND bill_status like '%SETTLED%'
                            GROUP BY arrangement_id;
                            """
                        },
                         {
                            "name": "Créer index idx_arrangement_id sur temp_arrangement_customers",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_arrangement_id ON temp_arrangement_customers (arrangement_id);"
                        },
                        {
                            "name": "Créer index idx_customer_id sur temp_arrangement_customers",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_customer_id ON temp_arrangement_customers (customer_id);"
                        },
                        {
                            "name": "Créer index idx_client_id sur temp_clients",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_client_id ON temp_clients (id);"
                        },
                        {
                            "name": "Créer index idx_account_id sur temp_accounts",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_account_id ON temp_accounts (id);"
                        },
                        {
                            "name": "Créer index idx_opening_date sur temp_accounts",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_opening_date ON temp_accounts (opening_date);"
                        },
                        {
                            "name": "Créer index idx_balance_id sur temp_balances",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_balance_id ON temp_balances (id);"
                        },
                        {
                            "name": "Créer index idx_type_sysdate sur temp_balances",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_type_sysdate ON temp_balances (type_sysdate);"
                        },
                        {
                            "name": "Créer index idx_echeance_arrangement_id sur temp_echeances",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_echeance_arrangement_id ON temp_echeances (arrangement_id);"
                        }
                    ]

                # Exemple d’utilisation :
                # sql = steps[23]["sql"].format(current_date="20250611")

            current_date = "20250531"
            cursor.execute("DELETE FROM init_status")
            requets_len=len(steps)
            
            yield {"status": "success", "data_step": steps}
            for i, step in enumerate(steps, 0):
                name = step["name"]
                yield {"name": name, "status": "processing","total":requets_len,"current":i}

                cursor.execute("SELECT status FROM init_status WHERE name = %s", (name,))
                existing = cursor.fetchone()

                if existing and existing[0] == "done":
                    yield {"name": name, "status": "skipped"}
                    continue
                try:
                    sql = step["sql"]
                    if "{current_date}" in sql:
                        sql = sql.format(current_date=current_date)
                    cursor.execute(sql)
                    cursor.execute(
                        "REPLACE INTO init_status (name, status, message) VALUES (%s, %s, %s)",
                        (name, "done", "OK")
                    )
                    yield {"name": name, "status": "done","total":requets_len,"current":i}
                except Exception as e:
                    cursor.execute(
                        "REPLACE INTO init_status (name, status, message) VALUES (%s, %s, %s)",
                        (name, "error", str(e))
                    )
                    yield {"name": name, "status": "error", "message": str(e)}
            conn.commit()
            yield {"name": name, "status": "done","message":"Toutes les étapes sont terminées"}
            return
            # return status_report
        except Exception as e:
            yield { "status": "error","message":str(e)}
            return
    
