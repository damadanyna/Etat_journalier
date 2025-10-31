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
        height="500px"
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
import { ref, watch, computed } from "vue"
import axios from "axios"

// 🧩 Props : nom de table venant de dat.vue
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
const itemsPerPage = ref(10)

// Pagination dynamique
const pageCount = computed(() =>
  Math.ceil(items.value.length / itemsPerPage.value)
)

// 🔁 Chargement des données via API
const fetchTableData = async (tableName) => {
  if (!tableName) {
    items.value = []
    headers.value = []
    return
  }
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/dat/${tableName}`)
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

// 🧠 Recharger quand tableName change
watch(() => props.tableName, fetchTableData, { immediate: true })
</script>

<style scoped>
.table-wrapper {
  display: flex;
  flex-direction: column;
  height: 600px;
  width: 100%;
  background-color: transparent;
}

/* 🔍 Barre de recherche fixée */
.table-search-bar {
  position: sticky;
  top: 0;
  z-index: 30;
  padding: 8px;
  border-bottom: 1px solid #333;
}

/* 📊 Conteneur scrollable */
.table-scroll {
  flex: 1;
  overflow-y: auto;
}

/* 📌 En-tête du tableau fixe et stylé */
.fixed-header-table ::v-deep(.v-data-table__wrapper) {
  overflow-y: auto;
  max-height: 500px;
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


/* 🩶 Style des cellules */
.fixed-header-table ::v-deep(td) {
  border-bottom: 1px solid #333;
  padding: 8px 12px;
  font-size: 14px;
}

/* 🌗 Alternance des lignes */

/* 💡 Effet hover sur une ligne */
.fixed-header-table ::v-deep(tr:hover td) {
  cursor: pointer;
}
</style>
