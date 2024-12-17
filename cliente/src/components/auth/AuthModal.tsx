import React, { useState, useEffect } from 'react';
import Login from './Login';

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

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      document.body.classList.add('modal-open');
    }
    return () => {
      document.body.style.overflow = 'unset';
      document.body.classList.remove('modal-open');
    };
  }, [isOpen]);

  return (
    <>
      <div 
        className="modal-backdrop fade show" 
        style={{display: 'block'}}
      />
      <div 
        className="modal fade show" 
        style={{display: 'block'}}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
      >
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">
                {showLoginForm ? 'Iniciar Sesión' : 'Continuar con el pedido'}
              </h5>
              <button
                type="button"
                className="btn-close"
                onClick={onClose}
                aria-label="Close"
              />
            </div>
            <div className="modal-body">
              {showLoginForm ? (
                <Login
                  onLoginSuccess={() => {
                    onLogin();
                    onClose();
                  }}
                  isModal={true}
                />
              ) : (
                <div className="d-grid gap-3">
                  <button
                    className="btn btn-primary btn-lg"
                    onClick={() => setShowLoginForm(true)}
                  >
                    <i className="bi bi-person-fill me-2"></i>
                    Iniciar Sesión
                  </button>
                  <button
                    className="btn btn-success btn-lg"
                    onClick={() => {
                      onGuestCheckout();
                      onClose();
                    }}
                  >
                    <i className="bi bi-person-walking me-2"></i>
                    Continuar como Invitado
                  </button>
                  <button
                    className="btn btn-outline-primary btn-lg"
                    onClick={() => window.location.href = '/register'}
                  >
                    <i className="bi bi-person-plus-fill me-2"></i>
                    Registrarse
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default AuthModal;