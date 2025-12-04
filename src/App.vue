<template>
  <popup_view v-if="usePopupStore().showPopupCDI"></popup_view>
  <VApp class="h-screen" >
      <login v-if="isLogged_status!==200"></login>
      <div v-else class="">
        <LayoutEcours v-if="popupStore.user_access.app !== 'paie'">
          <router-view />
        </LayoutEcours>
        <LayoutPaie v-else>
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
import { useRouter } from 'vue-router'
const api = inject('api') 
import login from './pages/login.vue';
import { usePopupStore} from './stores'
import LayoutEcours from '@/layouts/encours.vue'
import LayoutPaie from '@/layouts/paie.vue'
import { useSnackbar } from '@/composables/useSnackbar' 
import popup_view from './components/loading/file_porgress_bar_vues.vue';
import { useTheme } from 'vuetify' 
import { useRoute } from 'vue-router'
import { computed, onMounted,ref,inject, onBeforeMount } from 'vue' 

const popupStore = usePopupStore()

const router = useRouter();

const { snackbar } = useSnackbar()
const { global } = useTheme() 
  
const route = useRoute()

const isLogged_status= ref(400)

const layout = computed(() => route.meta.layout || 'default')

const get_stat = async () => {
  const token = localStorage.getItem("access_token");

  if (!token) {
    console.warn("Aucun token trouvé dans le localStorage");
    return;
  }

  const protectedResp = await fetch(`${api}/api/protected`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    }
  });
  isLogged_status.value=protectedResp.status  

  if (protectedResp.ok) {
    const data = await protectedResp.json(); 
    popupStore.user_access.name=data.username
    popupStore.user_access.access=data.privillege
    popupStore.user_access.app=data.app  
    // console.log("Headers:", protectedResp); 
    // console.log("application= ",popupStore.user_access.app);
    
  if (popupStore.user_access.app === 'paie') {
      router.replace({ path: '/paie/accueil' });
    } else {
      router.push({ path: '/app/credits' });
    }
    
  } else {
    const errorText = await protectedResp.text();
    console.error("Non authentifié ou erreur :", errorText);
  }
};
 
onMounted(() => { 

  get_stat()
  const theme = localStorage.getItem('theme')
  if (theme) {
    global.name.value = theme
  }
   
 

})

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
</style>