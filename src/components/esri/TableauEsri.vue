<template>
  <div class="table-wrapper">
    <div class="table-search-bar">
      <v-text-field
        v-model="search"
        label="Rechercher"
        clearable
        dense
        hide-details
      />
    </div>

    <div class="table-scroll">
      <v-data-table
        :headers="headers"
        :items="rows"
        :items-per-page="itemsPerPage"
        :page.sync="page"
        class="elevation-1 fixed-header-table"
        :search="search"
        dense
        fixed-header
        height="600px"
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
import { ref, computed, watch } from "vue"

const props = defineProps({
  columns: {
    type: Array,
    required: true
  },
  rows: {
    type: Array,
    required: true
  }
})

const search = ref("")
const page = ref(1)
const itemsPerPage = ref(20)

const headers = computed(() =>
  props.columns.map(col => ({
    title: col,
    key: col
  }))
)

const pageCount = computed(() =>
  Math.ceil(props.rows.length / itemsPerPage.value)
)

watch(
  () => props.rows,
  () => (page.value = 1)
)
</script>

<style scoped>
.table-wrapper {
   display: flex;
  flex-direction: column;
  width: 100%;
  overflow: hidden;
  max-width: 100%;
  height: 900px;
}

/* 🔍 Barre de recherche fixée */
.table-search-bar {
  position: sticky;
  top: 0;
  z-index: 20;
  background-color: #121212; /* couleur fond selon ton thème */
  padding: 8px;
  border-bottom: 1px solid #333;
}

/* 📊 Tableau avec zone scrollable */
.table-scroll {
  flex: 1;
  overflow-y: auto;
}

/* 📌 Rendre l'en-tête du tableau fixe */
.fixed-header-table ::v-deep(.v-data-table__wrapper) {
  overflow-y: auto;
  max-height: 500px;
}

.fixed-header-table ::v-deep(th) {
  position: sticky;
  top: 0;
  background-color: #1e1e1e; /* couleur header */
  z-index: 15;
}
</style>
