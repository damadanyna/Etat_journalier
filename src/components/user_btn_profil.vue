<template>
  <div class="text-center">
    <v-menu
      v-model="menu"
      :close-on-content-click="false"
      location="bottom"
    >
      <template v-slot:activator="{ props }">
        <v-btn
          color="green"
          v-bind="props"
          icon="mdi mdi-cog-box"
          style="font-size: 24px;"
        > 
        </v-btn>
      </template>

      <v-card min-width="300">
        <v-list>
          <v-list-item
            prepend-avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSIFYgpCPMtvHYo7rQ8fFSEgLa1BO78b_9hHA&s"
            subtitle="Compte"
            :title="popupStore.user_access.name"
          >
            <template v-slot:append>
              <v-btn
                class=" text-red"
                icon="mdi mdi-power"
                variant="text"
                @click="logout()"
              ></v-btn>
            </template>
          </v-list-item>
        </v-list>

        <v-divider></v-divider>

        <v-list>
          <v-list-item v-if="canChangeOwnPassword" @click="openPasswordDialog">
            <template #prepend>
              <v-icon color="primary">mdi-lock-reset</v-icon>
            </template>
            <v-list-item-title>Changer mon mot de passe</v-list-item-title>
          </v-list-item>

          <v-list-item>
            <v-switch
              v-model="isDark"
              color="green"
              label="Mode Sombre"
              hide-details 
              @update:modelValue="toggleTheme"
            ></v-switch>
          </v-list-item> 
        </v-list> 
      </v-card>
    </v-menu>

    <v-dialog v-model="showPasswordDialog" max-width="460">
      <v-card>
        <v-card-title class="text-h6">Changer mon mot de passe</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="passwordForm.currentPassword"
            type="password"
            label="Ancien mot de passe"
            variant="outlined"
            class="mb-3"
          />
          <v-text-field
            v-model="passwordForm.newPassword"
            type="password"
            label="Nouveau mot de passe"
            variant="outlined"
          />
          <div v-if="passwordError" class="text-red text-sm mt-2">{{ passwordError }}</div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="closePasswordDialog">Annuler</v-btn>
          <v-btn color="primary" :loading="passwordLoading" @click="submitPasswordChange">Confirmer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, ref , onMounted,inject} from 'vue'
import { useRouter } from 'vue-router'
import { usePopupStore } from '../stores'  
import { useSnackbar } from '@/composables/useSnackbar'
import { safeReadJson } from '@/utils/http'



const api = inject('api') 
const menu = ref(false) 
const hints = ref(true)
const popupStore = usePopupStore()
const isDark=ref(false)
const router = useRouter()
const { showSnackbar } = useSnackbar()
const showPasswordDialog = ref(false)
const passwordLoading = ref(false)
const passwordError = ref('')
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
})
 
import { useTheme } from 'vuetify'
const { global } = useTheme() 

const canChangeOwnPassword = computed(() => !['admin', 'superadmin'].includes(popupStore.user_access.access || ''))
 
  
// Définit le thème en clair
const setLightTheme=()=> {
  global.name.value = 'light'
  localStorage.setItem('theme', 'light')
}

// Définit le thème en sombre
const setDarkTheme=()=> {
  global.name.value = 'dark'
  localStorage.setItem('theme', 'dark')
} 

const toggleTheme=()=> { 
  
  if (isDark.value) {
    setDarkTheme()
  } else {
    setLightTheme()
  }
}

const resetPasswordForm = () => {
  passwordForm.value.currentPassword = ''
  passwordForm.value.newPassword = ''
  passwordError.value = ''
}

const openPasswordDialog = () => {
  menu.value = false
  resetPasswordForm()
  showPasswordDialog.value = true
}

const closePasswordDialog = () => {
  showPasswordDialog.value = false
  resetPasswordForm()
}

const submitPasswordChange = async () => {
  passwordError.value = ''

  if (!passwordForm.value.currentPassword || !passwordForm.value.newPassword) {
    passwordError.value = 'Veuillez remplir les deux champs.'
    return
  }

  if (passwordForm.value.newPassword.length < 8) {
    passwordError.value = 'Le nouveau mot de passe doit contenir au moins 8 caractères.'
    return
  }

  passwordLoading.value = true

  try {
    const endpoint = popupStore.user_access.app === 'paie' ? 'change_password_paie' : 'change_password'
    const formData = new FormData()
    formData.append('current_password', passwordForm.value.currentPassword)
    formData.append('new_password', passwordForm.value.newPassword)

    const response = await fetch(`${api}/api/${endpoint}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: formData,
    })

    const data = await safeReadJson(response)
    if (!response.ok) {
      throw new Error(data.detail || 'Erreur lors de la mise à jour du mot de passe')
    }

    showSnackbar({
      text: data.message || 'Mot de passe mis à jour avec succès',
      color: 'success',
      timeout: 3000,
    })
    closePasswordDialog()
  } catch (error) {
    passwordError.value = error.message || 'Erreur lors de la mise à jour du mot de passe'
  } finally {
    passwordLoading.value = false
  }
}

const logout=async ()=> {
    const currentUser= popupStore.user_access.name 
    const endpoint = popupStore.user_access.app === 'paie' ? `${api}/api/logoutpaie` : `${api}/api/logout`
    const requestOptions = popupStore.user_access.app === 'paie'
      ? {
          method: "POST",
          body: JSON.stringify({
            matricule: currentUser
          })
        }
      : {
          method: "POST"
        }

     const response = await fetch(endpoint, requestOptions)

      setLightTheme()
      console.log(response.status);
      if (response.status == 200) {
        localStorage.removeItem("access_token")
        window.dispatchEvent(new Event('auth:changed'))
        await router.replace('/login')
      }
      
}

onMounted(() => { 
   
  const theme = localStorage.getItem('theme')
  if (theme) {
    global.name.value = theme 
    if (theme=='dark') {
      isDark.value=true
    }
    
  }
   
})
</script>