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
                :color="user.block_status ? 'red' : (user.validate_status ? 'green' : 'orange')" 
                variant="flat"
                size="small"
              >
                <v-icon start small>
                  {{ user.block_status ? 'mdi-block-helper' : (user.validate_status ? 'mdi-check-circle' : 'mdi-clock-outline') }}
                </v-icon>
                {{ user.block_status ? 'Utilisateur bloqué' : (user.validate_status ? 'Compte validé' : 'En attente') }}
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
            @click="showDialog = true"
            color="success"
            size="large"
            class="validate-btn"
          >

            <v-icon start>mdi-block-helper</v-icon>
        {{ user.block_status ? "Debloquer" : "Valider" }} l'utilisateur
      </v-btn>
          
          <!-- MODALE DE VALIDATION -->
          <v-dialog v-model="showDialog" max-width="450">
            <v-card>
              <v-card-title class="text-h6">
                Confirmation {{ user.block_status ? "Deblockage" : "Validation" }} 
              </v-card-title>

              <v-card-text>
                <p><strong>Utilisateur :</strong> {{ user.username }}</p>

                <v-select
                  v-model="selectedRole"
                  :items="['user', 'admin']"
                  label="Attribuer un rôle"
                  variant="outlined"
                />

                <v-text-field
                  v-model="adminPassword"
                  type="password"
                  label="Mot de passe administrateur"
                  variant="outlined"
                />
              </v-card-text>

              <v-card-actions>
                <v-btn variant="text" @click="showDialog = false">Annuler</v-btn>
                <v-btn color="primary" @click="confirmValidation">Confirmer</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>

      <!-- BOUTON BLOQUER/DEBLOQUER -->
      <v-btn
        v-if="user.validate_status && !loading"
        color="error"
        size="large"
        class="block-user-btn mt-4"
        @click="showBlockDialog = true"
      >
        <v-icon start>mdi-block-helper</v-icon>
        {{ user.block_status ? "Débloquer" : "Bloquer" }} l'utilisateur
      </v-btn>

      <!-- MODALE BLOQUER/DEBLOQUER -->
      <v-dialog v-model="showBlockDialog" max-width="450">
        <v-card>
          <v-card-title class="text-h6">
            {{ user.block_status ? "Débloquer" : "Bloquer" }} l'utilisateur
          </v-card-title>

          <v-card-text>
            <p><strong>Utilisateur :</strong> {{ user.username }}</p>
            <v-text-field
              v-model="adminPassword"
              type="password"
              label="Mot de passe administrateur"
              variant="outlined"
            />
          </v-card-text>

          <v-card-actions>
            <v-btn variant="text" @click="showBlockDialog = false">Annuler</v-btn>
            <v-btn color="primary" @click="confirmBlockUser">Confirmer</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

          <!-- BOUTON MODIFIER ROLE -->
      <v-btn
        v-if="user.validate_status && !loading"
        color="warning"
        size="large"
        class="modify-role-btn mt-4"
        @click="showRoleDialog = true"
      >
        <v-icon start>mdi-account-edit</v-icon>
        Modifier le rôle
      </v-btn>

      <!-- MODALE DE MODIFICATION ROLE -->
      <v-dialog v-model="showRoleDialog" max-width="450">
        <v-card>
          <v-card-title class="text-h6">
            Modification du rôle
          </v-card-title>

          <v-card-text>
            <p><strong>Utilisateur :</strong> {{ user.username }}</p>

            <v-select
              v-model="newRole"
              :items="['user', 'admin', 'superadmin']"
              label="Choisir un rôle"
              variant="outlined"
            />

            <v-text-field
              v-model="adminPassword"
              type="password"
              label="Mot de passe administrateur"
              variant="outlined"
            />
          </v-card-text>

          <v-card-actions>
            <v-btn variant="text" @click="showRoleDialog = false">Annuler</v-btn>
            <v-btn color="primary" @click="confirmRoleChange">Confirmer</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>


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

const showDialog = ref(false)
const selectedRole = ref('user')
const adminPassword = ref('')



const confirmValidation = async () => {
  loading.value = true
  showDialog.value = false
  errorMsg.value = ''
  successMsg.value = ''

  try {
    const formData = new FormData()
    formData.append('username', user.value.username)
    formData.append('role', selectedRole.value)
    formData.append('admin_password', adminPassword.value)

    const response = await axios.post(`${api}/api/validate_user`, formData, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })

    successMsg.value = `Utilisateur validé avec le rôle "${selectedRole.value}"`

    await fetchUser()

  } catch (e) {
    errorMsg.value = "Erreur : Mot de passe incorrect ou privilège insuffisant"
  } finally {
    loading.value = false
  }
}

const showRoleDialog = ref(false)
const newRole = ref(user.value?.privillege || 'user')

const confirmRoleChange = async () => {
  loading.value = true
  showRoleDialog.value = false
  errorMsg.value = ''
  successMsg.value = ''

  try {
    const formData = new FormData()
    formData.append('username', user.value.username)
    formData.append('role', newRole.value)
    formData.append('admin_password', adminPassword.value)

    const response = await axios.post(`${api}/api/update_user_role`, formData, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })

    successMsg.value = `Rôle modifié avec succès en "${newRole.value}"`
    await fetchUser()

  } catch (e) {
    errorMsg.value = "Erreur : Mot de passe incorrect ou privilège insuffisant"
  } finally {
    loading.value = false
  }
}


const showBlockDialog = ref(false)

const confirmBlockUser = async () => {
  loading.value = true
  showBlockDialog.value = false
  errorMsg.value = ''
  successMsg.value = ''

  try {
    const formData = new FormData()
    formData.append('username', user.value.username)
    formData.append('admin_password', adminPassword.value)

    const response = await axios.post(`${api}/api/block_user`, formData, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })

    successMsg.value = response.data.message
    await fetchUser()
  } catch (e) {
    errorMsg.value = "Erreur : Mot de passe incorrect ou privilège insuffisant"
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.back-btn {
  align-self: flex-start;
  margin-bottom: 10px;
  transition: transform 0.2s;
}

.back-btn:hover {
  transform: translateX(-3px);
}

.user-card {
  margin-top: 20px;
  overflow: hidden;
  transition: box-shadow 0.3s;
}

.user-card:hover {
  box-shadow: 0px 8px 24px rgba(0,0,0,0.15);
}

.user-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 0;
}

.user-avatar {
  font-weight: bold;
  font-size: 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  text-transform: uppercase;
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
  margin-bottom: 12px;
}

.info-list {
  background: transparent;
}

.info-list :deep(.v-list-item) {
  border-radius: 8px;
  margin-bottom: 6px;
  transition: background-color 0.2s;
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
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}

.actions-section v-btn {
  min-width: 220px;
  font-weight: 500;
  transition: transform 0.2s, box-shadow 0.2s;
}

.actions-section v-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.v-dialog .v-card {
  border-radius: 16px;
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
  
  .header-section {
    text-align: center;
    align-items: center;
  }

  .back-btn {
    align-self: center;
  }
  
  .user-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .user-badges {
    justify-content: center;
  }

  .actions-section {
    gap: 16px;
  }
}

</style>