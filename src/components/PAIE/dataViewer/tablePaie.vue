<template> 
  <v-card v-if="isAdmin" flat style="background: transparent;" >
    <template #text>
      <v-text-field v-model="search" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line/>
    </template>
    <v-data-table  style="padding:0px 15px;" class="bg-transparent" :headers="header_paie" :items="dataPaie" :search="search" item-value="Numero_pret" item-key="id" fixed-header height="450px" :items-per-page="50" @click:row="showRow"> 
      <template #item.ID="{ item }"> {{ item.ID?.slice(0, 2) || '' }}</template>
      <template #item.index="{ index }"> {{ index + 1 }}</template>
    </v-data-table>
  </v-card> 
  <FormeViewPaie :data="selectedRow"  @close="selectedRow = null"  />
  <FolderViewerPaie :data="date_liste" v-if="!isAdmin" />
</template>

<script setup>
import { usePopupStore } from '../../../stores';
import { watch, ref,inject,computed, onMounted} from 'vue'; 
import FormeViewPaie from './formeViewPaie.vue'; 
import FolderViewerPaie from './folderViewerPaie.vue';
import { safeReadJson } from '@/utils/http'

const selectedRow = ref(null);
const showForme = ref(false);
const api = inject('api') 
const loading=ref(true)
const popupStore = usePopupStore()
const dataPaie=ref([])
const search=ref('')
const headersBase = [
  { align: 'start', sortable: false },
  { title: '#', value: 'index', sortable: false },
];
const 
  header_paie=ref(
    [
      ...headersBase,
      { key: 'matricule', title: 'Matricule' },
      { key: 'nom_et_prenom_s_', title: 'Nom et Prénoms' },
      { key: 'fonction', title: 'Fonction' },
      { key: 'departement', title: 'Département' },
      { key: 'direction', title: 'Direction' },
      { key: 'agence', title: 'Agence' },
      { key: 'categorie', title: 'Catégorie' },
      { key: 'type_de_contrat', title: 'Type de contrat' },
      { key: 'date_embauche', title: "Date d'embauche" },
      { key: 'numero_cnaps', title: 'Numéro CNAPS' },
      { key: 'solde_conge', title: 'Solde de congé' },
      { key: 'couverture_sante', title: 'Couverture santé' },
      { key: 'salaire_de_base', title: 'Salaire de base' },

      { key: 'rpl_salbase', title: 'Rappel salaire de base' },

      { key: 'cplt_panier', title: 'Complément panier' },
      { key: 'rpl_cpl_panier', title: 'Rappel complément panier' },

      { key: 'ind_logt', title: 'Indemnité logement' },
      { key: 'rpl_ind_logt', title: 'Rappel indemnité logement' },

      { key: 'ind_fonction', title: 'Indemnité de fonction' },
      { key: 'rpl_ind_fonction', title: 'Rappel indemnité de fonction' },

      { key: 'ind_resp_manageri', title: 'Indemnité responsabilité managériale' },
      { key: 'rappel_ind_resp_m', title: 'Rappel indemnité responsabilité managériale' },

      { key: 'ind_transport', title: 'Indemnité de transport' },
      { key: 'rappel_ind_trans', title: 'Rappel indemnité de transport' },

      { key: 'points_personnels', title: 'Points personnels' },
      { key: 'rpl_points_pers', title: 'Rappel points personnels' },

      { key: 'eau_et_elec', title: 'Indemnité eau et électricité' },
      { key: 'ind_probatoire', title: 'Indemnité probatoire' },
      { key: 'rappel_ind_prob', title: 'Rappel indemnité probatoire' },

      { key: 'rpl_eau_elec', title: 'Rappel eau et électricité' },

      { key: 'sld_conge_stc', title: 'Solde congé STC' },
      { key: 'preavi_sipem', title: 'Préavis SIPem' },

      { key: 'prime_mensuel', title: 'Prime mensuelle' },

      { key: 'compl_panier_2', title: 'Complément panier 2' },
      { key: 'rappel_compl_pan_2', title: 'Rappel complément panier 2' },

      { key: 'salaire_brut', title: 'Salaire brut' },
      { key: 'cnaps', title: 'CNAPS' },

      { key: 'smids', title: 'SMIDS' },
      { key: 'smimo', title: 'SMIMO' },
      { key: 'omsi', title: 'OMSI' },
      { key: 'omino', title: 'OMINO' },
      { key: 'osiem', title: 'OSIEM' },
      { key: 'funhece', title: 'FUNHECE' },
      { key: 'smisa', title: 'SMISA' },
      { key: 'smia', title: 'SMIA' },
      { key: 'omit', title: 'OMIT' },
      { key: 'ostie', title: 'OSTIE' },

      { key: 'avantage_nature', title: 'Avantage en nature' },
      { key: 'montant_imp', title: 'Montant imposable' },

      { key: 'irsa_avt_abt', title: 'IRSA avant abattement' },
      { key: 'abt_chg_famil', title: 'Abattement charge familiale' },
      { key: 'irsa', title: 'IRSA' },

      { key: 'credit_pers', title: 'Crédit personnel' },
      { key: 'autre_retenu', title: 'Autres retenues' },

      { key: 'avc_carburant', title: 'Avance carburant' },

      { key: 'alloc_famil', title: 'Allocation familiale' },

      { key: 'retrlte_cpl', title: 'Retraite complémentaire' },

      { key: 'credit_au_personnel', title: 'Crédit au personnel' },

      { key: 'ret_compl_stc', title: 'Retenue complémentaire STC' },

      { key: 'preavi_salarie', title: 'Préavis salarié' },

      { key: 'net_a_payer', title: 'Net à payer' },

      { key: 'chg_employeur_cnaps', title: 'Charge employeur CNAPS' },
      { key: 'chg_employeur_couv_sante', title: 'Charge employeur couverture santé' },
      { key: 'chg_employeur_ret_compl', title: 'Charge employeur retraite complémentaire' }
  ]

  )

const date_liste= ref([])

const showRow = (event, row) => {
  // selectedRow.value = ;
  selectedRow.value = [row.item ,  { "upload_date":  popupStore.selected_date }]   // données de la ligne cliquée
  showForme.value = true;         // ouvrir le formulaire
  // console.log("Ligne cliquée :", row.item);
};

const normalizePrivilege = (value) => String(value || '').trim().toLowerCase()
const normalizePayrollDate = (value) => String(value || '').replace(/-/g, '').trim()
const isAdmin = computed(() => {
  const privilege = normalizePrivilege(popupStore.user_access.access || localStorage.getItem('privilege'))
  return ['admin', 'superadmin'].includes(privilege)
})

const filteredMenu = computed(() => {
    const privilege = normalizePrivilege(popupStore.user_access.access)
    if (!['admin', 'superadmin'].includes(privilege)) {
       return 'non Admin'
       
    } 
});

const fetch_all_paie = async (matricule = null, dateStr = null) => {
  loading.value = true;
  const normalizedDate = normalizePayrollDate(dateStr)
  // console.log(popupStore.user_access.access);
  
  try {
    if (!/^\d{8}$/.test(normalizedDate)) {
      dataPaie.value = []
      return
    }

    // Construire l'URL avec paramètres query
    let url = `${api}/api/get_paie_list`;
    const params = new URLSearchParams();
    if (matricule) params.append("matricule", matricule);
    params.append("dateStr", normalizedDate);

    if ([...params].length > 0) {
      url += `?${params.toString()}`;
    }

    const response = await fetch(url);
    const json = await safeReadJson(response)

    if (!response.ok) throw new Error(json.detail || "Erreur inconnue");
    if (!Array.isArray(json.data?.users)) throw new Error("Réponse API invalide")

    // Nouvelle structure : data.users
    const capitalData = json.data?.users || [];
    // console.log(json.data.users);
    dataPaie.value = json.data.users;

    // Tu peux continuer à traiter capitalData ici...

  } catch (err) {
    console.log(err.message || "Erreur inconnue");
    console.error("Erreur fetch_all_paie:", err);

  } finally {
    loading.value = false;
  }
};

async function fetchData(baseUrl, date = null) {
  try {
    // Si une date est fournie, on l’ajoute à l’URL
    const url = date ? `${baseUrl}?date=${date}` : baseUrl

    const response = await fetch(url)
    if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`)

    const data = await safeReadJson(response)
    return data.response?.data || []
  } catch (error) {
    console.error('❌ Erreur de chargement :', error)
    return []
  }
}

onMounted(async () => {
  date_liste.value = await fetchData(`${api}/api/history_insert_paie`)
  // console.log(date_liste.value);
  
  // fetch_all_paie(null, popupStore.selected_date);
});
 

// Watch sur la date sélectionnée
watch(
  () => popupStore.selected_date,
  () => {  
    if (!isAdmin.value) {
      return
    }

    fetch_all_paie(null, popupStore.selected_date)
  },
  { immediate: true }
)
 
</script>

<style>

</style>