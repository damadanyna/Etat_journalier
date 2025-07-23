<template>
<div class=" flex flex-col mt-7">
    <v-tabs v-model="tab" class="bg_data ">
        <v-tab   v-for="item in tabs" :key="item.value" :value="item.value" >
        <span class="">{{ item.label }}</span>
        </v-tab>
    </v-tabs>

    <v-tabs-window v-model="tab" class="bg_data" style="  padding: 5px 40px; ">
        <v-tabs-window-item v-for="item in tabs" :key="item.value" :value="item.value">
        <v-card style="background: transparent;" :title="item.title" flat>
            <template v-slot:text>
            <v-text-field v-model="item.search" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line></v-text-field>
            </template> 
            <v-data-table class=" bg-transparent" :headers="item.headers"    item-value="Numero_pret" :search="item.search" fixed-header height="450px" item-key="id"  >
                <!-- Slot pour tronquer l'ID -->
                <template v-slot:item.ID="{ item }">
                {{ item.ID ? item.ID.slice(0, 2) : '' }}
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
const tab = ref("one"); 

const headers_encours = [
  {
    align: 'start',
    sortable: false,
  },
  { title: '#', value: 'index', sortable: false },
  { key: 'id', title: 'id' },
  { key: 'Agence', title: 'Agence' },
  { key: 'identification_client', title: 'identification_client' },
  { key: 'customer', title: 'customer' },
  { key: 'Numero_pret', title: 'Numero_pret' },
  { key: 'Nom_client', title: 'Nom_client' },
  { key: 'linked_appl_id', title: 'linked_appl_id' },
  { key: 'Date_pret', title: 'Date_pret' },
  { key: 'Date_fin_pret', title: 'Date_fin_pret' },
  { key: 'Produits', title: 'Produits' },
  { key: 'Amount', title: 'Amount' },
  { key: 'Duree_Remboursement', title: 'Duree_Remboursement' },
  { key: 'taux_d_interet', title: 'taux_d_interet' },
  { key: 'Nombre_de_jour_retard', title: 'Nombre_de_jour_retard' },
  { key: 'payment_date', title: 'payment_date' },
  { key: 'Capital_', title: 'Capital_' },
  { key: 'Total_interet_echus', title: 'Total_interet_echus' },
  { key: 'OD Pen', title: 'OD Pen' },
  { key: 'OD & PEN', title: 'OD & PEN' },
  { key: 'Genre', title: 'Genre' },
  { key: 'Secteur_d_activité', title: 'Secteur_d_activité' },
  { key: 'CODE', title: 'CODE' },
  { key: 'arr_status', title: 'arr_status' },
];


const tabs = [
  { value: 'one',search:'',headers:headers_encours, label: 'Etat des cours', title: 'Etats des encours' },
  { value: 'two',search:'', label: 'Etat DE Remboursement', title: 'Etats de remboursement' },
  { value: 'three',search:'', label: 'Limit AVM', title: 'Limite AVM' },
  { value: 'four',search:'', label: 'Limit CAUTION', title: 'Limite CAUTION' }
]


const get_encours_credits = async () => {
  try {
    const date = '20250711' 

    const response = await fetch(`http://192.168.1.212:8000/api/get_encours_credits?date=${date}`, {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
    }
    });

    if (!response.ok) {
      throw new Error(`Erreur HTTP : ${response.status}`);
    }

    const data = await response.json(); 
    console.log(data); 

  } catch (error) {
    console.error("❌ Erreur lors du chargement du fichier dans la base :", error);
  }
};

onMounted(() => {
   get_encours_credits()
  
})

</script>

<style scoped>
.bg_data{
    background-color: #00000022; 
}
</style>