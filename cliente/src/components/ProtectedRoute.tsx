import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
    children: React.ReactNode;
    allowedRoles?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
    children, 
    allowedRoles = [] 
}) => {
    const { isAuthenticated, user, isLoading } = useAuth();
    const location = useLocation();

    if (isLoading) {
        return <div>Cargando...</div>;
    }

    if (!isAuthenticated) {
        // Redirigir al login si no está autenticado
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    if (allowedRoles.length > 0 && user && !allowedRoles.includes(user.rol)) {
        // Redirigir a la página principal si no tiene el rol requerido
        return <Navigate to="/" replace />;
    }

    return <>{children}</>;
}; 