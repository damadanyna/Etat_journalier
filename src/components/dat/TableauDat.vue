<template>
  <div class="table-wrapper">
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

    <!-- 📊 Zone scrollable -->
    <div class="table-scroll">
      <v-data-table
        :headers="headers"
        :items="items"
        :items-per-page="itemsPerPage"
        :page.sync="page"
        class="elevation-1 fixed-header-table"
        :search="search"
        dense
        fixed-header
        height="700px"
      >
        <template v-slot:footer>
          <v-pagination
            v-model="page"
            :length="pageCount"
            circle
            class="my-2"
          />
        </template>

        <template v-slot:no-data>
          <v-alert type="info" border="left" color="blue" dark>
            Aucune donnée trouvée
          </v-alert>
        </template>
      </v-data-table>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed,inject } from "vue"
import axios from "axios"

const props = defineProps({
  tableName: {
    type: String,
    required: true
  }
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

const fetchTableData = async (tableName) => {
  if (!tableName) {
    items.value = []
    headers.value = []
    return
  }
  try {
    const res = await axios.get(`${api}/api/dat/${tableName}`)
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

watch(() => props.tableName, fetchTableData, { immediate: true })
</script>

<style scoped>
.table-wrapper {
  display: flex;
  flex-direction: column;
  height: 900px;
  width: 100%;
  background-color: transparent;
  
}

.table-search-bar {
  position: sticky;
  top: 0;
  z-index: 30;
  padding: 8px;
  border-bottom: 1px solid #333;
}

.table-scroll {
  flex: 1;
  overflow-y: auto;
}

.fixed-header-table ::v-deep(.v-data-table__wrapper) {
  overflow-y: auto;
  max-height: 500px;
}

.fixed-header-table ::v-deep(th) {
  position: sticky;
  top: 0;
  background: linear-gradient(180deg, #1e1e1e 0%, #2d2d2d 100%); 
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
  background-color: #181818; /* différence nette avec les headers */
  color: #dcdcdc;
  border-bottom: 1px solid #333;
  padding: 8px 12px;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.fixed-header-table ::v-deep(tr:hover td) {
  background-color: #2a2a2a;
  cursor: pointer;
}
</style>
