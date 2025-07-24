<template>
  <div class=" bg_data mr-4    ">

    

    <div class="flex flex-row justify-end items-center space-x-4">
        <div class="text-center mr-14"> 
          <v-btn prepend-icon=" mdi-share-variant" @click="exportToExcel">
              <span class="text-md">Exporter</span>
          <template v-slot:prepend>
              <v-icon color="success"></v-icon>
          </template>
          </v-btn> 
        </div> 

        <h3 class=" mr-5 text-xl">Date d'arrêt</h3>
        <div class="text-center">
            
          <v-btn prepend-icon="mdi-calendar-range">
          <template v-slot:prepend>
              <v-icon color="success"></v-icon>
          </template>
              <span class="text-2xl">2025-02-28</span>
          </v-btn> 
        </div> 
        <!-- <daugnut></daugnut> -->
    </div>

  </div>
</template>
<script setup>   
// import daugnut from '../doughnut/Dougnut.vue'
  import { ref, watch } from 'vue'
  import { usePopupStore } from '../stores' 
  import * as XLSX from 'xlsx'
  
  const listes_encours_credits = ref([])
  const popupStore = usePopupStore()
  const items = ['2025-02-28','2025-05-30','2025-06-30','2025-07-04',] 
  const value = ref('2025-02-28')

  watch(
    () => popupStore.encours_actual_data,
    (elt_resp) => {
      // console.log('ions');
      listes_encours_credits.value = elt_resp
      // console.log(elt_resp);
        
    },
    { immediate: true }
  )


function exportToExcel() {
  const data = listes_encours_credits.value

  if (!data || data.length === 0) {
    alert("Aucune donnée à exporter")
    return
  }

  // 1. Créer une feuille à partir des objets JS
  const worksheet = XLSX.utils.json_to_sheet(data)

  // 2. Créer le classeur contenant cette feuille
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, "Encours")

  // 3. Sauvegarder sous forme de fichier xlsx
  XLSX.writeFile(workbook, "encours_credits.xlsx")
}

</script>


<style scoped>
.bg_data{
    background-color: #00000022;
    border-radius: 20px ;
    padding: 10px 20px;
}
</style>