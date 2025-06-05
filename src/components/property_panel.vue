<template>  
        <v-navigation-drawer 
          permanent
        >
          <template v-slot:prepend>
            <v-list-item
              lines="two"
              prepend-avatar="https://randomuser.me/api/portraits/women/81.jpg"
              subtitle="Logged in"
              title="Jane Smith"
            ></v-list-item>
          </template>
  
          <v-divider></v-divider>
  
          <v-list density="compact" nav>
            <v-list-item v-for="item in menu_list" :key="item" :prepend-icon="item.icon" :title="item.title" :value="item.value"></v-list-item> 
          </v-list>
        </v-navigation-drawer>
  </template>
<script setup>
import { ref } from 'vue';
const menu_list = ref([
  {
    title: 'Home',
    icon: 'mdi-home-city',
    value: 'home'
  },
  {
    title: 'My Account',
    icon: 'mdi-account',
    value: 'account'
  },
  {
    title: 'Users',
    icon: 'mdi-account-group-outline',
    value: 'users'
  },  
])

</script>