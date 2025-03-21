// Register.tsx
import React, { useState, useEffect } from "react";
import api from "../../utils/api";
import { useNavigate } from "react-router-dom";
import { signUpWithEmail, signInWithGoogle, getGoogleRedirectResult } from "../../utils/firebase";

const Register = () => {
  const [nombre, setNombre] = useState<string>("");
  const [correo, setCorreo] = useState<string>("");
  const [telefono, setTelefono] = useState<string>("");
  const [contraseña, setContraseña] = useState<string>("");
  const [mensaje, setMensaje] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMensaje("");
    setIsLoading(true);

    try {
      // Primero intentar registro con Firebase
      const firebaseResult = await signUpWithEmail(correo, contraseña);
      
      if (firebaseResult.user) {
        // Si el registro en Firebase es exitoso, obtén el token
        const idToken = await firebaseResult.user.getIdToken();
        
        try {
          // Enviar los datos del usuario al backend junto con el token de Firebase
          const response = await api.post("/auth/firebase-register", { 
            nombre, 
            correo, 
            telefono,
            idToken
          });

          // Guardar el token JWT del backend
          if (response.data.token) {
            localStorage.setItem("token", response.data.token);
          }

          setMensaje("Registro exitoso. Redirigiendo...");
          
          // Esperar un momento antes de redirigir
          setTimeout(() => {
            navigate("/");
          }, 2000);
          
        } catch (backendErr) {
          // Si el backend falla, intentar el método tradicional
          fallbackRegister();
        }
      } else if (firebaseResult.error) {
        // Si Firebase reporta un error, intentar el método tradicional
        fallbackRegister();
      }
    } catch (err) {
      fallbackRegister();
    }
  };

  const fallbackRegister = async () => {
    try {
      // Método de registro tradicional como respaldo
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
      
      setTimeout(() => {
        navigate("/");
      }, 2000);
      
    } catch (err: any) {
      setError(err.response?.data?.error || "Error al registrar. Intenta nuevamente.");
    } finally {
      setIsLoading(false);
    }
  };

  // Añadir un useEffect para manejar el resultado de la redirección
  useEffect(() => {
    const handleRedirectResult = async () => {
      setIsLoading(true);
      setError("");
      setMensaje("");
      
      try {
        const googleResult = await getGoogleRedirectResult();
        
        if (googleResult.user) {
          const idToken = await googleResult.user.getIdToken();
          const userInfo = googleResult.user;
          
          try {
            // Enviar los datos del usuario obtenidos de Google al backend
            const response = await api.post("/auth/firebase-register", { 
              nombre: userInfo.displayName || "Usuario de Google", 
              correo: userInfo.email, 
              telefono: telefono || "No disponible",
              idToken
            });

            if (response.data.token) {
              localStorage.setItem("token", response.data.token);
            }

            setMensaje("Registro con Google exitoso. Redirigiendo...");
            
            setTimeout(() => {
              navigate("/");
            }, 2000);
            
          } catch (backendErr) {
            setError("Error al procesar el registro con Google en el servidor.");
          }
        }
      } catch (err) {
        // No mostrar error si no hay resultado de redirección
      } finally {
        setIsLoading(false);
      }
    };
    
    handleRedirectResult();
  }, []);

  const handleGoogleRegister = async () => {
    setError("");
    setMensaje("");
    setIsLoading(true);
    
    try {
      await signInWithGoogle();
      // La redirección ocurrirá, no es necesario hacer nada más aquí
    } catch (err) {
      setError("Error al conectar con el servicio de autenticación");
      setIsLoading(false);
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

                  <div className="d-grid gap-2">
                    <button 
                      type="submit" 
                      className="btn btn-primary"
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <><span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Procesando...</>
                      ) : (
                        <><i className="bi bi-person-plus-fill me-2"></i> Registrarse</>
                      )}
                    </button>
                    
                    <div className="text-center my-2"><span className="text-muted">o</span></div>
                    
                    <button 
                      type="button" 
                      className="btn btn-outline-danger"
                      onClick={handleGoogleRegister}
                      disabled={isLoading}
                    >
                      <i className="bi bi-google me-2"></i> Registrarse con Google
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