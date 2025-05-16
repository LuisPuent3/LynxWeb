import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import OrderConfirmation from '../components/checkout/OrderConfirmation';
import { Producto } from '../types/types';

interface OrderConfirmationPageProps {}

interface LocationState {
  cartItems: Array<Producto & { cantidad: number }>;
  orderId: number | null;
  total: number;
  discount: number;
  isProcessing?: boolean;
}

const OrderConfirmationPage: React.FC<OrderConfirmationPageProps> = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(true);
  const [isCompleted, setIsCompleted] = useState(false);
  
  // Obtener datos del estado de la locación
  const state = location.state as LocationState;
  const { cartItems, orderId, total, discount } = state || { 
    cartItems: [], 
    orderId: null, 
    total: 0, 
    discount: 0 
  };
  
  useEffect(() => {
    // Si no hay productos en el carrito, redireccionar a la página principal
    if (!state || cartItems.length === 0) {
      navigate('/');
      return;
    }
    
    // Simular tiempo de procesamiento
    const timer = setTimeout(() => {
      setIsProcessing(false);
      setIsCompleted(true);
    }, 2000); // 2 segundos para simular procesamiento
    
    return () => clearTimeout(timer);
  }, [state, cartItems, navigate]);
  
  const handleViewOrders = () => {
    navigate('/pedidos');
  };
  
  const handleContinueShopping = () => {
    navigate('/');
  };
  
  return (
    <OrderConfirmation
      isProcessing={isProcessing}
      isCompleted={isCompleted}
      orderId={orderId}
      cartItems={cartItems}
      total={total}
      discount={discount}
      onViewOrders={handleViewOrders}
      onContinueShopping={handleContinueShopping}
    />
  );
};

export default OrderConfirmationPage;
