<!-- filepath: d:\Etat_journalier\src\pages\app\session.vue -->

<template>
<v-container class="unified-container" fluid>
    <div>
        <UsersComponent v-if="!selectedUserId" :users="users" @select-user="handleSelectUser" />
        <userId v-else :user-id="selectedUserId" @back="selectedUserId = null" @user-validated="handleUserValidated" />
    </div>
</v-container>
</template>

<script setup>
import {
    ref,
    onMounted,
    inject,
    getCurrentInstance
} from 'vue'
import UsersComponent from '@/components/sessions/users.vue'
import userId from '@/components/PAIE/userId.vue'
import axios from 'axios'
import {
    useNotificationStore
} from '@/stores/notification'

const api = inject('api')
const users = ref([])
const selectedUserId = ref(null)

const notificationStore = useNotificationStore()

const {
    proxy
} = getCurrentInstance()

const fetchUsers = async () => {
    try {
        const response = await axios.get(`${api}/api/usersPaie`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
        })
        users.value = response.data.users
    } catch (e) {}
}

const handleSelectUser = (id) => {
    console.log('Selected user id:', id)
    selectedUserId.value = id
}

const handleUserValidated = async () => {
    await notificationStore.fetchDemandesValidation(api, 'usersPaie/pending_count')
    await fetchUsers()
}

onMounted(fetchUsers)
</script>

<style scoped>
.unified-container {
    max-height: 90vh;
    overflow-y: auto;
    padding-bottom: 20px;
    padding: 0 10px;
}

.unified-container::-webkit-scrollbar {
    display: none;
}
</style>
