<!-- Intitialise.vue (style amélioré, script intact) -->
<template>
<v-container class="init-container" fluid>
<HistorySelected ref="historyRef" @select="onSelectHistory" />


<v-row class="mt-10 fade-in" v-if="selectedHistory">
<v-col cols="12" class="text-center">
<h3 class="title-selected">Table sélectionnée : {{ selectedHistory.label }}</h3>


<v-btn
v-if="!selectedHistory.stat_compte"
color="primary"
class="mt-6 action-button"
@click="initializeTable"
:loading="loading"
>
Initialiser
</v-btn>


<v-alert
v-else
type="success"
border="start"
class="mt-6 nice-alert"
>
Déjà initialisé
</v-alert>


<v-alert
v-if="message"
:type="messageType"
border="start"
class="mt-4 nice-alert"
>
{{ message }}
</v-alert>
</v-col>
</v-row>


<v-progress-linear
v-if="loading"
:value="progress"
color="primary"
height="10"
rounded
striped
indeterminate
class="progress-bar"
/>
</v-container>
</template>



<script setup>
import { ref ,inject} from "vue"
import axios from "axios"
import HistorySelected from "@/components/dat/HistorySelected.vue"
import { onMounted } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()
const selectedHistory = ref(null)
const loading = ref(false)
const message = ref("")
const messageType = ref("info")
const progress = ref(0)

const historyRef = ref(null)
const api = inject('api') 

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
      `${api}/api/compte/compte_init/${selectedHistory.value.label}`
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
onMounted(async () => {
  await historyRef.value.fetchHistory()
  // Récupère la date depuis la query ou localStorage
  const label = route.query.label || localStorage.getItem("selectedTable")
  if (label) {
    const found = historyRef.value.history.find(h => h.label === label)
    if (found) selectedHistory.value = found
  }
})
</script>

<style scoped>
.unified-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
}
</style>
