<template>
<div class=" max-h-full  ">
    <button @click="telechargerPDF() " :disabled="isGeneratingPDF"class=" text-white border-stone-500 mb-3">
      <span class=" bg-green-700 px-3 py-1  rounded-2xl"> {{ isGeneratingPDF ? 'Génération en cours...' : 'Télécharger PDF' }}</span>
  </button>
    <div class="max-w-4xl mx-auto px-4 py-7 h-full bg-white"  id="file_" >
        <!-- Header avec logo et titre -->
        <div class=" flex items-center justify-between">
            <img class=" w-[100px] " src="../../../../public/img/logo.jpg" alt="">
            <div v-if="props.data" class=" flex flex-col items-center">
                <span class=" font-bold ">FICHE DE PAIE</span>
                <span class=" text-sm ">{{formaterMoisAnnee(props.data[1].upload_date) }}</span>
            </div>
            <div></div>
        </div>

        <!-- Informations employé et agence -->
        <div class=" flex justify-between  mt-4    ">
            <div class="space-y-2">
                <div class="flex">
                    <span class="font-semibold text-sm w-40">N° Matricule :</span>
                    <span class="text-sm border-[1px] font-bold px-7 border-black ">{{ matricule }}</span>
                </div>
                <div class="flex">
                    <span class="font-semibold text-sm w-40">Agent :</span>
                    <span class="text-sm font-semibold">{{ agent }}</span>
                </div>
                <div class="flex">
                    <span class="font-semibold text-sm w-40">Fonction :</span>
                    <span class="text-sm">{{ fonction }}</span>
                </div>
                <div class="flex">
                    <span class="font-semibold text-sm w-40">Date d'embauche :</span>
                    <span class="text-sm">{{ dateEmbauche }}</span>
                </div>
                <div class="flex">
                    <span class="font-semibold text-sm w-40">Département :</span>
                    <span class="text-sm">{{ departement }}</span>
                </div>
                <div class="flex">
                    <span class="font-semibold text-sm w-40">Direction :</span>
                    <span class="text-sm ">{{ direction }}</span>
                </div>
                <div class="flex">
                    <span class="font-semibold text-sm w-40">N°CNAPS :</span>
                    <span class="text-sm">980402005797</span>
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
                        <th class="border-[1px] border-gray-400 px-3 py-2 text-center font-bold">RUBRIQUES</th>
                        <th class="border-[1px] border-gray-400 px-3 py-2 text-center font-bold">INTIER</th>
                        <th class="border-[1px] border-gray-400 px-3 py-2 text-center font-bold">GAINS</th>
                        <th class="border-[1px] border-gray-400 px-3 py-2 text-center font-bold" colspan="2">RETENUS</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in rubriques" :key="index" :class="item.bold ? 'bg-yellow-50 font-bold' : ''">
                        <td class="border-[1px] border-gray-400 px-3 py-1" :class="item.bold ? 'font-bold' : ''">{{ item.label }}</td>
                        <td class="border-[1px] border-gray-400 px-3 py-1 text-right">{{ item.intier }}</td>
                        <td class="border-[1px] border-gray-400 px-3 py-1 text-right">{{ item.gains }}</td>
                        <td class="border-[1px] border-gray-400 px-3 py-1 text-right" colspan="2">{{ item.retenus }}</td>
                    </tr>
                </tbody>
                <tfoot>
                    <tr class="bg-gray-100 ">
                        <td class="border-[1px] border-gray-400 px-3 py-2">TOTAL</td>
                        <td class="border-[1px] border-gray-400 px-3 py-2 text-right">{{ totalIntier }}</td>
                        <td class="border-[1px] border-gray-400 px-3 py-2 text-right">{{ totalGains }}</td>
                        <td class="border-[1px] border-gray-400 px-3 py-2 text-right" colspan="2">{{ totalRetenus }}</td>
                    </tr>
                    <tr class="bg-gray-100">
                        <td class="border-[1px] border-gray-400 px-3 py-2">SALAIRE NET</td>
                        <td class="border-[1px] border-gray-400 px-3 py-2"></td>
                        <td class="border-[1px] border-gray-400 px-3 py-2"></td>
                        <td class="border-[1px] border-gray-400 px-3 py-2 text-right" colspan="2">{{ salaireNet }}</td>
                    </tr>
                    <tr class="bg-gray-100">
                        <td class="border-[1px] border-gray-400 px-3 py-2  font-semibold">NET A PAYER</td>
                        <td class="border-[1px] border-gray-400 px-3 py-2"></td>
                        <td class="border-[1px] border-gray-400 px-3 py-2"></td>
                        <td class="border-[1px] border-gray-400 px-3 py-2  font-semibold text-right text-lg" colspan="2">{{ netAPayer }}</td>
                    </tr>
                    <tr class="bg-gray-100">
                        <td class="border-[1px] border-gray-400 px-3 py-2 font-semibold">Solde Congé</td>
                        <td class="border-[1px] border-gray-400 px-3 py-2"></td>
                        <td class="border-[1px] border-gray-400 px-3 py-2"></td>
                        <td class="border-[1px] border-gray-400 px-3 py-2  font-semibold text-right" colspan="2">{{ soldeConge }}</td>
                    </tr>
                </tfoot>
            </table>
        </div> 
        <!-- Footer -->
        <div class="  mt-[200px] text-center w-full flex justify-end">
            <div class="flex flex-col">
                <div class="text-xs text-gray-600  flex flex-col">
                    <span>L'Employeur ou son</span>
                    <span>Représentant</span>
                </div>
                <img src="../../../../../back_end/load_file_paie/sign/signature.png" class=" w-[150px]" alt="">
        
            </div>
        </div>
    </div>
</div>
</template>

<script setup>

import { ref,computed,watch} from 'vue';
import html2pdf from 'html2pdf.js';

import domtoimage from 'dom-to-image'
import jsPDF from 'jspdf'

const isGeneratingPDF = ref(false)

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

const rubriques = ref([
    { label: 'Salaire de base', intier: '', gains: '', retenus: '' },
    { label: 'Rappel sur salaire de base', intier: '', gains: '', retenus: '' },
    { label: 'Complément panier', intier: '', gains: '', retenus: '' },
    { label: 'Rappel complément panier', intier: '', gains: '', retenus: '' },
    { label: 'Indemnité de logement', intier: '', gains: '', retenus: '' },
    { label: 'Rappel indemnité de logement', intier: '', gains: '', retenus: '' },
    { label: 'Indemnité de fonction', intier: '', gains: '', retenus: '' },
    { label: 'Rappel indemnité de fonction', intier: '', gains: '', retenus: '' },
    { label: 'Indemnité Responsabilité Manageriale', intier: '', gains: '', retenus: '' },
    { label: 'Rappel indemnité Responsabilité Manageriale', intier: '', gains: '', retenus: '' },
    { label: 'Indemnité de transport', intier: '', gains: '', retenus: '' },
    { label: 'Rappel indemnité de transport', intier: '', gains: '', retenus: '' },
    { label: 'Jirama', intier: '', gains: '', retenus: '' },
    { label: 'Rappel jirama', intier: '', gains: '', retenus: '' },
    { label: 'Indeminté probatoire', intier: '', gains: '', retenus: '' },
    { label: 'Rappel indeminté probatoire', intier: '', gains: '', retenus: '' },
    { label: 'Complément panier 2', intier: '', gains: '', retenus: '' },
    { label: 'Rappel complément panier 2', intier: '', gains: '', retenus: '' },
    { label: 'Points personnels', intier: '', gains: '', retenus: '' },
    { label: 'Rappel points personnels', intier: '', gains: '', retenus: '' },
    { label: 'Prime mensuel', intier: '', gains: '', retenus: '' },
    { label: 'Salaire brut', intier: '', gains: '', retenus: '' },
    { label: 'CNAPS', intier: '', gains: '', retenus: '' },
    { label: 'OSTIE', intier: '', gains: '', retenus: '' },
    { label: 'Montant imposable', intier: '', gains: '', retenus: '' },
    { label: 'Avantage en nature', intier: '', gains: '', retenus: '' },
    { label: 'Salaire net imposable', intier: '', gains: '', retenus: '' },
    { label: 'IRSA avant abattement', intier: '', gains: '', retenus: '' },
    { label: 'Abattement charge familiale', intier: '', gains: '', retenus: '' },
    { label: 'IRSA', intier: '', gains: '', retenus: '' },
    { label: 'Allocation familiale', intier: '', gains: '', retenus: '' },
    { label: 'Crédit personnel', intier: '', gains: '', retenus: '' },
    { label: 'Avance sur carburant', intier: '', gains: '', retenus: '' },
    { label: 'Autre retenu', intier: '', gains: '', retenus: '' },
    { label: 'Retraite complementaire', intier: '', gains: '', retenus: '' }
]);


const totalIntier=ref('')
const totalGains=ref('')
const totalRetenus=ref('')
const salaireNet=ref('')
const netAPayer=ref('')
const soldeConge=ref('')


// Mapping entre les labels des rubriques et les clés de l'objet de données
const mappingRubriquesVersData = {
  'Salaire de base': 'salaire_de_base',
  'Rappel sur salaire de base': 'rpl_salbase',
  'Complément panier': 'cplt_panier',
  'Rappel complément panier': 'rpl_cpl_panier',
  'Indemnité de logement': 'ind_logt',
  'Rappel indemnité de logement': 'rpl_ind_logt',
  'Indemnité de fonction': 'ind_fonction',
  'Rappel indemnité de fonction': 'rpl_ind_fonction',
  'Indemnité Responsabilité Manageriale': 'ind_resp_managéri',
  'Rappel indemnité Responsabilité Manageriale': 'rappel_ind_resp_m',
  'Indemnité de transport': 'ind_transport',
  'Rappel indemnité de transport': 'rappel_ind_trans',
  'Jirama': 'eau_et_elec',
  'Rappel jirama': 'rpl_eau_elec',
  'Indeminté probatoire': 'ind_probatoire',
  'Rappel indeminté probatoire': 'rappel_ind_prob_',
  'Complément panier 2': 'compl_panier_2',
  'Rappel complément panier 2': 'rappel_compl_pan_2',
  'Points personnels': 'points_personnels',
  'Rappel points personnels': '', // Pas de correspondance trouvée
  'Prime mensuel': 'prime_mensuel',
  'Salaire brut': 'salaire_brut',
  'CNAPS': 'cnaps',
  'OSTIE': 'ostie',
  'Montant imposable': 'montant_imp_',
  'Avantage en nature': 'avantage_nature',
  'Salaire net imposable': 'montant_imp_', // Calculé généralement
  'IRSA avant abattement': 'irsa_avt_abt',
  'Abattement charge familiale': 'abt_chg_famil',
  'IRSA': 'irsa',
  'Allocation familiale': 'alloc_famil',
  'Crédit personnel': 'crédit_au_personnel',
  'Avance sur carburant': 'avc_carburant',
  'Autre retenu': 'autre_retenu',
  'Retraite complementaire': 'retrite_cpl'
};

// Fonction pour remplir les gains
function remplirdata(rubriques, donneesEmploye) {
  rubriques.value.forEach(rubrique => {
    const cleData = mappingRubriquesVersData[rubrique.label];
    
    if (cleData && donneesEmploye[cleData]) {
      // Convertir la valeur en nombre et formater si nécessaire
      const valeur = parseFloat(donneesEmploye[cleData]) || '';
      
      // Condition spéciale pour "Salaire brut" et "Montant imposable"
      if (rubrique.label === 'Salaire brut' 
      || rubrique.label === 'Montant imposable' 
      || rubrique.label === 'Salaire net imposable' 
      || rubrique.label === 'Avantage en nature' 
      || rubrique.label === 'IRSA avant abattement' 
      || rubrique.label === 'Abattement charge familiale') {
        rubrique.intier = formaterValeur(valeur);
      } // Condition spéciale pour "Salaire brut" et "Montant imposable"
      else if (rubrique.label === 'CNAPS' 
      || rubrique.label === 'OSTIE' 
      || rubrique.label === 'IRSA' 
      || rubrique.label === 'Crédit personnel' 
      || rubrique.label === 'Avance sur carburant' 
      || rubrique.label === 'Autre retenu'
      || rubrique.label === 'Retraite complementaire') {
        rubrique.retenus = formaterValeur(valeur);
      } else {
        rubrique.gains = formaterValeur(valeur);
      }
    }
  });
}

 
function formaterValeur(valeur) { 
  if (!valeur || valeur === 0 || valeur === "0") {
    return "-";
  }
  const nombre = parseFloat(valeur); 
  if (isNaN(nombre)) {
    return "-";
  }  
  const nombreFormate = nombre.toFixed(2); 
  const [partieEntiere, partieDecimale] = nombreFormate.split('.'); 
  const partieEntiereFormatee = partieEntiere.replace(/\B(?=(\d{3})+(?!\d))/g, ' '); 
  return `${partieEntiereFormatee}.${partieDecimale}`;
}

// remplirdata(rubriques, donneesEmploye);

watch(() => props.data[0], (val) => {
    if (!val || !val.fonction) return;
    // console.log(val);
    fonction.value = val.fonction
    matricule.value = val.matricule
    agent.value = val.nom_et_prenom_s_
    dateEmbauche.value = val.date_d_embauche
    departement.value= val.département
    direction.value = val.direction
    cnaps.value = val.chg_employeur_cnaps 
    agence.value = val.agence
    categorie.value = val.catégorie
    type.value = val.type_de_contrat


    // const result = totalByKey('gains');

    totalIntier.value = val.total_intier;
    totalGains.value = formaterValeur(val.salaire_brut);
    totalRetenus.value = computed(() => {
        return formaterValeur(totalByKey('retenus'))
        })
    // totalRetenus.value =  formaterValeur(totalByKey('retenus')); 
    salaireNet.value =formaterValeur (val.net_à_payer) 
    netAPayer.value =formaterValeur(val.net_à_payer) 
    soldeConge.value = val.solde_congé 
    // Element de base 
    remplirdata(rubriques, val) 
}, {deep: true, immediate: true })

 

function totalByKey(key) {
  let total = 0;
  for (const row of rubriques.value) {
    const value = row[key];
    if (value) {
      const numeric = parseFloat(
        value.replace(/\s/g, '').replace(',', '.')
      );
      total += isNaN(numeric) ? 0 : numeric;
    }
  }

  return total;
}


async function telechargerPDF() {
  isGeneratingPDF.value = true
  
  try {
    const element = document.querySelector('#file_')
    element.style.width = '3480px'
    if (!element) {
      throw new Error('Élément non trouvé')
    }
    
    // Calculer les dimensions avec un scale élevé pour meilleure qualité
    const scale = 5 // Augmenter pour plus de qualité (2-4 recommandé)
    
    // Convertir en image avec dom-to-image en haute résolution
    const dataUrl = await domtoimage.toPng(element, {
      quality: 1,
      bgcolor: '#ffffff',
      width: element.offsetWidth * scale,
      height: element.offsetHeight * scale,
      style: {
        transform: `scale(${scale})`,
        transformOrigin: 'top left',
        width: `${element.offsetWidth}px`,
        height: `${element.offsetHeight}px`
      }
    })
    
    // Créer le PDF
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = pdf.internal.pageSize.getHeight()
    
    // Créer une image pour calculer les bonnes proportions
    const img = new Image()
    img.src = dataUrl
    
    await new Promise((resolve) => {
      img.onload = resolve
    })
    
    // Calculer les dimensions pour tenir sur une seule page avec marges
    const maxWidth = pdfWidth - 20 // marges de 10mm de chaque côté
    const maxHeight = pdfHeight - 20 // marges de 10mm en haut et en bas
    
    // Calculer le ratio pour ajuster l'image
    const imgRatio = img.width / img.height
    const pageRatio = maxWidth / maxHeight
    
    let imgWidth, imgHeight
    
    if (imgRatio > pageRatio) {
      // L'image est plus large, ajuster par la largeur
      imgWidth = maxWidth
      imgHeight = maxWidth / imgRatio
    } else {
      // L'image est plus haute, ajuster par la hauteur
      imgHeight = maxHeight
      imgWidth = maxHeight * imgRatio
    }
    
    // Centrer l'image sur la page
    const xPosition = (pdfWidth - imgWidth) / 2
    const yPosition = (pdfHeight - imgHeight) / 2
    
    // Ajouter l'image sur une seule page
    pdf.addImage(dataUrl, 'PNG', xPosition, yPosition, imgWidth, imgHeight, undefined, 'FAST')
    
    pdf.save(`bulletin-paie-${formaterMoisAnnee(props.data[1].upload_date)}.pdf`)
    
  } catch (error) {
    console.error('Erreur:', error)
    alert('Erreur lors de la génération du PDF')
  } finally {
    isGeneratingPDF.value = false
    element.style.width = 'auto'
  }
}



function formaterMoisAnnee(dateStr) {
  // Extraire l'année et le mois
  const annee = dateStr.substring(0, 4);
  const mois = dateStr.substring(4, 6);
  
  // Tableau des noms de mois
  const nomsMois = [
    'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
    'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
  ];
  
  // Convertir le mois en index (01 -> 0, 02 -> 1, etc.)
  const indexMois = parseInt(mois, 10) - 1;
  
  // Retourner le format "Mois-Année"
  return `${nomsMois[indexMois]} ${annee}`;
}


</script>

<style scoped>
 

</style>