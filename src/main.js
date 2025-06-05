import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import { createRouter, createWebHistory } from 'vue-router'
import routes from 'virtual:generated-pages' 
import '@mdi/font/css/materialdesignicons.css' 


const router = createRouter({
  history: createWebHistory(),
  routes,
}) 
createApp(App)
.use(vuetify)
.use(router)
.mount('#app')
  