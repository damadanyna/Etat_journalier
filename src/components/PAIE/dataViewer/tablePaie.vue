<template>
  
</template>

<script setup>
import { usePopupStore } from '../../../stores';
import { watch, ref,inject} from 'vue';

const api = inject('api') 
const loading=ref(true)
const popupStore = usePopupStore()

const fetchCapitalSums = async (matricule = null, dateStr = null) => {
  loading.value = true;

  try {
    // Construire l'URL avec paramètres query
    let url = `${api}/api/get_paie_list`;
    const params = new URLSearchParams();
    if (matricule) params.append("matricule", matricule);
    if (dateStr) params.append("dateStr", dateStr);

    if ([...params].length > 0) {
      url += `?${params.toString()}`;
    }

    const response = await fetch(url);
    const json = await response.json();

    if (!response.ok) throw new Error(json.detail || "Erreur inconnue");

    // Nouvelle structure : data.users
    const capitalData = json.data?.users || [];
    console.log(json);
    // Tu peux continuer à traiter capitalData ici...

  } catch (err) {
    console.log(err.message || "Erreur inconnue");
    console.error("Erreur fetchCapitalSums:", err);

  } finally {
    loading.value = false;
  }
};



// Watch sur la date sélectionnée
watch(
  () => popupStore.selected_date,
  () => { 
      fetchCapitalSums(null, popupStore.selected_date) 
  },
  { immediate: true }
)
 
</script>

<style>

</style>