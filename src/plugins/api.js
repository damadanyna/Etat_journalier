export default {
  install(app) {
    const protocol = window.location.protocol
    const hostname = window.location.hostname || '127.0.0.1'
    const apiPort = import.meta.env.VITE_API_PORT || '8000'
    const apiBaseUrl = `${protocol}//${hostname}:${apiPort}`

    app.config.globalProperties.$api = apiBaseUrl

    app.provide('api', app.config.globalProperties.$api)
  }
}
