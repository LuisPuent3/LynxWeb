// ResetPassword.tsx
import React, { useState, useEffect } from "react";
import { useFormik } from "formik";
import * as Yup from "yup";
import { Link, useParams, useNavigate } from "react-router-dom";
import { restablecerContraseña } from "../../services/passwordResetService";

const ResetPassword = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tokenValid, setTokenValid] = useState(true);

  useEffect(() => {
    // Verificar que el token esté presente
    if (!token) {
      setTokenValid(false);
      setError("El enlace de recuperación no es válido o ha expirado.");
    }
  }, [token]);

  const formik = useFormik({
    initialValues: {
      nuevaContraseña: "",
      confirmarContraseña: "",
    },
    validationSchema: Yup.object({
      nuevaContraseña: Yup.string()
        .min(8, "La contraseña debe tener al menos 8 caracteres")
        .matches(/[A-Z]/, "Debe contener al menos una mayúscula")
        .matches(/[a-z]/, "Debe contener al menos una minúscula")
        .matches(/[0-9]/, "Debe contener al menos un número")
        .required("La contraseña es requerida"),
      confirmarContraseña: Yup.string()
        .oneOf([Yup.ref("nuevaContraseña")], "Las contraseñas no coinciden")
        .required("Confirma tu contraseña"),
    }),    onSubmit: async (values) => {
      setIsLoading(true);
      setError(null);
      
      try {
        const result = await restablecerContraseña(token!, values.nuevaContraseña);
        
        if (!result.success) {
          throw result.error;
        }
        
        setResetSuccess(true);
        formik.resetForm();
        
        // Redireccionar al login después de unos segundos
        setTimeout(() => {
          navigate("/login", { 
            state: { 
              message: "Contraseña actualizada exitosamente. Puedes iniciar sesión con tu nueva contraseña." 
            }
          });
        }, 3000);
      } catch (err: any) {
        console.error("Error al restablecer contraseña:", err);
        setError(
          err.response?.data?.mensaje || 
          err.response?.data?.error || 
          "No se pudo restablecer la contraseña. El enlace podría ser inválido o haber expirado."
        );
      } finally {
        setIsLoading(false);
      }
    }
  });

  if (!tokenValid) {
    return (
      <div className="min-vh-100 d-flex align-items-center bg-light py-5">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-md-8 col-lg-6">
              <div className="card border-0 shadow-lg">
                <div className="card-body p-4 p-md-5 text-center">
                  <div className="text-danger mb-4">
                    <i className="bi bi-exclamation-triangle-fill" style={{ fontSize: "3rem" }}></i>
                  </div>
                  <h3 className="fw-bold mb-3">Enlace inválido</h3>
                  <p className="mb-4">El enlace de recuperación no es válido o ha expirado.</p>
                  <Link to="/request-reset" className="btn btn-primary">
                    Solicitar nuevo enlace
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-vh-100 d-flex align-items-center bg-light py-5">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-8 col-lg-6">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-4 p-md-5">
                <div className="text-center mb-4">
                  <h2 className="fw-bold">Crear nueva contraseña</h2>
                  <p className="text-muted">
                    Crea una nueva contraseña segura
                  </p>
                </div>

                {resetSuccess ? (
                  <div className="alert alert-success text-center" role="alert">
                    <i className="bi bi-check-circle me-2"></i>
                    <p className="mb-0">
                      Tu contraseña ha sido actualizada exitosamente. 
                      Serás redirigido a la página de inicio de sesión.
                    </p>
                  </div>
                ) : (
                  <form onSubmit={formik.handleSubmit}>
                    {error && (
                      <div className="alert alert-danger" role="alert">
                        <i className="bi bi-exclamation-triangle me-2"></i>
                        {error}
                      </div>
                    )}

                    <div className="mb-4">
                      <label htmlFor="nuevaContraseña" className="form-label">
                        Nueva Contraseña
                      </label>
                      <input
                        id="nuevaContraseña"
                        name="nuevaContraseña"
                        type="password"
                        className={`form-control form-control-lg ${
                          formik.touched.nuevaContraseña && formik.errors.nuevaContraseña
                            ? "is-invalid"
                            : ""
                        }`}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        value={formik.values.nuevaContraseña}
                      />
                      {formik.touched.nuevaContraseña && formik.errors.nuevaContraseña && (
                        <div className="invalid-feedback">
                          {formik.errors.nuevaContraseña}
                        </div>
                      )}
                    </div>

                    <div className="mb-4">
                      <label htmlFor="confirmarContraseña" className="form-label">
                        Confirmar Contraseña
                      </label>
                      <input
                        id="confirmarContraseña"
                        name="confirmarContraseña"
                        type="password"
                        className={`form-control form-control-lg ${
                          formik.touched.confirmarContraseña && formik.errors.confirmarContraseña
                            ? "is-invalid"
                            : ""
                        }`}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        value={formik.values.confirmarContraseña}
                      />
                      {formik.touched.confirmarContraseña && formik.errors.confirmarContraseña && (
                        <div className="invalid-feedback">
                          {formik.errors.confirmarContraseña}
                        </div>
                      )}
                    </div>

                    <button
                      type="submit"
                      className="btn btn-primary btn-lg w-100"
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <span
                            className="spinner-border spinner-border-sm me-2"
                            role="status"
                            aria-hidden="true"
                          ></span>
                          Actualizando...
                        </>
                      ) : (
                        "Actualizar Contraseña"
                      )}
                    </button>
                  </form>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;
