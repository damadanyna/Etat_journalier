from fastapi import Request
from fastapi.responses import StreamingResponse
import json
from typing import List
import os
from datetime import datetime
import time
import re 
import random
import string
import openpyxl
import pymysql.cursors
import csv 
import sys  
import shutil 
import pandas as pd
from db.db  import DB
from werkzeug.utils import secure_filename 
import aiofiles
import io
from sqlalchemy import text




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
    
    def load_file_csv_in_database(self, filename: str,  folder: str, str_date: str):
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
                    print({"status": "error", "message": f"[ERREUR] Le répertoire {folder_path} n'existe pas"})
                    return

                files_in_dir = os.listdir(folder_path)
                yield json.dumps({"status": "info", "message": f"[INFO] Fichiers disponibles dans le répertoire : {files_in_dir}"})
                print({"status": "info", "message": f"[INFO] Fichiers disponibles dans le répertoire : {files_in_dir}"})
                found_file = next((file for file in files_in_dir if file == filename), None)


                if not found_file:
                    yield json.dumps({"status": "error", "message": f"[ERREUR] Fichier {filename} introuvable dans {folder_path}",
                                    "task": f"Fichier {filename} introuvable dans"})
                    print({"status": "error", "message": f"[ERREUR] Fichier {filename} introuvable dans {folder_path}"})
                    return

                filepath = os.path.join(folder_path, found_file)
                yield json.dumps({"status": "info", "message": f"[INFO] Fichier trouvé : {found_file}"})
                print({"status": "info", "message": f"[INFO] Fichier rencontré : {found_file}"})
                yield json.dumps({"status": "info", "message": f"[INFO] Chemin complet du fichier : {filepath}"})
                print({"status": "info", "message": f"[INFO] Chemin complet du fichier : {filepath}"})

                try:
                    data = []
                    yield json.dumps({"status": "info", "message": "[INFO] Début de la lecture du fichier CSV...",
                                    "task": "Début de la lecture du fichier CSV."})
                    print({"status": "info", "message": "[INFO] Début de la lecture du fichier CSV..."})

                    with open(filepath, 'r', encoding='utf-8', newline='') as csvfile:
                        csv_reader = csv.reader(csvfile, delimiter='^')
                        row_count = 0
                        data = []

                        # Lire et nettoyer les en-têtes
                        try:
                            header_raw = next(csv_reader)
                        except StopIteration:
                            yield json.dumps({"status": "error", "message": "[ERREUR] Fichier vide ou invalide"})
                            return

                        headers = []
                        for i, cell in enumerate(header_raw):
                            cleaned_cell = cell.strip().replace('.', '_').lower()
                            if not cleaned_cell:
                                cleaned_cell = f'colonne_{i+1}'
                            cleaned_cell = ''.join(c if c.isalnum() or c == '_' else '_' for c in cleaned_cell)
                            if cleaned_cell and cleaned_cell[0].isdigit():
                                cleaned_cell = f'col_{cleaned_cell}'
                            headers.append(cleaned_cell)

                        data.append(headers)

                        # Lecture des lignes de données
                        for row in csv_reader:
                            cleaned_row = [cell.strip() for cell in row]
                            data.append(cleaned_row)
                            row_count += 1

                            if row_count % 1000 == 0:
                                yield json.dumps({
                                    "status": "reading",
                                    "task": "Lecture en cours",
                                    "row_count": row_count,
                                    "message": f"[INFO] Lecture en cours. Ligne : {row_count}"
                                })


                    if data:
                        yield json.dumps({
                            "status": "info",
                            "message": f"[INFO] Lecture réussie. Nombre de lignes : {len(data)}"
                        })
                        print({"status": "info", "message": f"[INFO] Lecture réussie. Nombre de lignes : {len(data)}"})
                        yield json.dumps({
                            "status": "info",
                            "message": f"[INFO] Entêtes détectées : {data[0] if data else 'Aucune'}"
                        })
                        print({"status": "info", "message": f"[INFO] Entités détectées : {data[0] if data else 'Aucune'}"})
                    else:
                        yield json.dumps({"status": "error", "message": "[ERREUR] Le fichier a été lu mais ne contient pas de données"})
                        print({"status": "error", "message": "[ERREUR] Le fichier a été lu mais ne contient pas de données"})
                        return

                except Exception as read_error:
                    yield json.dumps({
                        "status": "error",
                        "message": f"[ERREUR] Lecture du fichier CSV échouée : {str(read_error)}"
                    })
                    print({"status": "error", "message": f"[ERREUR] Lecture du fichier CSV échouée : {str(read_error)}"})
                    return

                try:
                    yield json.dumps({"status": "info", "message": "[INFO] Tentative de connexion à la base de données"})
                    print({"status": "info", "message": "[INFO] Tentative de connexion à la base de données"})
                    conn = self.db.connect()
                    yield json.dumps({"status": "info", "message": "[INFO] Connexion à la base de données établie"})
                    print({"status": "info", "message": "[INFO] Connexion à la base de données établie"})
                    cursor = conn.connection.cursor()
                    yield json.dumps({"status": "info", "message": "[INFO] Curseur créé avec succès"})
                    print({"status": "info", "message": "[INFO] Curseur création avec succès"})
                except Exception as db_error:
                    yield json.dumps({
                        "status": "error",
                        "message": f"[ERREUR] Échec de connexion à la base de données : {str(db_error)}"
                    })
                    print({"status": "error", "message": f"[ERREUR] Échec de connexion à la base de données : {str(db_error)}"})
                    return

                try:
                    headers = data[0]
                    yield json.dumps({
                        "status": "debug",
                        "message": f"[DEBUG] En-têtes avant traitement : {headers}"
                    })
                    print({"status": "debug", "message": f"[DEBUG] En-têtes avant traitement : {headers}"})

                    for i, header in enumerate(headers):
                        if not header or header.strip() == '':
                            headers[i] = f'colonne_{i+1}'
                            yield json.dumps({
                                "status": "warning",
                                "message": f"[WARNING] En-tête vide détecté à la position {i}, remplacé par 'colonne_{i+1}'"
                            })
                            print({"status": "warning", "message": f"[WARNING] En-tête vide détecté à la position {i}, remplacé par 'colonne_{i+1}'"})

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
                            print({"status": "warning", "message": f"[WARNING] En-tête dupliqué '{original_header}' renommé en '{headers[i]}'"})
                        seen_headers[headers[i]] = i

                    yield json.dumps({
                        "status": "debug",
                        "message": f"[DEBUG] En-têtes après nettoyage : {headers}",
                        "task": "En-têtes après nettoyage"
                    })
                    print({"status": "debug", "message": f"[DEBUG] En-têtes aprés nettoyage : {headers}"})

                    yield json.dumps({"status": "info", "message": f"[INFO] Suppression de la table existante {table_name}...",
                                    "task": "Suppression de la table existante"})
                    print({"status": "info", "message": f"[INFO] Suppression de la table existante {table_name}..."})
                    # Suppression de la table
                    conn.execute(text(f'DROP TABLE IF EXISTS `{table_name}`;'))
                    yield json.dumps({"status": "info", "message": "[INFO] Traitement des colonnes dupliquées..."})
                    print({"status": "info", "message": "[INFO] Traitement des colonnes dupliquées..."})
                    # Traitement des données
                    headers, data_rows = self.merge_duplicate_columns(headers, data[1:])
                    columns = ', '.join([f'`{col}` TEXT' for col in headers])
                    create_query = f'CREATE TABLE IF NOT EXISTS `{table_name}` ({columns});'

                    # Création de la table
                    conn.execute(text(create_query))
                    yield json.dumps({"status": "info", "message": f"[INFO] Table `{table_name}` créée avec succès"})
                    print({"status": "info", "message": f"[INFO] Table `{table_name}` création avec succès"})
                    total_rows = len(data_rows)
                    yield json.dumps({
                        "status": "start_insert",
                        "task": "Debut de l'insertion",
                        "total_rows": total_rows,
                        "message": f"[INFO] Début de l'insertion de {total_rows} lignes..."
                    })
                    print({"status": "start_insert", "task": "Debut de l'insertion", "total_rows": total_rows,})
                    batch_size = 10000
                    placeholders = ', '.join([f':val{j}' for j in range(len(headers))])
                    insert_query = text(f'INSERT INTO `{table_name}` VALUES ({placeholders})')

                    try:
                        for start in range(0, total_rows, batch_size):
                            end = min(start + batch_size, total_rows)
                            batch = data_rows[start:end]

                            # Normalisation des lignes (ajouter/remplir pour que chaque ligne ait la bonne longueur)
                            cleaned_batch = []
                            for row in batch:
                                # Corrige les longueurs
                                if len(row) < len(headers):
                                    row += [''] * (len(headers) - len(row))
                                elif len(row) > len(headers):
                                    row = row[:len(headers)]
                                cleaned_batch.append(row)

                            # Création de la liste de dictionnaires pour executemany
                            params_list = [
                                {f'val{j}': row[j] for j in range(len(headers))}
                                for row in cleaned_batch
                            ]

                            conn.execute(insert_query, params_list)

                            # Afficher la progression
                            if start % (batch_size * 5) == 0 or end == total_rows:
                                percentage = round((end / total_rows) * 100, 2)
                                yield json.dumps({
                                    "status": "inserting",
                                    "current": end,
                                    "total": total_rows,
                                    "percentage": percentage,
                                    "row_count": end,
                                    "task": "insertion",
                                    "message": f"[INFO] Insertion des lignes {start+1} à {end} / {total_rows}",
                                    "debug": f"[DEBUG] Batch insert : {start+1}-{end} | {len(cleaned_batch)} lignes"
                                })
                                sys.stdout.flush()

                        yield json.dumps({"status": "info", "message": "[INFO] Validation des modifications (commit)..."})
                        conn.commit()
                        yield json.dumps({
                            "status": "success",
                            "total_inserted": total_rows,
                            "table_name": table_name,
                            "message": f"[SUCCESS] {total_rows} lignes insérées avec succès dans la table `{table_name}`"
                        })

                    except Exception as insert_error:
                        yield json.dumps({
                            "status": "error",
                            "message": f"[ERREUR] Échec à l'insertion des lignes : {str(insert_error)}",
                        })
                        print(f"[ERREUR] Insertion échouée : {insert_error}")
                        conn.rollback()
                        return

                    print({"status": "info", "message": "[INFO] Validation des modifications (commit)..."})
                    conn.commit()
                    yield json.dumps({
                        "status": "success",
                        "total_inserted": total_rows,
                        "table_name": table_name,
                        "message": f"[SUCCESS] {total_rows} lignes insérées avec succès dans la table `{table_name}`"
                    })
                    print({"status": "success", "total_inserted": total_rows, "table_name": table_name,})
                except Exception as e:
                    yield json.dumps({
                        "status": "error",
                        "message": f"[ERREUR] Exception non gérée : {str(e)}"
                    })
                    print({"status": "error", "message": f"[ERREUR] Exception non gérée : {str(e)}"})
                    try:
                        conn.rollback()
                        yield json.dumps({"status": "info", "message": "[INFO] Rollback effectué"})
                        print({"status": "info", "message": "[INFO] Rollback effectué"})
                    except Exception as rollback_error:
                        yield json.dumps({
                            "status": "error",
                            "message": f"[ERREUR] Échec du rollback : {str(rollback_error)}"
                        })
                        print({"status": "error", "message": f"[ERREUR] Échec du rollback : {str(rollback_error)}"})
                finally:
                    try:
                        if 'conn' in locals() and conn:
                            conn.close()
                            yield json.dumps({"status": "info", "message": "[INFO] Connexion à la base de données fermée"})
                            print({"status": "info", "message": "[INFO] Connexion à la base de données fermée"})
                    except Exception as close_error:
                        yield json.dumps({
                            "status": "error",
                            "message": f"[ERREUR] Problème lors de la fermeture de la connexion : {str(close_error)}"
                        })
                        print({"status": "error", "message": f"[ERREUR] Problème lors de la fermeture de la connexion : {str(close_error)}"})
            except Exception as global_error:
                yield json.dumps({
                    "status": "critical_error",
                    "message": f"[ERREUR CRITIQUE] Exception non gérée dans la fonction principale : {str(global_error)}"
                })
                print({"status": "critical_error", "message": f"[ERREUR CRITIQUE] Exception non gérée dans la fonction principale : {str(global_error)}"})
                return
            yield json.dumps({"fait": "true", "message": "insertion fait"})
            print({"fait", "insertion fait"})
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
    
    def create_history_table(self):
        conn = self.db.connect()
        """
        Crée la table `history_insert` si elle n'existe pas déjà.
        """
        create_query = """
        CREATE TABLE IF NOT EXISTS `history_insert` ( 
            `label` VARCHAR(255) NOT NULL PRIMARY KEY,
            `stat_of` VARCHAR(100),
            `used` TINYINT(1) DEFAULT 0,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        conn.execute(text(create_query))

    def insert_into_history_table(self, label_value: str, used: int = 1, stat_of=None):
        try:
            conn = self.db.connect()

            # Étape 1 : mettre tous les used = 0
            reset_query = "UPDATE `history_insert` SET `used` = 0"
            conn.execute(text(reset_query))

            # Étape 2 : insérer ou mettre à jour la ligne ciblée
            upsert_query = """
                INSERT INTO `history_insert` (`label`, `stat_of`, `used`)
                VALUES (:label, :stat_of, :used)
                ON DUPLICATE KEY UPDATE
                    stat_of = VALUES(stat_of),
                    used = VALUES(used),
                    created_at = CURRENT_TIMESTAMP
            """
            conn.execute(text(upsert_query), {
                "label": label_value,
                "stat_of": stat_of,
                "used": used
            })

            conn.commit()
            print(f"[INFO] Mise à jour réussie de history_insert, actif: {label_value}")

        except Exception as e:
            print(f"[ERREUR] Erreur lors de la mise à jour de history_insert : {e}")
            try:
                conn.rollback()
            except:
                pass
        finally:
            try:
                if conn:
                    conn.close()
            except Exception as close_err:
                print(f"[ERREUR] Fermeture de la connexion échouée : {close_err}")

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
             
    def run_initialisation_sql(self, **kwargs):
        current_date = kwargs.get("str_date")
        try:
            conn = self.db.connect()
            # cursor = conn.cursor()
            cursor = conn.connection.cursor()
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
                                SELECT id, CONCAT(short_name, ' ', name_1) AS nom_complet, gender,phone_1,sms_1,industry
                                FROM customer_mcbc_live_full
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
                        },
                        {
                            "name": "Supression de la fonction calculate_all_capitals ",
                            "sql": "DROP FUNCTION IF EXISTS calculate_all_capitals"
                        },
                        {
                            "name": "Creation de la fonction calculate_all_capitals ",
                            "sql": """  
                            CREATE FUNCTION calculate_all_capitals(
                                type_sysdate TEXT,
                                open_balance TEXT,
                                credit_mvmt TEXT,
                                debit_mvmt TEXT
                            )
                            RETURNS TEXT
                            DETERMINISTIC
                            BEGIN
                                DECLARE token TEXT;
                                DECLARE remaining_type TEXT;
                                DECLARE remaining_open TEXT;
                                DECLARE remaining_credit TEXT;
                                DECLARE remaining_debit TEXT;
                                
                                DECLARE position INT DEFAULT 0;
                                DECLARE sep_pos INT;
                                
                                DECLARE open_val DECIMAL(20,2);
                                DECLARE credit_val DECIMAL(20,2);
                                DECLARE debit_val DECIMAL(20,2);
                                
                                DECLARE capital_non_appele DECIMAL(20,2) DEFAULT 0;
                                DECLARE capital_appele DECIMAL(20,2) DEFAULT 0;
                                DECLARE capital_total DECIMAL(20,2) DEFAULT 0;
                                 
                                SET remaining_type = type_sysdate;
                                SET remaining_open = open_balance;
                                SET remaining_credit = credit_mvmt;
                                SET remaining_debit = debit_mvmt;
                                 
                                WHILE LENGTH(remaining_type) > 0 DO 
                                    SET sep_pos = LOCATE('|', remaining_type);
                                    IF sep_pos = 0 THEN
                                        SET token = remaining_type;
                                        SET remaining_type = '';
                                    ELSE
                                        SET token = LEFT(remaining_type, sep_pos - 1);
                                        SET remaining_type = SUBSTRING(remaining_type, sep_pos + 1);
                                    END IF;
                                     
                                    SET sep_pos = LOCATE('|', remaining_open);
                                    IF sep_pos = 0 THEN
                                        SET open_val = IF(remaining_open = '' OR remaining_open IS NULL, 0, CAST(remaining_open AS DECIMAL(20,2)));
                                        SET remaining_open = '';
                                    ELSE
                                        SET open_val = IF(LEFT(remaining_open, sep_pos - 1) = '' OR LEFT(remaining_open, sep_pos - 1) IS NULL, 0, CAST(LEFT(remaining_open, sep_pos - 1) AS DECIMAL(20,2)));
                                        SET remaining_open = SUBSTRING(remaining_open, sep_pos + 1);
                                    END IF;
                                    
                                    SET sep_pos = LOCATE('|', remaining_credit);
                                    IF sep_pos = 0 THEN
                                        SET credit_val = IF(remaining_credit = '' OR remaining_credit IS NULL, 0, CAST(remaining_credit AS DECIMAL(20,2)));
                                        SET remaining_credit = '';
                                    ELSE
                                        SET credit_val = IF(LEFT(remaining_credit, sep_pos - 1) = '' OR LEFT(remaining_credit, sep_pos - 1) IS NULL, 0, CAST(LEFT(remaining_credit, sep_pos - 1) AS DECIMAL(20,2)));
                                        SET remaining_credit = SUBSTRING(remaining_credit, sep_pos + 1);
                                    END IF;
                                    
                                    SET sep_pos = LOCATE('|', remaining_debit);
                                    IF sep_pos = 0 THEN
                                        SET debit_val = IF(remaining_debit = '' OR remaining_debit IS NULL, 0, CAST(remaining_debit AS DECIMAL(20,2)));
                                        SET remaining_debit = '';
                                    ELSE
                                        SET debit_val = IF(LEFT(remaining_debit, sep_pos - 1) = '' OR LEFT(remaining_debit, sep_pos - 1) IS NULL, 0, CAST(LEFT(remaining_debit, sep_pos - 1) AS DECIMAL(20,2)));
                                        SET remaining_debit = SUBSTRING(remaining_debit, sep_pos + 1);
                                    END IF;
                                     
                                    IF (
                                        token IN ('CURACCOUNT', 'DUEACCOUNT') OR
                                        token LIKE 'CURACCOUNT%' OR
                                        token LIKE 'DUEACCOUNT%'
                                    ) AND ( 
                                        CAST(SUBSTRING(token, LOCATE('-', token) + 1) AS UNSIGNED) <= '{current_date}'
                                    ) THEN
                                    SET capital_non_appele = capital_non_appele + open_val + credit_val + debit_val;

                                    ELSEIF (
                                        token IN ('PA1ACCOUNT', 'PA2ACCOUNT', 'PA3ACCOUNT', 'PA4ACCOUNT') OR
                                        token LIKE 'PA1ACCOUNT%' OR
                                        token LIKE 'PA2ACCOUNT%' OR
                                        token LIKE 'PA3ACCOUNT%' OR
                                        token LIKE 'PA4ACCOUNT%'
                                    ) AND ( 
                                        CAST(SUBSTRING(token, LOCATE('-', token) + 1) AS UNSIGNED) <= '{current_date}'
                                    ) THEN
                                        SET capital_appele = capital_appele + open_val + credit_val + debit_val;

                                    END IF;

                            
                                    SET position = position + 1;
                                END WHILE; 
                                SET capital_total = capital_non_appele + capital_appele; 
                                RETURN CONCAT(capital_non_appele, '|', capital_appele, '|', capital_total);
                            END; """
                        },
                        {
                            "name": "Creation index idx_arrangement_product_status ",
                            "sql": "CREATE INDEX IF NOT EXISTS idx_arrangement_product_status ON aa_arrangement_mcbc_live_full(product_line, arr_status)"
                        },
                        {
                            "name": "Creation index idx_arrangement_linked_appl ",
                            "sql": " CREATE INDEX IF NOT EXISTS idx_arrangement_linked_appl ON aa_arrangement_mcbc_live_full(linked_appl_id)"
                        },
                        {
                            "name": "Creation index eb_cont_bal_mcbc_live_full ",
                            "sql": " CREATE INDEX IF NOT EXISTS idx_eb_cont_id ON eb_cont_bal_mcbc_live_full(id);"
                        },
                        {
                            "name": "Suppresion de la fonction calculate_total_interet_echus ",
                            "sql": "DROP FUNCTION IF EXISTS calculate_total_interet_echus;"
                        },
                        {
                            "name": "Creation de la fonction calculate_total_interet_echus ",
                            "sql": f""" 
                             
                                CREATE FUNCTION calculate_total_interet_echus(
                                    entries TEXT,
                                    open_balance TEXT,
                                    separator_ VARCHAR(10)
                                )
                                RETURNS DECIMAL(15,2)
                                DETERMINISTIC
                                BEGIN
                                    DECLARE indices_total_interet_echus TEXT DEFAULT '';
                                    DECLARE montant_pert_total DECIMAL(15,2) DEFAULT 0;
                                    DECLARE current_index INT;
                                    DECLARE open_balance_value TEXT;
                                    DECLARE current_open_balance DECIMAL(15,2);
                                    DECLARE result DECIMAL(15,2);
                                     
                                    DECLARE remaining_entries TEXT;
                                    DECLARE current_entry TEXT;
                                    DECLARE entry_index INT DEFAULT 0;
                                    DECLARE sep_pos INT;
                                     
                                    DECLARE remaining_indices TEXT;
                                    DECLARE index_str TEXT;
                                     
                                    DECLARE temp_balance TEXT;
                                    DECLARE temp_index INT DEFAULT 0;
                                     
                                    IF entries IS NULL OR entries = '' THEN
                                        RETURN 0;
                                    END IF;
                                     
                                    SET remaining_entries = entries;
                                    SET entry_index = 0;
                                     
                                    WHILE LENGTH(remaining_entries) > 0 DO 
                                        SET sep_pos = LOCATE(separator_, remaining_entries);
                                        IF sep_pos = 0 THEN
                                            SET current_entry = remaining_entries;
                                            SET remaining_entries = '';
                                        ELSE
                                            SET current_entry = LEFT(remaining_entries, sep_pos - 1);
                                            SET remaining_entries = SUBSTRING(remaining_entries, sep_pos + LENGTH(separator_));
                                        END IF;
                                         
                                        IF (current_entry LIKE '%PA1PRINCIPALINT%' OR 
                                            current_entry LIKE '%PA2PRINCIPALINT%' OR 
                                            current_entry LIKE '%PA3PRINCIPALINT%' OR 
                                            current_entry LIKE '%PA4PRINCIPALINT%') AND 
                                        current_entry NOT LIKE '%SP%' THEN
                                             
                                            IF indices_total_interet_echus = '' THEN
                                                SET indices_total_interet_echus = CAST(entry_index AS CHAR);
                                            ELSE
                                                SET indices_total_interet_echus = CONCAT(indices_total_interet_echus, ',', CAST(entry_index AS CHAR));
                                            END IF;
                                        END IF;
                                        
                                        SET entry_index = entry_index + 1;
                                    END WHILE;
                                     
                                    IF indices_total_interet_echus = '' THEN 
                                        RETURN 0;
                                    ELSE 
                                        SET montant_pert_total = 0;
                                        SET remaining_indices = indices_total_interet_echus; 
                                        WHILE LENGTH(remaining_indices) > 0 DO 
                                            SET sep_pos = LOCATE(',', remaining_indices);
                                            IF sep_pos = 0 THEN
                                                SET index_str = remaining_indices;
                                                SET remaining_indices = '';
                                            ELSE
                                                SET index_str = LEFT(remaining_indices, sep_pos - 1);
                                                SET remaining_indices = SUBSTRING(remaining_indices, sep_pos + 1);
                                            END IF;
                                            
                                            SET current_index = CAST(index_str AS UNSIGNED); 
                                            SET current_open_balance = 0; 
                                            IF open_balance IS NOT NULL AND open_balance != '' THEN 
                                                SET open_balance_value = ''; 
                                                SET temp_balance = open_balance;
                                                SET temp_index = 0;
                                                
                                                WHILE temp_index <= current_index AND LENGTH(temp_balance) > 0 DO
                                                    SET sep_pos = LOCATE(separator_, temp_balance);
                                                    IF sep_pos = 0 THEN
                                                        IF temp_index = current_index THEN
                                                            SET open_balance_value = temp_balance;
                                                        END IF;
                                                        SET temp_balance = '';
                                                    ELSE
                                                        IF temp_index = current_index THEN
                                                            SET open_balance_value = LEFT(temp_balance, sep_pos - 1);
                                                            SET temp_balance = '';
                                                        ELSE
                                                            SET temp_balance = SUBSTRING(temp_balance, sep_pos + LENGTH(separator_));
                                                        END IF;
                                                    END IF;
                                                    SET temp_index = temp_index + 1;
                                                END WHILE; 
                                                SET open_balance_value = TRIM(open_balance_value);
                                                IF open_balance_value = '' OR open_balance_value IS NULL THEN 
                                                    SET open_balance_value = '0.0';
                                                END IF;
                                                
                                                SET current_open_balance = CAST(open_balance_value AS DECIMAL(15,2));
                                            END IF; 
                                            SET montant_pert_total = ROUND(current_open_balance, 2);
                                        END WHILE; 
                                        IF montant_pert_total < 0 THEN
                                            SET result = montant_pert_total * -1;
                                        ELSE
                                            SET result = montant_pert_total;
                                        END IF; 
                                        RETURN result;
                                    END IF;
                                END;  
                            """
                        },
                        {
                            "name": "Suppression de la fonction get_customer ",
                            "sql": "DROP FUNCTION IF EXISTS get_customer"
                        },
                        {
                            "name": "Creation de la fonction get_customer ",
                            "sql": f"""  

                                CREATE FUNCTION get_customer(arrangement_ids VARCHAR(255)) 
                                RETURNS VARCHAR(255)
                                DETERMINISTIC
                                BEGIN 
                                    DECLARE first_id VARCHAR(50); 
                                    
                                    -- Vérifier si arrangement_ids est NULL ou vide
                                    IF arrangement_ids IS NULL OR arrangement_ids = '' THEN
                                        RETURN NULL;
                                    END IF;
                                    
                                    -- Extraire le premier ID avant le séparateur '|'
                                    SET first_id = SUBSTRING_INDEX(arrangement_ids, '|', 1);
                                    
                                    -- Nettoyer l'ID (supprimer les espaces)
                                    SET first_id = TRIM(first_id);  
                                    RETURN first_id;
                                END """
                        },
                        {
                            "name": "Suppression de la Table temp_AMOUNT ",
                            "sql": f""" DROP TABLE IF EXISTS temp_AMOUNT """
                        },
                        {
                            "name": "CREATION de la Table temp_AMOUNT ",
                            "sql": f"""  
                                CREATE TABLE temp_AMOUNT AS
                                    SELECT id_comp_1, amount 
                                    FROM AA_ARR_TERM_MCBC_LIVE_FULL 
                                    WHERE   activity IN ('LENDING-TAKEOVER-ARRANGEMENT', 'LENDING-NEW-ARRANGEMENT')
                            """
                        },
                        {
                            "name": "Suppression de la Table temp_payment_date ",
                            "sql": f""" DROP TABLE IF EXISTS temp_payment_date  """
                        },
                        {
                            "name": "Creation de la Table temp_payment_date ",
                            "sql": f"""   
                                    CREATE TABLE temp_payment_date AS
                                    SELECT  arrangement_id, 
                                                MIN(bill.payment_date) as payment_date 
                                            FROM aa_bill_details_mcbc_live_full  AS bill
                                            GROUP BY bill.arrangement_id """
                        },
                        {
                            "name": "Suppression de la Table temp_Nombre_de_jour_retard ",
                            "sql": f"""   DROP TABLE IF EXISTS temp_Nombre_de_jour_retard  """
                        },
                        {
                            "name": "CREATION de la Table temp_Nombre_de_jour_retard ",
                            "sql": """ 
                                    CREATE TABLE temp_Nombre_de_jour_retard AS
                                    SELECT arrangement_id,DATEDIFF('{current_date}', MIN(payment_date)) as Nombre_de_jour_retard  FROM aa_bill_details_mcbc_live_full 
                                            WHERE settle_status = 'UNPAID'
                                            GROUP BY arrangement_id
                            """
                        },
                        {
                            "name": "Suppression de la Table temp_od_pen ",
                            "sql": f"""   DROP TABLE IF EXISTS temp_od_pen  """
                        },
                        {
                            "name": "CREATION de la Table temp_od_pen ",
                            "sql": f""" 
                                    CREATE TABLE temp_od_pen AS
                                    SELECT arrangement_id, payment_date, SUM(os_total_amount) AS OD_PEN
                                    FROM (
                                        SELECT arrangement_id, payment_date, os_total_amount,
                                            ROW_NUMBER() OVER (PARTITION BY arrangement_id ORDER BY payment_date DESC) as rn
                                        FROM aa_bill_details_mcbc_live_full
                                    ) ranked
                                    WHERE rn = 1 
                                    GROUP BY arrangement_id, payment_date
                                    ORDER BY payment_date
                            """
                        },
                        {
                            "name": "Creation de la INDEX idx_id_comp_1 ",
                            "sql": "ALTER TABLE temp_AMOUNT ADD INDEX idx_id_comp_1 (id_comp_1)"
                        },
                        {
                            "name": "Creation de la INDEX idx_arrangement_id ",
                            "sql": "ALTER TABLE temp_payment_date ADD INDEX idx_arrangement_id (arrangement_id)"
                        },
                        {
                            "name": "Creation de la TABLE temp_Nombre_de_jour_retard  ADD INDEX idx_arrangement_id ",
                            "sql": "ALTER TABLE temp_Nombre_de_jour_retard  ADD INDEX idx_arrangement_id (arrangement_id);"
                        }, 
                        {
                            "name": "Creation de la TABLE temp_od_pen ADD INDEX idx_arrangement_id  ",
                            "sql": "ALTER TABLE temp_od_pen ADD INDEX idx_arrangement_id (arrangement_id)"
                        },
                        {
                            "name": "Suppression de la TABLE IF EXISTS temp_INTEREST ",
                            "sql": "DROP TABLE IF EXISTS temp_INTEREST"
                        },
                        {
                            "name": "Creation de la fonction temp_INTEREST ",
                            "sql": f""" CREATE TABLE temp_INTEREST AS
                                    SELECT id_comp_1,effective_rate as taux_d_interet,DATEDIFF(maturity_date, base_date)  AS Duree_Remboursement,maturity_date AS Date_fin_pret
                                        FROM aa_arr_interest_mcbc_live_full  
                                        INNER JOIN aa_account_details_mcbc_live_full as account
                                        ON account.id = id_comp_1
                                        WHERE  id_comp_2 = 'PRINCIPALINT' GROUP BY id_comp_1 """
                        },
                        {
                            "name": "Creation de la TABLE temp_INTEREST ADD INDEX idx_id_comp_1  ",
                            "sql": "ALTER TABLE temp_INTEREST ADD INDEX idx_id_comp_1 (id_comp_1)"
                        }, 
                        {
                            "name": "Creation de la TABLE industry_mcbc_live_full ADD INDEX idx_id_comp_1  ",
                            "sql": "ALTER TABLE industry_mcbc_live_full ADD INDEX idx_id_comp_1 (id)"
                        },
                        {
                            "name": "Creation de la TABLE temp_clients ADD PRIMAR  ",
                            "sql": "ALTER TABLE temp_clients ADD PRIMARY KEY (id), ADD INDEX idx_id (id);"
                        },
                        {
                            "name": "Creation de la temp_clients ADD INDEX idx_industy  ",
                            "sql": "ALTER TABLE temp_clients ADD INDEX idx_industy (industry)"
                        },
                        {
                            "name": """Suppression de la Table encours_credit_{current_date} """,
                            "sql": """DROP TABLE IF EXISTS encours_credit_{current_date}"""
                        },
                        {
                            "name":"""Creation de la Table  encours_credit_{current_date} """,
                            "sql": """ 
                            CREATE TABLE encours_credit_{current_date} AS
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
                                                -- AND NOT (tmp_od_pen.OD_PEN  = 0.0 AND (arrangement.arr_status = 'EXPIRED' OR arrangement.arr_status = 'CLOSE'))
                                                -- HAVING NOT (Capital_ = '0.00|0.00|0.00' AND (tmp_od_pen.OD_PEN='0.00' OR tmp_od_pen.OD_PEN =''))   
                            """
                        }, 
                        {
                            "name": """Ajustemen de la Table encours_credit_{current_date} """,
                            "sql": """
                                DELETE encours
                                FROM  encours_credit_{current_date}  AS encours
                                LEFT JOIN em_lo_application_mcbc_live_full AS em_
                                    ON em_.arrangement_id = encours.id 
                                WHERE em_.proc_status != 'DISBURSED';"""
                        }, 
                        {
                            "name": """Suppréssion de la DROP PROCEDURE calculate_capital_sums  IF EXISTS """,
                            "sql": """
                                DROP PROCEDURE IF EXISTS calculate_capital_sums """
                        }, 
                        {
                            "name": """ CREATING PROCEDURE calculate_capital_sum """,
                            "sql": """
                                CREATE PROCEDURE calculate_capital_sums()
                                BEGIN
                                    DECLARE done INT DEFAULT FALSE;
                                    DECLARE tbl_name VARCHAR(255);
                                    DECLARE sql_query TEXT;

                                    -- curseur pour toutes les tables qui commencent par encours_credit_
                                    DECLARE cur CURSOR FOR
                                        SELECT table_name
                                        FROM information_schema.tables
                                        WHERE table_schema = DATABASE()
                                        AND table_name LIKE 'encours_credit_%';

                                    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

                                    -- table temporaire pour stocker les résultats
                                    -- DROP  TABLE IF EXISTS tmp_capital_sums;
                                    DROP  TABLE IF EXISTS total_capital_encours_credit;
                                    CREATE  TABLE total_capital_encours_credit (
                                        table_name VARCHAR(255),
                                        Total_amount DECIMAL(30,6)
                                    );

                                    OPEN cur;

                                    read_loop: LOOP
                                        FETCH cur INTO tbl_name;
                                        IF done THEN
                                            LEAVE read_loop;
                                        END IF;

                                        -- construire la requête dynamique pour cette table
                                        SET @sql_query = CONCAT(
                                            'INSERT INTO total_capital_encours_credit ',
                                            'SELECT ''', tbl_name, ''' AS table_name, ',
                                            'SUM(ABS(CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(Capital_, ''|'', 3), ''|'', -1) AS DECIMAL(20,6)))) ',
                                            'FROM ', tbl_name
                                        );

                                        -- préparer et exécuter
                                        PREPARE stmt FROM @sql_query;
                                        EXECUTE stmt;
                                        DEALLOCATE PREPARE stmt;
                                    END LOOP;

                                    CLOSE cur;

                                    -- afficher les résultats
                                    SELECT * FROM total_capital_encours_credit;
                                END ;
                                """
                        }, 
                        {
                            "name": """ appelle du fonction calculate_capital_sums """,
                            "sql": """CALL calculate_capital_sums();"""
                        }, 
                    ]

                # Exemple d’utilisation :
                # sql = steps[23]["sql"].format(current_date="20250611")


            print("------------------------------------ icii ----------------------------------")

           
            cursor.execute("DELETE FROM init_status")
            requets_len=len(steps)
            
            yield {"status": "success", "data_step": steps}
            print( {"status": "success", "data_step": steps})
            for i, step in enumerate(steps, 0):
                name = step["name"]
                yield {"name": name, "status": "processing","total":requets_len,"current":i}
                print( {"name": name, "status": "processing","total":requets_len,"current":i})

                cursor.execute("SELECT status FROM init_status WHERE name = %s", (name,))
                existing = cursor.fetchone()

                if existing and existing[0] == "done":
                    yield {"name": name, "status": "skipped"}
                    print( {"name": name, "status": "skipped"})
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
                    print( {"name": name, "status": "done","total":requets_len,"current":i})
                except Exception as e:
                    cursor.execute(
                        "REPLACE INTO init_status (name, status, message) VALUES (%s, %s, %s)",
                        (name, "error", str(e))
                    )
                    yield {"name": name, "status": "error", "message": str(e)}
                    print( {"name": name, "status": "error_ici", "message": str(e)})
            conn.commit()
            yield {"name": name, "status": "done","message":"Toutes les étapes sont terminées"}
            yield "event: end\ndata: done\n\n" 
            print( {"name": name, "status": "done","message":"Toutes les étapes sont terminées"})
            return
            # return status_report
        except Exception as e:
            yield { "status": "error_ici_","message":str(e)}
            print( { "status": "error","message":str(e)})
            return
    
    def run_init(self):
        yield {"index": 1, "status": "running", "message": "Traitement des encours..."}
        time.sleep(1)  # Simulation
        yield {"index": 1, "status": "done", "message": "Encours terminés."}

    def run_etat_remboursement(self):
        yield {"index": 1, "status": "running", "message": "Traitement des etat_remboursements..."}
        time.sleep(1)
        yield {"index": 1, "status": "done", "message": "etat_remboursements terminés."}

    def run_remboursement(self):
        yield {"index": 2, "status": "running", "message": "Traitement des remboursements..."}
        time.sleep(1)
        yield {"index": 2, "status": "done", "message": "Remboursements terminés."}

    def run_previsionnel(self):
        yield {"index": 3, "status": "running", "message": "Génération de l'état prévisionnel..."}
        time.sleep(1)
        yield {"index": 3, "status": "done", "message": "Prévisionnel terminé."}

    def run_limit_avm(self):
        yield {"index": 4, "status": "running", "message": "Analyse des limites AVM..."}
        time.sleep(1)
        yield {"index": 4, "status": "done", "message": "Limite AVM traitée."}

    def run_limit_caution(self):
        yield {"index": 5, "status": "running", "message": "Analyse des limites de caution..."}
        time.sleep(1)
        yield {"index": 5, "status": "done", "message": "Limite caution traitée."}

    
