import axios from 'axios';

// Configuración básica de axios para la aplicación
const api = axios.create({
  baseURL: 'http://localhost:3000/api', // URL base para las solicitudes API
  timeout: 5000, // Tiempo máximo de espera para las solicitudes
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Interceptor para manejar respuestas
api.interceptors.response.use(
  response => response,
  error => {
    // Podemos realizar un manejo de errores centralizado aquí
    // Por ejemplo, redirigir al login si hay un error 401
    if (error.response && error.response.status === 401) {
      // Podríamos redireccionar al login o mostrar una alerta
      console.error('Error de autenticación');
    }
    
    // Reenviar el error para que pueda ser manejado por el componente
    return Promise.reject(error);
  }
);

// Interceptor para agregar token de autenticación a las solicitudes
api.interceptors.request.use(
  config => {
    // Obtener token del localStorage
    const token = localStorage.getItem('token');
    
    // Si existe un token, agregarlo al encabezado de autorización
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  error => Promise.reject(error)
);

export default api; 