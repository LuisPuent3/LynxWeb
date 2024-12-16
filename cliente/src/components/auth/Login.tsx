import React, { useState } from "react";
import api from "../../utils/api";
import { useNavigate } from "react-router-dom";

interface LoginProps {
  onLoginSuccess?: () => void;
  isModal?: boolean;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess, isModal = false }) => {
  const [correo, setCorreo] = useState("");
  const [contraseña, setContraseña] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await api.post("/auth/login", { correo, contraseña });
      localStorage.setItem("token", response.data.token);
      
      if (isModal && onLoginSuccess) {
        onLoginSuccess();
      } else {
        navigate("/");
      }
    } catch (err) {
      setError("Credenciales incorrectas");
    }
  };

  const formContent = (
    <>
      {error && (
        <div className="alert alert-danger d-flex align-items-center">
          <i className="bi bi-exclamation-circle-fill me-2"></i>
          {error}
        </div>
      )}
      <form onSubmit={handleLogin}>
        <div className="mb-3">
          <label className="form-label">Correo electrónico</label>
          <div className="input-group">
            <span className="input-group-text">
              <i className="bi bi-envelope"></i>
            </span>
            <input
              type="email"
              className="form-control"
              value={correo}
              onChange={(e) => setCorreo(e.target.value)}
              required
            />
          </div>
        </div>
        <div className="mb-3">
          <label className="form-label">Contraseña</label>
          <div className="input-group">
            <span className="input-group-text">
              <i className="bi bi-lock"></i>
            </span>
            <input
              type="password"
              className="form-control"
              value={contraseña}
              onChange={(e) => setContraseña(e.target.value)}
              required
            />
          </div>
        </div>
        <div className="d-grid">
          <button type="submit" className="btn btn-primary">
            <i className="bi bi-box-arrow-in-right me-2"></i>
            Iniciar Sesión
          </button>
        </div>
      </form>
    </>
  );

  if (isModal) {
    return formContent;
  }

  return (
    <div className="min-vh-100 d-flex align-items-center bg-light">
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-6 col-lg-5">
            <div className="card shadow-sm">
              <div className="card-body p-4">
                <div className="text-center mb-4">
                  <i className="bi bi-shop display-1 text-primary"></i>
                  <h2 className="mt-3 mb-1">Bienvenido a LynxShop</h2>
                  <p className="text-muted">Inicia sesión para continuar</p>
                </div>
                {formContent}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;