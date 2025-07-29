<template>
  <v-toolbar color=" " class="bg-transparent" title="Encours des crédits">
    <!-- Badge date -->
    <div class="flex items-center gap-1 green_transparent mr-2 px-5 rounded-md">
      <v-icon icon="mdi-database" />
      <span v-if="date_last_import_file !== ''" title="Dernière importation">
        {{ formatDateString(date_last_import_file) }}
      </span>
      <span v-else>Récupération ...</span>
    </div>

    <!-- ✅ Bouton menu d'exportation -->
    <v-menu offset-y>
      <template v-slot:activator="{ props }">
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
    <v-btn stacked>
      <v-avatar image="https://avatars.githubusercontent.com/u/60171474?v=4"></v-avatar>
    </v-btn>
  </v-toolbar>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { usePopupStore } from '../stores'
import * as XLSX from 'xlsx'

const popupStore = usePopupStore()

// 🗓️ Importation de la date
const date_last_import_file = ref('')

const get_last_import_file = async () => {
  try {
    const response = await fetch('http://192.168.1.212:8000/api/get_last_import_file', {
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

onMounted(() => get_last_import_file())

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
</script>

<style>
.green_transparent {
  background-color: #00dc54a4;
}
</style>
