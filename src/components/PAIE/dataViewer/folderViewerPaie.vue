<template>
  <div class="flex flex-row h-[89vh] px-3">
    <div v-if="hasFolders" class="grid grid-cols-5 gap-5 w-full h-2.5">
      <div v-for="item,i in props.data" :key="i" class="cursor-pointer">
        <button
          @click="selectDate(item.label)"
          class="flex w-full flex-col items-center text-center rounded-lg px-3 py-2 transition-colors"
          :style="getFolderItemStyle(item.label)"
        >
          <span class="mdi mdi-folder-arrow-down text-7xl" :style="getFolderIconStyle(item.label)"></span>
          <span :style="getFolderTextStyle(item.label)">{{ item.label }}</span>
        </button>
      </div>
    </div>
    <div v-else class="flex w-full h-full items-center justify-center pr-6">
      <div class="flex flex-col items-center text-center max-w-sm text-stone-600">
        <span class="mdi mdi-file-document-remove-outline text-7xl text-stone-400"></span>
        <span class="mt-3 text-lg font-semibold text-stone-700">Fiche de paie vide</span>
        <span class="text-sm">Aucune fiche de paie n'est disponible pour le moment.</span>
      </div>
    </div>
    <v-divider vertical></v-divider>
    <div class="flex max-w-[55%] justify-center w-full items-center overflow-auto">
      <FactureViewerPaie v-if="hasPaieData" :data="dataPaie" class="w-full"></FactureViewerPaie>
      <div v-else class="flex items-center w-full h-full justify-center">
        <div class="flex flex-col items-center text-center max-w-sm text-stone-600">
          <span class="mdi mdi-file-document-remove-outline text-7xl text-stone-400"></span>
          <span class="mt-3 text-lg font-semibold text-stone-700">{{ emptyStateTitle }}</span>
          <span class="text-sm">{{ emptyStateMessage }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup >
import FactureViewerPaie from './factureViewerPaie.vue';
import { computed, ref, inject } from 'vue';
import { usePopupStore } from '../../../stores';
import { useActivityLogger } from '@/composables/useActivityLogger'
import { safeReadJson } from '@/utils/http'

const dataPaie=ref([])
const selectedDate = ref('')
const api = inject('api') 
const popupStore = usePopupStore() 
const { logUserActivity } = useActivityLogger(api)
const normalizePayrollDate = (value) => {
  const rawValue = String(value || '').trim()
  if (/^\d{2}-\d{4}$/.test(rawValue)) {
    const [month, year] = rawValue.split('-')
    return `${month}${year}`
  }
  if (/^\d{6}$/.test(rawValue)) {
    return rawValue
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(rawValue)) {
    const [year, month] = rawValue.split('-')
    return `${month}${year}`
  }
  if (/^\d{8}$/.test(rawValue)) {
    return `${rawValue.slice(4, 6)}${rawValue.slice(0, 4)}`
  }
  return rawValue.replace(/-/g, '')
}


const fetch_all_paie = async (matricule = null, dateStr = null) => {
  const normalizedDate = normalizePayrollDate(dateStr)
  dataPaie.value = []
  
  // console.log(dateStr);
  
  try {
    if (!/^\d{6}$/.test(normalizedDate)) {
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

    if (!response.ok) {
      const errorMessage = json.detail || "Erreur lors de la récupération des données."
      throw new Error(errorMessage)
    }
    if (!Array.isArray(json.data?.users)) throw new Error("Réponse API invalide")
  
    dataPaie.value = [ ...json.data.users, { "upload_date": normalizedDate }];

  } catch (err) {
    dataPaie.value = []
    console.log(err.message || "Erreur inconnue");
    console.error("Erreur fetch_all_paie:", err);

  } finally {
    // loading.value = false;
  }
};


const props = defineProps({
  data: { type: Array, default: () => [] }
});

const hasFolders = computed(() => Array.isArray(props.data) && props.data.length > 0)
const hasPaieData = computed(() => dataPaie.value.length > 1)
const isSelectedFolder = (label) => selectedDate.value === label
const getFolderItemStyle = (label) => ({
  backgroundColor: isSelectedFolder(label) ? 'rgba(34, 197, 94, 0.05)' : 'transparent'
})
const getFolderIconStyle = (label) => ({
  color: isSelectedFolder(label) ? 'rgb(22, 163, 74)' : 'rgb(120, 113, 108)'
})
const getFolderTextStyle = (label) => ({
  color: isSelectedFolder(label) ? 'rgb(21, 128, 61)' : 'inherit',
  fontWeight: isSelectedFolder(label) ? '600' : '400'
})
const emptyStateTitle = computed(() => {
  if (!hasFolders.value) {
    return 'Fiche de paie vide'
  }
  if (selectedDate.value) {
    return 'Aucune fiche de paie trouvée'
  }
  return 'Aucune fiche sélectionnée'
})
const emptyStateMessage = computed(() => {
  if (!hasFolders.value) {
    return "Aucune fiche de paie n'est disponible pour le moment."
  }
  if (selectedDate.value) {
    return `Aucune fiche de paie n'est disponible pour la période ${selectedDate.value}.`
  }
  return 'Sélectionnez une période de paie pour afficher votre fiche.'
})

const selectDate = (date) => {
    selectedDate.value = date
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