<template> 
  <v-btn @click="runAllSteps()"
          class="me-2 text-none ml-10 text-white"
          color="#00DF76"
          prepend-icon="mdi-play-circle"
          variant="flat"
          :disabled="isRunning"
          :style="{ opacity: isRunning ? 0.3 : 1 }"
        >
          Lancer
        </v-btn>
  <div class="stepper-container">
    <v-stepper alt-labels v-model="currentStep" class="transparent-stepper">
      <v-stepper-header>
        <template v-for="(step, index) in steps" :key="index">
          <v-stepper-item
            :value="index + 1"
            :complete="step.status === 'success'"
            :color="getColor(step.status)"
          >
            <template v-slot:title>
              {{ step.title }}
            </template>

            <template v-slot:subtitle>
              <span>{{ getSubtitle(step.status) }}</span>
            </template>
          </v-stepper-item>

          <v-divider v-if="index + 1 < steps.length"></v-divider>
        </template>
      </v-stepper-header>
    </v-stepper>
    <div class="flex px-6 ">
    </div>
  </div> 
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const steps = ref([
  { title: 'Initialisation', status: 'pending' },
  { title: 'États des encours', status: 'pending' },
  { title: 'État des remboursements', status: 'pending' },
  { title: 'État prévisionnel de remboursement', status: 'pending' },
  { title: 'Limit AVM', status: 'pending' },
  { title: 'Limit Caution', status: 'pending' },
])

const currentStep = ref(1)
const isRunning = ref(false)

const runStep = async (index) => {
  steps.value[index].status = 'running'
  try {
    // Simuler une exécution (remplace par le vrai code)
    await new Promise((resolve, reject) => {
      setTimeout(() => {
        const fail = Math.random() < 0.15
        fail ? reject() : resolve()
      }, 1500)
    })
    steps.value[index].status = 'success'
  } catch {
    steps.value[index].status = 'error'
  }
}

watch(isRunning, (newVal) => {
  if (newVal) {
    steps.value.forEach((step) => {
      step.status = 'pending'
    })
  }
})

const runAllSteps = async () => {
  isRunning.value = true
  for (let i = 0; i < steps.value.length; i++) {
    currentStep.value = i + 1
    await runStep(i)
  }
  isRunning.value = false
}

const getColor = (status) => {
  switch (status) {
    case 'success': return 'green'
    case 'error': return 'red'
    case 'running': return 'white'
    default: return ''
  }
}

const getSubtitle = (status) => {
  switch (status) {
    case 'success': return 'Terminé'
    case 'error': return 'Erreur'
    case 'running': return 'En cours...'
    case 'pending': return 'En attente'
    default: return ''
  }
}

onMounted(() => {
  
})
</script>

<style scoped>
.transparent-stepper {
  background-color: transparent !important;
  box-shadow: none !important;
}
</style>
