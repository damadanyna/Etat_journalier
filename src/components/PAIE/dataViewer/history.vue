<template> 
  <v-card v-if="popupStore.user_access.access=='admin'" flat style="background: transparent;" >
    <template #text>
      <v-text-field v-model="search" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line/>
    </template>
    <v-data-table  style="padding:0px 15px;" class="bg-transparent" :headers="header_paie" :items="dataPaie" :search="search" item-value="Numero_pret" item-key="id" fixed-header height="450px" :items-per-page="50" @click:row="showRow"> 
      <template #item.ID="{ item }"> {{ item.ID?.slice(0, 2) || '' }}</template>
      <template #item.index="{ index }"> {{ index + 1 }}</template>
    </v-data-table>
  </v-card> 
  <FormeViewPaie :data="selectedRow"  @close="selectedRow = null"  />
  <FolderViewerPaie :data="date_liste" v-if="popupStore.user_access.access!='admin'" />
</template>

<script setup>
import { usePopupStore } from '../../../stores';
import { watch, ref,inject,computed, onMounted} from 'vue'; 
import FormeViewPaie from './formeViewPaie.vue'; 
import FolderViewerPaie from './folderViewerPaie.vue';

const selectedRow = ref(null);
const showForme = ref(false);
const api = inject('api') 
const loading=ref(true)
const popupStore = usePopupStore()
const dataPaie=ref([])
const search=ref('')
const headersBase = [
  { align: 'start', sortable: false },
  { title: '#', value: 'index', sortable: false },
];
const 
  header_paie=ref(
    [
      ...headersBase, 
  { key: 'user_id', title: 'User ID' },
  { key: 'action', title: 'Action' },
  { key: 'entity_type', title: "Type d'entité" },
  { key: 'description', title: 'Description' },
  { key: 'old_value', title: 'Ancienne valeur' },
  { key: 'new_value', title: 'Nouvelle valeur' },
  { key: 'ip_address', title: 'Adresse IP' }, 
  { key: 'created_at', title: 'Date de création' }  
  ]

  )

const date_liste= ref([])

const showRow = (event, row) => {
  // selectedRow.value = ;
  selectedRow.value = [row.item ,  { "upload_date":  popupStore.selected_date }]   // données de la ligne cliquée
  showForme.value = true;         // ouvrir le formulaire
  // console.log("Ligne cliquée :", row.item);
};

const filteredMenu = computed(() => {
    const privilege = popupStore.user_access.access || '';
    if (!['admin', 'superadmin'].includes(privilege)) {
       return 'non Admin'
       
    } 
});

const fetch_all_activites = async () => {
  loading.value = true;
  // console.log(popupStore.user_access.access);
  
  try {
    // Construire l'URL avec paramètres query
    let url = `${api}/api/get_activite_list`;
    const params = new URLSearchParams(); 

    if ([...params].length > 0) {
      url += `?${params.toString()}`;
    }

    const response = await fetch(url);
    const json = await response.json();
    console.log("Réponse de l'API get_activite_list:", json);

    if (!response.ok) throw new Error(json.detail || "Erreur inconnue");

    // Nouvelle structure : data.users
    const capitalData = json.data?.users || [];
    // console.log(json.data.users);
    dataPaie.value = json.data.users;

    // Tu peux continuer à traiter capitalData ici...

  } catch (err) {
    console.log(err.message || "Erreur inconnue");
    console.error("Erreur fetch_all_activites:", err);

  } finally {
    loading.value = false;
  }
};
 
onMounted(async () => { 
  
    const access=popupStore.user_access.access
  if(access=='admin'){
    fetch_all_activites()
  } 
   
});
 
 
</script>

<style>

</style>