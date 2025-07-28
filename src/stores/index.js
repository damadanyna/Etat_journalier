// stores/usePopupStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePopupStore = defineStore('popup', () => {
  const showPopup = ref(false)
  const showPopupCDI = ref(false)
  const cdi_list_stream= ref([])
  const cdi_list_file_stream= ref([])
  const precentage=ref(0)
  const loadFile=ref("Préparation ...");
  const list_a_traiter=ref([])
  const selected_date=ref(null)
  const encours_actual_data=ref([])
  const remboursement_actual_data=ref([])
  const limit_avm_actual_data=ref([]) 
  const limit_caution_actual_data=ref([])
  const show_notification=ref({status:false,message:"null",ico:"null"})
  const user_access=ref([{
    name:"rgpp-onisoa",
    password:"123456",
    app:"gpp",
    url:'/gpp/dec_credit'
  },
  {
    name:"a",
    password:"a",
    app:"cdi",
    url:'/cdi/list_cdi'
  },
  {
    name:"d",
    password:"d",
    app:"reportico",
    url:'/reportico/compensation'
  },
])

  const togglePopup = () => {
    showPopup.value = !showPopup.value
  }
  const togglePopupCDI = () => {
    showPopupCDI.value = !showPopupCDI.value
  }

  return { showPopup,
    togglePopupCDI,
    precentage,
    showPopupCDI,
    cdi_list_file_stream,
    cdi_list_stream,
     togglePopup,
    loadFile,
    show_notification,
    user_access,
    list_a_traiter,
    selected_date,
    encours_actual_data,
    remboursement_actual_data,
    limit_caution_actual_data, 
    limit_avm_actual_data

  }
})
