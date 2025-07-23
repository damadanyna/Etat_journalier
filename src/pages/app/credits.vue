<template>  
<div v-if="selected_date?.stat_of==null || selected_date?.stat_of=='' || selected_date?.stat_of=='NULL'">
  <v-btn @click="runAllSteps()"
          class="me-2 text-none ml-10 text-white"
          color="#00DF76"
          prepend-icon="mdi-play-circle"
          variant="flat"
          :disabled="isRunning"
          :style="{ opacity: isRunning ? 0.3 : 1 }"
        >
          Lancer
        </v-btn>
  <div class="stepper-container">
    <v-stepper alt-labels v-model="currentStep" class="transparent-stepper">
    <v-stepper-header>
      <template v-for="(step, index) in steps" :key="index">
        <v-stepper-item
          :value="index + 1"
          :complete="step.status === 'done'"
          :color="getColor(step.status)"
        >
          <template v-slot:title>
            {{ step.title }}
          </template>

          <template v-slot:subtitle>
            <span>{{ getSubtitle(step.status) }}</span>
          </template>
        </v-stepper-item>

        <v-divider v-if="index + 1 < steps.length"></v-divider>
      </template>
    </v-stepper-header>
  </v-stepper>

    <div class="flex px-6 ">
    </div>
  </div> 

   <v-col   class="flex items-center justify-center flex-row">
        <div class="">
          <v-progress-circular :model-value="template.percentage" :rotate="360" :size="250" :width="2.5" color="green">
            <div class="flex flex-col items-center justify-center" > 
              <span  class=" text-4xl font-bold" v-if="template.percentage!=0">{{ template.percentage }}</span>
            <span v-else class=" animate-ping"> Chargement ...</span>
            <!-- <span title="Temps de chargement" class="  text-stone-100 font-bold">{{ formattedTime }}</span> -->
            </div>
          </v-progress-circular>  
        </div>
        <v-col>
          <div class="" style=" padding-right: 30px;  overflow-y: auto; height: 300px;">
            <div v-for="item,i in table_list_processing_init" :key="i" class=" flex border-b" >  
              <div v-if="item['current']==i && item['status']!='done' "  style=" padding: 16px;">
                <v-progress-circular  :size="15" :width="5" color="green" indeterminate  ></v-progress-circular>
              </div>

              <span  v-else-if=" i <=item['current'] && item['status']=='done'" style="padding: 15px; color: #53e053; font-size: 18px;" class="mdi mdi-check-circle" ></span>
              <div v-else style=" padding: 16px;">
                <v-progress-circular style=" " :size="15" :width="5" color="green"  ></v-progress-circular>
              </div>
              
              <div v-if="item['status']!='done' && item['current']!=i"  style=" display: flex; flex-direction: column; ">
                <span  style=" font-size: 14px; color: gray; ">{{item.name}}</span>
                <span style=" font-size: 10px; color: gray; ">En attente ...</span>
              </div>

              <div v-else style=" display: flex; flex-direction: column;">
                <span style=" font-size: 14px; color: white; ">{{item.name}}</span>
                <div style=" display: flex;"> 
                  <span style=" font-size: 10px; color: gray; ">Effectuée </span> 
                </div>
              </div>
            </div>
 
          </div>
        </v-col>
      </v-col>
</div>
<div class="flex flex-col px-3 overflow-auto max-h-[91vh] hide-scrollbar " v-else> 
    <sparkLineVue :selected_date="selected_date"   ></sparkLineVue> 
    <div class=" my-2"></div>
    <Data_viewer></Data_viewer>
    <div class=" my-2"></div>
    <v-divider></v-divider>
    <Data_table_view style="" ></Data_table_view> 
  <!-- <Dougnut></Dougnut> -->

</div>


</template>

<script setup>
// import Dougnut from '../../components/doughnut/Dougnut.vue';
import { ref, watch } from 'vue' 
import { usePopupStore } from '../../stores'
import sparkLineVue from '../../components/sparkLines/sparkLineVue.vue';
import Data_viewer from '../../components/Data_Cart_view.vue';
import Data_table_view from '../../components/Data_table_view.vue';
const popupStore = usePopupStore();
const isRunning = ref(false)
const currentStep = ref(0)
const template= ref([])
const table_list_processing_init= ref([]) 
const selected_date= ref(null)
const steps = ref([
  { title: 'Initialisation', status: 'pending' },
  { title: 'États des encours', status: 'pending' },
  { title: 'État des remboursements', status: 'pending' },
  // { title: 'État prévisionnel de remboursement', status: 'pending' },
  { title: 'Limit AVM', status: 'pending' },
  { title: 'Limit Caution', status: 'pending' },
])

const isReady = ref(false)
watch(isRunning, (newVal) => {
  if (newVal) {
    steps.value.forEach((step) => {
      step.status = 'pending'
    })
  }
   
})

// Watch 2 : Réagit au changement de popupStore.selected_date
watch(
  () => popupStore.selected_date,
  (elt_resp) => {
    selected_date.value = elt_resp;
    console.log('[watch] selected_date =', elt_resp);
  },
  { immediate: true }
);

const runStep_ = async (index) => {
  // Exemple de logique pour chaque étape
  steps.value[index].status = 'running'
  await new Promise((resolve) => setTimeout(resolve, 1000)) // Simule une tâche asynchrone
  steps.value[index].status = 'done'
}

const runAllSteps = async () => {
  runStep()
  // const methode = [runStep, runStep_, runStep_, runStep_, runStep_, runStep_] // pour chaque étape

  // isRunning.value = true

  // for (let i = 0; i < steps.value.length; i++) {

  //   if (typeof methode[i] === 'function') {
  //     try {
  //       await methode[i](i) // attend que chaque runStep termine
  //     } catch (err) {
  //       console.error(`Erreur dans l'étape ${i + 1}`, err)
  //       break // stop si erreur
  //     }
  //   } else {
  //     steps.value[i].status = 'skipped'
  //   }
    
  //   currentStep.value = i + 1
  // }

  // isRunning.value = false
}





const runStep = (index) => {
  return new Promise((resolve, reject) => {
    // steps.value[index].status = 'running'
    var index=null
    const str_date = selected_date.value.label; // ta variable dynamique
    // console.log('str_date',str_date);
    
    const evtSource = new EventSource(`http://192.168.1.212:8000/api/run_encours?str_date=${encodeURIComponent(str_date)}`);
    evtSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
 
          // console.log(data);  
          
          processing_data(data)
          if(data.status_parent){
            index=data.step 
            steps.value[index].status = data.status_parent 
          }
          if(data.status_final==='done'){
            steps.value[index].status = 'done'
            evtSource.close()
            resolve() // Résout la promesse
          }
  
      } catch (e) {
        steps.value[index].status = 'error'
        evtSource.close()
        reject(e)
      }
    }
    evtSource.addEventListener("end", (event) => {
      console.log("Fin reçue :", event.data);
      evtSource.close();
    });

    evtSource.onerror = (error) => {
      console.error("Erreur SSE :", error)
      steps.value[index].status = 'error'
      evtSource.close()
      reject(error)
    }
  })
}



  const processing_data=  (data)=>{  
       
      if (data.status_global==='pending') {
          console.log(data);
          
          if (data.step.data_step) { 
            table_list_processing_init.value=data.step.data_step; 
            const  Target = table_list_processing_init.value.map(table_list_processing_init => ({
              ...table_list_processing_init,
              status: null,
              current: null
            }));
            console.log('Target: ',Target);
            
            // table_list_processing_init.value=Target
          }
          if (data.step.current) {    
            updateStatusIfNameMatches(data.step.name,data.step.status,data.step.current)  
          } 
        } 
    }

  const updateStatusIfNameMatches = (value, status, current) => {
    template.value['len_total'] = table_list_processing_init.value.length
    template.value['percentage']=Math.round((current * 100 / template.value['len_total']) * 100) / 100   
    
    const index = table_list_processing_init.value.findIndex(item => item.name === value)

    // console.log("Taille: ", table_list_processing_init.value.length);
    

    // console.log(table_list_processing_init.value);
    
/*     table_list_processing_init.value[0].status = 'done'
    table_list_processing_init.value[0].current = current 
    if (index !== -1) {
      table_list_processing_init.value[index].status = status
      table_list_processing_init.value[index].current = current 
    } */
    
    
    
    template.value['percentage']=Math.round(((current+1) * 100 / template.value['len_total']) * 100) / 100   
}
 

const getColor = (status) => {
  switch (status) {
    case 'success': return 'green'
    case 'done': return 'green'
    case 'error': return 'red'
    case 'running': return 'white'
    default: return ''
  }
}



const getSubtitle = (status) => {
  switch (status) {
    case 'success': return 'Terminé'
    case 'error': return 'Erreur'
    case 'running': return 'En cours...'
    case 'pending': return 'En attente'
    case 'done': return 'Fait'
    default: return ''
  }
}

 
 
 
</script>

<style scoped>
.transparent-stepper {
  background-color: transparent !important;
  box-shadow: none !important;
}

.hide-scrollbar::-webkit-scrollbar {
  display: none;
}

.hide-scrollbar {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;     /* Firefox */
}

</style>
