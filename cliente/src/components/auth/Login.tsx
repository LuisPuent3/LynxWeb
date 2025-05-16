// Login.tsx
import React, { useState, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { useFormik } from "formik";
import * as Yup from "yup";
import api from "../../utils/api";
import { useAuth } from "../../contexts/AuthContext";

interface LocationState {
  from?: string;
  message?: string;
  returnToCart?: boolean;
}

interface LoginProps {
  onLoginSuccess?: () => void;
  isModal?: boolean;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess, isModal = false }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const locationState = location.state as LocationState || {};
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(
    locationState.message || null
  );
  
  // Verificar si hay carrito guardado
  const hasCart = localStorage.getItem('tempCarrito') && 
                 JSON.parse(localStorage.getItem('tempCarrito') || '[]').length > 0;

  // Limpiar el mensaje de éxito después de 5 segundos
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const formik = useFormik({
    initialValues: {
      correo: "",
      contraseña: ""
    },
    validationSchema: Yup.object({
      correo: Yup.string()
        .email("Correo electrónico inválido")
        .required("El correo es requerido"),
      contraseña: Yup.string()
        .required("La contraseña es requerida")
    }),
    onSubmit: async (values) => {
      setIsLoading(true);
      setError(null);
      try {
        // Usando la ruta correcta de la API
        const response = await api.post("/auth/login", {
          correo: values.correo,
          contraseña: values.contraseña
        });

        const { token, usuario } = response.data;
        
        // Guardar el token y actualizar el contexto de autenticación
        await login(token, usuario);

        // For modal use, call onLoginSuccess and return
        if (isModal && onLoginSuccess) {
          setSuccessMessage("Inicio de sesión exitoso");
          setTimeout(() => {
            onLoginSuccess();
          }, 500);
          return;
        }

        // Decidir dónde redirigir al usuario basado en diferentes factores
        if (usuario.rol === "Administrador") {
          // Los administradores siempre van al dashboard
          navigate("/admin/dashboard");
        } else if (locationState.returnToCart || hasCart) {
          // Si venimos del proceso de compra o hay carrito pendiente
          setSuccessMessage("Inicio de sesión exitoso. Continuando con tu compra...");
          
          // Always redirect to cart page for review before checkout
          setTimeout(() => {
            navigate("/cart");
          }, 1000);
        } else if (locationState.from) {
          // Si hay una URL de redirección específica
          navigate(locationState.from);
        } else {
          // Redirección por defecto para clientes
          navigate("/");
        }
      } catch (err: any) {
        console.error("Error de login:", err);
        setError(
          err.response?.data?.error || 
          "Credenciales incorrectas. Por favor, verifica tu correo y contraseña."
        );
      } finally {
        setIsLoading(false);
      }
    }
  });

  return (
    <div className="min-vh-100 d-flex align-items-center bg-light py-5">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-6 col-lg-5">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-4 p-md-5">
                {/* Header */}
                <div className="text-center mb-4">
                  <div className="bg-primary bg-opacity-10 rounded-circle p-3 mx-auto mb-3" style={{width: 'fit-content'}}>
                    <i className="bi bi-box-arrow-in-right text-primary display-6"></i>
                  </div>
                  <h2 className="fw-bold text-primary mb-2">Iniciar sesión</h2>
                  <p className="text-muted">
                    {hasCart ? 'Inicia sesión para completar tu compra' : 'Bienvenido de nuevo a LynxShop'}
                  </p>
                </div>

                {/* Mensajes de éxito/error */}
                {successMessage && (
                  <div className="alert alert-success d-flex align-items-center mb-4 fade-in">
                    <i className="bi bi-check-circle-fill me-2"></i>
                    {successMessage}
                  </div>
                )}

                {error && (
                  <div className="alert alert-danger d-flex align-items-center mb-4 fade-in">
                    <i className="bi bi-exclamation-circle-fill me-2"></i>
                    {error}
                  </div>
                )}

                {/* Formulario */}
                <form onSubmit={formik.handleSubmit} className="needs-validation" noValidate>
                  {/* Correo */}
                  <div className="form-floating mb-3">
                    <input
                      type="email"
                      className={`form-control ${formik.touched.correo && formik.errors.correo ? 'is-invalid' : formik.touched.correo ? 'is-valid' : ''}`}
                      id="correo"
                      placeholder="correo@ejemplo.com"
                      {...formik.getFieldProps("correo")}
                    />
                    <label htmlFor="correo">Correo electrónico</label>
                    {formik.touched.correo && formik.errors.correo && (
                      <div className="invalid-feedback">{formik.errors.correo}</div>
                    )}
                  </div>

                  {/* Contraseña */}
                  <div className="form-floating mb-4">
                    <input
                      type="password"
                      className={`form-control ${formik.touched.contraseña && formik.errors.contraseña ? 'is-invalid' : formik.touched.contraseña ? 'is-valid' : ''}`}
                      id="contraseña"
                      placeholder="Contraseña"
                      {...formik.getFieldProps("contraseña")}
                    />
                    <label htmlFor="contraseña">Contraseña</label>
                    {formik.touched.contraseña && formik.errors.contraseña && (
                      <div className="invalid-feedback">{formik.errors.contraseña}</div>
                    )}
                  </div>

                  {/* Botón de inicio de sesión */}
                  <div className="d-grid gap-2">
                    <button 
                      type="submit" 
                      className="btn btn-primary btn-lg py-3"
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Iniciando sesión...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-box-arrow-in-right me-2"></i>
                          Iniciar sesión
                        </>
                      )}
                    </button>
                  </div>
                </form>

                {/* Enlaces adicionales */}
                <div className="text-center mt-4">
                  <p className="mb-0">
                    ¿No tienes una cuenta?{" "}
                    <Link to="/register" className="text-primary text-decoration-none fw-semibold">
                      Regístrate
                    </Link>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;