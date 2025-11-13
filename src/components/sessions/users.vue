<!-- filepath: d:\Etat_journalier\src\components\sessions\users.vue -->
<template>
  <div>
    <h2 class="text-h5 mb-4">👥 Liste des utilisateurs</h2>
    
    <v-card elevation="3" class="rounded-lg">
      <v-card-text class="pa-0">
        <v-data-table
          :headers="headers"
          :items="users"
          :items-per-page="10"
          class="elevation-1"
          density="comfortable"
          hover
          @click:row="(event, { item }) => $emit('select-user', item.id)"
        >
          <template v-slot:item.validate_status="{ item }">
            <v-chip
              :color="item.validate_status ? 'green' : 'orange'"
              variant="flat"
              size="small"
            >
              <v-icon start size="18">
                {{ item.validate_status ? 'mdi-check-circle' : 'mdi-timer-sand' }}
              </v-icon>
              {{ item.validate_status ? 'Validé' : 'En attente' }}
            </v-chip>
          </template>

          <template v-slot:item.privillege="{ item }">
            <v-chip
              :color="getPrivilegeColor(item.privillege)"
              variant="flat"
              size="small"
            >
              {{ item.privillege }}
            </v-chip>
          </template>

          <template v-slot:item.id="{ item }">
            <span class="font-weight-bold text-blue-darken-2">
              #{{ item.id }}
            </span>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
defineProps({
  users: Array
})

// Configuration des colonnes (déclarée dans le template)
const headers = [
  { title: 'ID', key: 'id', align: 'center', width: '80px' },
  { title: 'Nom d\'utilisateur', key: 'username' },
  { title: 'Immatricule', key: 'immatricule' },
  { title: 'Privilège', key: 'privillege', align: 'center' },
  { title: 'Statut', key: 'validate_status', align: 'center' }
]

// Fonction pour les couleurs des privilèges
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
  color: #2b2b2b;
}

:deep(.v-chip) {
  font-weight: 500;
}
</style>