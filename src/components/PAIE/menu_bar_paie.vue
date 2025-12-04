<template>
<v-toolbar color=" " class="bg-transparent" title="Pay By">
    <div v-if="popupStore.user_access.access=='admin'" class=" flex flex-row">
        <h3 class="mr-5 text-xl">Date de paie</h3> 

            <v-menu   v-model="menu" close-on-content-click offset-y max-width="200" min-width="200">
                <template #activator="{ props }">
                    <v-btn v-bind="props" prepend-icon="mdi-calendar-range" variant="outlined">
                        <template #prepend>
                            <v-icon color="success" />
                        </template>
                        <span class="text-2xl">{{ selectedDate }}</span>
                    </v-btn>
                </template>
                <v-list style="max-height: 200px; overflow-y: auto;">
                    <v-list-item v-for="date in historyDates" :key="date.label" @click="() => selectDateStatOf(date.label, date.stat_of)" role="button">
                        <div class="flex" :title="date.stat_of!='init'? 'Base non initialisé':''"> 
                            <v-icon   color="success" class=" mr-2">mdi mdi-calendar</v-icon>
                            <v-list-item-title>{{ date.label }}</v-list-item-title>
                        </div>
                    </v-list-item>
                </v-list>
            </v-menu>
    </div>
    
    <user_btn_profil class=" mx-4"></user_btn_profil>
</v-toolbar>
</template>

<script setup>
import user_btn_profil from '../user_btn_profil.vue'
import {
    ref,
    watch,
    onMounted,
    inject,
    computed
} from 'vue'
import {
    useRoute
} from 'vue-router'
import {
    usePopupStore
} from '../../stores'
import * as XLSX from 'xlsx'
import {
    useRouter
} from 'vue-router'

const route = useRoute()
const api = inject('api')
const selectedDate = ref('Chargement en cours...')
const menu = ref(false)
const popupStore = usePopupStore()
const exporting = ref(false)
const router = useRouter()

const historyDates = ref([])

async function selectDateStatOf(date, stat_of) {
    selectedDate.value = date

    // 🔹 Met à jour le store Pinia
    popupStore.selected_date = date
    popupStore.selected_date_stat_of = stat_of

    // 🔹 Ferme le menu
    menu.value = false

    // 🔹 Émet un événement global
    window.dispatchEvent(new CustomEvent('table-date-stat-of-selected', {
        detail: {
            date,
            stat_of
        }
    }))
}
async function fetchData(baseUrl, date = null) {
  try {
    // Si une date est fournie, on l’ajoute à l’URL
    const url = date ? `${baseUrl}?date=${date}` : baseUrl

    const response = await fetch(url)
    if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`)

    const data = await response.json()
    return data.response.data
  } catch (error) {
    console.error('❌ Erreur de chargement :', error)
    return []
  }
}

watch(historyDates, (val) => {
  if (Array.isArray(val) && val.length > 0) {
    // Trie les dates du plus récent au plus ancien
    const sorted = [...val].sort((a, b) => b.label.localeCompare(a.label))
    const lastDate = sorted[0].label
    const lastStatCompte = sorted[0].stat_compte

    selectedDate.value = lastDate
    popupStore.selected_date = lastDate
    popupStore.selected_date_stat_compte = lastStatCompte
    localStorage.setItem("selectedTable", lastDate)

    // Émet l'événement pour synchroniser la sélection
    
    // console.log("📅 Dernière date sélectionnée automatiquement :", lastDate)
  }
}, { immediate: true })

onMounted(() => {
    (async () => {
        historyDates.value = await fetchData(`${api}/api/history_insert_paie`)
    })(); 
})
</script>

<style>
.green_transparent {
    background-color: #00dc54a4;
}
</style>
