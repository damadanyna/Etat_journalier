export default {
  install(app) {
    // ✅ Définit une propriété globale accessible dans tous les composants
    app.config.globalProperties.$api = 'http://127.0.0.1:8000'

    // ✅ (optionnel) Tu peux aussi l’ajouter à app.provide pour l’injecter avec `inject()`
    app.provide('api', app.config.globalProperties.$api)
  }
}
