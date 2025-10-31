<template>
  <v-card class="pa-4 history-card" outlined>
    <v-card-title class="text-h6">Historique des insertions</v-card-title>
    <v-divider></v-divider>

    <v-list class="history-list">
      <v-list-item
        v-for="item in history"
        :key="item.label"
        @click="selectHistory(item)"
        class="d-flex align-center justify-space-between"
      >
        <!-- Nom de la table -->
        <v-list-item-title>{{ item.label }}</v-list-item-title>

        <!-- Statuts dynamiques -->
        <div class="d-flex gap-2">
          <v-chip
            v-for="status in statusKeys"
            :key="status.key"
            :color="item[status.key] ? 'green' : 'red'"
            dark
            small
          >
            {{ status.label }}
          </v-chip>
        </div>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script setup>
import { ref, onMounted, defineExpose } from "vue"
import axios from "axios"

const history = ref([])

const statusKeys = [
  { key: "dat_status", label: "DAT" },
  { key: "dav_status", label: "DAV" },
  { key: "epr_status", label: "EPR" },
]

const fetchHistory = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/history/liste")
    history.value = res.data.history || []
  } catch (err) {
    console.error("Erreur lors du chargement de l'history_insert:", err)
  }
}

const emit = defineEmits(["select"])
const selectHistory = (item) => emit("select", item)

defineExpose({ fetchHistory, history })

onMounted(fetchHistory)
</script>

<style scoped>
.history-card {
  max-height: 400px; /* hauteur fixe du bloc */
  overflow-y: auto;  /* scroll vertical */
  scrollbar-width: thin;
}

/* pour un scroll plus esthétique */
.history-card::-webkit-scrollbar {
  width: 8px;
}
.history-card::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}
</style>
