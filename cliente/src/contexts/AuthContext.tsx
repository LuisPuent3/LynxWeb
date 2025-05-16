import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';

interface User {
  id_usuario: number;
  nombre: string;
  correo: string;
  rol: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, userData: User) => Promise<void>;
  logout: () => void;
  error: string | null;
  procesarPedidoPendiente: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Configurar el interceptor de axios para incluir el token en las peticiones
  useEffect(() => {
    const interceptor = api.interceptors.request.use(
      (config) => {
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Limpiar el interceptor cuando el componente se desmonte
    return () => {
      api.interceptors.request.eject(interceptor);
    };
  }, [token]);

  // Verificar el token al cargar la aplicación
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        // Ruta correcta a la API
        const response = await api.get('/auth/verify');
        // Actualizando el nombre del campo según la respuesta real del servidor
        setUser(response.data.usuario);
      } catch (err) {
        console.error('Error al verificar el token:', err);
        // Si hay un error, limpiar el estado de autenticación
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    verifyToken();
  }, [token]);

  // Escuchar el evento loginSuccess para procesar pedidos pendientes
  useEffect(() => {
    const handleLoginSuccess = () => {
      procesarPedidoPendiente();
    };

    document.addEventListener('loginSuccess', handleLoginSuccess);

    return () => {
      document.removeEventListener('loginSuccess', handleLoginSuccess);
    };
  }, []);

  const login = async (newToken: string, userData: User) => {
    try {
      // Guardar el token en localStorage
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setUser(userData);
      setError(null);
      
      // Configurar el encabezado de autorización para futuras peticiones
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    } catch (err) {
      console.error('Error en login:', err);
      setError('Error al iniciar sesión');
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('guestMode');
    setToken(null);
    setUser(null);
    
    // Limpiar el encabezado de autorización
    delete api.defaults.headers.common['Authorization'];
  };

  // Función para procesar un pedido pendiente después del login
  const procesarPedidoPendiente = async () => {
    if (!token || !user) return;
    
    try {
      // Verificar si hay un carrito guardado
      const savedCarrito = localStorage.getItem('tempCarrito');
      if (!savedCarrito) return;
      
      const carrito = JSON.parse(savedCarrito);
      if (carrito.length === 0) return;
      
      // Preparar los datos del pedido
      const pedidoData = {
        carrito: carrito.map((item: any) => ({
          id_producto: Number(item.id_producto),
          cantidad: Number(item.cantidad),
          precio: Number(item.precio)
        })),
        id_usuario: user.id_usuario
      };
      
      // Realizar la solicitud al backend
      console.log('Procesando pedido pendiente:', pedidoData);
      const response = await api.post('/pedidos', pedidoData);
      
      if (response.data && response.data.mensaje) {
        alert('¡Pedido realizado con éxito!');
        // Limpiar el carrito después de procesar el pedido
        localStorage.removeItem('tempCarrito');
      }
    } catch (error) {
      console.error('Error al procesar el pedido pendiente:', error);
      alert('Hubo un problema al procesar tu pedido. Por favor intenta nuevamente.');
    }
  };

  // Añadir una función de log para depurar información del usuario
  useEffect(() => {
    if (user) {
      console.log('Información del usuario autenticado:', {
        id: user.id_usuario,
        nombre: user.nombre,
        correo: user.correo,
        rol: user.rol
      });
    }
  }, [user]);

  const value = {
    user,
    token,
    isAuthenticated: !!token,
    isLoading,
    login,
    logout,
    error,
    procesarPedidoPendiente
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext; 