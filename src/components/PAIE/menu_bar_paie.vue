<template>
  <v-toolbar color=" " class="bg-transparent" title="Pay By"> 
     <user_btn_profil class=" mx-4"></user_btn_profil> 
  </v-toolbar>
</template>

<script setup>
import user_btn_profil from '../user_btn_profil.vue'
import { ref, watch, onMounted,inject,computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePopupStore } from '../../stores'
import * as XLSX from 'xlsx'
import { useRouter } from 'vue-router'


const route = useRoute()
const api = inject('api') 
const selectedDate = ref('Chargement en cours...')
const menu = ref(false)
const popupStore = usePopupStore()
const exporting = ref(false)
const router = useRouter()

const historyDates  = ref([])


 
 
  

 
</script>

<style>
.green_transparent {
  background-color: #00dc54a4;
}
</style>
