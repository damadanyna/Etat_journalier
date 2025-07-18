<template>
    <v-toolbar color=" " class=" bg-transparent" title="Encours des crédits">
      
      <div class="flex items-center gap-1 green_transparent mr-2 px-5 rounded-md">
        <v-icon icon="mdi-database" />
        <span v-if="date_last_import_file!=''" title="Dernière importation"  >{{ formatDateString(date_last_import_file) }}</span>
        <span v-else>Recupération ...</span>
      </div>
  
      <v-btn stacked>
        <v-avatar image="https://avatars.githubusercontent.com/u/60171474?v=4"></v-avatar>
      </v-btn>
   
    </v-toolbar>
</template>
<script setup>
import { onMounted, ref } from 'vue';

const date_last_import_file = ref('');

const get_last_import_file = async () => {
  try {
    const response = await fetch('http://192.168.1.212:8000/api/get_last_import_file', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`Erreur HTTP : ${response.status}`);
    }

    const data = await response.json(); 
    console.log(data);
    

    // ✅ Exemple de réponse attendue : { date: "2025-07-18" }
    if (data?.response) {
      date_last_import_file.value = data.response.label;
      console.log("✅ Dernière date de chargement :", date_last_import_file.value);
      
    } else {
      console.warn("⚠️ Réponse reçue mais sans champ 'date' :", data);
    }

  } catch (error) {
    console.error("❌ Erreur lors du chargement du fichier dans la base :", error);
  }
};

const formatDateString=(rawDate)=> {
  if (!/^\d{8}$/.test(rawDate)) {
    console.warn("Date invalide :", rawDate);
    return null;
  }

  const year = rawDate.slice(0, 4);
  const month = rawDate.slice(4, 6);
  const day = rawDate.slice(6, 8);

  return `${year}-${month}-${day}`;
}

onMounted(() => {
  get_last_import_file();
})
</script>

<style>
  .green_transparent {
    background-color: #00dc54a4;
  }
</style>