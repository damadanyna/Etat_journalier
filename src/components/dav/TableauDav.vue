<template>
  <div class="table-container">
    <!-- 🔍 Barre de recherche fixée -->
    <div class="table-search-bar">
      <v-text-field
        v-model="search"
        label="Rechercher"
        clearable
        dense
        hide-details
      />
    </div>

    <!-- 📊 Zone défilable -->
    <div class="table-content">
      <v-data-table
        :headers="headers"
        :items="items"
        :items-per-page="itemsPerPage"
        :page.sync="page"
        class="elevation-1 fixed-header-table"
        :search="search"
        dense
        fixed-header
        height="100%"
        hide-default-footer
      >
        <template v-slot:no-data>
          <v-alert type="info" border="left" color="blue" dark>
            Aucune donnée trouvée
          </v-alert>
        </template>
      </v-data-table>
    </div>

    <!-- 📄 Pagination toujours visible -->
    <div class="table-pagination">
      <v-pagination
        v-model="page"
        :length="pageCount"
        circle
        class="my-2"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from "vue"
import axios from "axios"
import * as XLSX from "xlsx"

const props = defineProps({
  tableName: {
    type: String,
    required: true
  }
})

const headers = ref([])
const items = ref([])
const search = ref("")
const page = ref(1)
const itemsPerPage = ref(20)

const pageCount = computed(() =>
  Math.ceil(items.value.length / itemsPerPage.value)
)

const fetchTableData = async (tableName) => {
  if (!tableName) {
    items.value = []
    headers.value = []
    return
  }
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/dav/${tableName}`)
    items.value = res.data.data || []
    headers.value = (res.data.columns || []).map(col => ({
      title: col,
      key: col
    }))
    page.value = 1
  } catch (err) {
    console.error("Erreur lors du chargement de la table:", err)
  }
}

const exportToExcel = () => {
  if (!items.value.length) {
    alert("Aucune donnée à exporter")
    return
  }
  const dataToExport = items.value.map(row => {
    const exportedRow = {}
    headers.value.forEach(header => {
      exportedRow[header.title] = row[header.key] || ""
    })
    return exportedRow
  })
  const wb = XLSX.utils.book_new()
  const ws = XLSX.utils.json_to_sheet(dataToExport)
  XLSX.utils.book_append_sheet(wb, ws, "DAV Data")
  XLSX.writeFile(wb, `dav_${props.tableName}.xlsx`)
}

const handleExportEvent = (event) => {
  if (event.detail.type === "DAV") exportToExcel()
}

onMounted(() => {
  window.addEventListener("export-dav-data", handleExportEvent)
})
onUnmounted(() => {
  window.removeEventListener("export-dav-data", handleExportEvent)
})

watch(() => props.tableName, fetchTableData, { immediate: true })
</script>

<style scoped>
.table-container {
  display: flex;
  flex-direction: column;
  height: 100vh; /* 🔹 Prend toute la hauteur visible */
  width: 100%;
  overflow: hidden; /* Évite le scroll global */
}

.table-search-bar {
  flex: 0 0 auto;
  position: sticky;
  top: 0;
  z-index: 30;
  padding: 8px;
  border-bottom: 1px solid #333;
  background-color: #1e1e1e;
}

.table-content {
  flex: 1 1 auto;
  overflow-y: auto; /* 🔹 Seule cette partie défile */
  background-color: #121212;
}

.table-pagination {
  flex: 0 0 auto;
  position: sticky;
  bottom: 0;
  background-color: #1e1e1e;
  border-top: 1px solid #333;
  display: flex;
  justify-content: center;
  padding: 8px 0;
}

.fixed-header-table ::v-deep(th) {
  position: sticky;
  top: 0;
  background: linear-gradient(180deg, #1e1e1e 0%, #2a2a2a 100%);
  font-weight: 600;
  text-transform: uppercase;    
  letter-spacing: 0.5px;
  border-bottom: 2px solid #444; 
  border-right: 1px solid #333;
  padding: 10px 12px;
  z-index: 15;
  white-space: nowrap;
}

.fixed-header-table ::v-deep(td) {
  border-bottom: 1px solid #333;
  padding: 8px 12px;
  font-size: 14px;
}

.fixed-header-table ::v-deep(tr:hover td) {
  cursor: pointer;
  background-color: #2a2a2a;
}
</style>
