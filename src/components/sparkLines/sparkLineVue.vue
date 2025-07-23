<template>
  <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
// import {
//   Chart as ChartJS,
//   LineElement,
//   PointElement,
//   LinearScale,
//   CategoryScale,
//   Filler,
//   Tooltip,
// } from 'chart.js'
import { Line } from 'vue-chartjs'
import { onMounted, ref, computed  } from 'vue' 
const capitalSums = ref([])
const loading = ref(true)
const error = ref(null) 
// ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Filler, Tooltip)
 

const label_val = ref([])
const values = ref([])
// dégradé vert transparent (sera défini dynamiquement via `ctx`)
const chartData = computed(() => ({
  labels: label_val.value,
  datasets: [
    {
      label: 'Valeurs',
      data: values.value,
      fill: true,
      borderColor: '#00E676',
      tension: 0.2,
      pointRadius: 0,
      backgroundColor: (ctx) => {
        const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, 300)
        gradient.addColorStop(0, 'rgba(0, 230, 118, 0.4)')
        gradient.addColorStop(1, 'rgba(0, 230, 118, 0)')
        return gradient
      },
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      ticks: {
        color: '#bbb',
      },
      grid: {
        display: false,
      },
    },
    y: {
      ticks: {
        color: '#bbb',
      },
      grid: {
        color: '#33333300',
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      mode: 'index',
      intersect: false,
    },
  },
}

const fetchCapitalSums = async () => {
  try {
    const response = await fetch('http://192.168.1.212:8000/api/get_capital_sums');
    const json = await response.json();

    if (!response.ok) throw new Error(json.detail || 'Erreur inconnue');

    const capitalData = json.data?.capital_sums || [];
    capitalSums.value = capitalData;
    console.log("Capital Sums:", capitalData);

    const { labels: newLabels, values: newValues } = adaptCapitalSumsToChart(capitalData);
    label_val.value =  newLabels;
    values.value = newValues;
    console.log("Labels:", newLabels)
    console.log("Values:", newValues)


  } catch (err) {
    error.value = err.message || 'Erreur inconnue';
    console.error("Erreur fetchCapitalSums:", err);

  } finally {
    loading.value = false;
  }
};

function adaptCapitalSumsToChart(capital_sums) {
  const labels = capital_sums.map(item => {
    const dateStr = item.table_name.slice(-8); // "20250711"
    const month = dateStr.slice(4, 6);          // "07"
    const day = dateStr.slice(6, 8);            // "11"
    return `${month}-${day}`;                   // => "07-11"
  });

  const values = capital_sums.map(item => item.Total_amount);

  return { labels, values };
}


onMounted(() => {
  fetchCapitalSums()
})


</script>

<style scoped>
.chart-container {
  height: 300px;
  width: 100%;
  background-color: #00000022;
  padding: 16px;
  border-radius: 12px;
}
</style>
