import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AdminDashboard from './pages/AdminDashboard';
import Home from './pages/home';
import CartPage from './pages/CartPage';
import OrderConfirmationPage from './pages/OrderConfirmationPage';
import OrderSummaryPage from './pages/OrderSummaryPage';
import OrderHistoryPage from './pages/OrderHistoryPage';
import { useAuth } from './contexts/AuthContext';

const App = () => {
  const { isAuthenticated, isLoading } = useAuth();

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
        <Route path="/" element={<Home />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/order/summary" element={<OrderSummaryPage />} />
        <Route path="/order/confirmation" element={<OrderConfirmationPage />} />
        <Route path="/pedidos" element={
          <ProtectedRoute allowedRoles={[]}>
            {localStorage.getItem('guestMode') !== 'true' ? (
              <OrderHistoryPage />
            ) : (
              <Navigate to="/" replace />
            )}
          </ProtectedRoute>
        } />
        <Route path="/admin/dashboard" element={
          <ProtectedRoute allowedRoles={['Administrador']}>
            <AdminDashboard />
          </ProtectedRoute>
        } />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
};

export default App;

