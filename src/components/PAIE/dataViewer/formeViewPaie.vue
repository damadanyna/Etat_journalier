<template>
  <v-dialog 
    v-model="dialog" 
    width="450"
    @update:modelValue="onDialogUpdate"   
  >
    <v-card>
      <v-card-title class="text-h6">Détail</v-card-title>

      <v-card-text>
        <pre>{{ props.data }}</pre>
      </v-card-text>

      <v-card-actions>
        <v-btn text class="ms-auto" @click="closeDialog">
          OK
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  data: { type: Object, default: null }
});

const emit = defineEmits(["close"]);

const dialog = ref(false);

// Ouvre automatiquement si une ligne est sélectionnée
watch(() => props.data, (v) => {
  if (v) dialog.value = true;
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
