<template>
  <div>
    <h2 class="text-h5 mb-4">👥 Liste des utilisateurs</h2>
    
    <v-card elevation="3" class="rounded-lg">
      <v-card-text class="pa-0">
        <template #text>
          <v-text-field v-model="search" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line/>
        </template>
        <v-data-table  :search="search" :headers="headers" :items="users" :items-per-page="10" class="elevation-1" density="comfortable" hover @click:row="(event, { item }) => $emit('select-user', item.id)">
          <template v-slot:item.validate_status="{ item }">
            <v-chip  :color="item.block_status ? 'red' : (item.validate_status ? 'green' : 'orange')"  variant="flat" size="small">
                <v-icon start small>{{ item.block_status ? 'mdi-block-helper' : (item.validate_status ? 'mdi-check-circle' : 'mdi-clock-outline') }}</v-icon>
                {{ item.block_status ? 'Utilisateur bloqué' : (item.validate_status ? 'Compte validé' : 'En attente') }}
            </v-chip>
          </template>

          <template v-slot:item.privillege="{ item }">
            <v-chip :color="getPrivilegeColor(item.privillege)" variant="flat" size="small"> {{ item.privillege }}
            </v-chip>
          </template>

          <template v-slot:item.id="{ item }">
            <span class="font-weight-bold text-blue-darken-2">{{ item.id }}</span>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  users: Array
})

const headers = [
  { title: 'ID', key: 'id', align: 'center', width: '80px' },
  { title: 'Nom d\'utilisateur', key: 'username' },
  { title: 'Immatricule', key: 'immatricule' },
  { title: 'Privilège', key: 'privillege', align: 'center' },
  { title: 'Statut', key: 'validate_status', align: 'center' }
]

const search=ref('')

function getPrivilegeColor(priv) {
  switch (priv?.toLowerCase()) {
    case 'admin': return 'red-lighten-1'
    case 'superadmin': return 'deep-purple-lighten-1'
    case 'user': return 'blue-lighten-1'
    default: return 'grey-lighten-1'
  }
}
</script>

<style scoped>
:deep(.v-data-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.v-data-table-row) {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

:deep(.v-data-table-row:hover) {
  background-color: #f5f5f5;
}

h2 {
  font-weight: 600;
}

:deep(.v-chip) {
  font-weight: 500;
}
</style>