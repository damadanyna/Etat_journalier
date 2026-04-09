<template> 
  <v-card v-if="canViewHistory" flat style="background: transparent;" >
    <template #text>
      <v-text-field v-model="search" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line/>
    </template>
    <v-data-table  style="padding:0px 15px;" class="bg-transparent" :headers="header_paie" :items="dataPaie" :search="search" item-value="Numero_pret" item-key="id" fixed-header height="450px" :items-per-page="50" @click:row="showRow"> 
      <template #item.ID="{ item }"> {{ item.ID?.slice(0, 2) || '' }}</template>
      <template #item.index="{ index }"> {{ index + 1 }}</template>
      <template #item.created_at="{ item }"> {{ formatHistoryDate(item.created_at) }}</template>
    </v-data-table>
  </v-card> 
  <FormeViewPaie :data="selectedRow"  @close="selectedRow = null"  />
  <FolderViewerPaie :data="date_liste" v-if="!canViewHistory" />
</template>

<script setup>
import { usePopupStore } from '../../../stores';
import { watch, ref,inject,computed, onMounted, onBeforeUnmount} from 'vue'; 
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

const formatHistoryDate = (value) => {
  if (!value) {
    return ''
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  const months = [
    'Janvier',
    'Fevrier',
    'Mars',
    'Avril',
    'Mai',
    'Juin',
    'Juillet',
    'Aout',
    'Septembre',
    'Octobre',
    'Novembre',
    'Decembre',
  ]

  const day = String(date.getDate()).padStart(2, '0')
  const month = months[date.getMonth()]
  const year = date.getFullYear()
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')

  return `${day} ${month} ${year} a ${hours}h ${minutes}`
}

const showRow = (event, row) => {
  // selectedRow.value = ;
  selectedRow.value = [row.item ,  { "upload_date":  popupStore.selected_date }]   // données de la ligne cliquée
  showForme.value = true;         // ouvrir le formulaire
  // console.log("Ligne cliquée :", row.item);
};

const canViewHistory = computed(() => ['admin', 'superadmin'].includes(popupStore.user_access.access || ''))

const handleUserActivityUpdated = async () => {
  if (!canViewHistory.value) {
    return
  }

  await fetch_all_activites()
}

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

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    const json = await response.json();

    if (!response.ok) throw new Error(json.detail || "Erreur inconnue");

    dataPaie.value = json.data?.users || [];

  } catch (err) {
    console.log(err.message || "Erreur inconnue");
    console.error("Erreur fetch_all_activites:", err);

  } finally {
    loading.value = false;
  }
};
 
onMounted(async () => { 
  
  if (canViewHistory.value) {
    fetch_all_activites()
  }

  window.addEventListener('socket:user-activity-updated', handleUserActivityUpdated)
});

onBeforeUnmount(() => {
  window.removeEventListener('socket:user-activity-updated', handleUserActivityUpdated)
})
 
 
</script>

<style>

</style>