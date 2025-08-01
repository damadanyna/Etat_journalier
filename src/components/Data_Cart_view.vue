<template>
  <div class="bg_data mr-4">
    <div class="flex flex-row justify-end items-center space-x-4">
      <h3 class="mr-5 text-xl">Date d'arrêt</h3>

      <v-menu
        v-model="menu"
        close-on-content-click
        offset-y
        max-width="200"
        min-width="200"
      >
        <template #activator="{ props }">
          <v-btn v-bind="props" prepend-icon="mdi-calendar-range" variant="outlined">
            <template #prepend>
              <v-icon color="success" />
            </template>
            <span class="text-2xl">{{ selectedDate }}</span>
          </v-btn>
        </template>

      <v-list style="max-height: 200px; overflow-y: auto;">
        <v-list-item
          v-for="date in historyDates"
          :key="date.label"
          @click="selectDate(date.label)"
          clickable
        > 
        <div class="flex" :title="date.stat_of!='init'? 'Base non initialisé':''">
          
          <v-icon v-if="date.stat_of !== 'init'"   class=" mr-2 text-red-700">mdi-database-alert</v-icon> 
          <v-icon v-else color="success" class=" mr-2">mdi-database-check</v-icon> 
          <v-list-item-title>{{ date.label }}</v-list-item-title>
        </div>
        </v-list-item>
      </v-list>
      </v-menu>
    </div>
 
    <div class="grid grid-cols-2 gap-4">
      <doughnut
        v-for="(item, index) in charts"
        :key="item.id"
        :id="item.id"
        :title="item.title"
        :data="item.data"
        :labels="item.labels"
        :colors="item.colors"
      />
    </div> 
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import doughnut from './doughnut/Dougnut.vue'

const charts = [
  {
    id: 'pa_chart',
    title: 'Répartition des PA',
    data: [15, 50, 20, 15],
    labels: ['PA1', 'PA2', 'PA3', 'PA4'],
    colors: ['#FF0031', '#00c62b', '#ffffff', '#00FFFF']
  },
  {
    id: 'second_chart',
    title: 'Autre graphique',
    data: [25, 25, 25, 25],
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    colors: ['#eab308', '#3b82f6', '#f43f5e', '#10b981']
  }
]

const menu = ref(false)
const selectedDate = ref('Chargement en cours...')

// Tableau des dates prédéfinies
const historyDates  = ref([])

function selectDate(date) {
  selectedDate.value = date
  menu.value = false // ferme le menu après sélection
}

// history_insert
async function fetchData(url, targetRef) {
  try {
    const response = await fetch(url)
    if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`)
    const data = await response.json()
    targetRef.value = data.response.data
  } catch (error) {
    console.error('❌ Erreur de chargement :', error)
  }
} 

watch(historyDates, (val) => {
  if (Array.isArray(val) && val.length > 0) {
    // Si tes éléments sont des objets avec une propriété `label`
    selectedDate.value = val[0].label
    console.log("📅 Date sélectionnée automatiquement :", selectedDate.value)
  }
}, { immediate: true })

onMounted(() => {
  
  fetchData('http://192.168.1.212:8000/api/history_insert', historyDates)

})

</script>

<style scoped>
.bg_data {
  background-color: #00000022;
  border-radius: 20px;
  padding: 10px 20px;
}
</style>
