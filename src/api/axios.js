// src/axios.js
import axios from 'axios';

const protocol = window.location.protocol;
const hostname = window.location.hostname || '127.0.0.1';
const apiPort = import.meta.env.VITE_API_PORT || '8000';

const api = axios.create({
  baseURL: `${protocol}//${hostname}:${apiPort}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
