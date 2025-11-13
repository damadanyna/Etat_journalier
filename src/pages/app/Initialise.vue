<template>
  <v-container class="unified-container" fluid>
    <!-- Liste des history_insert -->
    <HistorySelected ref="historyRef" @select="onSelectHistory" />

    <v-row class="mt-6" v-if="selectedHistory">
      <v-col cols="12" class="text-center">
        <h3>Table sélectionnée : {{ selectedHistory.label }}</h3>

        <!-- Si non initialisé -->
        <v-btn
          v-if="!selectedHistory.stat_compte"
          color="primary"
          class="mt-4"
          @click="initializeTable"
          :loading="loading"
        >
          Initialiser                         
        </v-btn>

        <v-alert
          v-else
          type="success"
          border="start"
          class="mt-4"
        >
          Déjà initialisé
        </v-alert>

        <v-alert
          v-if="message"
          :type="messageType"
          border="start"
          class="mt-4"
        >
          {{ message }}
        </v-alert>
      </v-col>
    </v-row>

    <v-progress-linear
      v-if="loading"
      :value="progress"
      color="primary"
      height="8"
      striped
      indeterminate
      class="mb-4"
    />
  </v-container>
</template>

<script setup>
import { ref } from "vue"
import axios from "axios"
import HistorySelected from "@/components/dat/HistorySelected.vue"

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
  const interval = setInterval(() => {
    if (progress.value < 90) progress.value += 5
  }, 500)
  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/compte/compte_init/${selectedHistory.value.label}`,
      {},
      { timeout: 990000 } // 120 secondes
    )

    if (res.data.status === "success") {
      message.value = res.data.message || "Initialisation réussie ✅"
      messageType.value = "success"

      await historyRef.value.fetchHistory()

      const updated = historyRef.value.history.find(
        h => h.label === selectedHistory.value.label
      )
      if (updated) selectedHistory.value = updated
       setTimeout(() => {
        window.location.reload()
      }, 2000)
      
    } else {
      message.value = res.data.message || "tss lors de l'initialisation ❌"
      messageType.value = "error"
    }

     } catch (err) {
    message.value = "Erreur de connexion au serveur ⚠️"
    messageType.value = "error"
  } finally {
    clearInterval(interval)
    loading.value = false
   }
}

</script>

<style scoped>
.unified-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
}
</style>
