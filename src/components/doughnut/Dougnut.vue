<template>
  <div>
    <div class="text-center font-semibold mb-2">{{ title }}</div>
    <div :style="`width: 100%; height: ${props.heigth};`">
      <canvas :id="canvasId"></canvas>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { Chart, DoughnutController, ArcElement, Tooltip, Legend } from 'chart.js'

// Enregistrer manuellement les composants requis si tree-shaking
Chart.register(DoughnutController, ArcElement, Tooltip, Legend)

const props = defineProps({
  id: { type: String, required: true },             // identifiant unique du canvas
  data: { type: Array, required: true },            // ex: [15, 50, 20, 15]
  labels: { type: Array, required: true },          // ex: ['PA1', 'PA2', ...]
  colors: { type: Array, required: true },          // couleurs de fond
  title: { type: String, default: '' },           // titre facultatif
  circumference: { type: String, default: 180 } ,            // titre facultatif
  heigth: { type: String, default: 100 } ,            // titre facultatif
})

const canvasId = `canvas-${props.id}`
let chartInstance = null

onMounted(() => {
  const ctx = document.getElementById(canvasId).getContext('2d')

  chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: props.labels,
      datasets: [{
        data: props.data,
        backgroundColor: props.colors,
        borderColor: '#101010',
        borderWidth: 8
      }]
    },
    options: {
      responsive: true,
      rotation: -90,
      circumference: props.circumference,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  })
})

onBeforeUnmount(() => {
  if (chartInstance) chartInstance.destroy()
})
</script>
