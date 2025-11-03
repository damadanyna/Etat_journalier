<template>
  <div class="bg_data">

    <div class="flex flex-row   w-full   "> 
      <div   v-for="(item) in charts" key="item.id" class=" w-full h-full flex justify-between"> 
         
        <div   class=" flex flex-col">
          <doughnut 
            :key="item.id"
            :id="item.id"
            :title="item.title"
            :data="item.data"
            :labels="item.labels"
            :colors="item.colors"
            :circumference="item.circumference"
            :heigth="item.heigths"
          />
        </div> 
      </div>
    </div> 
  </div>
</template>

<script setup>
import { onMounted, ref, watch,inject } from 'vue'
import doughnut from './doughnut/Dougnut.vue'
import { usePopupStore } from '../stores'
 
const charts = ref([]) 
const api = inject('api') 


// Tableau des dates prédéfinies
const stat_local_ref  = ref([])
const stat_PA  = ref([])

// async function selectDate(date) {
  
//  charts.value = []
//   selectedDate.value = date
//   usePopupStore().selected_date.value = date
//   menu.value = false
   

// }


watch(usePopupStore().selected_date, async(data) => {  
  charts.value = []
     stat_PA.value = await fetchData(`${api}/api/get_pa_class`,data.value) 
    updateSecondChartFromData(stat_PA.value,'theard_chart',180,['#FF0031',  '#FF00FF','#00FFFF','#00c62b','#ffffff'], '300px') 
    
    stat_local_ref.value = await fetchData(`${api}/api/get_local_ref`, data.value,'1000px') 
    updateSecondChartFromData(stat_local_ref.value,'second_chart',360)
  
});

 

// history_insert
async function fetchData(baseUrl, date = null) {
  try {
    // Si une date est fournie, on l’ajoute à l’URL
    const url = date ? `${baseUrl}?date=${date}` : baseUrl

    const response = await fetch(url)
    if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`)

    const data = await response.json()
    return data.response.data
  } catch (error) {
    console.error('❌ Erreur de chargement :', error)
    return []
  }
}

function updateSecondChartFromData(dataArray,name, circumference,color = null,height = null) {
  if (!Array.isArray(dataArray) || dataArray.length === 0) return

  const labels = []
  const data = []
  const colors = [] 

  dataArray.forEach((item) => {
    labels.push(item.initial || 'Inconnu')
    data.push(item.total || 0)
    colors.push(generateRandomColor())
  })
  var chart_Data= {
                    id: name,
                    title: 'Local ref',
                    data: [25, 25, 25, 25],
                    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                    colors: ['#eab308', '#3b82f6', '#f43f5e', '#10b981'],
                    circumference: circumference, 
                    heigths:'400px' 
                  }
  chart_Data.data=data
  chart_Data.labels=labels
  chart_Data.colors=color===null?colors: color
  chart_Data.heigths=color===null?'400px': height 
  charts.value.push(chart_Data) 
}

function generateRandomColor() {
  const letters = '0123456789ABCDEF'
  let color = '#'
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)]
  }
  return color
}




onMounted(() => {
  


 (async () => {
    stat_PA.value = await fetchData(`${api}/api/get_pa_class`,'20251028') 
    updateSecondChartFromData(stat_PA.value,'theard_chart',180,['#FF0031',  '#FF00FF','#00FFFF','#00c62b','#ffffff'], '300px') 
  })();

  
 (async () => {
    stat_local_ref.value = await fetchData(`${api}/api/get_local_ref`,'20251028','1000px') 
    updateSecondChartFromData(stat_local_ref.value,'second_chart',360)
    
  })();
})

</script>

<style scoped>
.bg_data {
  background-color: #00000022;
  border-radius: 20px;
  padding: 10px 20px;
}
</style>
