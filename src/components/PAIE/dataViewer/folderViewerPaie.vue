<template>
  <div class="flex flex-row h-[89vh] px-3">
    
    <div class=" grid grid-cols-5 gap-5 w-full h-2.5 ">

        <div v-for="item,i in props.data" :key="i" class=" cursor-pointer  ">
          <button @click="selectDate(item.label)"  class="flex flex-col"> 
            <span class="mdi mdi-folder-arrow-down text-7xl text-stone-500" ></span>
            <span>{{item.label}}</span>
          </button> 
        </div> 
    </div>
    <v-divider vertical></v-divider>
    <div  class="flex max-w-[55%] justify-center w-full items-center overflow-auto  ">
      <FactureViewerPaie  v-if="dataPaie[0]"  :data="dataPaie" class=" w-full"></FactureViewerPaie>
      <div v-else class="flex items-center w-full h-full justify-center">
        <div class=" flex flex-col items-center">    
          <span class="mdi mdi-email-seal-outline text-7xl  text-stone-800"></span>
          <span class=" text-stone-700 font-bold"> Auccun fichier trouvé</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup >
import FactureViewerPaie from './factureViewerPaie.vue';
import { ref, inject } from 'vue';  
import { usePopupStore } from '../../../stores';
import { useActivityLogger } from '@/composables/useActivityLogger'
import { safeReadJson } from '@/utils/http'

const dataPaie=ref([])
const api = inject('api') 
const popupStore = usePopupStore() 
const { logUserActivity } = useActivityLogger(api)
const normalizePayrollDate = (value) => String(value || '').replace(/-/g, '').trim()


const fetch_all_paie = async (matricule = null, dateStr = null) => {
  const normalizedDate = normalizePayrollDate(dateStr)
  
  // console.log(dateStr);
  
  try {
    if (!/^\d{8}$/.test(normalizedDate)) {
      dataPaie.value = []
      return
    }

    // Construire l'URL avec paramètres query
    let url = `${api}/api/get_paie_list`;
    const params = new URLSearchParams();
    if (matricule) params.append("matricule", matricule);
    params.append("dateStr", normalizedDate);

    if ([...params].length > 0) {
      url += `?${params.toString()}`;
    }

    const response = await fetch(url);
    const json = await safeReadJson(response)

    if (!response.ok) throw new Error(json.detail || "Erreur inconnue");
    if (!Array.isArray(json.data?.users)) throw new Error("Réponse API invalide")
  
    
    
    dataPaie.value = [ ...json.data.users, { "upload_date": normalizedDate }];
     
    

  } catch (err) {
    console.log(err.message || "Erreur inconnue");
    console.error("Erreur fetch_all_paie:", err);

  } finally {
    // loading.value = false;
  }
};


const props = defineProps({
  data: { type: Object, default: null }
});

const selectDate = (date) => {
    const matricule = popupStore.user_access.name 
    logUserActivity({
      action: 'view_bulletin_paie',
      entityType: 'bulletin_paie',
      entityId: matricule,
      description: `Consultation du bulletin de paie de ${matricule} pour la période ${date}`,
    })
    fetch_all_paie(matricule, date) 
}
</script>

<style>

</style>