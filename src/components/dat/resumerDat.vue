<!-- src/components/dat/Resumer.vue -->
<template>
  Bilan
  <v-card v-if="resume" class="mb-4 pa-4" outlined>
    <v-row>
      <v-col cols="12" md="3">
        <strong>Nombre de lignes :</strong> {{ resume.nb_lignes }}
      </v-col>
      <v-col cols="12" md="3">
        <strong>Nombre de clients :</strong> {{ resume.nb_clients }}
      </v-col>
      <v-col cols="12" md="3">
        <strong>Total Capital :</strong> {{ resume.total_montant_capital }}
      </v-col>
      <v-col cols="12" md="3">
        <strong>Total Paiement :</strong> {{ resume.total_montant_pay_total }}
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { ref, watch,inject } from "vue"
import axios from "axios"
const api = inject('api')

// Props venant de dat.vue
const props = defineProps({
  tableName: {
    type: String,
    required: true
  }
})

const resume = ref(null)

const fetchResume = async (tableName) => {

  if (!tableName) return
  console.log("📋 TableName utilisé pour résumé :", tableName)
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/dat/${tableName}/resume`)
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
