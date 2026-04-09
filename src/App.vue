<template>
  <popup_view v-if="usePopupStore().showPopupCDI"></popup_view>
  <VApp class="h-screen " style=" height: 80vh;" >
      <div v-if="authLoading" class="app-loading-state">
        Vérification de la session...
      </div>
      <login v-else-if="isLogged_status!==200"></login>
      <div v-else class="">
        <LayoutPaie>
          <router-view />
        </LayoutPaie>

        <VSnackbar v-model="snackbar.show" :color="snackbar.color" :timeout="snackbar.timeout">
          {{snackbar.text}}
          <template #actions>
            <VBtn color="white" variant="text" @click="snackbar.show = false">Close</VBtn>
          </template>
        </VSnackbar>
      </div>
  </VApp>
</template>

<script setup> 
import login from './pages/login.vue';
import { usePopupStore} from './stores'
import LayoutPaie from '@/layouts/paie.vue'
import { useSnackbar } from '@/composables/useSnackbar' 
import popup_view from './components/loading/file_porgress_bar_vues.vue';
import { useTheme } from 'vuetify' 
import { useRoute, useRouter } from 'vue-router'
import { onBeforeUnmount, onMounted, ref, inject, watch } from 'vue' 
import { useActivityLogger } from '@/composables/useActivityLogger'
import { useNotificationStore } from '@/stores/notification'
import { connectSocketClient, disconnectSocketClient, getSocketClient } from '@/composables/useSocketClient'
import { safeReadJson } from '@/utils/http'

const api = inject('api') 
const { logUserActivity } = useActivityLogger(api)
const notificationStore = useNotificationStore()

const popupStore = usePopupStore()

const router = useRouter();

const { snackbar, showSnackbar } = useSnackbar()
const { global } = useTheme() 
  
const route = useRoute()

const isLogged_status= ref(400)
const authLoading = ref(true)
const lastLoggedRoute = ref('')
const pendingValidationCount = ref(0)
const INACTIVITY_TIMEOUT_MS = 5 * 60 * 1000
const ACTIVITY_EVENTS = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart', 'click']
const inactivityTimer = ref(null)
const isAutoLoggingOut = ref(false)
const lastActivityResetAt = ref(0)

const getHomeRoute = () => '/paie/accueil'
const normalizePrivilege = (value) => String(value || '').trim().toLowerCase()

const shouldRedirectToHome = () => route.path === '/' || route.path === '/login'

const clearAuthState = () => {
  isLogged_status.value = 401
  popupStore.user_access.name = ''
  popupStore.user_access.access = ''
  popupStore.user_access.app = 'paie'
  notificationStore.setDemandesValidation(0)
  pendingValidationCount.value = 0
  clearInactivityTimer()
  disconnectSocketClient()
}

function clearInactivityTimer() {
  if (inactivityTimer.value) {
    window.clearTimeout(inactivityTimer.value)
    inactivityTimer.value = null
  }
}

async function logoutCurrentSession(reason = 'manual') {
  if (isAutoLoggingOut.value) {
    return
  }

  isAutoLoggingOut.value = true
  clearInactivityTimer()

  try {
    const currentUser = popupStore.user_access.name

    if (currentUser) {
      if (reason === 'inactivity') {
        await logUserActivity({
          action: 'auto_logout',
          entityType: 'session',
          entityId: currentUser,
          description: `Déconnexion automatique après 5 minutes d'inactivité pour ${currentUser}`,
        })
      }

      await fetch(`${api}/api/logoutpaie`, {
        method: 'POST',
        body: JSON.stringify({
          matricule: currentUser,
        }),
      })
    }
  } catch (error) {
    console.error('Erreur lors de la déconnexion automatique :', error)
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('privilege')
    clearAuthState()
    window.dispatchEvent(new Event('auth:changed'))
    await router.replace('/login')
    isAutoLoggingOut.value = false
  }
}

function resetInactivityTimer() {
  if (authLoading.value || isLogged_status.value !== 200 || isAutoLoggingOut.value) {
    return
  }

  const now = Date.now()
  if (now - lastActivityResetAt.value < 1000) {
    return
  }

  lastActivityResetAt.value = now
  clearInactivityTimer()
  inactivityTimer.value = window.setTimeout(async () => {
    await logoutCurrentSession('inactivity')
  }, INACTIVITY_TIMEOUT_MS)
}

function registerActivityListeners() {
  ACTIVITY_EVENTS.forEach((eventName) => {
    window.addEventListener(eventName, resetInactivityTimer, { passive: true })
  })
}

function unregisterActivityListeners() {
  ACTIVITY_EVENTS.forEach((eventName) => {
    window.removeEventListener(eventName, resetInactivityTimer)
  })
}

const handlePendingValidationSocket = (payload = {}) => {
  if (payload.app !== 'paie') {
    return
  }

  const nextCount = Number(payload.count || 0)
  const previousCount = Number(pendingValidationCount.value || 0)
  const canNotify = popupStore.user_access.app === 'paie' && ['admin', 'superadmin'].includes(normalizePrivilege(popupStore.user_access.access))

  if (canNotify && nextCount > previousCount) {
    const demandes = nextCount - previousCount
    showSnackbar({
      text: demandes > 1
        ? `${demandes} nouvelles demandes d'inscription en attente de validation.`
        : "Nouvelle demande d'inscription en attente de validation.",
      color: 'error',
      timeout: 4500,
    })
  }

  pendingValidationCount.value = nextCount
  notificationStore.setDemandesValidation(nextCount)
  window.dispatchEvent(new CustomEvent('socket:pending-validation-updated', { detail: payload }))
}

const handlePayrollDateSocket = (payload = {}) => {
  if (payload.app !== 'paie') {
    return
  }

  window.dispatchEvent(new CustomEvent('socket:payroll-date-updated', { detail: payload }))
}

const handleUserActivitySocket = (payload = {}) => {
  if (payload.app !== 'paie') {
    return
  }

  window.dispatchEvent(new CustomEvent('socket:user-activity-updated', { detail: payload }))
}

const bindSocketListeners = () => {
  const socket = getSocketClient(api)

  if (!socket) {
    return
  }

  socket.off('pending_validation_updated', handlePendingValidationSocket)
  socket.off('payroll_date_updated', handlePayrollDateSocket)
  socket.off('user_activity_logged', handleUserActivitySocket)
  socket.on('pending_validation_updated', handlePendingValidationSocket)
  socket.on('payroll_date_updated', handlePayrollDateSocket)
  socket.on('user_activity_logged', handleUserActivitySocket)
}

const syncSocketConnection = () => {
  if (isLogged_status.value === 200) {
    bindSocketListeners()
    connectSocketClient(api)
    return
  }

  disconnectSocketClient()
}

const get_stat = async () => {
  authLoading.value = true
  const token = localStorage.getItem("access_token");

  if (!token) {
    clearAuthState()
    authLoading.value = false
    return;
  }

  try {
    const protectedResp = await fetch(`${api}/api/protected`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    });

    isLogged_status.value = protectedResp.status

    if (protectedResp.ok) {
      const data = await safeReadJson(protectedResp)
      popupStore.user_access.name = data.username || data.sub || ''
      popupStore.user_access.access = normalizePrivilege(data.privillege || data.privilege || localStorage.getItem('privilege'))
      popupStore.user_access.app = 'paie'
      pendingValidationCount.value = Number(notificationStore.demandesValidation || 0)
      syncSocketConnection()

      if (shouldRedirectToHome()) {
        const homeRoute = getHomeRoute()
        if (route.path !== homeRoute) {
          await router.replace({ path: homeRoute })
        }
      }
    } else {
      localStorage.removeItem('access_token')
      localStorage.removeItem('privilege')
      clearAuthState()
    }
  } catch (error) {
    console.error('Erreur de vérification de session :', error)
    clearAuthState()
  } finally {
    authLoading.value = false
  }
};

const handleAuthChanged = async () => {
  await get_stat()
}

onMounted(() => { 
  get_stat()
  window.addEventListener('auth:changed', handleAuthChanged)
  bindSocketListeners()
  registerActivityListeners()

  const theme = localStorage.getItem('theme')
  if (theme) {
    global.name.value = theme
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('auth:changed', handleAuthChanged)
  unregisterActivityListeners()
  clearInactivityTimer()
  const socket = getSocketClient(api)
  if (socket) {
    socket.off('pending_validation_updated', handlePendingValidationSocket)
    socket.off('payroll_date_updated', handlePayrollDateSocket)
    socket.off('user_activity_logged', handleUserActivitySocket)
  }
  disconnectSocketClient()
})

watch(
  () => route.path,
  async (path) => {
    if (authLoading.value || isLogged_status.value !== 200) {
      return
    }

    if (popupStore.user_access.app !== 'paie' || !path.startsWith('/paie')) {
      return
    }

    if (lastLoggedRoute.value === path) {
      return
    }

    lastLoggedRoute.value = path
    await logUserActivity({
      action: 'page_view',
      entityType: 'route',
      entityId: path,
      description: `Consultation de la page ${path}`,
    })
  },
  { immediate: true }
)

watch(
  () => [isLogged_status.value, popupStore.user_access.app],
  () => {
    syncSocketConnection()
    if (isLogged_status.value === 200) {
      resetInactivityTimer()
    } else {
      clearInactivityTimer()
    }
  },
  { immediate: true }
)

watch(
  () => notificationStore.demandesValidation,
  (count) => {
    pendingValidationCount.value = Number(count || 0)
  },
  { immediate: true }
)

watch(
  () => route.fullPath,
  () => {
    resetInactivityTimer()
  }
)

// Optionally, handle dynamic layouts here if necessary
</script>
<style>
/* Cache la scrollbar sur tous les navigateurs */
html, body {
  overflow: hidden;
}

/* Facultatif : si tu veux quand même que le contenu puisse scroller via la molette sans scrollbar visible */
body {
  scrollbar-width: none; /* Firefox */
}

body::-webkit-scrollbar {
  display: none; /* Chrome, Safari */
}
#app{
  overflow: hidden;
}

.app-loading-state {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: #374151;
  background: linear-gradient(135deg, #d6d6d6, #ffffff);
}
</style>