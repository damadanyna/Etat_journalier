<template>
  <div class=" bg_data mr-4    ">
    <div class="flex flex-row justify-end items-center space-x-4">
    <h3 class=" mr-5">Date d'arrêt</h3>
    <div class="text-center">
       
    <v-btn prepend-icon="mdi-calendar-range">
    <template v-slot:prepend>
        <v-icon color="success"></v-icon>
    </template>
        <span class="text-h5">2025-02-28</span>
    </v-btn> 
  </div>
  
    <!-- <daugnut></daugnut> -->
</div>

  </div>
</template>
<script setup>   
// import daugnut from '../doughnut/Dougnut.vue'
  import { ref } from 'vue'
  const items = ['2025-02-28','2025-05-30','2025-06-30','2025-07-04',] 
  const value = ref('2025-02-28')
</script>


<style>
.bg_data{
    background-color: #00000022;
    border-radius: 20px ;
    padding: 10px 20px;
}
</style>