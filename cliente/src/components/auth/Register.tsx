// Register.tsx
import React, { useState } from "react";
import api from "../../utils/api";
import { useNavigate } from "react-router-dom";

const Register = () => {
  const [nombre, setNombre] = useState<string>("");
  const [correo, setCorreo] = useState<string>("");
  const [telefono, setTelefono] = useState<string>("");
  const [contraseña, setContraseña] = useState<string>("");
  const [mensaje, setMensaje] = useState<string>("");
  const [error, setError] = useState<string>("");
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMensaje("");

    try {
      const response = await api.post("/auth/register", { 
        nombre, 
        correo, 
        telefono, 
        contraseña 
      });

      // Guardar el token si el backend lo proporciona
      if (response.data.token) {
        localStorage.setItem("token", response.data.token);
      }

      setMensaje("Registro exitoso. Redirigiendo...");
      
      // Esperar un momento antes de redirigir para que el usuario vea el mensaje
      setTimeout(() => {
        navigate("/");  // El carrito temporal se mantendrá en localStorage
      }, 2000);
      
    } catch (err: any) {
      setError(err.response?.data?.error || "Error al registrar. Intenta nuevamente.");
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center bg-light">
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-6 col-lg-5">
            <div className="card shadow-sm">
              <div className="card-body p-4">
                <div className="text-center mb-4">
                  <i className="bi bi-person-plus display-1 text-primary"></i>
                  <h2 className="mt-3 mb-1">Crear cuenta</h2>
                  <p className="text-muted">Regístrate para comenzar</p>
                </div>

                {mensaje && (
                  <div className="alert alert-success">
                    <i className="bi bi-check-circle me-2"></i>
                    {mensaje}
                  </div>
                )}

                {error && (
                  <div className="alert alert-danger">
                    <i className="bi bi-exclamation-circle me-2"></i>
                    {error}
                  </div>
                )}

                <form onSubmit={handleRegister}>
                  <div className="mb-3">
                    <label className="form-label">Nombre</label>
                    <div className="input-group">
                      <span className="input-group-text">
                        <i className="bi bi-person"></i>
                      </span>
                      <input
                        type="text"
                        className="form-control"
                        value={nombre}
                        onChange={(e) => setNombre(e.target.value)}
                        required
                      />
                    </div>
                  </div>

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
                    <label className="form-label">Teléfono</label>
                    <div className="input-group">
                      <span className="input-group-text">
                        <i className="bi bi-phone"></i>
                      </span>
                      <input
                        type="tel"
                        className="form-control"
                        value={telefono}
                        onChange={(e) => setTelefono(e.target.value)}
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
                      <i className="bi bi-person-plus-fill me-2"></i>
                      Registrarse
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;