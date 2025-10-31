<template>
  <v-container class="change-container" fluid>
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
          @click="fetchChangeData"
          :loading="loading"
          class="mr-2"
        >
          Charger les données
        </v-btn>

        
      </v-col>
    </v-row>

    <v-alert
      v-if="message"
      :type="status === 'error' ? 'error' : (status === 'warning' ? 'warning' : 'success')"
      border="left"
      dark
      class="mb-4"
    >
      {{ message }}
    </v-alert>

    <v-tabs v-if="hasData" v-model="activeTab" class="mb-4">
      <v-tab>Synthèse</v-tab>
      <v-tab>État</v-tab>
      <v-tab>Allocation</v-tab>
    </v-tabs>

    <v-window v-if="hasData" v-model="activeTab">
      <v-window-item>
        <TableauChange
          :columns="syntheseColumns"
          :rows="syntheseRows"
          title="Tableau de Synthèse"
        />
      </v-window-item>

      <v-window-item>
        <TableauChange
          :columns="etatColumns"
          :rows="etatRows"
          title="Tableau d'État"
        />
      </v-window-item>

      <v-window-item>
        <TableauChange
          :columns="allocationColumns"
          :rows="allocationRows"
          title="Tableau d'Allocation"
        />
      </v-window-item>
    </v-window>
  </v-container>
</template>

<script setup>
import { ref, computed,onMounted, onUnmounted } from "vue"
import axios from "axios"
import * as XLSX from "xlsx"
import { watch } from "vue"
import TableauChange from "@/components/change/TableauChange.vue"

const dateDebut = ref("")
const dateFin = ref("")
const loading = ref(false)
const exporting = ref(false)
const status = ref(null)
const message = ref("")
const activeTab = ref(0)

const syntheseRows = ref([])
const syntheseColumns = ref([])
const etatRows = ref([])
const etatColumns = ref([])
const allocationRows = ref([])
const allocationColumns = ref([])

const hasData = computed(() =>
  syntheseRows.value.length > 0 ||
  etatRows.value.length > 0 ||
  allocationRows.value.length > 0
)

const saveToLocalStorage = () => {
  const dataToSave = {
    dateDebut: dateDebut.value,
    dateFin: dateFin.value,
    status: status.value,
    message: message.value,
    synthese: syntheseRows.value,
    etat: etatRows.value,
    allocation: allocationRows.value,
  }
  localStorage.setItem("changeData", JSON.stringify(dataToSave))
}

const fetchChangeData = async () => {
  if (!dateDebut.value || !dateFin.value) {
    status.value = "error"
    message.value = "Veuillez remplir les dates de début et de fin."
    return
  }

  loading.value = true
  status.value = null
  message.value = ""

  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/change/generate_report`,
      null,
      {
        params: {
          date_debut: dateDebut.value,
          date_fin: dateFin.value,
        },
      }
    )

    const data = res.data
    status.value = data.status

    if (data.status === "success") {
      message.value = `Rapport généré avec succès pour la période ${dateDebut.value} - ${dateFin.value}`

      if (data.synthese?.length) {
        syntheseColumns.value = Object.keys(data.synthese[0])
        syntheseRows.value = data.synthese
      }

      if (data.etat?.length) {
        etatColumns.value = Object.keys(data.etat[0])
        etatRows.value = data.etat
      }

      if (data.allocation?.length) {
        allocationColumns.value = Object.keys(data.allocation[0])
        allocationRows.value = data.allocation
      }

      saveToLocalStorage()

    } else {
      message.value = data.message || "Erreur lors de la génération du rapport."
    }
  } catch (err) {
    console.error("Erreur lors du chargement des données Change:", err)
    status.value = "error"
  if (err.response?.data?.message) {
    message.value = err.response.data.message
  } else {
    message.value = "Erreur serveur ou réseau."
  }

}finally {
    loading.value = false
  }
}

const exportToExcel = () => {
  if (!hasData.value || !dateDebut.value || !dateFin.value) {
    message.value = "Aucune donnée à exporter ou dates manquantes."
    status.value = "error"
    return
  }

  exporting.value = true

  try {
    const wb = XLSX.utils.book_new()

    const addSheet = (rows, name) => {
      if (rows.length) {
        const ws = XLSX.utils.json_to_sheet(rows)
        XLSX.utils.book_append_sheet(wb, ws, name)
      }
    }

    addSheet(syntheseRows.value, "Synthèse")
    addSheet(etatRows.value, "État")
    addSheet(allocationRows.value, "Allocation")

    const fileName = `change_${dateDebut.value}_${dateFin.value}.xlsx`
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
    const saved = localStorage.getItem("changeData")
  if (saved) {
    const parsed = JSON.parse(saved)
    dateDebut.value = parsed.dateDebut || ""
    dateFin.value = parsed.dateFin || ""
    status.value = parsed.status || null
    message.value = parsed.message || ""
    syntheseRows.value = parsed.synthese || []
    etatRows.value = parsed.etat || []
    allocationRows.value = parsed.allocation || []
    if (parsed.synthese?.length) {
      syntheseColumns.value = Object.keys(parsed.synthese[0])
    }
    if (parsed.etat?.length) {
      etatColumns.value = Object.keys(parsed.etat[0])
    }
    if (parsed.allocation?.length) {
      allocationColumns.value = Object.keys(parsed.allocation[0])
    }
    
  }
  window.addEventListener('export-change-data', handleExportEvent)
})

onUnmounted(() => {
  window.removeEventListener('export-change-data', handleExportEvent)
})

watch(
  [syntheseRows, etatRows, allocationRows, dateDebut, dateFin],
  saveToLocalStorage,
  { deep: true }
)
</script>

<style scoped>
.change-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
}
</style>
