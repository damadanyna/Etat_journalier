<template>
  <v-card
    v-if="resume"
    class="mb-6 pa-6 rounded-xl"
    elevation="3"
  >
    <h3 class="text-h6 mb-4 font-weight-bold d-flex align-center">
  <span>Résumé du DAT</span>
  <v-chip
    v-if="props.tableName"
    color="yellow"
    class="ml-4"
    size="grand"
    label
    style="font-size:1.2rem;font-weight:500;"
  >
    {{ props.tableName }}
  </v-chip>
</h3>
    <v-row dense>
      <v-col cols="12" md="3">
        <v-card variant="tonal" color="primary" class="pa-3 rounded-lg">
          <div class="d-flex align-center">
            <v-icon class="mr-2">mdi-table</v-icon>
            <div>
              <div class="text-caption text-primary">Nombre de lignes</div>
              <div class="text-h6 font-weight-bold">{{ resume.nb_lignes }}</div>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card variant="tonal" color="blue" class="pa-3 rounded-lg">
          <div class="d-flex align-center">
            <v-icon class="mr-2">mdi-account-group</v-icon>
            <div>
              <div class="text-caption text-blue">Nombre de clients</div>
              <div class="text-h6 font-weight-bold">{{ resume.nb_clients }}</div>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card variant="tonal" color="green" class="pa-3 rounded-lg">
          <div class="d-flex align-center">
            <v-icon class="mr-2">mdi-cash-multiple</v-icon>
            <div>
              <div class="text-caption text-green">Total Capital</div>
              <div class="text-h6 font-weight-bold">{{ resume.total_montant_capital }}</div>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card variant="tonal" color="teal" class="pa-3 rounded-lg">
          <div class="d-flex align-center">
            <v-icon class="mr-2">mdi-bank-transfer</v-icon>
            <div>
              <div class="text-caption text-teal">Total Paiement</div>
              <div class="text-h6 font-weight-bold">{{ resume.total_montant_pay_total }}</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup>
import { ref, watch, inject } from "vue"
import axios from "axios"

const api = inject("api")

const props = defineProps({
  tableName: {
    type: String,
    required: true
  }
})

const resume = ref(null)

const fetchResume = async (tableName) => {
  if (!tableName) return

  try {
    const res = await axios.get(`${api}/api/dat/${tableName}/resume`)
    resume.value = res.data
  } catch (err) {
    console.error("Erreur lors du chargement du résumé:", err)
  }
}

watch(() => props.tableName, fetchResume, { immediate: true })
</script>
