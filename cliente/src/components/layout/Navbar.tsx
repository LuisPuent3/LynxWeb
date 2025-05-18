import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Navbar: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  
  // Verificar si es un usuario invitado
  const isGuestUser = () => {
    return localStorage.getItem('guestMode') === 'true';
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
      <div className="container">
        <Link className="navbar-brand d-flex align-items-center" to="/">
          <i className="bi bi-shop me-2"></i>
          LynxShop
        </Link>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarContent"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarContent">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item">
              <Link className="nav-link" to="/">Inicio</Link>
            </li>
            {isAuthenticated && (
              <li className="nav-item">
                <Link className="nav-link" to="/pedidos">
                  <i className="bi bi-receipt me-1"></i>
                  Mis Pedidos
                </Link>
              </li>
            )}
            {isAuthenticated && user?.rol === 'Administrador' && (
              <li className="nav-item">
                <Link className="nav-link" to="/admin/dashboard">Panel Admin</Link>
              </li>
            )}
          </ul>

          <div className="ms-auto d-flex align-items-center">
            {isAuthenticated ? (
              <>
                <Link to="/cart" className="btn btn-outline-light me-3 position-relative">
                  <i className="bi bi-cart3"></i>
                </Link>
                <div className="btn-group">
                  <button 
                    type="button" 
                    className="btn btn-outline-light dropdown-toggle" 
                    data-bs-toggle="dropdown" 
                    aria-expanded="false"
                  >
                    <i className="bi bi-person-circle me-1"></i>
                    {isGuestUser() ? 'Invitado' : (user?.nombre || 'Usuario')}
                    {isGuestUser() && <span className="badge bg-warning text-dark ms-1" style={{ fontSize: '0.6rem' }}>Invitado</span>}
                  </button>
                  <ul className="dropdown-menu dropdown-menu-end">
                    <li>
                      <Link className="dropdown-item" to="/pedidos">
                        <i className="bi bi-receipt me-2"></i>
                        Mis pedidos
                      </Link>
                    </li>
                    {isGuestUser() && (
                      <li>
                        <Link className="dropdown-item" to="/register">
                          <i className="bi bi-person-plus me-2"></i>
                          Crear cuenta permanente
                        </Link>
                      </li>
                    )}
                    <li><hr className="dropdown-divider"/></li>
                    <li>
                      <button 
                        className="dropdown-item text-danger" 
                        onClick={handleLogout}
                      >
                        <i className="bi bi-box-arrow-right me-2"></i>
                        Cerrar sesión
                      </button>
                    </li>
                  </ul>
                </div>
              </>
            ) : (
              <>
                <Link className="btn btn-outline-light me-2" to="/login">
                  <i className="bi bi-person me-1"></i>
                  Iniciar Sesión
                </Link>
                <Link className="btn btn-light" to="/register">
                  <i className="bi bi-person-plus me-1"></i>
                  Registrarse
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;