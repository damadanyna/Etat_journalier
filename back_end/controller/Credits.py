from fastapi import Request
from fastapi.responses import StreamingResponse
import json
from typing import List
import os
import shutil
from werkzeug.utils import secure_filename

class Credits:
    def __init__(self, db=None):
        
        self.db = db  # au cas où tu veux utiliser la BDD
        self.upload_folder = 'load_file' 
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
        print("Credit initialisé") 

    def get_data(self):
        return {"message": "Données Credit"}

    def create_multiple_table(self):
        async def endpoint(request: Request):
            data = await request.json()

            if 'files' not in data or 'app' not in data or 'folder' not in data:
                return StreamingResponse(
                    content=iter([json.dumps({"error": "Paramètres manquants : files, app et folder requis"})]),
                    media_type="application/json"
                )

            filenames: List[str] = data['files']
            app_name: str = data['app']
            folder: str = data['folder']

            if not isinstance(filenames, list) or not filenames:
                return StreamingResponse(
                    content=iter([json.dumps({"error": "files doit être une liste non vide"})]),
                    media_type="application/json"
                )

            def generate_all():
                for filename in filenames:
                    yield json.dumps({
                        "status": "start",
                        "message": f"[INFO] Début du traitement du fichier : {filename}",
                        "filename": filename
                    }) + "\n"

                    try:
                        generator = self.load_file_csv_in_database(filename, app_name, folder)
                        if generator is None:
                            yield json.dumps({
                                "status": "critical_error",
                                "message": f"[ERREUR] Aucun message retourné pour {filename} (retour = None)"
                            }) + "\n"
                            continue

                        for message in generator:
                            yield message + "\n"

                    except Exception as e:
                        yield json.dumps({
                            "status": "critical_error",
                            "message": f"[ERREUR] Problème lors du traitement de {filename} : {str(e)}"
                        }) + "\n"

                    yield json.dumps({
                        "status": "end",
                        "message": f"[INFO] Fin du traitement du fichier : {filename}"
                    }) + "\n"

            return StreamingResponse(generate_all(), media_type="application/json")
        return endpoint
    
    def load_file_csv_in_database(self, filename: str, app_name: str, folder: str):
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

                found_file = None
                for file in files_in_dir:
                    if file == filename or file.startswith(filename.split('.')[0]):
                        found_file = file
                        break

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

    def upload_multiple_files(self, files, app_name, folder_name=None):
        total = len(files)
        for i, file in enumerate(files, 1):
            try:
                # Itérer sur le générateur et yield chaque dictionnaire produit
                for progress in self.upload_file_manual_in_detail(file, app_name, folder_name, i, total):
                    yield progress
            except Exception as e:
                yield {
                    "status": "error",
                    "file": file.filename if hasattr(file, "filename") else str(file),
                    "current": i,
                    "total": total,
                    "percentage": round((i / total) * 100, 2),
                    "message": f"[ERREUR] Échec du téléchargement de {file} : {str(e)}"
                }

    def show_files(self, app=None):
        """
        Renvoie une structure arborescente des sous-dossiers de `upload_folder/app`
        compatible avec Vuetify <v-treeview>, sans inclure le dossier racine.
        """

        base_folder = os.path.join(self.upload_folder, app) if app else self.upload_folder

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
    
    def upload_file_manual_in_detail(self, file, app_name, folder_name=None, current=None, total=None):
        if not file or not self.allowed_file(file.filename):
            yield {"status": "error", "file": str(file), "message": "Format invalide"}
            return

        filename = secure_filename(file.filename)
        
        # Construire le chemin de destination
        if folder_name:
            folder = os.path.join(app_name, folder_name) if app_name else folder_name
        else:
            folder = app_name
        folder_path = os.path.join(self.upload_folder, folder) if folder else self.upload_folder
        os.makedirs(folder_path, exist_ok=True)

        final_filepath = os.path.join(folder_path, filename)
        backup_filepath = None
        
        try:
            # Créer un backup si le fichier existe déjà
            if os.path.exists(final_filepath):
                backup_filepath = final_filepath + '.backup'
                shutil.copy2(final_filepath, backup_filepath)
            
            chunk_size = 1024 * 1024  # 1 MB
            total_size = 0

            # Récupérer la taille attendue du fichier
            total_expected_size = 0
            try:
                file.stream.seek(0, 2)
                total_expected_size = file.stream.tell()
                file.stream.seek(0)
            except Exception as e:
                yield {
                    "status": "warning", 
                    "file": filename,
                    "message": f"Impossible de déterminer la taille du fichier: {str(e)}"
                }

            # Écriture directe dans le fichier final
            with open(final_filepath, 'wb') as f:
                while True:
                    try:
                        chunk = file.stream.read(chunk_size)
                        if not chunk:
                            break
                        
                        bytes_written = f.write(chunk)
                        if bytes_written != len(chunk):
                            raise IOError(f"Erreur d'écriture: {bytes_written} octets écrits au lieu de {len(chunk)}")
                        
                        # Forcer l'écriture sur disque périodiquement
                        f.flush()
                        
                        total_size += len(chunk)

                        yield {
                            "status": "progress",
                            "file": filename,
                            "current": current,
                            "total": total,
                            "received_mb": round(total_size / (1024 * 1024), 2),
                            "total_mb": round(total_expected_size / (1024 * 1024), 2) if total_expected_size else None,
                            "percentage_file": round((total_size / total_expected_size) * 100, 2) if total_expected_size else None,
                            "message": f"[Serveur] Reçu {total_size / (1024 * 1024):.2f} MB..."
                        }
                        
                    except Exception as e:
                        # Restaurer le backup en cas d'erreur
                        if backup_filepath and os.path.exists(backup_filepath):
                            shutil.move(backup_filepath, final_filepath)
                            backup_filepath = None
                        
                        yield {
                            "status": "error",
                            "file": filename,
                            "message": f"Erreur durant le transfert: {str(e)}"
                        }
                        return

                # Synchronisation finale
                f.flush()
                os.fsync(f.fileno())

            # Vérification de l'intégrité
            if total_expected_size > 0 and total_size != total_expected_size:
                # Restaurer le backup
                if backup_filepath and os.path.exists(backup_filepath):
                    shutil.move(backup_filepath, final_filepath)
                    backup_filepath = None
                
                yield {
                    "status": "error",
                    "file": filename,
                    "message": f"Transfert incomplet: {total_size} octets reçus au lieu de {total_expected_size}"
                }
                return

            # Succès - supprimer le backup
            if backup_filepath and os.path.exists(backup_filepath):
                os.remove(backup_filepath)

            yield {
                "status": "success",
                "file": filename,
                "received_mb": round(total_size / (1024 * 1024), 2),
                "message": f"✅ Fichier {filename} transféré avec succès ({total_size / (1024 * 1024):.2f} MB)"
            }

        except Exception as e:
            # Restaurer le backup en cas d'erreur générale
            if backup_filepath and os.path.exists(backup_filepath):
                try:
                    shutil.move(backup_filepath, final_filepath)
                except:
                    pass
            
            yield {
                "status": "error",
                "file": filename,
                "message": f"Erreur lors de l'upload: {str(e)}"
            }
        
        finally:
            # Nettoyer le backup s'il reste
            if backup_filepath and os.path.exists(backup_filepath):
                try:
                    os.remove(backup_filepath)
                except:
                    pass