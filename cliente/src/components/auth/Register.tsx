// Register.tsx
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useFormik } from "formik";
import * as Yup from "yup";
import api from "../../utils/api";

const Register = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const formik = useFormik({
    initialValues: {
      nombre: "",
      apellidoP: "",
      apellidoM: "",
      correo: "",
      telefono: "",
      contraseña: "",
      confirmarContraseña: ""
    },
    validationSchema: Yup.object({
      nombre: Yup.string()
        .required("El nombre es requerido")
        .min(2, "El nombre debe tener al menos 2 caracteres"),
      apellidoP: Yup.string()
        .required("El apellido paterno es requerido")
        .min(2, "El apellido debe tener al menos 2 caracteres"),
      apellidoM: Yup.string()
        .required("El apellido materno es requerido")
        .min(2, "El apellido debe tener al menos 2 caracteres"),
      correo: Yup.string()
        .email("Correo electrónico inválido")
        .required("El correo es requerido"),
      telefono: Yup.string()
        .matches(/^[0-9]{10}$/, "El teléfono debe tener 10 dígitos")
        .required("El teléfono es requerido"),
      contraseña: Yup.string()
        .min(8, "La contraseña debe tener al menos 8 caracteres")
        .matches(/[A-Z]/, "Debe contener al menos una mayúscula")
        .matches(/[a-z]/, "Debe contener al menos una minúscula")
        .matches(/[0-9]/, "Debe contener al menos un número")
        .required("La contraseña es requerida"),
      confirmarContraseña: Yup.string()
        .oneOf([Yup.ref("contraseña")], "Las contraseñas no coinciden")
        .required("Confirma tu contraseña")
    }),
    onSubmit: async (values) => {
      setIsLoading(true);
      setError(null);
      setSuccessMessage(null);
      
      try {
        // Usar la ruta correcta del backend
        const response = await api.post("/auth/register", {
          nombre: values.nombre,
          apellidoP: values.apellidoP,
          apellidoM: values.apellidoM,
          correo: values.correo,
          telefono: values.telefono,
          contraseña: values.contraseña
        });
        
        setSuccessMessage("¡Registro exitoso! Redirigiendo al inicio de sesión...");
        
        // Limpiar el formulario
        formik.resetForm();
        
        // Esperar 2 segundos y redirigir al login
        setTimeout(() => {
          navigate("/login", { 
            state: { 
              message: "Cuenta creada exitosamente. Por favor inicia sesión." 
            }
          });
        }, 2000);
          } catch (err: any) {
        console.error("Error de registro:", err);
        // Mostrar mensaje de error específico si está disponible, o un mensaje genérico
        setError(
          err.response?.data?.mensaje || 
          err.response?.data?.error || 
          "No se pudo completar el registro. Intenta nuevamente."
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
          <div className="col-md-10 col-lg-8">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-4 p-md-5">
                {/* Header */}
                <div className="text-center mb-4">
                  <div className="bg-primary bg-opacity-10 rounded-circle p-3 mx-auto mb-3" style={{width: 'fit-content'}}>
                    <i className="bi bi-person-plus-fill text-primary display-6"></i>
                  </div>
                  <h2 className="fw-bold text-primary mb-2">Crear cuenta</h2>
                  <p className="text-muted">Únete a LynxShop y comienza a comprar</p>
                </div>

                {/* Mensajes de error/éxito */}
                {error && (
                  <div className="alert alert-danger d-flex align-items-center mb-4 fade-in">
                    <i className="bi bi-exclamation-circle-fill me-2"></i>
                    {error}
                  </div>
                )}
                
                {successMessage && (
                  <div className="alert alert-success d-flex align-items-center mb-4 fade-in">
                    <i className="bi bi-check-circle-fill me-2"></i>
                    {successMessage}
                  </div>
                )}

                {/* Formulario */}
                <form onSubmit={formik.handleSubmit} className="needs-validation" noValidate>
                  <div className="row g-3">
                    {/* Nombre */}
                    <div className="col-md-4">
                      <div className="form-floating">
                        <input
                          type="text"
                          className={`form-control ${formik.touched.nombre && formik.errors.nombre ? 'is-invalid' : formik.touched.nombre ? 'is-valid' : ''}`}
                          id="nombre"
                          placeholder="Nombre"
                          {...formik.getFieldProps("nombre")}
                        />
                        <label htmlFor="nombre">Nombre</label>
                        {formik.touched.nombre && formik.errors.nombre && (
                          <div className="invalid-feedback">{formik.errors.nombre}</div>
                        )}
                      </div>
                    </div>

                    {/* Apellido Paterno */}
                    <div className="col-md-4">
                      <div className="form-floating">
                        <input
                          type="text"
                          className={`form-control ${formik.touched.apellidoP && formik.errors.apellidoP ? 'is-invalid' : formik.touched.apellidoP ? 'is-valid' : ''}`}
                          id="apellidoP"
                          placeholder="Apellido Paterno"
                          {...formik.getFieldProps("apellidoP")}
                        />
                        <label htmlFor="apellidoP">Apellido Paterno</label>
                        {formik.touched.apellidoP && formik.errors.apellidoP && (
                          <div className="invalid-feedback">{formik.errors.apellidoP}</div>
                        )}
                      </div>
                    </div>

                    {/* Apellido Materno */}
                    <div className="col-md-4">
                      <div className="form-floating">
                        <input
                          type="text"
                          className={`form-control ${formik.touched.apellidoM && formik.errors.apellidoM ? 'is-invalid' : formik.touched.apellidoM ? 'is-valid' : ''}`}
                          id="apellidoM"
                          placeholder="Apellido Materno"
                          {...formik.getFieldProps("apellidoM")}
                        />
                        <label htmlFor="apellidoM">Apellido Materno</label>
                        {formik.touched.apellidoM && formik.errors.apellidoM && (
                          <div className="invalid-feedback">{formik.errors.apellidoM}</div>
                        )}
                      </div>
                    </div>

                    {/* Correo */}
                    <div className="col-md-6">
                      <div className="form-floating">
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
                    </div>

                    {/* Teléfono */}
                    <div className="col-md-6">
                      <div className="form-floating">
                        <input
                          type="tel"
                          className={`form-control ${formik.touched.telefono && formik.errors.telefono ? 'is-invalid' : formik.touched.telefono ? 'is-valid' : ''}`}
                          id="telefono"
                          placeholder="1234567890"
                          {...formik.getFieldProps("telefono")}
                        />
                        <label htmlFor="telefono">Teléfono</label>
                        {formik.touched.telefono && formik.errors.telefono && (
                          <div className="invalid-feedback">{formik.errors.telefono}</div>
                        )}
                      </div>
                    </div>

                    {/* Contraseña */}
                    <div className="col-md-6">
                      <div className="form-floating">
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
                    </div>

                    {/* Confirmar Contraseña */}
                    <div className="col-md-6">
                      <div className="form-floating">
                        <input
                          type="password"
                          className={`form-control ${formik.touched.confirmarContraseña && formik.errors.confirmarContraseña ? 'is-invalid' : formik.touched.confirmarContraseña ? 'is-valid' : ''}`}
                          id="confirmarContraseña"
                          placeholder="Confirmar contraseña"
                          {...formik.getFieldProps("confirmarContraseña")}
                        />
                        <label htmlFor="confirmarContraseña">Confirmar contraseña</label>
                        {formik.touched.confirmarContraseña && formik.errors.confirmarContraseña && (
                          <div className="invalid-feedback">{formik.errors.confirmarContraseña}</div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Información de seguridad de la contraseña */}
                  <div className="mt-3 mb-4 small text-muted">
                    <p className="mb-1"><i className="bi bi-shield-lock me-1"></i> La contraseña debe tener:</p>
                    <ul className="ps-4">
                      <li>Al menos 8 caracteres</li>
                      <li>Al menos una letra mayúscula</li>
                      <li>Al menos una letra minúscula</li>
                      <li>Al menos un número</li>
                    </ul>
                  </div>

                  {/* Botón de registro */}
                  <div className="d-grid gap-2 mt-4">
                    <button 
                      type="submit" 
                      className="btn btn-primary btn-lg py-3"
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Procesando...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-person-plus-fill me-2"></i>
                          Crear cuenta
                        </>
                      )}
                    </button>
                  </div>
                </form>

                {/* Enlace a login */}
                <div className="text-center mt-4">
                  <p className="mb-0">
                    ¿Ya tienes una cuenta?{" "}
                    <Link to="/login" className="text-primary text-decoration-none fw-semibold">
                      Inicia sesión
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

export default Register;