<!-- filepath: d:\Etat_journalier\src\pages\app\session.vue -->

<template>
  <div>
    <UsersComponent
      v-if="!selectedUserId"
      :users="users"
      @select-user="handleSelectUser"
    />
    <userId
      v-else
      :user-id="selectedUserId"
      @back="selectedUserId = null"
    />
  </div>
</template>

<script setup>
import { ref, onMounted ,inject} from 'vue'
import UsersComponent from '@/components/sessions/users.vue'
import userId from '@/components/sessions/userId.vue'
import axios from 'axios'
const api = inject('api') 

const users = ref([])
const selectedUserId = ref(null)

const fetchUsers = async () => {
  try {
    const response = await axios.get(`${api}/api/users`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    users.value = response.data.users
  } catch (e) {
    // gestion d'erreur
  }
}

const handleSelectUser = (id) => {
  console.log('Selected user id:', id)
  selectedUserId.value = id
}

onMounted(fetchUsers)
</script>
