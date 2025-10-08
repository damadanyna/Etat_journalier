<template>
  <v-toolbar color=" " class="bg-transparent" title="Encours des crédits">
    <!-- Badge date -->

      <div class="flex flex-row justify-end items-center space-x-4 mx-4" >
        <h3 class="mr-5 text-xl">Date d'arrêt</h3>

        <v-menu
          v-model="menu"
          close-on-content-click
          offset-y
          max-width="200"
          min-width="200"
        >
          <template #activator="{ props }">
            <v-btn v-bind="props" prepend-icon="mdi-calendar-range" variant="outlined">
              <template #prepend>
                <v-icon color="success" />
              </template>
              <span class="text-2xl">{{ selectedDate }}</span>
            </v-btn>
          </template>

        <v-list style="max-height: 200px; overflow-y: auto;">
          <v-list-item
            v-for="date in historyDates"
            :key="date.label"
            @click="() => selectDate(date.label)"
            role="button"
          >

          <div class="flex" :title="date.stat_of!='init'? 'Base non initialisé':''">
            
            <v-icon v-if="date.stat_of !== 'init'"   class=" mr-2 text-red-700">mdi-database-alert</v-icon> 
            <v-icon v-else color="success" class=" mr-2">mdi-database-check</v-icon> 
            <v-list-item-title>{{ date.label }}</v-list-item-title>
          </div>
          </v-list-item>
        </v-list>
        </v-menu>
      </div>
    <!-- <div class="flex items-center gap-1 green_transparent mr-2 px-5 rounded-md">
      <v-icon icon="mdi-database" />
      <span v-if="date_last_import_file !== ''" title="Dernière importation">
        {{ formatDateString(date_last_import_file) }}
      </span>
      <span v-else>Récupération ...</span>
    </div> -->

    <!-- ✅ Bouton menu d'exportation -->
    <v-menu offset-y  >
      <template v-slot:activator="{ props }" style=" margin: 0px 15px;">
        <v-btn v-bind="props" prepend-icon="mdi-share-variant">
          <template #prepend><v-icon color="success"></v-icon></template>
          <span class="text-md">Exporter</span>
        </v-btn>
      </template>

      <v-list>
        <v-list-item @click="exportToExcel_encours" >
          <template #prepend><v-icon color="success">mdi-file-chart</v-icon></template>
          <v-list-item-title style="font-size: 15px;">Encours</v-list-item-title>
        </v-list-item>

        <v-list-item @click="exportToExcel_LIMIT_AVM">
          <template #prepend><v-icon color="success">mdi-chart-bubble</v-icon></template>
          <v-list-item-title style="font-size: 15px;">Limit AVM</v-list-item-title>
        </v-list-item>

        <v-list-item @click="exportToExcel_LIMIT_CAUTION">
          <template #prepend><v-icon color="success">mdi-shield-check</v-icon></template>
          <v-list-item-title style="font-size: 15px;">Limit Caution</v-list-item-title>
        </v-list-item>

        <v-list-item @click="exportToExcel_remboursement">
          <template #prepend><v-icon color="success">mdi-cash-refund</v-icon></template>
          <v-list-item-title style="font-size: 15px;">État Remboursement</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <!-- Avatar à droite -->
     <user_btn_profil class=" mx-4"></user_btn_profil>
    <!-- <v-btn stacked>
      <v-icon icon="mdi mdi-account"></v-icon>
      <span class=" text-xs">daa</span>
    </v-btn> -->
  </v-toolbar>
</template>

<script setup>
import user_btn_profil from './user_btn_profil.vue'
import { ref, watch, onMounted } from 'vue'
import { usePopupStore } from '../stores'
import * as XLSX from 'xlsx'

const selectedDate = ref('Chargement en cours...')
const menu = ref(false)
const popupStore = usePopupStore()

const historyDates  = ref([])

// 🗓️ Importation de la date
const date_last_import_file = ref('')

const get_last_import_file = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/get_last_import_file', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })

    const data = await response.json()
    if (data?.response) {
      date_last_import_file.value = data.response.label
      popupStore.selected_date = data.response
    }
  } catch (error) {
    console.error("❌ Erreur :", error)
  }
}

const formatDateString = (rawDate) => {
  if (!/^\d{8}$/.test(rawDate)) return null
  return `${rawDate.slice(0, 4)}-${rawDate.slice(4, 6)}-${rawDate.slice(6, 8)}`
}

 onMounted(() => {
    (async () => {
      historyDates.value = await fetchData('http://127.0.0.1:8000/api/history_insert')
    })();
  get_last_import_file()
 })

// 📦 Données à exporter
const listes_encours_credits = ref([])
const listes_remboursement_credits = ref([])
const listes_limit_avm = ref([])
const listes_limit_caution = ref([])

watch(() => popupStore.encours_actual_data, (val) => {
  listes_encours_credits.value = val
}, { immediate: true })

watch(() => popupStore.remboursement_actual_data, (val) => {
  listes_remboursement_credits.value = val
}, { immediate: true })

watch(() => popupStore.limit_avm_actual_data, (val) => {
  listes_limit_avm.value = val
}, { immediate: true })

watch(() => popupStore.limit_caution_actual_data, (val) => {
  listes_limit_caution.value = val
}, { immediate: true })

// 📤 Fonction générique d’export
function exportToExcel(data, filenameBase, sheetName = 'Feuille1') {
  if (!data || data.length === 0) {
    alert('Aucune donnée à exporter')
    return
  }

  const date = new Date().toISOString().slice(0, 10)
  const filename = `${filenameBase}_${date}.xlsx`

  const worksheet = XLSX.utils.json_to_sheet(data)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)
  XLSX.writeFile(workbook, filename)
}

// 🎯 Fonctions spécifiques
const exportToExcel_encours = () => exportToExcel(listes_encours_credits.value, 'Encours', 'Encours')
const exportToExcel_remboursement = () => exportToExcel(listes_remboursement_credits.value, 'Etat_de_remboursement', 'Remboursement')
const exportToExcel_LIMIT_AVM = () => exportToExcel(listes_limit_avm.value, 'Limit_AVM', 'LIMIT_AVM')
const exportToExcel_LIMIT_CAUTION = () => exportToExcel(listes_limit_caution.value, 'Limit_Caution', 'LIMIT_CAUTION')

async function fetchData(baseUrl, date = null) {
  try {
    // Si une date est fournie, on l’ajoute à l’URL
    const url = date ? `${baseUrl}?date=${date}` : baseUrl

    const response = await fetch(url)
    if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`)

    const data = await response.json()
    return data.response.data
  } catch (error) {
    console.error('❌ Erreur de chargement :', error)
    return []
  }
}

async function selectDate(date) {
  
  selectedDate.value = date
  usePopupStore().selected_date.value = date
  menu.value = false
   

}


watch(historyDates, (val) => {
  if (Array.isArray(val) && val.length > 0) { 
    selectedDate.value = val[0].label
    console.log("📅 Date sélectionnée automatiquement :", selectedDate.value)
  }
}, { immediate: true })
</script>

<style>
.green_transparent {
  background-color: #00dc54a4;
}
</style>
