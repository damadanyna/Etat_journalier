export default {
  install(app) {
    const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
    const apiBaseUrl = configuredApiBaseUrl.replace(/\/api\/?$/, '')

    app.config.globalProperties.$api = apiBaseUrl

    app.provide('api', app.config.globalProperties.$api)
  }
}
