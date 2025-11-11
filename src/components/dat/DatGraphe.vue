<template>
  <v-card class="pa-4 mb-6" outlined>
    <!-- Sélecteurs X et Y -->
    <v-row>
      <v-col cols="12" md="4">
        <v-select
          v-model="x"
          :items="fieldsX"
          label="Axe X"
          outlined
          dense
        />
      </v-col>

      <v-col cols="12" md="4">
        <v-select
          v-model="y"
          :items="fieldsY"
          label="Axe Y"
          outlined
          dense
        />
      </v-col>

      <v-col cols="12" md="4" class="d-flex align-center">
        <v-btn
          color="primary"
          @click="fetchData"
          :disabled="!x || !y"
        >
          Générer
        </v-btn>
      </v-col>
    </v-row>

    <!-- Graphique -->
    <div  v-if="chartData" class="mt-6">
      <Bar :data="chartData" :options="chartOptions" />
    </div>

    <!-- Alerte par défaut -->
    <v-alert
      v-else
      type="info"
      border="left"
      color="green"
      dark
      class="mt-4"
    >
      Sélectionnez X et Y puis cliquez sur "Générer".
    </v-alert>
  </v-card>
</template>

<script setup>
import { ref, watch,inject } from "vue"
import axios from "axios"
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from "chart.js"
import { Bar } from "vue-chartjs"

// Enregistrement des éléments Chart.js
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

// Props venant de dat.vue
const props = defineProps({
  tableName: {
    type: String,
    required: true
  }
})
const api = inject('api') 


// Champs disponibles pour X et Y
const fieldsY = [ "montant_capital", "montant_pay_total"]
const fieldsX = ["Agence", "code_client", "Produits"]

const x = ref(localStorage.getItem("x") || null)
const y = ref(localStorage.getItem("y") ||null)
const chartData = ref(null)

// Options Chart.js
const chartOptions = {
  responsive: true,
  plugins: {
    legend: { position: "top" },
    title: { display: true, text: "Graphique dynamique" }
  }
}

// Récupération des données backend
const fetchData = async () => {
  if (!props.tableName || !x.value || !y.value) return
  try {
    const res = await axios.get(
      `${api}/api/datGraphe/${props.tableName}`,
      { params: { x: x.value, y: y.value } }
    )

    console.log("Réponse API :", res.data)

    const rows = Array.isArray(res.data) ? res.data : (res.data.rows || [])

    chartData.value = {
      labels: rows.map((d) => d[x.value]),
      datasets: [
        {
          label: y.value,
          data: rows.map((d) => d.value),
          backgroundColor: "rgba(54, 162, 235, 0.6)"
        }
      ]
    }
  } catch (err) {
    console.error("Erreur chargement graphe:", err)
  }
}
watch([x, y], (newVal) => {
  if (newVal)
  localStorage.setItem("x", x.value)
  localStorage.setItem("y", y.value)
})
</script>
