<template>
  <div id="upload-container">
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
      <input type="file" accept=".csv" multiple ref="fileInput" class="hidden-file-input" @change="handleFileUpload">
    </v-card>
    <v-dialog max-width="500">
      <template v-slot:activator="{ props: activatorProps }">
        <v-btn @click="showFiles" id="history" v-bind="activatorProps" icon="mdi-history" variant="flat"></v-btn>
      </template>

      <template v-slot:default="{ isActive }">
        <v-card title="Explorateur de fichier">
          <div style="max-height: 400px; overflow-y: auto; padding: 0 30px;">
            <v-treeview v-if="list_file.length" v-model:opened="open" :items="list_file" density="compact" item-value="title" activatable open-on-click >
              <template v-slot:prepend="{ item, isOpen }">
                <v-icon v-if="!item.file" :icon="isOpen ? 'mdi-folder-open' : 'mdi-folder'" />
                <v-icon v-else icon="mdi-file-chart-outline" style=" font-size: 15px;" />
                <button v-if="!item.file" style="position:absolute; margin-left: 400px;" @click.stop="chargerDossier(item,isActive)" >
                  <v-icon icon="mdi mdi-database " size="24" style=" position: relative; margin-left: -20px; margin-top: 7px; " />
                  <v-icon :id="'refresh' + item.title.replaceAll(/[^a-zA-Z0-9_-]/g, '_')" icon="mdi mdi mdi-sync " size="12" style=" position: relative; margin-top: 20px;margin-left:-7px; background-color: black;border-radius: 15px;" />
                </button>
              </template>
              <template #title="{ item }">
                <span :class="item.file ? 'custom_title' : ''">{{ item.title }}</span>
              </template>
            </v-treeview>
          </div>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text="Fermer" @click="isActive.value = false" />
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
          <v-btn text @click="isDialogActive = false">Fermer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <import_progress v-if="show_progress_import">
    </import_progress>
  </div>
</template>

<script setup>
import { ref,inject } from 'vue'
import axios from '@/api/axios'
import { usePopupStore } from '../../stores'
import Cookies from 'js-cookie'
import import_progress from '../../components/loading/import_progress.vue'
import { VTreeview } from 'vuetify/labs/VTreeview'


const api = inject('api') 
const file_names = ref([]);  // noms des fichiers
const file_name = ref("Importer un fichier");
const fileInput = ref(null)
const files_data = ref(null)
const is_exist_file = ref(false);
const today = new Date().toISOString().split('T')[0]
const isDialogActive = ref(false)
const show_progress_import = ref(false)
// Fonction pour ouvrir la boîte de dialogue de sélection de fichiers
const triggerFileInput = () => {
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
      file: !!child.file
    })) : []
  }));
};

const handleFileUpload = (event) => {
  const files = event.target.files;
  const elt_ = document.getElementById('file_name');

  if (files.length < 5 || files.length > 21) {
    alert("Vous ne pouvez sélectionner que de 18 à 21  fichiers.");
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
  load_database(refresh,file.children,file.title,date_string) 
  setTimeout(() => {
    usePopupStore().togglePopupCDI();
  }, 300);

};


const cancel = () => {
  fileInput.value.value = "";
  file_name.value = "Importer un fichier";
  file_names.value = [];
  files_data.value = [];
  is_exist_file.value = false;
  document.getElementById('file_name').classList.remove('file_loaded');

};

const check_data_state = () => {
  if (date_dossier.value) {
    is_full.value = true
  }
}

const open_dialoge_date=()=> {
  isDialogActive.value = true
}

const load_database = async (refresh, files, folder,date_string) => {

  var index_table=0;
  try {
    const response = await fetch('http://192.168.1.212:8000/api/create_multiple_table', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        files: files.map(f => f.title),
        app: null,
        folder: folder,
        str_date:date_string
      })
    });

    if (!response.body) {
      throw new Error("Pas de flux en réponse !");
    } 
    

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    usePopupStore().precentage=0
    let partial = "";
    while (true) {
      
      const { done, value } = await reader.read();
      if (done) break;

      partial += decoder.decode(value, { stream: true });

      // Découper les lignes (JSON par ligne)
      let lines = partial.split("\n");  
      // console.log(lines);
      
      partial = lines.pop();
      for (const line of lines) {
        if (line.trim()) {
          try {
            const msg = JSON.parse(line);
            if (msg.fait) {
              usePopupStore().precentage=0
              usePopupStore().cdi_list_file_stream[index_table].success=true
              index_table++
              if (index_table==files.length) {
                setTimeout(() => {
                  usePopupStore().showPopupCDI = false
                }, 200);
              }

            }
            if(msg.filename ){
              usePopupStore().cdi_list_file_stream.push([
                {file_name:msg.filename},
                {task:msg.task},
                {row_count:msg.row_count},
                {success:false},
                {total:msg.total}])

            }else{
               if(msg.task){
                usePopupStore().cdi_list_file_stream[index_table].task=msg.task
                }
                if(msg.row_count){
                    usePopupStore().cdi_list_file_stream[index_table].row_count=msg.row_count
                }
                if(msg.total){
                    usePopupStore().cdi_list_file_stream[index_table].total=msg.total
                }
                if(msg.percentage){
                    usePopupStore().precentage=parseFloat(msg.percentage)
                }
            }

          } catch (e) {
            console.warn("Impossible de parser la ligne :", line,e);
          }
        }
      }
    }

  } catch (error) {
    console.error("Erreur lors du chargement du fichier dans la base :", error);
  } finally {
    refresh.classList.remove('animIt');
    index_table=0
    usePopupStore().cdi_list_file_stream=[]
  }
};

const check_file = () => {
  if (date_dossier.value) {
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
    const response = await fetch('http://192.168.1.212:8000/api/upload_multiple_files', {
      method: 'POST',
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

  } catch (error) {
    console.error('Erreur upload:', error);
  }
};



// Méthode pour afficher les fichiers
const showFiles = async () => {
  try {
    const response = await axios.get('/api/show_files', {
      params: {
        app:app_type.value
      }
    });
    // console.log(response.data.files);
    list_file.value = normalizeTree(response.data.files);// Affichage des fichiers reçus
  } catch (error) {
    console.error("Erreur lors de la récupération des fichiers:", error); // Gestion des erreurs
  }
};

const show_popup=()=>{
  usePopupStore().togglePopup()
  // console.log(usePopupStore().showPopup,file_name);
  // usePopupStore().loadFile=file_name

}



</script>



<style scoped>
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
