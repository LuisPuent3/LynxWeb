// src/utils/api.ts
import axios from 'axios';

// Crear una instancia de axios con configuración predeterminada
const api = axios.create({
  baseURL: import.meta.env.PROD ? '/api' : 'http://localhost:5000/api', // URL base para todas las solicitudes
  timeout: 30000, // Tiempo máximo de espera ampliado a 30 segundos
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Interceptor para mostrar información de solicitudes en la consola (para depuración)
api.interceptors.request.use(
  config => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    return config;
  },
  error => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Interceptor para mostrar información de respuestas en la consola (para depuración)
api.interceptors.response.use(
  response => {
    console.log(`API Response: ${response.status} desde ${response.config.url}`);
    return response;
  },
  error => {
    if (error.response) {
      console.error(`API Error: ${error.response.status} desde ${error.config.url}`);
      console.error('Error data:', error.response.data);
    } else {
      console.error('API Error sin respuesta:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;