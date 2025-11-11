<template>
  <div class="table-container">
    <div class="table-search-bar">
      <v-text-field
        v-model="search"
        label="Rechercher"
        clearable
        dense
        hide-details
      />
    </div>

    <div class="table-main">
      <v-data-table
        :headers="headers"
        :items="items"
        :items-per-page="itemsPerPage"
        :page.sync="page"
        class="elevation-1 fixed-header-table"
        :search="search"
        dense
        fixed-header
        height="700px">
        <template v-slot:footer>
          <v-pagination
            v-model="page"
            :length="pageCount"
            circle
            class="my-2"
          />
        </template>

        <template v-slot:no-data>
          <v-alert type="info" border="left" color="green" dark>
            Aucune donnée trouvée
          </v-alert>
        </template>
      </v-data-table>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, inject } from "vue"
import axios from "axios"

const props = defineProps({
  tableName: { type: String, required: true }
})
const api = inject('api') 

const headers = ref([])
const items = ref([])
const search = ref("")
const page = ref(1)
const itemsPerPage = ref(20)

const pageCount = computed(() =>
  Math.ceil(items.value.length / itemsPerPage.value)
)

const paginatedItems = computed(() => {
  const start = (page.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return items.value.slice(start, end)
})

const fetchTableData = async (tableName) => {
  if (!tableName) {
    items.value = []
    headers.value = []
    return
  }
  try {
    const res = await axios.get(`${api}/api/dav/${tableName}`)
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

onMounted(() => fetchTableData(props.tableName))
watch(() => props.tableName, fetchTableData)
</script>

<style scoped>
.table-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow: hidden;
  max-width: 100%;
  height: 900px;
}

.table-search-bar {
  flex: 0 0 auto;
  padding: 8px;
  border-bottom: 1px solid #333;
  z-index: 10;
}

.table-main {
  flex: 1 1 auto;
  overflow-y: auto;
}

.fixed-header-table ::v-deep(th) {
  position: sticky;
  top: 0;
  background: linear-gradient(180deg, #1e1e1e 0%, #2d2d2d 100%); /* ✅ Fond différent et contrasté */
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #444;
  border-right: 1px solid #333;
  padding: 10px 12px;
  z-index: 15;
  white-space: nowrap;
}

/* ✅ Lignes du tableau avec fond légèrement différent */
.fixed-header-table ::v-deep(td) {
  background-color: #181818; /* différence nette avec les headers */
  color: #dcdcdc;
  border-bottom: 1px solid #333;
  padding: 8px 12px;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

/* ✅ Effet au survol pour mieux distinguer la ligne active */
.fixed-header-table ::v-deep(tr:hover td) {
  background-color: #2a2a2a;
  cursor: pointer;
}
.table-scroll::-webkit-scrollbar {
  display: none; 
}
</style>
