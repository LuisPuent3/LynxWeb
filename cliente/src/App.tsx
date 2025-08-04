import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import RequestPasswordReset from './components/auth/RequestPasswordReset';
import ResetPassword from './components/auth/ResetPassword';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AdminDashboard from './pages/AdminDashboard';
import AdminProductsPage from './pages/AdminProductsPage';
import AdminHome from './pages/AdminHome';
import AdminCategoriesPage from './pages/AdminCategoriesPage';
import Home from './pages/Home';
import CartPage from './pages/CartPage';
import OrderConfirmationPage from './pages/OrderConfirmationPage';
import OrderSummaryPage from './pages/OrderSummaryPage';
import OrderHistoryPage from './pages/OrderHistoryPage';
import { useAuth } from './contexts/AuthContext';
import './styles/admin.css';

const App = () => {
  const { isAuthenticated, isLoading, user } = useAuth();

  // Comprobar si el usuario actual es administrador
  const isAdmin = user?.rol === 'Administrador';

  if (isLoading) {
    return (
      <div className="min-vh-100 d-flex align-items-center justify-content-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
      </div>
    );
  }

  return (
    <>
      <Routes>
        <Route path="/login" element={
          isAuthenticated ? <Navigate to="/" replace /> : <Login />
        } />
        <Route path="/register" element={
          isAuthenticated ? <Navigate to="/" replace /> : <Register />
        } />
        <Route path="/request-reset" element={
          isAuthenticated ? <Navigate to="/" replace /> : <RequestPasswordReset />
        } />
        <Route path="/reset-password/:token" element={
          isAuthenticated ? <Navigate to="/" replace /> : <ResetPassword />
        } />
        <Route path="/" element={<Home />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/order/summary" element={<OrderSummaryPage />} />
        <Route path="/order/confirmation" element={<OrderConfirmationPage />} />
        <Route path="/pedidos" element={
          <ProtectedRoute allowedRoles={[]}>
            <OrderHistoryPage />
          </ProtectedRoute>
        } />

        {/* Rutas de administrador */}
        <Route path="/admin/dashboard" element={
          <ProtectedRoute allowedRoles={['Administrador']}>
            <AdminDashboard />
          </ProtectedRoute>
        } />
        <Route path="/admin/products" element={
          <ProtectedRoute allowedRoles={['Administrador']}>
            <AdminProductsPage />
          </ProtectedRoute>
        } />
        <Route path="/admin/home" element={
          <ProtectedRoute allowedRoles={['Administrador']}>
            <AdminHome />
          </ProtectedRoute>
        } />
        <Route path="/admin/categories" element={
          <ProtectedRoute allowedRoles={['Administrador']}>
            <AdminCategoriesPage />
          </ProtectedRoute>
        } />
        
        {/* Redireccion a panel de administrador o a home según el rol */}
        <Route path="/admin" element={
          isAuthenticated ? (
            isAdmin ? 
              <Navigate to="/admin/home" replace /> : 
              <Navigate to="/" replace />
          ) : (
            <Navigate to="/login" replace state={{ from: '/admin' }} />
          )
        } />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
};

export default App;

