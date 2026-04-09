<template>
<v-navigation-drawer v-model="drawer" :rail="rail" permanent>
    <v-list-item :title="popupStore.user_access.name" nav @click.stop="rail = !rail">
        <template v-slot:append>
            <v-btn icon="mdi-menu" variant="text"></v-btn>
        </template>
    </v-list-item>

    <v-divider></v-divider>

    <v-list density="compact" nav>
        <v-list-item v-for="item in filteredMenu" :key="item.to" :to="item.to" color="green-accent-3"  >
            <template #prepend>
                <v-badge v-if="item.badge && item.badge() > 0" :content="item.badge()" color="red" overlap bordered style="margin-right:8px;">
                    <v-icon :icon="item.icon"></v-icon>
                </v-badge>
                <v-icon v-else :icon="item.icon"></v-icon>
            </template>
            <template #title>
                {{ item.title }}
            </template>
        </v-list-item>
    </v-list>
</v-navigation-drawer>
</template>

<script setup>
import {
    usePopupStore
} from '../../stores';
import {
    ref,
    computed,
    onMounted,
    onBeforeUnmount,
    inject
} from 'vue';
import {
    useNotificationStore
} from '../../stores/notification'

const notificationStore = useNotificationStore()

const drawer = ref(true);
const rail = ref(true);
const popupStore = usePopupStore();

const api = inject('api')

const list_menu = [{
        icon: 'mdi-home-city',
        title: 'Accueil',
        to: '/paie/accueil', 
        access: 'all'
    },
    {
        icon: 'mdi-shield-account',
        title: 'Demande de Validation ',
        to: '/paie/session',
        access: 'admin',
        badge: () => notificationStore.demandesValidation
    },
    {
        icon: 'mdi-file',
        title: 'Importation',
        to: '/paie/file_manager',
        access: 'admin'
    }, 
    { icon: 'mdi-file-table-box-multiple-outline', title: 'Historique', to: '/paie/history', access: 'admin' },
];

const fetchDemandesValidation = async () => {
    try {
        await notificationStore.fetchDemandesValidation(api, 'usersPaie/pending_count')
    } catch (e) {
        notificationStore.setDemandesValidation(0)
    }
}

const handlePendingValidationUpdated = (event) => {
    const count = event.detail?.count || 0
    notificationStore.setDemandesValidation(count)
}
 
const filteredMenu = computed(() => {
    const privilege = popupStore.user_access.access || '';
    if (['admin', 'superadmin'].includes(privilege)) {
        return list_menu;
    }
    return list_menu.filter(item => item.access !== 'superadmin' && item.access !== 'admin');
});

onMounted(() => {
    fetchDemandesValidation()
    window.addEventListener('socket:pending-validation-updated', handlePendingValidationUpdated)
})

onBeforeUnmount(() => {
    window.removeEventListener('socket:pending-validation-updated', handlePendingValidationUpdated)
})
defineExpose({
    fetchDemandesValidation
})
</script>
