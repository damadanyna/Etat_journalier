<template>
  <div class="container_cdi">
    <v-card width="850px" height="400px" style="display: flex; flex-direction: column;" id="v-card">
       <v-card-title class=" "></v-card-title>
      <v-col  class="flex items-center justify-center flex-row">
        <div class="">
          <v-progress-circular :model-value="usePopupStore().precentage" :rotate="360" :size="250" :width="2.5" color="green">
            <div class="flex flex-col items-center justify-center" > 
              <span  class=" text-4xl font-bold" v-if="usePopupStore().precentage!=0">{{ usePopupStore().precentage }}</span>
            <span v-else class=" animate-ping"> Chargement ...</span>
            <span title="Temps de chargement" class="  text-stone-100 font-bold">{{ formattedTime }}</span>
            </div>
          </v-progress-circular>  
        </div>
        <v-col>
          <div class="" style=" padding-right: 30px;  overflow-y: auto; height: 300px;">
            <div v-for="item,i in usePopupStore().cdi_list_stream" :key="i" class=" flex border-b">
              <v-progress-circular v-if="usePopupStore().cdi_list_file_stream[i] && !usePopupStore().cdi_list_file_stream[i].success" :size="15" :width="5" color="green" indeterminate ></v-progress-circular>
              <span v-else-if="usePopupStore().cdi_list_file_stream[i] && usePopupStore().cdi_list_file_stream[i].success" style="padding: 15px; color: #53e053; font-size: 18px;" class="mdi mdi-check-circle" ></span>
              <v-progress-circular v-else  :size="15" :width="5" color="green"  ></v-progress-circular>
              <div v-if="usePopupStore().cdi_list_file_stream[i]"  style=" display: flex; flex-direction: column;">
                <span style=" font-size: 14px; color: white; ">{{item.title}}</span>
                <div style=" display: flex;">

                <span style=" font-size: 10px; color: gray; ">{{ usePopupStore().cdi_list_file_stream[i].task}}</span>
                <span style=" font-size: 10px; color: gray;margin-left: 10px; ">{{ usePopupStore().cdi_list_file_stream[i].row_count}}</span>
                <span v-if="usePopupStore().cdi_list_file_stream[i].total" style=" font-size: 10px; color: gray;margin-left: 10px; ">{{'/'+ usePopupStore().cdi_list_file_stream[i].total}}</span>
                </div>
              </div>
              <div v-else style=" display: flex; flex-direction: column;">
                <span  style=" font-size: 14px; color: gray; ">{{item.title}}</span>
                <span style=" font-size: 10px; color: gray; ">En attente ...</span>
              </div>
            </div>
          </div>
        </v-col>
      </v-col>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted,computed , onBeforeUnmount,watch  } from 'vue'
import { usePopupStore } from '../../stores'
const elapsedSeconds = ref(0)
let timer = null
const interval = ref(null)
const value = ref(0)

// let sound = null

onMounted(() => {
  //  if (sound) {
  //   sound.pause()
  //   sound = null
  // }
  timer = setInterval(() => {
    elapsedSeconds.value++
  }, 1000)
  interval.value = setInterval(() => {
    value.value = value.value === 100 ? 0 : value.value + 10
  }, 1000)
  // console.log(usePopupStore().cdi_list_stream);
})

// watch(
//   () => usePopupStore().precentage,
//   (newVal, oldVal) => {
//     if (newVal !== 0 && oldVal === 0) {
//       // Démarre le son en boucle
//       sound = new Audio('/sound/process_data.mp3') // Doit être dans public/sound/
//       sound.loop = true
//       sound.play().catch(err => {
//         console.error('Erreur de lecture audio :', err)
//       })
//     }

//     if (newVal === 0 && oldVal !== 0 && sound) {
//       // Stoppe le son si le pourcentage revient à zéro
//       sound.pause()
//       sound.currentTime = 0
//       sound = null
//     }
//   }
// )


const formattedTime = computed(() => {
  const hours = String(Math.floor(elapsedSeconds.value / 3600)).padStart(2, '0')
  const minutes = String(Math.floor((elapsedSeconds.value % 3600) / 60)).padStart(2, '0')
  const seconds = String(elapsedSeconds.value % 60).padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
})

onBeforeUnmount(() => {
  
  if (timer) clearInterval(timer)
  if (interval.value) clearInterval(interval.value)
})
</script>

<style scoped>
.container_cdi {
  background-color: rgba(0, 0, 0, 0.5);
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1000;
  width: 100vw;
  height: 100vh;
  display: flex;
  place-items: center;
  justify-content: center;
}

.v-progress-circular {
  margin: 1rem;
}
</style>
