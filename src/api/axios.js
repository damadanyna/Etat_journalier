// src/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://192.168.1.212:8000', // ton IP de backend Flask
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
