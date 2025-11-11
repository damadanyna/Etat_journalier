<template>
  <div class="table-wrapper">
    <div class="table-search-bar">
      <v-text-field
        v-model="search"
        label="Rechercher"
        clearable
        dense
        hide-details
        class="mx-4 mb-2"
      />
    </div>

    <div class="table-scroll">
      <v-data-table
        :headers="headers"
        :items="rows"
        :items-per-page="itemsPerPage"
        :page.sync="page"
        :search="search"
        class="elevation-1 fixed-header-table"
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
          <v-alert type="info" border="left" color="green" dark>
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

.table-search-bar {
  position: sticky;
  top: 0;
  z-index: 20;
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

</style>
