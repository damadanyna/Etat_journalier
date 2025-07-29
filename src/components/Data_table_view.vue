<template>
  <div class="flex flex-col mt-7">
    <v-tabs v-model="tab" class="bg_data">
      <v-tab v-for="item in tabs" :key="item.value" :value="item.value">
        {{ item.label }}
      </v-tab>
    </v-tabs>

    <v-tabs-window v-model="tab" class="bg_data px-10 py-1">
      <v-tabs-window-item v-for="item in tabs" :key="item.value" :value="item.value">
        <v-card flat style="background: transparent;" :title="item.title">
          <template #text>
            <v-text-field
              v-model="item.search"
              label="Search"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              hide-details
              single-line
            />
          </template>
          <v-data-table
            class="bg-transparent"
            :headers="item.headers"
            :items="item.liste"
            :search="item.search"
            item-value="Numero_pret"
            item-key="id"
            fixed-header
            height="450px"
            :items-per-page="50"
          >
            <template #item.ID="{ item }">
              {{ item.ID?.slice(0, 2) || '' }}
            </template>
            <template #item.index="{ index }">
              {{ index + 1 }}
            </template>
          </v-data-table>
        </v-card>
      </v-tabs-window-item>
    </v-tabs-window>
  </div>
</template> 
 
<script setup>
import { onMounted, ref } from 'vue';
import { usePopupStore } from '../stores';

const tab = ref("one");

const listes = {
  encours: ref([]),
  remboursement: ref([]),
  avm: ref([]),
  caution: ref([]),
};

const headersBase = [
  { align: 'start', sortable: false },
  { title: '#', value: 'index', sortable: false },
];

const headers = {
  encours: [
    ...headersBase,
    { key: 'id', title: 'id' },
    { key: 'Agence', title: 'Agence' },
    { key: 'Numero_pret', title: 'Numero_pret' },
    { key: 'identification_client', title: 'identification_client' }, 
    { key: 'Nom_client', title: 'Nom_client' },
    { key: 'Genre', title: 'Genre' },
    { key: 'linked_appl_id', title: 'linked_appl_id' },
    { key: 'Date_pret', title: 'Date_pret' },
    { key: 'Date_fin_pret', title: 'Date_fin_pret' },
    { key: 'Produits', title: 'Produits' },
    { key: 'Amount', title: 'Amount' },
    { key: 'Duree_Remboursement', title: 'Duree_Remboursement' }, 
    { key: 'capital_appele', title: 'capital_appele' },
    { key: 'capital_non_appele', title: 'capital_non_appele' },
    { key: 'Total_interet_echus', title: 'Total_interet_echus' },
    { key: 'taux_d_interet', title: 'taux_d_interet' },
    { key: 'Nombre_de_jour_retard', title: 'Nombre_de_jour_retard' },
    { key: 'payment_date', title: 'payment_date' }, 
    { key: 'OD Pen', title: 'OD Pen' },
    { key: 'OD & PEN', title: 'OD & PEN' },
    { key: 'Chiffre_Affaire', title: 'Chiffre_Affaire' },
    { key: 'Secteur_d_activité', title: 'Secteur_d_activité' },
    { key: 'CODE', title: 'CODE' },
    { key: 'status', title: 'status' },
  ],
  remboursement: [
    ...headersBase,
    { key: 'arrangement_id', title: 'arrangement_id' },
    { key: 'Date_pret', title: 'Date_pret' },
    { key: 'product', title: 'product' },
    { key: 'co_code', title: 'co_code' },
    { key: 'linked_appl_id', title: 'linked_appl_id' },
    { key: 'Nom_client', title: 'Nom_client' },
    { key: 'customer', title: 'customer' },
    { key: 'echeance', title: 'echeance' },
    { key: 'date_echeance', title: 'date_echeance' },
    { key: 'payment_date', title: 'payment_date' },
    { key: 'Capital', title: 'Capital' },
    { key: 'principal_int', title: 'principal_int' },
    { key: 'penality_int', title: 'penality_int' },
    { key: 'TOTAL', title: 'TOTAL' },
  ],
  avm: [
    ...headersBase,
    { key: 'id', title: 'id' },
    { key: 'Name', title: 'Name' },
    { key: 'approval_date', title: 'approval_date' },
    { key: 'expiry_date', title: 'expiry_date' },
    { key: 'internal_amount', title: 'internal_amount' },
    { key: 'total_os', title: 'total_os' },
    { key: 'avail_amt', title: 'avail_amt' },
  ],
  caution: [
    ...headersBase,
    { key: 'id', title: 'id' },
    { key: 'Name', title: 'Name' },
    { key: 'approval_date', title: 'approval_date' },
    { key: 'expiry_date', title: 'expiry_date' },
    { key: 'internal_amount', title: 'internal_amount' },
    { key: 'total_os', title: 'total_os' },
    { key: 'avail_amt', title: 'avail_amt' },
  ],
};

const tabs = ref([
  { value: 'one', label: 'Etat des cours', title: 'Etats des encours', liste: listes.encours.value, headers: headers.encours, search: '' },
  { value: 'two', label: 'Etat DE Remboursement', title: 'Etats de remboursement', liste: listes.remboursement.value, headers: headers.remboursement, search: '' },
  { value: 'three', label: 'Limit AVM', title: 'Limite AVM', liste: listes.avm.value, headers: headers.avm, search: '' },
  { value: 'four', label: 'Limit CAUTION', title: 'Limite CAUTION', liste: listes.caution.value, headers: headers.caution, search: '' }
]);

async function fetchData(url, listRef, storeKey) {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
    const data = await response.json();
    data.response.data.forEach(item => listRef.value.push(item));
    usePopupStore()[storeKey] = listRef;
  } catch (error) {
    console.error("❌ Erreur de chargement :", error);
  }
}


onMounted(() => {
  console.log(usePopupStore().selected_date);
  
  const date = '20250725';
  fetchData(`http://192.168.1.212:8000/api/get_encours_credits?date=${date}`, listes.encours, 'encours_actual_data');
  fetchData(`http://192.168.1.212:8000/api/encours_remboursement?date=${date}`, listes.remboursement, 'remboursement_actual_data');
  fetchData(`http://192.168.1.212:8000/api/encours_limit?limit_type=8400`, listes.avm, 'limit_avm_actual_data');
  fetchData(`http://192.168.1.212:8000/api/encours_limit?limit_type=2900`, listes.caution, 'limit_caution_actual_data');
});
</script>
<style scoped>
.bg_data {
  background-color: #00000022;
}
</style>
