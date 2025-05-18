import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import Dashboard from "../components/admin/Dashboard";
import "../styles/admin.css";

const AdminHome: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  
  // Protección básica para asegurar que solo los administradores accedan
  useEffect(() => {
    if (user?.rol !== "Administrador") {
      navigate("/");
    }
  }, [user, navigate]);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="admin-dashboard min-vh-100 bg-light">
      {/* Barra superior administrativa */}
      <nav className="navbar navbar-expand-lg navbar-dark sticky-top">
        <div className="container-fluid">
          <a 
            className="navbar-brand d-flex align-items-center" 
            href="/admin" 
            onClick={(e) => {
              e.preventDefault();
              navigate("/admin");
            }}
          >
            <i className="bi bi-shop me-2" style={{ fontSize: "1.4rem" }}></i>
            LynxShop <span className="ms-2 badge bg-light text-dark">Admin</span>
          </a>
          
          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#adminNavbarContent"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          
          <div className="collapse navbar-collapse" id="adminNavbarContent">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <li className="nav-item">
                <a
                  className={`nav-link ${activeTab === "dashboard" ? "active" : ""}`}
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveTab("dashboard");
                  }}
                >
                  <i className="bi bi-speedometer2 me-1"></i>
                  Dashboard
                </a>
              </li>
              <li className="nav-item">
                <a
                  className="nav-link"
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    navigate("/admin/products");
                  }}
                >
                  <i className="bi bi-box-seam me-1"></i>
                  Productos
                </a>
              </li>
              <li className="nav-item">
                <a
                  className="nav-link"
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    navigate("/admin/dashboard");
                    // Establecer la pestaña de pedidos activa
                  }}
                >
                  <i className="bi bi-bag me-1"></i>
                  Pedidos
                </a>
              </li>
              <li className="nav-item">
                <a
                  className="nav-link"
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    navigate("/admin/categories");
                  }}
                >
                  <i className="bi bi-tags me-1"></i>
                  Categorías
                </a>
              </li>
            </ul>
            
            <div className="d-flex align-items-center">
              <button 
                className="btn btn-outline-light me-3"
                onClick={() => navigate("/")}
              >
                <i className="bi bi-shop me-1"></i>
                Ver Tienda
              </button>
              
              <div className="dropdown">
                <button
                  className="btn btn-light dropdown-toggle d-flex align-items-center"
                  type="button"
                  id="userDropdown"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  <i className="bi bi-person-circle me-2"></i>
                  <span>{user?.nombre?.split(" ")[0] || "Admin"}</span>
                </button>
                <ul className="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                  <li>
                    <a className="dropdown-item" href="#">
                      <i className="bi bi-person me-2"></i>
                      Perfil
                    </a>
                  </li>
                  <li>
                    <a className="dropdown-item" href="#">
                      <i className="bi bi-gear me-2"></i>
                      Configuración
                    </a>
                  </li>
                  <li>
                    <hr className="dropdown-divider" />
                  </li>
                  <li>
                    <a 
                      className="dropdown-item" 
                      href="#"
                      onClick={(e) => {
                        e.preventDefault();
                        handleLogout();
                      }}
                    >
                      <i className="bi bi-box-arrow-right me-2"></i>
                      Cerrar sesión
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Contenido principal */}
      <div className="container-fluid py-4">
        {renderContent()}
      </div>
    </div>
  );
};

export default AdminHome; 