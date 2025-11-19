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
      
 <!-- ...dans le <template> juste avant <v-data-table> -->
<div v-if="headers.length" class="d-flex flex-wrap align-center mb-4 px-2">
  <span class="mr-3 font-weight-bold">Colonnes à afficher :</span>
  <v-checkbox
    v-for="header in headers"
    :key="header.key"
    v-model="visibleColumns"
    :label="header.title"
    :value="header.key"
    density="compact"
    hide-details
    class="mr-2"
  />
</div>
<div class="d-flex flex-wrap align-center mb-4 px-2">
  <span class="mr-3 font-weight-bold">Tableaux à afficher :</span>
  <v-checkbox
    v-for="type in ['dav', 'dat', 'epr']"
    :key="type"
    v-model="visibleTables"
    :label="type.toUpperCase()"
    :value="type"
    density="compact"
    hide-details
    class="mr-2"
  />
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

      <!-- TABLE -->
      <v-row dense class="mt-8">
        <!-- DAV -->
        <v-col
          v-if="visibleTables.includes('dav') && Array.isArray(resultsDav) && resultsDav.length"
          cols="12"
          md="4"
        >
          <v-data-table
            class="elevation-2 fade-in full-table table-dav"
            :headers="headers.filter(h => visibleColumns.includes(h.key))"
            :items="resultsDav.map(item => {
              const filtered = {};
              visibleColumns.forEach(col => filtered[col] = item[col]);
              return filtered;
            })"
            density="comfortable"
            height="400px"
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
          md="4"
        >
          <v-data-table
            class="elevation-2 fade-in full-table table-dat"
            :headers="headers.filter(h => visibleColumns.includes(h.key))"
            :items="resultsDat.map(item => {
              const filtered = {};
              visibleColumns.forEach(col => filtered[col] = item[col]);
              return filtered;
            })"
            density="comfortable"
            height="400px"
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
          md="4"
        >
          <v-data-table
            class="elevation-2 fade-in full-table table-epr"
            :headers="headers.filter(h => visibleColumns.includes(h.key))"
            :items="resultsEpr.map(item => {
              const filtered = {};
              visibleColumns.forEach(col => filtered[col] = item[col]);
              return filtered;
            })"
            density="comfortable"
            height="400px"
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
const headers = ref([])
const visibleColumns = ref([]) // Colonnes à afficher
const visibleTables = ref(['dav', 'dat', 'epr']) // Par défaut, tout est affiché

const isAllAgence = computed(() => agence.value === 'all')

const rechercher = async () => {
  loading.value = true
  message.value = ""
  resultsDav.value = []
  resultsDat.value = []
  resultsEpr.value = []
  headers.value = []
  visibleColumns.value = []

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
        if (type === 'dav') resultsDav.value = res.data
        if (type === 'dat') resultsDat.value = res.data
        if (type === 'epr') resultsEpr.value = res.data
      } else {
        if (type === 'dav') resultsDav.value = []
        if (type === 'dat') resultsDat.value = []
        if (type === 'epr') resultsEpr.value = []
      }
    }

    // Génère les headers dynamiquement pour chaque type si des résultats existent
    if (resultsDav.value.length) {
      headers.value = Object.keys(resultsDav.value[0]).map(key => ({
        title: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        key
      }))
      visibleColumns.value = headers.value.map(h => h.key)
    } else if (resultsDat.value.length) {
      headers.value = Object.keys(resultsDat.value[0]).map(key => ({
        title: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        key
      }))
      visibleColumns.value = headers.value.map(h => h.key)
    } else if (resultsEpr.value.length) {
      headers.value = Object.keys(resultsEpr.value[0]).map(key => ({
        title: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        key
      }))
      visibleColumns.value = headers.value.map(h => h.key)
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
  width: 100%;
  border-radius: 0 !important; /* pas d'arrondi */
}

.full-table {
  width: 100%;
}

/* Animation */
.fade-in {
  animation: fadeIn 0.5s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.table-title {
  text-align: center; /* Centrer le texte horizontalement */
  padding: 8px 0; /* Ajouter un peu d'espace autour du texte */
  color: #fff; /* Couleur du texte (blanc) */
  border-radius: 4px; /* Arrondi des coins */
}

.table-title-dat {
  color: #43a047; /* Vert pour DAT */
}

.table-title-epr {
  color: #fbc02d; /* Jaune pour EPR */
}

.table-title-dav {
 color: #1976d2; /* Bleu pour DAV (si nécessaire) */
}

.table-dav {
  border: 2px solid #1976d2; /* Bleu pour DAV */
  border-radius: 8px;
}

.table-dat {
  border: 2px solid #43a047; /* Vert pour DAT */
  border-radius: 8px;
}

.table-epr {
  border: 2px solid #fbc02d; /* Jaune pour EPR */
  border-radius: 8px;
}
</style>


