// src/stores/notification.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useNotificationStore = defineStore('notification', () => {
  const demandesValidation = ref(0)
  const setDemandesValidation = (count) => {
    demandesValidation.value = count || 0
  }

  const fetchDemandesValidation = async (api, endpoint = 'users/pending_count') => {
    try {
      const res = await axios.get(`${api}/api/${endpoint}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
      demandesValidation.value = res.data.count || 0
    } catch (e) {
      demandesValidation.value = 0
    }
  }
  return { demandesValidation, setDemandesValidation, fetchDemandesValidation }
})