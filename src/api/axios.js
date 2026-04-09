// src/axios.js
import axios from 'axios';

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
const configuredBackendUrl = import.meta.env.VITE_DEV_BACKEND_URL || ''
const shouldUseAbsoluteBackend = typeof window !== 'undefined'
  && window.location.protocol === 'file:'
  && configuredApiBaseUrl.startsWith('/')
  && configuredBackendUrl
const resolvedApiBaseUrl = shouldUseAbsoluteBackend
  ? `${configuredBackendUrl.replace(/\/$/, '')}${configuredApiBaseUrl}`
  : configuredApiBaseUrl

const api = axios.create({
  baseURL: resolvedApiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
