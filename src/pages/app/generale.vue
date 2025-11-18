<template>
  <v-container class="py-8">
    <v-card class="pa-6 rounded-xl elevation-3" max-width="700" mx-auto>
      <h2 class="text-h6 font-weight-bold mb-4 text-center">
        Recherche par Produit / Agence
      </h2>
      <v-row>
        <v-col cols="12" md="3">
          <v-select
            v-model="typeTable"
            :items="['dav', 'dat', 'epr']"
            label="Type de Table"
            dense
            outlined
            required
          />
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field
            v-model="agence"
            label="Agence (code ou 'all')"
            dense
            outlined
            clearable
          />
        </v-col>
        <v-col cols="12" md="2">
          <v-text-field
            v-model="dateDebut"
            label="Date début (YYYYMMDD)"
            dense
            outlined
            clearable
          />
        </v-col>
        <v-col cols="12" md="2">
          <v-text-field
            v-model="dateFin"
            label="Date fin (YYYYMMDD)"
            dense
            outlined
            clearable
          />
        </v-col>
        <v-col cols="12" md="2">
          <v-text-field
            v-model="singleDate"
            label="Date unique (YYYYMMDD)"
            dense
            outlined
            clearable
          />
        </v-col>
      </v-row>
      <v-btn
        color="primary"
        class="mt-4"
        :loading="loading"
        @click="rechercher"
        rounded="lg"
      >
        <v-icon left>mdi-magnify</v-icon>
        Rechercher
      </v-btn>
      <v-alert
        v-if="message"
        :type="messageType"
        class="mt-4"
        border="start"
        rounded="lg"
      >
        {{ message }}
      </v-alert>
      <v-data-table
        v-if="results.length"
        :headers="headers"
        :items="results"
        class="mt-6 elevation-1"
        dense
        height="400px"
      />
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, inject } from "vue"
import axios from "axios"

const api = inject("api")
const typeTable = ref("dav")
const agence = ref("")
const singleDate = ref("")
const dateDebut = ref("")
const dateFin = ref("")
const loading = ref(false)
const message = ref("")
const messageType = ref("info")
const results = ref([])

const headers = ref([
  { title: "Date", key: "date" },
  { title: "Agence", key: "agence" },
  { title: "Clients", key: "nb_clients" },
  { title: "Montant", key: "total_montant" },
  { title: "Débit", key: "total_debit" },
  { title: "Crédit", key: "total_credit" },
])

const rechercher = async () => {
  loading.value = true
  message.value = ""
  results.value = []
  try {
    const res = await axios.get(`${api}/api/resume/total-produit/${typeTable.value}`, {
      params: {
        agence: agence.value,
        single_date_if_all: singleDate.value,
        date_debut: dateDebut.value,
        date_fin: dateFin.value,
      }
    })
    if (Array.isArray(res.data)) {
      results.value = res.data
      messageType.value = "success"
      message.value = `Résultats trouvés : ${res.data.length}`
    } else if (res.data.message) {
      messageType.value = "error"
      message.value = res.data.message
    } else {
      messageType.value = "info"
      message.value = "Aucun résultat."
    }
  } catch (err) {
    messageType.value = "error"
    message.value = "Erreur lors de la recherche."
  } finally {
    loading.value = false
  }
}
</script>