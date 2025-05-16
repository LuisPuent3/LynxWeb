import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Navbar: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

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
            {isAuthenticated && user?.rol === 'Administrador' && (
              <li className="nav-item">
                <Link className="nav-link" to="/admin/dashboard">Panel Admin</Link>
              </li>
            )}
          </ul>

          <div className="ms-auto d-flex align-items-center">
            {isAuthenticated ? (
              <>
                <span className="text-light me-3 d-none d-md-inline">
                  Hola, {user?.nombre || 'Usuario'}
                </span>
                <button 
                  className="btn btn-outline-light" 
                  onClick={handleLogout}
                >
                  <i className="bi bi-box-arrow-right me-1"></i>
                  Cerrar sesión
                </button>
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