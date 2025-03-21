// Login.tsx
import React, { useState, useEffect } from "react";
import api from "../../utils/api";
import { useNavigate } from "react-router-dom";
import { signInWithEmail, signInWithGoogle, getGoogleRedirectResult } from "../../utils/firebase";

interface LoginProps {
  onLoginSuccess?: () => void;
  isModal?: boolean;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess, isModal = false }) => {
  const [correo, setCorreo] = useState("");
  const [contraseña, setContraseña] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleRedirectResult = async () => {
      setIsLoading(true);
      setError("");
      
      try {
        const googleResult = await getGoogleRedirectResult();
        
        if (googleResult.user) {
          const idToken = await googleResult.user.getIdToken();
          
          try {
            const response = await api.post("/auth/firebase-login", { idToken });
            localStorage.setItem("token", response.data.token);
            localStorage.removeItem("guestMode");
            
            if (isModal && onLoginSuccess) {
              onLoginSuccess();
            } else {
              navigate("/");
            }
          } catch (backendErr) {
            setError("Error al procesar el inicio de sesión con Google");
          }
        } else if (googleResult.error) {
          setError("Error al iniciar sesión con Google");
        }
      } catch (err) {
        // No mostrar error si no hay resultado de redirección
      } finally {
        setIsLoading(false);
      }
    };
    
    handleRedirectResult();
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      // Intenta primero autenticación con Firebase
      const firebaseResult = await signInWithEmail(correo, contraseña);
      
      if (firebaseResult.user) {
        // Si la autenticación con Firebase es exitosa, obtén un token del backend
        const idToken = await firebaseResult.user.getIdToken();
        
        try {
          // Verifica el token con tu backend para obtener el token JWT de tu sistema
          const response = await api.post("/auth/firebase-login", { idToken });
          localStorage.setItem("token", response.data.token);
          localStorage.removeItem("guestMode");
          
          if (isModal && onLoginSuccess) {
            onLoginSuccess();
          } else {
            navigate("/");
          }
        } catch (backendErr) {
          // Si el servidor no puede procesar el token de Firebase, intenta login tradicional
          fallbackLogin();
        }
      } else {
        // Si Firebase falla, intenta el método tradicional
        fallbackLogin();
      }
    } catch (err) {
      // Si hay un error con Firebase, intenta el método tradicional
      fallbackLogin();
    }
  };

  const fallbackLogin = async () => {
    try {
      // Método de autenticación tradicional como respaldo
      const response = await api.post("/auth/login", { correo, contraseña });
      localStorage.setItem("token", response.data.token);
      localStorage.removeItem("guestMode");
      
      if (isModal && onLoginSuccess) {
        onLoginSuccess();
      } else {
        navigate("/");
      }
    } catch (err) {
      setError("Credenciales incorrectas");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    setError("");
    
    try {
      await signInWithGoogle();
      // La redirección ocurrirá, no es necesario hacer nada más aquí
    } catch (err) {
      setError("Error al conectar con el servicio de autenticación");
      setIsLoading(false);
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
        <div className="d-grid gap-2">
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? (
              <><span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Procesando...</>
            ) : (
              <><i className="bi bi-box-arrow-in-right me-2"></i> Iniciar Sesión</>
            )}
          </button>
          
          <div className="text-center my-2"><span className="text-muted">o</span></div>
          
          <button 
            type="button" 
            className="btn btn-outline-danger" 
            onClick={handleGoogleLogin}
            disabled={isLoading}
          >
            <i className="bi bi-google me-2"></i> Continuar con Google
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