// src/axios.js
import axios from 'axios';

const api = axios.create({
<<<<<<< HEAD
  baseURL: 'http://10.192.1.94:8000', // ton IP de backend Flask
=======
  baseURL: 'http://127.0.0.1:8000', // ton IP de backend Flask
>>>>>>> master
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
