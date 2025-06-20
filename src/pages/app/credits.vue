<template> 
  <v-btn @click="runStep()"
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
            :complete="step.status === 'success'"
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

   <v-col  class="flex items-center justify-center flex-row">
        <div class="">
          <v-progress-circular :model-value="template.precentage" :rotate="360" :size="250" :width="2.5" color="green">
            <div class="flex flex-col items-center justify-center" > 
              <span  class=" text-4xl font-bold" v-if="template.precentage!=0">{{ template.precentage }}</span>
            <span v-else class=" animate-ping"> Chargement ...</span>
            <span title="Temps de chargement" class="  text-stone-100 font-bold">{{ formattedTime }}</span>
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
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
 
const steps = ref([
  { title: 'Initialisation', status: 'pending' },
  { title: 'États des encours', status: 'pending' },
  { title: 'État des remboursements', status: 'pending' },
  { title: 'État prévisionnel de remboursement', status: 'pending' },
  { title: 'Limit AVM', status: 'pending' },
  { title: 'Limit Caution', status: 'pending' },
])

const currentStep = ref(1)
const isRunning = ref(false)
const template= ref([])
const table_list_processing_init= ref([]) 
 
watch(isRunning, (newVal) => {
  if (newVal) {
    steps.value.forEach((step) => {
      step.status = 'pending'
    })
  }
}) 

const runStep = () => {
  const evtSource = new EventSource('http://192.168.1.212:8000/api/run_encours');

  evtSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      // console.log("Step reçu :", data); 
      processing_data(data); 
      // Si la tâche est terminée, on ferme proprement la connexion SSE
      if (data.status === 'done') {
        console.log("Tâche terminée, fermeture du flux SSE.");
        evtSource.close();
      }

    } catch (e) {
      console.error("Erreur JSON SSE :", e);
    }
  };


  evtSource.onerror = (err) => {
    // Ne log l'erreur que si la connexion n'est pas déjà fermée
    if (evtSource.readyState !== EventSource.CLOSED) {
      console.error("Erreur EventSource :", err);
    }
    evtSource.close();
  };

  
};


  const processing_data=  (data)=>{ 
      if (data.status_global==='pending') {
          if (data.step.data_step) { 
            table_list_processing_init.value=data.step.data_step; 
           const  Target = table_list_processing_init.value.map(table_list_processing_init => ({
              ...table_list_processing_init,
              status: null,
              current: null
            }));
            table_list_processing_init.value=Target
          }
          if (data.step.current) {    
            updateStatusIfNameMatches(data.step.name,data.step.status,data.step.current)  
          } 
        } 
    }

  const updateStatusIfNameMatches = (value, status, current) => {
    const index = table_list_processing_init.value.findIndex(item => item.name === value)
    if (index !== -1) {
      table_list_processing_init.value[index].status = status
      table_list_processing_init.value[index].current = current
    }
}

const loading_processing= (i,elt)=>{ 
     table_list_processing_init.value[i]['current']=elt.current
     table_list_processing_init.value[i]['status']= elt.status 
    
     
  }



const runAllSteps = async () => { 
  // isRunning.value = true
  // for (let i = 0; i < steps.value.length; i++) {
  //   currentStep.value = i + 1
  //   await runStep(i)
  // }
  // isRunning.value = false
}

const getColor = (status) => {
  switch (status) {
    case 'success': return 'green'
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
    default: return ''
  }
}

onMounted(() => {
  
})
</script>

<style scoped>
.transparent-stepper {
  background-color: transparent !important;
  box-shadow: none !important;
}
</style>
