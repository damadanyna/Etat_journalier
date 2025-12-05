<template>
  <div v-if="dialog" class=" absolute top-0 left-0 max-h-[100vh] flex w-full h-full items-center justify-center"> 
    <div class="flex absolute top-0 left-0 w-full h-full blur-md   bg-black opacity-40 z-10" @click="closeDialog()"></div>
    <div class="fex overflow-auto w-[54vw] z-30 max-h-[90vh]">
      <FactureViewerPaie v-if="dialog" :data="props.data"></FactureViewerPaie>
    </div>
  </div>
    
</template>

<script setup>
import { ref, watch } from "vue";
import FactureViewerPaie from "./factureViewerPaie.vue";


const props = defineProps({
  data: { type: Object, default: null }
});

const emit = defineEmits(["close"]);

const dialog = ref(false);

// Ouvre automatiquement si une ligne est sélectionnée
watch(() => props.data, (v) => {
  if (v) dialog.value = true;
  console.log(props.data);
 
  
});

// Ferme via bouton OK
const closeDialog = () => {
  dialog.value = false;
};

// Ferme via overlay ou Échap
const onDialogUpdate = (value) => {
  if (!value) {
    emit("close");
  }
};
</script>
