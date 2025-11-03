<template>
  <v-card class="pa-4" outlined>
    <v-row align="center">
      <v-col cols="12" md="4">
        <v-select
          v-model="selectedType"
          :items="['dat', 'dav', 'epr']"
          label="Type de table"
          outlined
          dense
        />
      </v-col>
    </v-row>

    <!-- Graphique -->
    <div v-if="chartData" class="chart-container mt-6" style="width:100%;">
      <Line :data="chartData" :options="chartOptions" />
    </div>

    <!-- Alerte -->
    <v-alert
      v-else
      type="info"
      border="left"
      color="blue"
      dark
      class="mt-4"
    >
      Sélectionnez un type pour voir l’évolution.
    </v-alert>
  </v-card>
</template>

<script setup>
import { ref, watch } from "vue"
import axios from "axios"
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
} from "chart.js"
import { Line } from "vue-chartjs"

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale)

const selectedType = ref("dat") 
const chartData = ref(null)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false, // très important pour que height soit respecté

  plugins: {
    legend: { position: "top" },
    title: { display: true, text: "Évolution des totaux par table" },
  },
}

watch(selectedType, async (newType) => {
  if (!newType) {
    chartData.value = null
    return
  }
  await fetchData(newType)
})

const fetchData = async (type) => {
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/resume/all/${type}`)
    const data = res.data || []

    if (!data.length) {
      chartData.value = null
      return
    }

    data.sort((a, b) => a.table_name.localeCompare(b.table_name))
    const labels = data.map(d => d.table_name.replace(`${type}_`, ""))

    let datasets = []

    if (type === "dav") {
      datasets = [
        { label: "Nombre de clients", data: data.map(d => d.nb_clients || 0), borderColor: "#3B82F6" },
        { label: "Montant total DAV", data: data.map(d => d.total_montant_dav || 0), borderColor: "#10B981" },
        { label: "Total Débit DAV", data: data.map(d => d.total_debit_dav || 0), borderColor: "#F59E0B" },
        { label: "Total Crédit DAV", data: data.map(d => d.total_credit_dav || 0), borderColor: "#EF4444" },
      ]
    }

    if (type === "dat") {
      datasets = [
       
        { label: "Nombre de clients", data: data.map(d => d.nb_clients || 0), borderColor: "#3B82F6" },
        { label: "Montant Capital", data: data.map(d => d.total_montant_capital || 0), borderColor: "#10B981" },
        { label: "Montant Payé Total", data: data.map(d => d.total_montant_pay_total || 0), borderColor: "#F59E0B" },
      ]
    }

    if (type === "epr") {
      datasets = [
        { label: "Nombre de clients", data: data.map(d => d.nb_clients || 0), borderColor: "#3B82F6" },
        { label: "Montant Total EPR", data: data.map(d => d.total_montant_epr || 0), borderColor: "#10B981" },
        { label: "Total Débit EPR", data: data.map(d => d.total_debit_epr || 0), borderColor: "#F59E0B" },
        { label: "Total Crédit EPR", data: data.map(d => d.total_credit_epr || 0), borderColor: "#EF4444" },
      ]
    }

    chartData.value = {
      labels,
      datasets: datasets.map(ds => ({
        ...ds,
        borderWidth: 2,
        fill: false,
        tension: 0.2,
      })),
    }

  } catch (err) {
    console.error("Erreur lors du chargement :", err)
  }
}

fetchData(selectedType.value)
</script>

<style scoped>
.v-card {
  width: 100%;        /* occupe toute la largeur */
  max-width: 100%;    /* supprime la limite */
  margin: 0;          /* plus de centrage automatique */
  padding: 16px;      /* garde un peu de padding interne */
  box-sizing: border-box;
  background-color: #040404; /* couleur de fond légère */
}
.chart-container {
  width: 100%;
  max-width: 100%;
  height: 500px; /* ajuster selon tes besoins */
}

</style>
