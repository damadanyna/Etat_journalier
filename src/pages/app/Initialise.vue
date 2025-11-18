<template>
  <v-container class="init-container" fluid>
    
    <!-- Bloc historique -->
    <v-row>
      <v-col cols="12" md="4">
        <HistorySelected 
          ref="historyRef" 
          @select="onSelectHistory" 
        />
      </v-col>

      <!-- Bloc d'initialisation -->
      <v-col cols="12" md="8">
        <v-card 
          class="pa-6 rounded-xl elevation-3 fade-in init-card"
          v-if="selectedHistory"
        >
          <h2 class="text-h6 font-weight-bold mb-4 text-center">
            Table sélectionnée : 
            <span class="text-primary">{{ selectedHistory.label }}</span>
          </h2>

          <div class="text-center mt-4">
            <!-- Bouton Initialiser -->
            <v-btn
              v-if="!selectedHistory.stat_compte"
              color="primary"
              class="action-button"
              size="large"
              rounded="lg"
              @click="initializeTable"
              :loading="loading"
            >
              <v-icon left>mdi-cog-sync</v-icon>
              Initialiser
            </v-btn>

            <!-- Déjà initialisé -->
            <v-alert
              v-else
              type="success"
              class="nice-alert mt-4"
              rounded="lg"
              border="start"
            >
              <v-icon class="mr-2">mdi-check-circle</v-icon>
              Déjà initialisé
            </v-alert>

            <!-- Message -->
            <v-alert
              v-if="message"
              :type="messageType"
              class="nice-alert mt-4"
              border="start"
              rounded="lg"
            >
              <v-icon class="mr-2">mdi-information</v-icon>
              {{ message }}
            </v-alert>
          </div>

          <!-- Progress bar -->
          <v-progress-linear
            v-if="loading"
            color="primary"
            height="8"
            class="mt-6 rounded-pill"
            indeterminate
          />
        </v-card>
      </v-col>
    </v-row>

  </v-container>
</template>

<script setup>
import { ref ,inject,onMounted } from "vue"
import axios from "axios"
import HistorySelected from "@/components/dat/HistorySelected.vue"
import { useRoute } from "vue-router"

const api = inject('api')
const route = useRoute()

const selectedHistory = ref(null)
const loading = ref(false)
const message = ref("")
const messageType = ref("info")
const progress = ref(0)

const historyRef = ref(null)

const onSelectHistory = (item) => {
  selectedHistory.value = item
  message.value = ""
}

const initializeTable = async () => {
  if (!selectedHistory.value) return

  loading.value = true
  progress.value = 0

  try {
    const res = await axios.post(
      `${api}/api/compte/compte_init/${selectedHistory.value.label}`
    )

    if (res.data.status === "success") {
      message.value = res.data.message || "Initialisation réussie 🎉"
      messageType.value = "success"

      await historyRef.value.fetchHistory()

      const updated = historyRef.value.history.find(
        h => h.label === selectedHistory.value.label
      )
      if (updated) selectedHistory.value = updated

      setTimeout(() => window.location.reload(), 2000)

    } else {
      message.value = "Erreur lors de l'initialisation ❌"
      messageType.value = "error"
    }

  } catch (err) {
    message.value = "Erreur de connexion ⚠️"
    messageType.value = "error"

  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await historyRef.value.fetchHistory()

  const label = route.query.label || localStorage.getItem("selectedTable")
  if (label) {
    const found = historyRef.value.history.find(h => h.label === label)
    if (found) selectedHistory.value = found
  }
})
</script>

<style scoped>
.init-card {
  min-height: 350px;
}

.fade-in {
  animation: fadeIn 0.6s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.history-container {
  padding-right: 10px;
}
</style>
