<template>
  <v-container fluid class="pa-0 full-container">
    <v-card
      class="pa-8 rounded-0 elevation-2 fade-in full-card"
      flat
    >
      
      <!-- FORMULAIRE -->
      <v-row dense class="px-4">
        <v-col cols="12" sm="3">
          <v-select
            v-model="typeTable"
            :items="['all', 'dav', 'dat', 'epr']"
            label="Type de Table"
            variant="outlined"
            rounded="lg"
            density="comfortable"
            required
          />
        </v-col>

        <v-col cols="12" sm="3">
          <v-text-field
            v-model="agence"
            label="Agence (code ou 'all')"
            variant="outlined"
            rounded="lg"
            clearable
            density="comfortable"
          />
        </v-col>

        <template v-if="!isAllAgence">
          <v-col cols="12" sm="2">
            <v-text-field
              v-model="dateDebut"
              label="Date début"
              placeholder="YYYYMMDD"
              variant="outlined"
              rounded="lg"
              clearable
              density="comfortable"
            />
          </v-col>

          <v-col cols="12" sm="2">
            <v-text-field
              v-model="dateFin"
              label="Date fin"
              placeholder="YYYYMMDD"
              variant="outlined"
              rounded="lg"
              clearable
              density="comfortable"
            />
          </v-col>
        </template>

        <template v-else>
          <v-col cols="12" sm="2">
            <v-text-field
              v-model="singleDate"
              label="Date unique"
              placeholder="YYYYMMDD"
              variant="outlined"
              rounded="lg"
              clearable
              density="comfortable"
            />
          </v-col>
        </template>
      </v-row>

      <!-- BOUTON -->
      <div class="text-center mt-6">
        <v-btn
          color="primary"
          size="large"
          rounded="lg"
          :loading="loading"
          @click="rechercher"
          class="px-8"
        >
          <v-icon left>mdi-magnify</v-icon>
           recherche
        </v-btn>
      </div>

      <!-- SELECTION DES COLONNES PAR TYPE -->
      <div v-if="hasResults" class="d-flex flex-column mb-4 px-2">
  <span class="font-weight-bold mb-3">Colonnes à afficher :</span>
  
  <div class="d-flex flex-wrap gap-4">
    <!-- Colonnes pour DATE & AGENCE -->
<template v-if="(infoDav.length || infoDat.length || infoEpr.length)">
  <div class="column-group">
    <div class="group-title mb-2" style="background:#424242; color:white;">
      Info (Date & Agence)
    </div>

    <div class="d-flex flex-wrap gap-2">
      <v-checkbox
        v-for="col in ['date','agence']"
        :key="col"
        v-model="visibleColumns.info"
        :label="col.toUpperCase()"
        :value="col"
        density="compact"
        hide-details
        class="column-checkbox"
      />
    </div>
  </div>
</template>

    <!-- Colonnes pour DAV -->
    <template v-if="visibleTables.includes('dav') && resultsDav.length">
      <div class="column-group">
        <div class="group-title group-title-dav mb-2">DAV</div>
        <div class="d-flex flex-wrap gap-2">
          <v-checkbox
            v-for="header in headersDav"
            :key="header.key"
            v-model="visibleColumns.dav"
            :label="header.title"
            :value="header.key"
            density="compact"
            hide-details
            class="column-checkbox"
          />
        </div>
      </div>
    </template>

    <!-- Colonnes pour DAT -->
    <template v-if="visibleTables.includes('dat') && resultsDat.length">
      <div class="column-group">
        <div class="group-title group-title-dat mb-2">DAT</div>
        <div class="d-flex flex-wrap gap-2">
          <v-checkbox
            v-for="header in headersDat"
            :key="header.key"
            v-model="visibleColumns.dat"
            :label="header.title"
            :value="header.key"
            density="compact"
            hide-details
            class="column-checkbox"
          />
        </div>
      </div>
    </template>

    <!-- Colonnes pour EPR -->
    <template v-if="visibleTables.includes('epr') && resultsEpr.length">
      <div class="column-group">
        <div class="group-title group-title-epr mb-2">EPR</div>
        <div class="d-flex flex-wrap gap-2">
          <v-checkbox
            v-for="header in headersEpr"
            :key="header.key"
            v-model="visibleColumns.epr"
            :label="header.title"
            :value="header.key"
            density="compact"
            hide-details
            class="column-checkbox"
          />
        </div>
      </div>
    </template>
  </div>
</div>

     <!-- SELECTION DES TABLEAUX -->
<div class="d-flex flex-column mb-4 px-2">
  <span class="font-weight-bold mb-3">Tableaux à afficher :</span>
  <div class="d-flex flex-wrap align-center gap-3">
    <v-checkbox
      v-for="type in ['dav', 'dat', 'epr']"
      :key="type"
      v-model="visibleTables"
      :label="type.toUpperCase()"
      :value="type"
      density="compact"
      hide-details
      class="table-checkbox-styled"
      :class="`table-checkbox-${type}`"
    />
  </div>
</div>

      <!-- MESSAGE -->
      <v-alert
        v-if="message"
        :type="messageType"
        class="mt-2 mx-2"
        rounded="lg"
        border="start"
        elevation="1"
        density="compact"
        style="font-size: 0.95rem; padding: 8px 16px;"
      >
        {{ message }}
      </v-alert>

      <!-- TABLEAUX -->
      <v-row dense class="mt-8">
         <v-col cols="12" md="2">
            <v-data-table
              
              :headers="headersInfo.filter(h => visibleColumns.info.includes(h.key))"

              :items="(infoDav.length ? infoDav : infoDat.length ? infoDat : infoEpr).map(item => {
                const filtered = {}
                visibleColumns.info.forEach(col => filtered[col] = item[col])
                return filtered
              })"

              density="comfortable"
              hide-default-footer
              :items-per-page="-1"

              fixed-header
              class="elevation-2 fade-in data-table-fixed1"
            >
              <template #top>
                <h3 class="text-h6 font-weight-bold mb-2 table-title">Date & Agence</h3>
              </template>
            </v-data-table>
          </v-col>
        <!-- DAV -->

        <v-col
          v-if="visibleTables.includes('dav') && Array.isArray(resultsDav) && resultsDav.length"
          cols="12"
          md="3"
        >
          <v-data-table
            class="elevation-2 fade-in full-table table-dav data-table-fixed"
            :headers="headersDav.filter(h => visibleColumns.dav.includes(h.key))"
            :items="resultsDav.map(item => {
              const filtered = {};
              visibleColumns.dav.forEach(col => filtered[col] = item[col]);
              return filtered;
            })"
            density="comfortable"
            hide-default-footer
            :items-per-page="-1"
            fixed-header
          >
            <template #top>
              <h3 class="text-h6 font-weight-bold mb-2 table-title table-title-dav">DAV</h3>
            </template>
          </v-data-table>
        </v-col>

        <!-- DAT -->
        <v-col
          v-if="visibleTables.includes('dat') && Array.isArray(resultsDat) && resultsDat.length"
          cols="12"
          md="3"
        >
          <v-data-table
            class="elevation-2 fade-in full-table table-dat data-table-fixed"
            :headers="headersDat.filter(h => visibleColumns.dat.includes(h.key))"
            :items="resultsDat.map(item => {
              const filtered = {};
              visibleColumns.dat.forEach(col => filtered[col] = item[col]);
              return filtered;
            })"
            density="comfortable"
            hide-default-footer
            :items-per-page="-1"
            fixed-header
          >
            <template #top>
              <h3 class="text-h6 font-weight-bold mb-2 table-title table-title-dat">DAT</h3>
            </template>
          </v-data-table>
        </v-col>

        <!-- EPR -->
        <v-col
          v-if="visibleTables.includes('epr') && Array.isArray(resultsEpr) && resultsEpr.length"
          cols="12"
          md="3"
        >
          <v-data-table
            class="elevation-2 fade-in full-table table-epr data-table-fixed"
            :headers="headersEpr.filter(h => visibleColumns.epr.includes(h.key))"
            :items="resultsEpr.map(item => {
              const filtered = {};
              visibleColumns.epr.forEach(col => filtered[col] = item[col]);
              return filtered;
            })"
            density="comfortable"
            hide-default-footer
            :items-per-page="-1"
            fixed-header
          >
            <template #top>
              <h3 class="text-h6 font-weight-bold mb-2 table-title table-title-epr">EPR</h3>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, inject, computed } from "vue"
import axios from "axios"

const api = inject("api")

const typeTable = ref("all")
const agence = ref("")
const singleDate = ref("")
const dateDebut = ref("")
const dateFin = ref("")

const loading = ref(false)
const message = ref("")
const messageType = ref("info")
const resultsDav = ref([])
const resultsDat = ref([])
const resultsEpr = ref([])
const infoDav = ref([])
const infoDat = ref([])
const infoEpr = ref([])

// Headers séparés par type
const headersDav = ref([])
const headersDat = ref([])
const headersEpr = ref([])
const headersInfo = computed(() => [
  { title: 'Date', key: 'date' },
  { title: 'Agence', key: 'agence' }
])

// Colonnes visibles séparées par type
const visibleColumns = ref({
    info: ['date', 'agence'], // Par défaut, Date et Agence sont sélectionnées

  dav: [],
  dat: [],
  epr: []
})

const visibleTables = ref(['dav', 'dat', 'epr'])

const isAllAgence = computed(() => agence.value === 'all')
const hasResults = computed(() => 
  resultsDav.value.length > 0 || resultsDat.value.length > 0 || resultsEpr.value.length > 0
)


const generateHeaders = (data) => {
  if (!data.length) return []

  return Object.keys(data[0]).map(key => ({
    title: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    key,
    align: key.includes('total') || key.includes('montant') ? 'end' : 'start'
  }))
}


const rechercher = async () => {
  loading.value = true
  message.value = ""
  resultsDav.value = []
  resultsDat.value = []
  resultsEpr.value = []
  headersDav.value = []
  headersDat.value = []
  headersEpr.value = []
  
  // Réinitialiser les colonnes visibles
  visibleColumns.value = {info: ['date', 'agence'], dav: [], dat: [], epr: [] }

  try {
    let types = typeTable.value === 'all' ? ['dav', 'dat', 'epr'] : [typeTable.value]

    for (const type of types) {
      const res = await axios.get(`${api}/api/resume/total-produit/${type}`, {
        params: {
          agence: agence.value,
          single_date_if_all: singleDate.value,
          date_debut: dateDebut.value,
          date_fin: dateFin.value,
        }
      })
      
      if (Array.isArray(res.data) && res.data.length) {
  if (type === 'dav') {
    infoDav.value = res.data.map(item => item.date_agence)
    resultsDav.value = res.data.map(item => item.data)
    headersDav.value = generateHeaders(resultsDav.value)
    visibleColumns.value.dav = headersDav.value.map(h => h.key)
  }

  if (type === 'dat') {
    infoDat.value = res.data.map(item => item.date_agence)
    resultsDat.value = res.data.map(item => item.data)
    headersDat.value = generateHeaders(resultsDat.value)
    visibleColumns.value.dat = headersDat.value.map(h => h.key)
  }

  if (type === 'epr') {
    infoEpr.value = res.data.map(item => item.date_agence)
    resultsEpr.value = res.data.map(item => item.data)
    headersEpr.value = generateHeaders(resultsEpr.value)
    visibleColumns.value.epr = headersEpr.value.map(h => h.key)
  }
}

    }

    const total =
      resultsDav.value.length +
      resultsDat.value.length +
      resultsEpr.value.length

    if (total) {
      messageType.value = "success"
      message.value = `Résultats trouvés : ${total}`
    } else {
      messageType.value = "info"
      message.value = "Aucun résultat trouvé."
    }
  } catch {
    messageType.value = "error"
    message.value = "❌ Une erreur est survenue lors de la recherche."
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Vos styles existants restent les mêmes */
.full-container {
  width: 100%;
  height: 100vh;
  overflow-y: auto;
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
  padding: 0 10px; 
}

.full-card {
  border-radius: 0 !important;
}

/* Styles uniformes pour tous les tableaux */
.data-table-fixed {
  width: 100%;
} 

.data-table-fixed1 {
  width: 100%;
}

.table-dav,
.table-dat,
.table-epr {
  width: 100%;
  border-radius: 8px;
}

/* Styles communs pour toutes les cellules de tableau */
:deep(.table-dav .v-data-table__td),
:deep(.table-dav .v-data-table__th),
:deep(.table-dat .v-data-table__td),
:deep(.table-dat .v-data-table__th),
:deep(.table-epr .v-data-table__td),
:deep(.table-epr .v-data-table__th) {
  padding-left: 8px !important;
  padding-right: 8px !important;
  width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Assurer que tous les tableaux ont la même hauteur et largeur */
:deep(.v-data-table) {
  table-layout: fixed;
  width: 100%;
}

:deep(.v-data-table__wrapper) {
  width: 100%;
}

.fade-in {
  animation: fadeIn 0.5s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.table-title {
  text-align: center;
  padding: 8px 0;
  color: #fff;
  border-radius: 4px;
}

.table-title-dat {
  background-color: #43a047;
}

.table-title-epr {
  background-color: #fbc02d;
}

.table-title-dav {
  background-color: #1976d2;
}

/* Bordures colorées pour chaque tableau */
.table-dav {
  border: 2px solid #1976d2;
}

.table-dat {
  border: 2px solid #43a047;
}

.table-epr {
  border: 2px solid #fbc02d;
}

.column-group {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  min-width: 200px;
}

.group-title {
  font-weight: bold;
  font-size: 0.9rem;
  padding: 4px 8px;
  border-radius: 4px;
  text-align: center;
}

.group-title-dav {
  background-color: #1976d2;
}

.group-title-dat {
  background-color: #43a047;
}

.group-title-epr {
  background-color: #fbc02d;
}

.column-checkbox {
  min-width: 140px;
  margin: 2px 0;
}

/* Espacement entre les groupes */
.gap-4 {
  gap: 16px;
}

.gap-2 {
  gap: 8px;
}


</style>