<template>
  <div v-if="user" class="user-details-container">
    <div class="header-section">
      <v-btn 
        @click="$emit('back')" 
        color="primary" 
        variant="text"
        class="back-btn"
      >
        <v-icon start>mdi-arrow-left</v-icon>
        Retour à la liste
      </v-btn>
      <h1 class="text-h4 font-weight-bold primary--text">
         Profil Utilisateur
      </h1>
    </div>

    <v-card elevation="4" class="rounded-xl user-card">
      <v-card-text>
        <div class="user-header">
          <v-avatar color="primary" size="64" class="user-avatar">
            <span class="text-h5 white--text">
              {{ user.username?.charAt(0).toUpperCase() }}
            </span>
          </v-avatar>
          <div class="user-title">
            <h2 class="text-h5 font-weight-bold">{{ user.username }}</h2>
            <div class="user-badges">
              <v-chip 
                :color="getPrivilegeColor(user.privillege)" 
                variant="flat"
                size="small"
              >
                <v-icon start small>mdi-shield-account</v-icon>
                {{ user.privillege }}
              </v-chip>
              <v-chip 
                :color="user.validate_status ? 'green' : 'orange'" 
                variant="flat"
                size="small"
              >
                <v-icon start small>
                  {{ user.validate_status ? 'mdi-check-circle' : 'mdi-clock-outline' }}
                </v-icon>
                {{ user.validate_status ? 'Compte validé' : 'En attente' }}
              </v-chip>
            </div>
          </div>
        </div>

        <v-divider class="my-6"></v-divider>
        
        <v-row>
          <v-col cols="12" md="6">
            <h3 class="text-h6 mb-4 section-title">
              <v-icon color="primary" class="mr-2">mdi-account-details</v-icon>
              Informations personnelles
            </h3>
            
            <v-list density="comfortable" class="info-list">
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="grey">mdi-identifier</v-icon>
                </template>
                <v-list-item-title class="font-weight-bold">ID</v-list-item-title>
                <v-list-item-subtitle class="text-value">#{{ user.id }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="grey">mdi-badge-account</v-icon>
                </template>
                <v-list-item-title class="font-weight-bold">Nom d'utilisateur</v-list-item-title>
                <v-list-item-subtitle class="text-value">{{ user.username }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="grey">mdi-car</v-icon>
                </template>
                <v-list-item-title class="font-weight-bold">Immatricule</v-list-item-title>
                <v-list-item-subtitle class="text-value">{{ user.immatricule }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-col>

          <v-col cols="12" md="6">
            <h3 class="text-h6 mb-4 section-title">
              <v-icon color="primary" class="mr-2">mdi-account-cog</v-icon>
              Informations du compte
            </h3>
            
            <v-list density="comfortable" class="info-list">
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="grey">mdi-calendar-plus</v-icon>
                </template>
                <v-list-item-title class="font-weight-bold">Créé le</v-list-item-title>
                <v-list-item-subtitle class="text-value">{{ formatDate(user.created_at) }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item v-if="user.validate_at">
                <template v-slot:prepend>
                  <v-icon color="grey">mdi-calendar-check</v-icon>
                </template>
                <v-list-item-title class="font-weight-bold">Validé le</v-list-item-title>
                <v-list-item-subtitle class="text-value">{{ formatDate(user.validate_at) }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item v-if="user.validate_by">
                <template v-slot:prepend>
                  <v-icon color="grey">mdi-account-check</v-icon>
                </template>
                <v-list-item-title class="font-weight-bold">Validé par</v-list-item-title>
                <v-list-item-subtitle class="text-value">{{ user.validate_by }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>

        <v-divider class="my-6"></v-divider>
        
        <div class="actions-section">
          <v-btn
            v-if="!user.validate_status && !loading"
            @click="validateUser"
            color="success"
            size="large"
            class="validate-btn"
          >
            <v-icon start>mdi-check-circle</v-icon>
            Valider cet utilisateur
          </v-btn>

          <v-progress-circular
            v-if="loading"
            indeterminate
            color="primary"
            class="mx-4"
          ></v-progress-circular>

          <v-alert
            v-if="successMsg"
            type="success"
            variant="tonal"
            class="mt-4"
          >
            {{ successMsg }}
          </v-alert>

          <v-alert
            v-if="errorMsg"
            type="error"
            variant="tonal"
            class="mt-4"
          >
            {{ errorMsg }}
          </v-alert>
        </div>
      </v-card-text>
    </v-card>
  </div>

  <div v-else class="loading-container">
    <v-progress-circular
      indeterminate
      color="primary"
      size="64"
    ></v-progress-circular>
    <p class="text-h6 mt-4">Chargement des informations...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, inject } from 'vue'
import axios from 'axios'
const api = inject('api') 

const props = defineProps({
  userId: Number
})

const user = ref(null)
const loading = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const fetchUser = async () => {
  try {
    const response = await axios.get(`${api}/api/user/${props.userId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    user.value = response.data.user
  } catch (e) {
    errorMsg.value = "Erreur lors du chargement de l'utilisateur"
  }
}

const validateUser = async () => {
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const formData = new FormData()
    formData.append('username', user.value.username)
    await axios.post(`${api}/api/validate_user`, formData, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    successMsg.value = "Utilisateur validé avec succès"
    await fetchUser()
  } catch (e) {
    errorMsg.value = "Erreur lors de la validation"
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getPrivilegeColor = (priv) => {
  switch (priv?.toLowerCase()) {
    case 'admin': return 'red'
    case 'superadmin': return 'deep-purple'
    case 'user': return 'blue'
    default: return 'grey'
  }
}

onMounted(fetchUser)
watch(() => props.userId, fetchUser)
</script>

<style scoped>
.user-details-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.header-section {
  margin-bottom: 30px;
  text-align: center;
}

.back-btn {
  margin-bottom: 20px;
}

.user-card {
  margin-top: 20px;
  overflow: hidden;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 0;
}

.user-title {
  flex: 1;
}

.user-badges {
  display: flex;
  gap: 10px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.section-title {
  display: flex;
  align-items: center;
  color: #1960a8;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 8px;
}

.info-list {
  background: transparent;
}

.info-list :deep(.v-list-item) {
  border-radius: 8px;
  margin-bottom: 4px;
}

.info-list :deep(.v-list-item:hover) {
  background-color: #f5f5f5;
}

.text-value {
  font-size: 1rem !important;
  font-weight: 500;
}

.actions-section {
  text-align: center;
  padding: 20px 0;
}

.validate-btn {
  min-width: 200px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #666;
}

/* Responsive */
@media (max-width: 768px) {
  .user-details-container {
    padding: 10px;
  }
  
  .user-header {
    flex-direction: column;
    text-align: center;
  }
  
  .user-badges {
    justify-content: center;
  }
}
</style>