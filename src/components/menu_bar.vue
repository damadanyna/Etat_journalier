<template>
  <v-toolbar color=" " class="bg-transparent" :title="toolbarTitle">
    <!-- Badge date -->

      <div class="flex flex-row justify-end items-center space-x-4 mx-4" >
        <h3 class="mr-5 text-xl">Date d'arrêt</h3>

        <v-menu
        v-if="isCompte"
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
            v-for="date in filteredHistoryDates"
            :key="date.label"
            @click="() => selectDate(date.label, date.stat_compte)"
            role="button"
          >
            <div class="flex" :title="date.stat_of!='init'? 'Base non initialisé':''">
              <v-icon v-if="date.stat_compte !== 1 " class=" mr-2 text-red-700">mdi-database-alert</v-icon> 
              <v-icon v-else color="success" class=" mr-2">mdi-database-check</v-icon> 
              <v-list-item-title>{{ date.label }}</v-list-item-title>
            </div>
          </v-list-item>
        </v-list>
      </v-menu>

        <v-menu
        v-else
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
  @click="() => selectDateStatOf(date.label, date.stat_of)"
            role="button"
          >
            <div class="flex" :title="date.stat_of!='init'? 'Base non initialisé':''">
              <v-icon v-if="date.stat_of !== 'init'" class=" mr-2 text-red-700">mdi-database-alert</v-icon> 
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


    <!-- Menu change et esri export -->
    <v-btn 
      v-if="isEsriPage || isChangePage" 
      @click="handleExport" 
      prepend-icon="mdi-share-variant"
      :loading="exporting"
    >
      <template #prepend><v-icon color="success"></v-icon></template>
      <span class="text-md">Exporter</span>
    </v-btn>

    <!-- Menu export dav, dat, epr -->

    <v-menu v-else-if="isCompte" offset-y>
          <template v-slot:activator="{ props }">
            <v-btn v-bind="props" prepend-icon="mdi-share-variant">
              <template #prepend><v-icon color="success"></v-icon></template>
              <span class="text-md">Exporter</span>
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="exportDAT">
              <template #prepend><v-icon color="success">mdi-table</v-icon></template>
              <v-list-item-title style="font-size: 15px;">DAT</v-list-item-title>
            </v-list-item>
            <v-list-item @click="exportDAV">
              <template #prepend><v-icon color="success">mdi-chart-bar</v-icon></template>
              <v-list-item-title style="font-size: 15px;">DAV</v-list-item-title>
            </v-list-item>
            <v-list-item @click="exportEPR">
              <template #prepend><v-icon color="success">mdi-chart-line</v-icon></template>
              <v-list-item-title style="font-size: 15px;">EPR</v-list-item-title>
            </v-list-item>
            <v-list-item @click="exportDECAISSEMENT">
              <template #prepend><v-icon color="success">mdi-chart-line</v-icon></template>
              <v-list-item-title style="font-size: 15px;">DECAISSEMENT</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>

    <!-- Menu menu d'exportation -->
    <v-menu v-else offset-y  >
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
import { ref, watch, onMounted,inject,computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePopupStore } from '../stores'
import * as XLSX from 'xlsx'
import { useRouter } from 'vue-router'


const route = useRoute()
const api = inject('api') 
const selectedDate = ref('Chargement en cours...')
const menu = ref(false)
const popupStore = usePopupStore()
const exporting = ref(false)
const router = useRouter()

const historyDates  = ref([])


const isEsriPage = computed(() => route.path === '/app/esri')
const isChangePage = computed(() => route.path === '/app/change')
const isCompte = computed(() => route.path === '/app/dav')
const isSession = computed(() => route.path === '/app/session')
const isInitialise = computed(() => route.path === '/app/Initialise')
const isgenerale = computed(() => route.path === '/app/generale')


const toolbarTitle = computed(() => {
  if (isEsriPage.value) return 'ESRI'
  if (isChangePage.value) return 'Change'
  if (isCompte.value) return 'Encours Compte'
  if (isSession.value) return 'Gestion des utilisateurs'
  if (isInitialise.value) return 'Initialisation Compte'
  if (isgenerale.value) return 'Vue'

  return 'Encours des crédits'
})


const handleExport = () => {
  if (isEsriPage.value) {
    exportEsriData()
  } else if (isChangePage.value) {
    exportChangeData()
  }
}


const exportEsriData = async () => {
  exporting.value = true
  try {
    window.dispatchEvent(new CustomEvent('export-esri-data'))
  } catch (error) {
    console.error('Erreur export ESRI:', error)
  } finally {
    exporting.value = false
  }
}

const exportChangeData = async () => {
  exporting.value = true
  try {
    window.dispatchEvent(new CustomEvent('export-change-data'))
  } catch (error) {
    console.error('Erreur export change:', error)
  } finally {
    exporting.value = false
  }
}


const exportDAT = () => {
  exporting.value = true
  console.log('Export DAT déclenché')
  window.dispatchEvent(new CustomEvent('export-dav-data', { detail: { type: 'DAT' } }))
}

const exportDAV = () => {
  exporting.value = true
  console.log('Export DAV déclenché')
  window.dispatchEvent(new CustomEvent('export-dav-data', { detail: { type: 'DAV' } }))
}

const exportEPR = () => {
  exporting.value = true
  console.log('Export EPR déclenché')
  window.dispatchEvent(new CustomEvent('export-dav-data', { detail: { type: 'EPR' } }))
}
const exportDECAISSEMENT = () => {
  exporting.value = true
  console.log('Export decaissement déclenché')
  window.dispatchEvent(new CustomEvent('export-dav-data', { detail: { type: 'DECAISSEMENT' } }))
}

// 🗓️ Importation de la date
const date_last_import_file = ref('')

const get_last_import_file = async () => {
  try {
    const response = await fetch(`${api}/api/get_last_import_file`, {
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



const filteredHistoryDates = computed(() => {
  return historyDates.value
})


const formatDateString = (rawDate) => {
  if (!/^\d{8}$/.test(rawDate)) return null
  return `${rawDate.slice(0, 4)}-${rawDate.slice(4, 6)}-${rawDate.slice(6, 8)}`
}

 onMounted(() => {
    (async () => {
      historyDates.value = await fetchData(`${api}/api/history_insert`)
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

async function selectDate(date,stat_compte) {
  
  selectedDate.value = date
  popupStore.selected_date = date
  popupStore.selected_date_stat_compte = stat_compte
  localStorage.setItem("selectedTable", date) // <-- Ajout ici

  menu.value = false
   
 if (isCompte.value) {
    if (stat_compte === 0) {
      router.push({ name: 'Initialise', query: { label: date } })
    } else {
      window.dispatchEvent(new CustomEvent('table-date-selected', { detail: { date, stat_compte } }))
    }
  }
}  
async function selectDateStatOf(date, stat_of) {
  selectedDate.value = date

  // 🔹 Met à jour le store Pinia
  popupStore.selected_date = date
  popupStore.selected_date_stat_of = stat_of

  // 🔹 Ferme le menu
  menu.value = false

  // 🔹 Émet un événement global
  window.dispatchEvent(new CustomEvent('table-date-stat-of-selected', {
    detail: { date, stat_of }
  }))
}



watch(historyDates, (val) => {
  if (Array.isArray(val) && val.length > 0) {
    // Trie les dates du plus récent au plus ancien
    const sorted = [...val].sort((a, b) => b.label.localeCompare(a.label))
    const lastDate = sorted[0].label
    const lastStatCompte = sorted[0].stat_compte

    selectedDate.value = lastDate
    popupStore.selected_date = lastDate
    popupStore.selected_date_stat_compte = lastStatCompte
    localStorage.setItem("selectedTable", lastDate)

    // Émet l'événement pour synchroniser la sélection
    if (isCompte.value) {
      window.dispatchEvent(new CustomEvent('table-date-selected', { detail: { date: lastDate, stat_compte: lastStatCompte } }))
    }
    console.log("📅 Dernière date sélectionnée automatiquement :", lastDate)
  }
}, { immediate: true })
</script>

<style>
.green_transparent {
  background-color: #00dc54a4;
}
</style>
