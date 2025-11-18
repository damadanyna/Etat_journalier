<template>
  <v-card class="pa-4 rounded-xl elevation-3 history-card">

    <v-card-title class="text-h6 font-weight-bold">
      Historique des insertions
    </v-card-title>

    <v-divider></v-divider>

    <v-list class="history-list">

      <v-list-item
        v-for="item in history"
        :key="item.label"
        class="history-item rounded-lg mb-2"
        @click="selectHistory(item)"
      >
        <v-list-item-content>
          <v-list-item-title class="font-weight-medium">
            {{ item.label }}
          </v-list-item-title>
        </v-list-item-content>

        <v-list-item-action>
          <div class="d-flex gap-2">
            <v-chip
              v-for="status in statusKeys"
              :key="status.key"
              :color="item[status.key] ? 'green' : 'red'"
              variant="flat"
              size="small"
            >
              {{ status.label }}
            </v-chip>
          </div>
        </v-list-item-action>
      </v-list-item>

    </v-list>
  </v-card>
</template>

<script setup>
import { ref, inject, onMounted } from "vue"
import axios from "axios"

const api = inject("api")
const history = ref([])

const statusKeys = [
  { key: "dat_status", label: "DAT" },
  { key: "dav_status", label: "DAV" },
  { key: "epr_status", label: "EPR" },
  { key: "dec_status", label: "DEC" },
]

const fetchHistory = async () => {
  try {
    const res = await axios.get(`${api}/api/history/liste`)
    history.value = res.data.history || []
  } catch (err) {
    console.error("Erreur lors du chargement de l'historique :", err)
  }
}

const emit = defineEmits(["select"])
const selectHistory = (item) => emit("select", item)

defineExpose({ fetchHistory, history })

onMounted(fetchHistory)
</script>

<style scoped>
.history-card {
  max-height: 450px;
  overflow-y: auto;
}

.history-item {
  cursor: pointer;
  transition: 0.2s;
}

.history-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.history-card::-webkit-scrollbar {
  width: 6px;
}
.history-card::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}
</style>
