<!-- src/components/dat/Resumer.vue -->
<template>
  <v-card v-if="resume" class="mb-4 pa-4" outlined>
    <v-row>
      
      <v-col cols="12" md="3">
        <strong>Nombre de clients :</strong> {{ resume.nb_clients }}
      </v-col>
      <v-col cols="12" md="3">
        <strong>total montant capital :</strong> {{ resume.total_montant_capital }}
      </v-col>
      <v-col cols="12" md="3">
        <strong>total frais de dossier :</strong> {{ resume.total_frais_de_dossier }}
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { ref, watch,inject } from "vue"
import axios from "axios"

// Props venant de dat.vue
const props = defineProps({
  tableName: {
    type: String,
    required: true
  }
})
const api = inject('api') 


const resume = ref(null)

const fetchResume = async (tableName) => {
  if (!tableName) return
  try {
    const res = await axios.get(`${api}/api/decaissement/${tableName}/resume`)
    resume.value = res.data
  } catch (err) {
    console.error("Erreur lors du chargement du résumé:", err)
  }
}

// Recharger quand tableName change
watch(
  () => props.tableName,
  (newVal) => {
    fetchResume(newVal)
  },
  { immediate: true }
)
</script>
