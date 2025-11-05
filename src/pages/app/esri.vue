<template>
  <v-container class="esri-container"  fluid>
    
    <v-row class="mb-4">
      <v-col cols="12" md="3">
        <v-text-field
          v-model="dateDebut"
          label="Date début (YYYYMMDD)"
          outlined
          dense
        />
      </v-col>

      <v-col cols="12" md="3">
        <v-text-field
          v-model="dateFin"
          label="Date fin (YYYYMMDD)"
          outlined
          dense
        />
      </v-col>

  

      <v-col cols="12" md="3" class="d-flex align-center">
        <v-btn
          color="primary"
          @click="fetchEsriData"
          :loading="loading"
          class="mr-2"
        >
          Charger les données
        </v-btn>
        
       
      </v-col>
    </v-row>

    <!-- Message d'état -->
    <v-alert
      v-if="message"
      :type="status === 'error' ? 'error' : (status === 'warning' ? 'warning' : 'success')"
      border="left"
      dark
      class="mb-4"
    >
      {{ message }}
    </v-alert>
    <v-card v-if="status === 'success' && bilan.length" class="mt-4 pa-4" outlined>
      <v-list>
        <v-list-item
          v-for="(item, index) in bilan"
          :key="index"
        >
          <v-list-item-content>
            <v-list-item-title>
              {{ item.Type }} : {{ item['Total Montant'].toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>

    <TablesEsri
      v-if="status === 'success' && rows.length"
      :columns="columns"
      :rows="rows"
      ref="tableEsriRef"
    />
  </v-container>
</template>


<script setup>
import { ref, onMounted, onUnmounted,inject } from "vue"
import axios from "axios"
import * as XLSX from "xlsx"
import TablesEsri from "@/components/esri/TableauEsri.vue"

const dateDebut = ref("")
const dateFin = ref("")
const loading = ref(false)
const exporting = ref(false)
const status = ref(null)
const message = ref("")
const columns = ref([])
const rows = ref([])
const tableEsriRef = ref(null)
const api = inject('api') 
const bilan = ref([])

const fetchEsriData = async () => {
  if (!dateDebut.value || !dateFin.value) {
    status.value = "error"
    message.value = "Veuillez remplir toutes les informations."
    return
  }
  
  loading.value = true
  status.value = null
  message.value = ""

  try {
    const res = await axios.post(
      `${api}/api/esri/create_esri_precompute`,
      null,
      {
        params: {
          date_debut: dateDebut.value,
          date_fin: dateFin.value,
        },
      }
    )


    if (res.status === "error") {
      
      status.value = "error"
      message.value = data.message || "Erreur lors du chargement des données."
      return
    }

    const data = res.data
    status.value = data.status
    message.value = data.message
    columns.value = data.columns || []
    rows.value = data.rows || []
    bilan.value = data.bilan || []

   localStorage.setItem(
  "esriData",
  JSON.stringify({
    dateDebut: dateDebut.value,
    dateFin: dateFin.value,
    status: status.value,
    message: message.value,
  })
)

  } catch (err) {
    console.error("Erreur lors du chargement des données ESRI:", err)
    if (err.response && err.response.data && err.response.data.message) {
      message.value = err.response.data.message
    } else {
      message.value = "Erreur serveur ou réseau."
    }

    status.value = "error"
  } 
  finally {
    loading.value = false
  }
}


const exportToExcel = () => {
  if (!rows.value.length || !dateDebut.value || !dateFin.value) {
    message.value = "Aucune donnée à exporter ou dates manquantes."
    status.value = "error"
    return
  }

  exporting.value = true

  try {
    const dataToExport = rows.value.map(row => {
      const exportedRow = {}
      columns.value.forEach(col => {
        exportedRow[col] = row[col] || ""
      })
      return exportedRow
    })

    const wb = XLSX.utils.book_new()
    
    const ws = XLSX.utils.json_to_sheet(dataToExport)
    
    XLSX.utils.book_append_sheet(wb, ws, "Données ESRI")
    
    const fileName = `esri_${dateDebut.value}_${dateFin.value}.xlsx`
    
    XLSX.writeFile(wb, fileName)
    
    message.value = "Export Excel réussi !"
    status.value = "success"
    
  } catch (error) {
    console.error("Erreur lors de l'export Excel:", error)
    message.value = "Erreur lors de l'export Excel."
    status.value = "error"
  } finally {
    exporting.value = false
  }
}

const handleExportEvent = () => {
  exportToExcel()
}

onMounted(() => {
  const saved = localStorage.getItem("esriData")
  if (saved) {
    const parsed = JSON.parse(saved)
    dateDebut.value = parsed.dateDebut || ""
    dateFin.value = parsed.dateFin || ""
    
  }

  window.addEventListener('export-esri-data', handleExportEvent)
})

onUnmounted(() => {
  window.removeEventListener('export-esri-data', handleExportEvent)
})
</script>

<style scoped>
.esri-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
}
.esri-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Edge (basé sur Chromium) */
}
</style>