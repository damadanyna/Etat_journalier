<template>
  <v-container fluid class="pa-0 full-container">
    <v-card
      class="pa-8 rounded-0 elevation-2 fade-in full-card"
      flat
    >
      <h2 class="text-h5 font-weight-bold mb-6 text-center">
      </h2>

      <!-- FORMULAIRE -->
      <v-row dense class="px-4">
        <v-col cols="12" sm="3">
          <v-select
            v-model="typeTable"
            :items="['dav', 'dat', 'epr']"
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
<div v-if="headers.length" class="d-flex flex-wrap align-center mb-4 px-2">
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
      <v-data-table
        v-if="results.length"
        :headers="headers.filter(h => visibleColumns.includes(h.key))"
        :items="results.map(item => {
          const filtered = {};
          visibleColumns.forEach(col => filtered[col] = item[col]);
          return filtered;
        })"
        class="mt-8 elevation-2 fade-in full-table"
        density="comfortable"
        height="700px"
      />
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, inject, computed } from "vue"
import axios from "axios"

const api = inject("api")

const typeTable = ref("dav")
const agence = ref("")
const singleDate = ref("")
const dateDebut = ref("")
const dateFin = ref("")

const loading = ref(false)
const message = ref("")
const messageType = ref("info")
const results = ref([])
const headers = ref([])
const visibleColumns = ref([]) // Colonnes à afficher

const isAllAgence = computed(() => agence.value === 'all')

const rechercher = async () => {
  loading.value = true
  message.value = ""
  results.value = []
  headers.value = []

  try {
    const res = await axios.get(`${api}/api/resume/total-produit/${typeTable.value}`, {
      params: {
        agence: agence.value,
        single_date_if_all: singleDate.value,
        date_debut: dateDebut.value,
        date_fin: dateFin.value,
      }
    })

    if (Array.isArray(res.data) && res.data.length) {
      results.value = res.data
      headers.value = Object.keys(res.data[0]).map(key => ({
        title: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        key
      }))
      visibleColumns.value = headers.value.map(h => h.key) // Toutes visibles par défaut
      messageType.value = "success"
      message.value = `Résultats trouvés : ${res.data.length}`
    } else if (res.data.message) {
      messageType.value = "error"
      message.value = res.data.message
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
</style>


