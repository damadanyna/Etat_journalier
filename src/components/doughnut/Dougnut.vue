<template>
  <div class="p-4 grid grid-cols-1 md:grid-cols-2 gap-8" v-if="isReady">
    <!-- Doughnut Chart -->
    <div>
      <h2 class="text-xl mb-2 font-semibold">Doughnut Chart</h2>
      <Doughnut :chart-data="chartData_" :options="chartOptions" />
    </div>
  </div>

  <div v-else>
    Chargement des graphiques...
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Doughnut } from 'vue-chartjs'

const chartData_ = ref({
  labels: [],
  datasets: []
})
const chartOptions = ref({})
const isReady = ref(false)

onMounted(() => {
  // Initialise les données et options une fois
  chartData_.value = {
    labels: ['Rouge', 'Bleu', 'Jaune'],
    datasets: [
      {
        label: 'Votes',
        data: [30, 50, 20],
        backgroundColor: ['#f87171', '#60a5fa', '#facc15'],
        borderWidth: 1,
      }
    ]
  }

  chartOptions.value = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom'
      }
    }
  }

  // Définir isReady à true pour afficher le graphique
  isReady.value = true
})
</script>
