import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Login from './Login';
import api from '../../utils/api';
import { useAuth } from '../../contexts/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLogin: () => void;
  onGuestCheckout: () => void;
  vaciarCarrito: () => void;
}

const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onLogin,
  onGuestCheckout,
  vaciarCarrito
}) => {
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  // Manejador especial para el modo invitado
  const handleGuestLogin = async () => {
    setIsLoading(true);
    try {
      const guestData = {
        nombre: `Guest_${Date.now()}`,
        correo: `guest_${Date.now()}@lynxshop.com`,
        telefono: `000${Date.now().toString().slice(-7)}`,
        contraseña: `guest${Date.now()}`
      };

      const response = await api.post('/auth/register', guestData);
      
      if (response.data && response.data.token) {
        // Guardar datos en localStorage
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('guestMode', 'true');
        
        // Guardar información del usuario
        if (response.data.usuario) {
          localStorage.setItem('usuario', JSON.stringify(response.data.usuario));
          
          // Iniciar sesión con los datos de invitado
          await login(response.data.token, response.data.usuario);
        }
        
        // Cerrar el modal
        onClose();
        
        // Obtener el carrito actual de localStorage
        const savedCarrito = localStorage.getItem('tempCarrito');
        let cartItems = [];
        let total = 0;
        
        if (savedCarrito) {
          cartItems = JSON.parse(savedCarrito);
          // Calcular el total del carrito
          total = cartItems.reduce((sum, item) => sum + (Number(item.precio) * item.cantidad), 0);
        }
        
        // Utilizar setTimeout para dar tiempo al estado de React a actualizarse
        setTimeout(() => {
          // Navigate guests to the order summary page with cart data
          const cartItems = JSON.parse(localStorage.getItem('cart') || '[]');
          navigate('/checkout', {
            state: {
              items: cartItems,
              total: cartItems.reduce((sum, item) => sum + (item.precio * item.cantidad), 0),
              paymentMethod: 'efectivo'
            }
          });
        }, 50); // Un pequeño retraso es suficiente
      } else {
        throw new Error('No se pudo crear usuario invitado');
      }
    } catch (error) {
      console.error('Error al procesar como invitado:', error);
      alert('Error al procesar como invitado. Por favor intente nuevamente.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <>
      <div className="modal-header border-0 bg-primary text-white py-4">
        <h5 className="modal-title fs-4 d-flex align-items-center">
          <i className="bi bi-cart-check-fill me-2"></i>
          {showLoginForm ? 'Iniciar Sesión' : 'Finalizar tu Compra'}
        </h5>
        <button
          type="button"
          className="btn-close btn-close-white"
          onClick={onClose}
        />
      </div>

      <div className="modal-body p-4 bg-light">
        {showLoginForm ? (
          <Login
            onLoginSuccess={() => {
              onLogin();
              onClose();
            }}
            isModal={true}
          />
        ) : (
          <>
            <div className="text-center mb-4">
              <h4 className="text-primary fw-bold mb-3">Accede a tu cuenta</h4>
              <p className="text-muted">Para una mejor experiencia de compra</p>
            </div>

            {/* Opción principal - Login */}
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body text-center p-5">
                <div className="bg-primary bg-opacity-10 rounded-circle p-3 mx-auto mb-3" style={{width: 'fit-content'}}>
                  <i className="bi bi-person-fill text-primary fs-2"></i>
                </div>
                <h5 className="card-title mb-3">Iniciar Sesión</h5>
                <p className="card-text text-muted mb-4">Accede a tu cuenta para gestionar tus pedidos</p>
                <button 
                  className="btn btn-primary btn-lg px-5"
                  onClick={() => setShowLoginForm(true)}
                >
                  Ingresar
                </button>
              </div>
            </div>

            {/* Opciones secundarias */}
            <div className="row g-3">
              <div className="col-md-6">
                <div className="card h-100 border-0 hover-shadow transition" style={{backgroundColor: '#e8f4f8'}}>
                  <div className="card-body text-center p-3">
                    <div className="bg-info bg-opacity-10 rounded-circle p-2 mx-auto mb-2" style={{width: 'fit-content'}}>
                      <i className="bi bi-person-plus-fill text-info"></i>
                    </div>
                    <h6 className="card-title mb-2">¿No tienes cuenta?</h6>
                    <button 
                      className="btn btn-outline-info btn-sm"
                      onClick={() => window.location.href = '/register'}
                    >
                      Registrarse
                    </button>
                  </div>
                </div>
              </div>

              <div className="col-md-6">
                <div className="card h-100 border-0 hover-shadow transition" style={{backgroundColor: '#fff3cd'}}>
                  <div className="card-body text-center p-3">
                    <div className="bg-warning bg-opacity-10 rounded-circle p-2 mx-auto mb-2" style={{width: 'fit-content'}}>
                      <i className="bi bi-person-badge text-warning"></i>
                    </div>
                    <h6 className="card-title mb-2">Compra rápida</h6>
                    <button 
                      className="btn btn-warning btn-sm text-dark"
                      onClick={handleGuestLogin}
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                          Procesando...
                        </>
                      ) : (
                        'Continuar como invitado'
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
};

export default AuthModal;