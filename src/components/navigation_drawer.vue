<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="rail"
    permanent
  >
    <v-list-item 
      :title="popupStore.user_access.name"
      nav
      @click.stop="rail = !rail"
    >
      <template v-slot:append>
        <v-btn icon="mdi-menu" variant="text"></v-btn>
      </template>
    </v-list-item>

    <v-divider></v-divider>

    <v-list density="compact" nav>
      <v-list-item
        v-for="item in filteredMenu"
        :key="item.to"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        color="green-accent-3"
      />
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
import { usePopupStore } from '../stores';
import { ref, computed } from 'vue';

const drawer = ref(true);
const rail = ref(true);
const popupStore = usePopupStore();

const list_menu = [
  { icon: 'mdi-home-city', title: 'Crédits', to: '/app/credits', access: 'all' },
  { icon: 'mdi-bank', title: 'My Account', to: '/app/dav', access: 'all' },
  { icon: 'mdi-account', title: 'ESRI', to: '/app/esri', access: 'all' },
  { icon: 'mdi-swap-horizontal', title: 'CHANGE', to: '/app/change', access: 'all' },
  { icon: 'mdi-shield-account', title: 'Admin', to: '/app/session', access: 'admin' },
  { icon: 'mdi-file-table-box-multiple-outline', title: 'Mes Fichiers', to: '/app/file_manager', access: 'admin' },
];

const filteredMenu = computed(() => {
  const privilege = popupStore.user_access.access|| '';
  if (['admin', 'superadmin'].includes(privilege)) {
    return list_menu; 
  }
  return list_menu.filter(item => item.access !== 'superadmin' && item.access !== 'admin');
});
</script>
