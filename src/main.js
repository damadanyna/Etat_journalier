import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import { createRouter, createWebHistory } from 'vue-router'
import routes from 'virtual:generated-pages' 
import '@mdi/font/css/materialdesignicons.css' 
import { createPinia } from 'pinia'
import './plugins/chart'
import api from './plugins/api' 
// Initialize Pinia
const pinia = createPinia()
const router = createRouter({
  history: createWebHistory(),
  routes,
}) 

 

createApp(App)
  .use(pinia)
  .use(vuetify)
  .use(router)
  .use(api)
  .mount('#app')