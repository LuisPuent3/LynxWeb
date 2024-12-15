// src/utils/PrivateRoute.tsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';

interface CustomJwtPayload {
  rol?: number;
  id?: number;
  exp?: number;
}

interface PrivateRouteProps {
  children: React.ReactNode;
  adminOnly?: boolean;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children, adminOnly = false }) => {
  const token = localStorage.getItem('token');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  try {
    const decodedToken = jwtDecode<CustomJwtPayload>(token);

    // Verificar expiración
    if (decodedToken.exp && decodedToken.exp < Date.now() / 1000) {
      localStorage.removeItem('token');
      return <Navigate to="/login" replace />;
    }

    // Verificar rol para rutas de admin
    if (adminOnly) {
      if (decodedToken.rol !== 2) {
        return <Navigate to="/" replace />;
      }
    }

    return <>{children}</>;
  } catch (error) {
    localStorage.removeItem('token');
    return <Navigate to="/login" replace />;
  }
};

export default PrivateRoute;