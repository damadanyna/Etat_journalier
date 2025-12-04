<template>
<div class=" max-h-full  ">
    <div class="max-w-4xl mx-auto px-4 py-7 h-full bg-white">
        <!-- Header avec logo et titre -->
        <div class=" flex items-center justify-between">
            <img class=" w-[100px] " src="https://www.sipembanque.mg/wp-content/uploads/2024/07/logo-vertical.webp" alt="">
            <div class=" flex flex-col items-center">
                <span class=" font-bold ">FICHE DE PAIE</span>
                <span class=" text-sm">Oct-25</span>
            </div>
            <div></div>
        </div>

        <!-- Informations employé et agence -->
        <div class=" flex justify-between  mt-4    ">
            <div class="space-y-2">
                <div class="flex mt-1">
                    <span class="font-semibold text-sm w-40">N° Matricule :</span>
                    <span class="text-sm border-[1px] font-bold px-7 border-black ">{{ matricule }}</span>
                </div>
                <div class="flex mt-1">
                    <span class="text-sm w-40">Agent :</span>
                    <span class="text-sm">{{ agent }}</span>
                </div>
                <div class="flex mt-1">
                    <span class="font-semibold text-sm w-40">Fonction :</span>
                    <span class="text-sm">{{ fonction }}</span>
                </div>
                <div class="flex mt-1">
                    <span class="font-semibold text-sm w-40">Date d'embauche :</span>
                    <span class="text-sm">{{ dateEmbauche }}</span>
                </div>
                <div class="flex mt-1">
                    <span class="font-semibold text-sm w-40">Département :</span>
                    <span class="text-sm">{{ departement }}</span>
                </div>
                <div class="flex mt-1">
                    <span class="font-semibold text-sm w-40">Direction :</span>
                    <span class="text-sm ">{{ direction }}</span>
                </div>
                <div class="flex mt-1">
                    <span class="font-semibold text-sm w-40">N°CNAPS :</span>
                    <span class="text-sm">{{ cnaps }}</span>
                </div>
            </div>
            <div class="space-y-2">
                <div class="flex">
                    <span class="font-semibold text-sm w-32">Agence :</span>
                    <span class="text-sm font-bold">{{ agence }}</span>
                </div>
            </div>
        </div>

        <!-- Tableau des salaires -->
        <div class="p-6  ">
            <table class="w-full border-collapse text-sm">
                <thead>
                    <tr class=" ">
                        <th class=" px-3 py-2 text-left font-bold">Catégorie :</th>
                        <th class=" px-3 py-2 text-center font-bold">{{ categorie }}</th>
                        <th class=" px-3 py-2 text-center font-bold">Type :</th>
                        <th class=" px-3 py-2 text-center font-bold" colspan="2">{{ type }}</th>
                    </tr>
                    <tr class="bg-gray-100">
                        <th class="border border-gray-400 px-3 py-2 text-center font-bold">RUBRIQUES</th>
                        <th class="border border-gray-400 px-3 py-2 text-center font-bold">INTIER</th>
                        <th class="border border-gray-400 px-3 py-2 text-center font-bold">GAINS</th>
                        <th class="border border-gray-400 px-3 py-2 text-center font-bold" colspan="2">RETENUS</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in rubriques" :key="index" :class="item.bold ? 'bg-yellow-50 font-bold' : ''">
                        <td class="border border-gray-400 px-3 py-1" :class="item.bold ? 'font-bold' : ''">{{ item.label }}</td>
                        <td class="border border-gray-400 px-3 py-1 text-right">{{ item.intier }}</td>
                        <td class="border border-gray-400 px-3 py-1 text-right">{{ item.gains }}</td>
                        <td class="border border-gray-400 px-3 py-1 text-right" colspan="2">{{ item.retenus }}</td>
                    </tr>
                </tbody>
                <tfoot>
                    <tr class="bg-gray-100 ">
                        <td class="border border-gray-400 px-3 py-2">TOTAL</td>
                        <td class="border border-gray-400 px-3 py-2 text-right">{{ totalIntier }}</td>
                        <td class="border border-gray-400 px-3 py-2 text-right">{{ totalGains }}</td>
                        <td class="border border-gray-400 px-3 py-2 text-right" colspan="2">{{ totalRetenus }}</td>
                    </tr>
                    <tr class="bg-gray-100">
                        <td class="border border-gray-400 px-3 py-2">SALAIRE NET</td>
                        <td class="border border-gray-400 px-3 py-2"></td>
                        <td class="border border-gray-400 px-3 py-2"></td>
                        <td class="border border-gray-400 px-3 py-2 text-right" colspan="2">{{ salaireNet }}</td>
                    </tr>
                    <tr class="bg-gray-100">
                        <td class="border border-gray-400 px-3 py-2">NET A PAYER</td>
                        <td class="border border-gray-400 px-3 py-2"></td>
                        <td class="border border-gray-400 px-3 py-2"></td>
                        <td class="border border-gray-400 px-3 py-2 text-right text-lg" colspan="2">{{ netAPayer }}</td>
                    </tr>
                    <tr class="bg-gray-100">
                        <td class="border border-gray-400 px-3 py-2 font-semibold">Solde Congé</td>
                        <td class="border border-gray-400 px-3 py-2"></td>
                        <td class="border border-gray-400 px-3 py-2"></td>
                        <td class="border border-gray-400 px-3 py-2 text-right" colspan="2">{{ soldeConge }}</td>
                    </tr>
                </tfoot>
            </table>
        </div>

        <!-- Footer -->
        <div class="p-6 border-t-2 border-gray-300 text-center">
            <p class="text-xs text-gray-600 italic">L'Employeur ou son représentant</p>
        </div>
    </div>
</div>
</template>

<script setup>

import { ref,inject} from 'vue';  
const props = defineProps({
  data: { type: Object, default: null }
}); 
    
        
const matricule=ref('')
const agent=ref('')
const fonction=ref('')
const dateEmbauche=ref('')
const departement=ref('')
const direction=ref('')
const cnaps=ref('')
const agence=ref('')
const categorie=ref('')
const type=ref('')

const rubriques=ref( [{
                    label: 'Salaire de base',
                    intier: '',
                    gains: '1 251 510,00',
                    retenus: ''
                },
                {
                    label: 'Rappel sur salaire de base',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Complément poste',
                    intier: '',
                    gains: '144 778,66',
                    retenus: ''
                },
                {
                    label: 'Rappel complément poste1',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Indemnité de logement',
                    intier: '',
                    gains: '252 288,00',
                    retenus: ''
                },
                {
                    label: 'Rappel indemnité de logement',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Indemnité de fonction',
                    intier: '',
                    gains: '194 367,61',
                    retenus: ''
                },
                {
                    label: 'Rappel indemnité de fonction',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Indemnité Responsabilité Managériale',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Rappel indemnité Responsabilité',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Prime',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Indemnité de transport',
                    intier: '',
                    gains: '-',
                    retenus: ''
                },
                {
                    label: 'Rappel indemnité de transport',
                    intier: '',
                    gains: '-',
                    retenus: ''
                },
                {
                    label: 'Jours',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Rappel jirains',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Indemnité probatoire',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Rappel indemnité probatoire',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Rappel complément poste 2',
                    intier: '',
                    gains: '-',
                    retenus: ''
                },
                {
                    label: 'Prime personnel',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Rappel points personnels',
                    intier: '',
                    gains: '-',
                    retenus: ''
                },
                {
                    label: 'Prime repas',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Salaire brut',
                    intier: '1 777 145,45',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'CNAPS',
                    intier: '',
                    gains: '',
                    retenus: '17 771,45'
                },
                {
                    label: 'Osie',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Montant imposable',
                    intier: '1 759 375,00',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Avantages en nature',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Salaire net imposable',
                    intier: '1 759 375,00',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'IRSA avant abattement',
                    intier: '259 350,00',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Abattement charge familiale',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'IRSA',
                    intier: '',
                    gains: '',
                    retenus: '259 350,00'
                },
                {
                    label: 'Sanitaire',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Crédit personnel',
                    intier: '',
                    gains: '',
                    retenus: '492 850,32'
                },
                {
                    label: 'Avance sur carburant',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Autre retenu',
                    intier: '',
                    gains: '',
                    retenus: ''
                },
                {
                    label: 'Retraite complémentaire',
                    intier: '',
                    gains: '',
                    retenus: '17 771,45'
                }
            ]);

const totalIntier=ref('')
const totalGains=ref('')
const totalRetenus=ref('')
const salaireNet=ref('')
const netAPayer=ref('')
const soldeConge=ref('')
 
</script>
