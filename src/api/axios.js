// src/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://10.192.1.94:8000', // ton IP de backend Flask
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
