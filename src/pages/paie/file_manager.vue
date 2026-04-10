<template>
  <div id="upload-container">
             
            <div class="text-center pa-4">
              <v-dialog
                v-model="dialog"
                max-width="200"
                max-height="400"
                persistent  
                style=" background-color: #000000EE;"           
              >
              
                <div class="   w-full flex-col flex items-center justify-center"  >    
                    <v-progress-circular :model-value="percentage" :rotate="360" :size="150" :width="1.5" color="green">
                      <div class="flex flex-col items-center justify-center" > 
                        <span  class=" text-xl font-bold" v-if="percentage!=0">{{!'100.00%'?'100%':percentage}}</span>
                        <span v-else class=" animate-ping"> Chargement ...</span>
                        <span title="Temps de chargement" class="  text-stone-100 font-bold" v-text=" percentage=='100.00%'?'Fait':'Encours'"></span>
                      </div>
                    </v-progress-circular> 

                    <div>
                      <span class="white underline">Telechargement</span>
                      <div class="flex flex-row  text-green-500 mt-2">
                         <v-icon icon="mdi-file-chart-outline ml-2 mr-5"></v-icon>
                        {{download_file_name}}
                      </div>
                    </div>
                </div  > 
              </v-dialog>
            </div> 

    <popup_view v-if="usePopupStore().show_notification.status" style=" z-index: 10000;"></popup_view>
    <v-card class="upload-box" outlined>
      <v-icon size="48" class="upload-icon">mdi-cloud-upload</v-icon>
      <p class="upload-text">Importer les Fichiers ici</p>
      <p class="upload-subtext">ou choisissez localement</p>
      <div style="display: flex; flex-direction: row; align-items: center;">
        <v-btn variant="outlined" class="upload-btn" @click="triggerFileInput" id="file_name">  {{ file_name }}</v-btn>
        <div v-if="is_exist_file" style="display: flex; flex-direction: row; align-items: center;">
          <v-icon @click="cancel" size="24" title="Annuler" style="color: red; padding: 20px; margin-left: 10px; border-radius: 25px;">mdi-file-remove-outline</v-icon>
          <v-icon @click="open_dialoge_date" size="16" title="Charger le fichier" style="background: green; padding: 12px; margin-left: 10px; border-radius: 25px;"> mdi-check</v-icon>
        </div>
      </div>
      <ul v-if="file_names.length > 0" style="margin-top: 10px; list-style: none; padding-left: 0; max-height: 40vh; overflow-y: auto;">
        <li v-for="(name, index) in file_names" :key="index" style="display: flex; align-items: center;">
          <v-icon size="14" style="margin-right: 5px;">mdi-file</v-icon> {{ name }}
        </li>
      </ul>
      <input type="file" accept=".xlsx" multiple ref="fileInput" class="hidden-file-input" @change="handleFileUpload">
    </v-card>
    <v-dialog max-width="500">
      <template v-slot:activator="{ props: activatorProps }">
        <v-btn @click="showFiles" id="history" v-bind="activatorProps" icon="mdi-history" variant="flat"></v-btn>
      </template>      
      <template v-slot:default="{ isActive }">
        <v-card title="Explorateur de fichier">
          <div style="max-height: 400px; overflow-y: auto; padding: 0 30px;">
            <v-treeview v-if="list_file.length" v-model:opened="open" :items="list_file" density="compact" item-value="title" activatable open-on-click >
              <template v-slot:prepend="{ item, isOpen }" >
                <v-icon v-if="!item.file" :icon="isOpen ? 'mdi-folder-open' : 'mdi-folder'" />
                <v-icon v-else icon="mdi-file-chart-outline" style=" font-size: 15px;" />
                <button v-if="!item.file" style="position:absolute; margin-left: 400px;" @click.stop="chargerDossier(item,isActive)" >
                  <v-icon icon="mdi mdi-database " size="24" style=" position: relative; margin-left: -20px; margin-top: 7px; " />
                  <v-icon :id="'refresh' + item.title.replaceAll(/[^a-zA-Z0-9_-]/g, '_')" icon="mdi mdi-sync " size="12" style=" position: relative; margin-top: 20px;margin-left:-7px; background-color: black;border-radius: 15px;" />
                </button>
                <button  v-if="item.file"  style="position:absolute; margin-left: 380px;"  @click.stop="downloadFile(item)" >  
                  <v-icon :id="'download' + item.title.replaceAll(/[^a-zA-Z0-9_-]/g, '_')" icon="mdi mdi-download" size="17" style="position: relative; margin-top: -7px; margin-left:-40px; background-color: transparent; border-radius: 15px;"  />
                </button>
              </template>
              <template #title="{ item }">
                <span :class="item.file ? 'custom_title' : ''">{{CastString( item.title )}} </span>
                
              </template>
            </v-treeview>
          </div>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text="Fermer" @click="closeExplorerDialog(isActive)" />
          </v-card-actions>
        </v-card>
      </template>
    </v-dialog>
    <v-dialog v-model="isDialogActive" max-width="500">
      <v-card title="Date du dossier" >
        <!-- contenu du dialogue -->
        <div style=" padding: 0px 70px;">
          <v-text-field
            v-model="date_dossier"
            label="Date de traitement dans fichier"
            type="date"
            dense
            :max="today"
            @change="check_data_state" variant="outlined"/></div>
        <v-card-actions>
          <v-btn @click="check_file"   :disabled="!is_full" :color="is_full ? 'red' : 'gray'"  variant="flat" class="ml-2">Importer?</v-btn>
          <v-btn text @click="closeImportDateDialog">Fermer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

 
 </div>
 
 
</template>

<script setup>
import { ref,inject } from 'vue'
import axios from '@/api/axios'
import { usePopupStore } from '../../stores'
import Cookies from 'js-cookie'
import import_progress from '../../components/loading/import_progress.vue'
import { VTreeview } from 'vuetify/labs/VTreeview'
import { useActivityLogger } from '@/composables/useActivityLogger'

const dialog = ref(false)
const download_file_name= ref('')
const api = inject('api') 
const file_names = ref([]);  // noms des fichiers
const file_name = ref("Importer un fichier");
const fileInput = ref(null)
const files_data = ref(null)
const is_exist_file = ref(false);
const today = new Date().toISOString().split('T')[0]
const isDialogActive = ref(false)
const show_progress_import = ref(false)
const percentage= ref(0)
const { logUserActivity } = useActivityLogger(api)

const trackFileManagerAction = (payload) => {
  void logUserActivity(payload)
}

const getAuthHeaders = (extraHeaders = {}) => {
  const token = localStorage.getItem('access_token')
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extraHeaders,
  }
}

// Fonction pour ouvrir la boîte de dialogue de sélection de fichiers
const triggerFileInput = () => {
  trackFileManagerAction({
    action: 'open_file_picker',
    entityType: 'file_input',
    entityId: 'paie_upload',
    description: 'Ouverture du sélecteur de fichier de la page file_manager',
  })
  fileInput.value.click()
}
const list_file = ref([]);
const is_full=ref(false)
const date_dossier=ref()
const app_type=ref( Cookies.get('app'))

const open = ref([]);

// Créer une variable réactive pour stocker le nom du fichier
// Fonction pour gérer l'upload (facultatif)



const normalizeTree = (data) => {
  return data.map(item => ({
    title: item.title,
    children: Array.isArray(item.children) ? item.children.map(child => ({
      title: child.title,
      file: !!child.file,
      date: item.title,
    })) : []
  }));
};

const CastString = (str) => {
  if (str.length <= 40) return str
  else return str.substring(0, 37) + '...' 
}

const handleFileUpload = (event) => {
  const files = event.target.files;
  const elt_ = document.getElementById('file_name');

  if (files.length >1 ) {
    trackFileManagerAction({
      action: 'select_upload_file',
      entityType: 'file_input',
      entityId: 'multiple_files',
      description: `Échec de sélection: ${files.length} fichiers choisis au lieu d'un seul`,
      status: 'FAILED',
    })
    alert("Vous ne pouvez sélectionner que de 1  fichiers.");
    event.target.value = ""; // reset
    file_name.value = "Importer un fichier";
    file_names.value = [];
    files_data.value = [];
    elt_.classList.remove('file_loaded');
    is_exist_file.value = false;
    return;
  }

  const file = files[0];
  if (file) {
    // console.log('Fichier sélectionné :', file.name);
    files_data.value = Array.from(files); // tous les fichiers
    file_names.value = Array.from(files).map(f => f.name); // noms des fichiers
    file_name.value = `${files.length} fichier(s) sélectionné(s)`;
    elt_.classList.add('file_loaded');
    is_exist_file.value = true;
    trackFileManagerAction({
      action: 'select_upload_file',
      entityType: 'file',
      entityId: file.name,
      description: `Sélection du fichier ${file.name} pour import`,
    })
  }

    event.target.value = ""; // reset
};

const chargerDossier = (file,activatorProps) => {
  activatorProps.value=false
  let date_string= file.title.replace(/-/g, "")
  const id = 'refresh' + file.title.replaceAll(/[^a-zA-Z0-9_-]/g, '_');
  const refresh = document.getElementById(id);

  if (refresh) {
    refresh.classList.add('animIt')
  }
  // console.log(file.children);
  usePopupStore().cdi_list_stream=file.children  
  logUserActivity({
    action: 'load_folder',
    entityType: 'folder',
    entityId: file.title,
    description: `Chargement du dossier ${file.title}`,
  })
  load_database(refresh,file.children,file.title,date_string) 
  setTimeout(() => {
    usePopupStore().togglePopupCDI();
  }, 300);

};


const cancel = () => {
  const selectedNames = file_names.value.join(', ')
  fileInput.value.value = "";
  file_name.value = "Importer un fichier";
  file_names.value = [];
  files_data.value = [];
  is_exist_file.value = false;
  document.getElementById('file_name').classList.remove('file_loaded');

  trackFileManagerAction({
    action: 'cancel_upload_selection',
    entityType: 'file',
    entityId: selectedNames || 'none',
    description: selectedNames
      ? `Annulation de la sélection de fichier(s): ${selectedNames}`
      : 'Annulation de la sélection de fichier sans fichier actif',
  })

};

const check_data_state = () => {
  if (date_dossier.value) {
    is_full.value = true
    trackFileManagerAction({
      action: 'select_import_date',
      entityType: 'folder',
      entityId: date_dossier.value,
      description: `Sélection de la date d'import ${date_dossier.value} dans file_manager`,
    })
  }
}

const open_dialoge_date=()=> {
  isDialogActive.value = true
  trackFileManagerAction({
    action: 'open_import_date_dialog',
    entityType: 'dialog',
    entityId: 'import_date',
    description: 'Ouverture du dialogue de date avant import de fichier',
  })
}

const closeImportDateDialog = () => {
  isDialogActive.value = false
  trackFileManagerAction({
    action: 'close_import_date_dialog',
    entityType: 'dialog',
    entityId: 'import_date',
    description: 'Fermeture du dialogue de date d\'import',
  })
}

const closeExplorerDialog = (isActive) => {
  isActive.value = false
  trackFileManagerAction({
    action: 'close_file_explorer',
    entityType: 'dialog',
    entityId: 'file_explorer',
    description: 'Fermeture de l\'explorateur de fichiers paie',
  })
}

const load_database = async (refresh, files, folder, date_string) => {
  let index_table = 0;
  
  try {
    const response = await fetch(`${api}/api/create_multiple_table_paie`, {
      method: 'POST',
      headers: getAuthHeaders({
        'Content-Type': 'application/json',
      }),
      body: JSON.stringify({
        files: files.map(f => f.title),
        app: null,
        folder: folder,
        str_date: date_string
      })
    });

    if (!response.body) {
      throw new Error("Pas de flux en réponse !");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    
    // Initialisation
    usePopupStore().precentage = 0;
    usePopupStore().cdi_list_file_stream = [];
    
    let partial = "";
    let currentFileIndex = -1;
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      partial += decoder.decode(value, { stream: true });

      // Découper les lignes (JSON par ligne)
      let lines = partial.split("\n");
      partial = lines.pop() || "";
      
      for (const line of lines) {
        if (!line.trim()) continue;
        
        try {
          const msg = JSON.parse(line);
          
          console.log('[STREAM]', msg);

          // Détection d'un nouveau fichier
          if (msg.status === 'start' && msg.filename) {
            currentFileIndex++;
            usePopupStore().cdi_list_file_stream.push({
              file_name: msg.filename,
              task: 'En attente...',
              row_count: 0,
              total: 0,
              success: false
            });
            usePopupStore().precentage = 0;
          }

          // Mise à jour du fichier en cours
          if (currentFileIndex >= 0 && currentFileIndex < usePopupStore().cdi_list_file_stream.length) {
            const currentFile = usePopupStore().cdi_list_file_stream[currentFileIndex];

            // Mise à jour de la tâche
            if (msg.task) {
              currentFile.task = msg.task;
            }

            // Mise à jour du compteur de lignes
            if (msg.row_count) {
              currentFile.row_count = msg.row_count;
            }

            // Mise à jour du total
            if (msg.total) {
              currentFile.total = msg.total;
            }

            // Mise à jour du pourcentage
            if (msg.percentage !== undefined) {
              usePopupStore().precentage = parseFloat(msg.percentage);
            }

            // Fichier terminé avec succès
            if (msg.fait === true) {
              currentFile.success = true;
              usePopupStore().precentage = 100;
              
              console.log(`[FICHIER TERMINÉ] ${currentFile.file_name}`);
              
              // Si c'est le dernier fichier
              if (currentFileIndex === files.length - 1) {
                console.log('[TOUS LES FICHIERS TERMINÉS]');
                setTimeout(() => {
                  usePopupStore().showPopupCDI = false;
                }, 500);
              }
            }
          }

          // Messages d'erreur
          if (msg.status === 'error' || msg.status === 'critical_error') {
            console.error('[ERREUR]', msg.message);
            if (currentFileIndex >= 0) {
              usePopupStore().cdi_list_file_stream[currentFileIndex].task = 'Erreur';
              usePopupStore().cdi_list_file_stream[currentFileIndex].success = false;
            }
          }

          // Message final global
          if (msg.status === 'done') {
            console.log('[PROCESSUS TERMINÉ]', msg.summary);
          }

        } catch (e) {
          console.warn("Impossible de parser la ligne :", line, e);
        }
      }
    }

    console.log('[STREAMING TERMINÉ]');
    await logUserActivity({
      action: 'load_folder_database',
      entityType: 'folder',
      entityId: folder,
      description: `Chargement en base terminé pour le dossier ${folder}`,
    })

  } catch (error) {
    console.error("Erreur lors du chargement du fichier dans la base :", error);
    await logUserActivity({
      action: 'load_folder_database',
      entityType: 'folder',
      entityId: folder,
      description: `Échec du chargement en base pour le dossier ${folder}`,
      status: 'FAILED',
    })
  } finally {
    refresh.classList.remove('animIt');
  }
};

const check_file = () => {
  if (date_dossier.value) {
    trackFileManagerAction({
      action: 'confirm_import_file',
      entityType: 'folder',
      entityId: date_dossier.value,
      description: `Confirmation de l'import dans le dossier ${date_dossier.value}`,
    })
    show_progress_import.value=true
    uploadFile(date_dossier.value)
    isDialogActive.value = false
  }
  date_dossier.value=''
}

const uploadFile = async (folder_name) => {
  const formData = new FormData();
  files_data.value.forEach((file) => {
    formData.append('files', file);
  });
  formData.append('app', app_type.value);
  formData.append('folder_name', folder_name);
  try {
    const response = await fetch(`${api}/api/upload_multiple_files_paie`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let { value: chunk, done: readerDone } = await reader.read();
    let buffer = '';

    while (!readerDone) {
      buffer += decoder.decode(chunk, { stream: true });

      // Découper par lignes (chaque ligne = un JSON)
      let lines = buffer.split('\n');
      buffer = lines.pop(); // dernière ligne incomplète

      for (const line of lines) {
        if (line.trim()) {
          try {
            const msg = JSON.parse(line);
            // console.log('Progress:', msg);
            if (msg.total_files) {
              // console.log(msg.total_files);
              
            }
            if (msg.status=="info" && msg.file) { 
              usePopupStore().loadFile="Chargement de "+msg.file
            }
            // if (msg.status==='success') {
           
            // }

            // // Mettre à jour ton store ou UI ici avec msg
            // if (msg.percentage) {
            //   usePopupStore().precentage = msg.percentage;
            //   console.log(usePopupStore().precentage);
              
            // }
            // if (msg.message) {
            //   usePopupStore().show_notification.message = msg.message;
            // }
            // etc...
          } catch (e) {
            console.warn('Erreur JSON:', e);
          } 
        }
      }

      ({ value: chunk, done: readerDone } = await reader.read());
    }

    // Fin de lecture
    if (buffer.trim()) {
      try {
        const msg = JSON.parse(buffer);
        // console.log('Final message:', msg);
      } catch(e) {
        console.warn('Erreur JSON fin de flux:', e);
      }
    }

    // Après upload, réinitialiser si besoin
    files_data.value = [];
    file_names.value = [];
    file_name.value = "Importer un fichier";
    is_exist_file.value = false;
    usePopupStore().loadFile='Fait'
    setTimeout(() => {
                show_progress_import.value=false
                usePopupStore().loadFile="Préparation ..."
              }, 2000);

    usePopupStore().show_notification.status = true;
    usePopupStore().show_notification.message = 'Fichier importé';
    usePopupStore().show_notification.ico = 'mdi mdi-check';
    await logUserActivity({
      action: 'upload_file',
      entityType: 'folder',
      entityId: folder_name,
      description: `Import de fichier dans le dossier ${folder_name}`,
    })

  } catch (error) {
    console.error('Erreur upload:', error);
    await logUserActivity({
      action: 'upload_file',
      entityType: 'folder',
      entityId: folder_name,
      description: `Échec d'import dans le dossier ${folder_name}`,
      status: 'FAILED',
    })
  }
};



// Méthode pour afficher les fichiers
const showFiles = async () => {
  try {
    const response = await axios.get('/show_files_paie', {
      headers: getAuthHeaders(),
      params: {
        app:app_type.value
      }
    });
    console.log(response.data.files);
    list_file.value = normalizeTree(response.data.files);// Affichage des fichiers reçus
    await logUserActivity({
      action: 'show_files',
      entityType: 'file_explorer',
      entityId: 'paie',
      description: 'Ouverture de l’explorateur des fichiers paie',
    })
  } catch (error) {
    console.error("Erreur lors de la récupération des fichiers:", error); // Gestion des erreurs
    await logUserActivity({
      action: 'show_files',
      entityType: 'file_explorer',
      entityId: 'paie',
      description: 'Échec de l’ouverture de l’explorateur des fichiers paie',
      status: 'FAILED',
    })
  }
};

const show_popup=()=>{
  usePopupStore().togglePopup()
  // console.log(usePopupStore().showPopup,file_name);
  // usePopupStore().loadFile=file_name

}

const exportDialog = ref(false)
const exportType = ref('dav')
const exportDateDebut = ref('')
const exportDateFin = ref('')
const exportFormat = ref('csv')

const exportMulti = async () => {
  if (!exportDateDebut.value || !exportDateFin.value) {
    alert('Veuillez choisir une période')
    return
  }
  const params = new URLSearchParams({
    type: exportType.value,
    date_debut: exportDateDebut.value.replaceAll('-', ''),
    date_fin: exportDateFin.value.replaceAll('-', ''),
    format: exportFormat.value
  })
  const url = `${api}/api/export/multi?${params.toString()}`
  window.open(url, '_blank')
  await logUserActivity({
    action: 'export_multi',
    entityType: exportType.value,
    entityId: `${exportDateDebut.value}_${exportDateFin.value}`,
    description: `Export ${exportType.value} du ${exportDateDebut.value} au ${exportDateFin.value} en ${exportFormat.value}`,
  })
  exportDialog.value = false
}


const importDialog = ref(false)
const importError = ref("")
const importSuccess = ref("")
const importFilesInput = ref(null)
const selectedFiles = ref([])

const handleImportFiles = (event) => {
  selectedFiles.value = Array.from(event.target.files)
}

const triggerImport = async () => {
  importError.value = ""
  importSuccess.value = ""
  if (!selectedFiles.value.length) {
    importError.value = "Veuillez sélectionner au moins un fichier."
    return
  }
  const formData = new FormData()
  selectedFiles.value.forEach(file => formData.append("files", file))
  try {
    const res = await fetch(`${api}/api/import/multi`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: formData
    })
    const data = await res.json()
    if (data.errors && data.errors.length) {
      importError.value = data.errors.join("\n")
    }
    if (data.success && data.success.length) {
      importSuccess.value = data.success.join("\n")
      await logUserActivity({
        action: 'import_multi',
        entityType: 'multi_import',
        entityId: selectedFiles.value.map(file => file.name).join(', '),
        description: `Import multiple réussi pour ${selectedFiles.value.length} fichier(s)`,
      })
    }
  } catch (e) {
    importError.value = "Erreur réseau ou serveur"
    await logUserActivity({
      action: 'import_multi',
      entityType: 'multi_import',
      entityId: selectedFiles.value.map(file => file.name).join(', '),
      description: 'Échec de l’import multiple',
      status: 'FAILED',
    })
  }
}
const downloadFile = async (item) => {
  dialog.value = true
  percentage.value = 0
  download_file_name.value=item.title
  const date = item.date
  if (!date) {
    console.error("Impossible d'extraire la date");
    dialog.value = false
    await logUserActivity({
      action: 'download_file',
      entityType: 'file',
      entityId: item?.title || '',
      description: `Échec du téléchargement du fichier ${item?.title || ''} : date introuvable`,
      status: 'FAILED',
    })
    return;
  }

  try {
    console.log("Préparation du téléchargement...");

    const response = await fetch(
      `${api}/api/download-file-paie?filename=${encodeURIComponent(item.title)}&date=${encodeURIComponent(date)}`,
      {
        headers: getAuthHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error("Erreur API");
    }

    const reader = response.body.getReader();
    const contentLength = +response.headers.get("Content-Length") || 0;
    let receivedLength = 0;
    const chunks = [];

    console.log("Téléchargement en cours...");

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      receivedLength += value.length;

      if (contentLength) {
        const percent = ((receivedLength / contentLength) * 100).toFixed(2);
        percentage.value = percent+ '%'
        if(percent==100){
          setTimeout(() => {
            dialog.value = false
            percentage.value=0
          }, 500);
        }
        console.log(`Téléchargé : ${percent}%`);
      }
    }

    const blob = new Blob(chunks);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = item.title;
    a.click();
    URL.revokeObjectURL(url);

    console.log("Téléchargement terminé ✅");
    await logUserActivity({
      action: 'download_file',
      entityType: 'file',
      entityId: item.title,
      description: `Téléchargement du fichier ${item.title}`,
    })

  } catch (err) {
    console.error("Erreur téléchargement :", err);
    dialog.value = false
    percentage.value = 0
    await logUserActivity({
      action: 'download_file',
      entityType: 'file',
      entityId: item?.title || '',
      description: `Échec du téléchargement du fichier ${item?.title || ''}`,
      status: 'FAILED',
    })
  }
};


</script>



<style scoped>
.export-floating {
  position: absolute;
  top: 14px;
  right: 70px;
  z-index: 500;
  font-weight: bold;
    width: 150px;

}
.export-floating_import {
  position: absolute;
  top: 100px;
  right: 70px;
  z-index: 500;
  font-weight: bold;
    width: 250px;

}

.custom_title{

  font-size: 12px;
}
.file_loaded{
  background: green;
  color: white;
}
#list_{
  margin:71px 0px;
}
#separateur{
  height: 1px;
  margin-top: 20px;
  margin-bottom: 12px;
  background: gray;
}
#modal-content{
  display: flex;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  backdrop-filter: blur(4px);
  background: rgba(0, 0, 0, 0.257);
  align-items: center;
  justify-content: center;
  z-index: 100;
}
#modal-list{
  display: flex;
  flex-direction: column;
  background: wheat;
  color: black ;
  padding: 10px 20px;
  border-radius: 5px;

}
#title{
  font-size: 19px;
  font-weight: bold;
  color: rgb(49, 49, 49);
}
#history{
  position: absolute;
  bottom: 80px;
  right: 80px;
  font-size: 20px;
}
#history:hover{
  cursor: pointer;
  color: white;
}
/* Conteneur principal centré */
#upload-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh; 
}

/* Boîte d'upload */
.upload-box {
  width: 500px;
  background: #00000000;
  border: 2px dashed #666;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  text-align: center;
  padding: 20px;
}

/* Icône Upload */
.upload-icon {
  color: #ccc;
  margin-bottom: 10px;
}

/* Texte principal */
.upload-text {
  font-size: 20px;
  font-weight: bold;
  margin: 0;
}

/* Texte secondaire */
.upload-subtext {
  font-size: 14px;
  color: #bbb;
  margin: 10px 0;
}

/* Bouton pour choisir un fichier */
.upload-btn {
  border-color: #fff;
  color: #fff;
}

/* Cacher l'input file */
.hidden-file-input {
  display: none;
}
.animIt{
 animation:   spin .5s linear infinite;
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}




</style>
