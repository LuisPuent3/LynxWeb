// RequestPasswordReset.tsx
import React, { useState } from "react";
import { useFormik } from "formik";
import * as Yup from "yup";
import { Link } from "react-router-dom";
import { diagnosticarSistema, solicitarRecuperacion } from "../../services/passwordResetService";

const RequestPasswordReset = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [requestSent, setRequestSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const formik = useFormik({
    initialValues: {
      correo: "",
    },
    validationSchema: Yup.object({
      correo: Yup.string()
        .email("Correo electrónico inválido")
        .required("El correo es requerido"),
    }),    onSubmit: async (values) => {
      setIsLoading(true);
      setError(null);
      try {
        console.log("Enviando solicitud de recuperación para:", values.correo);
        
        // Verificar primero si la ruta de diagnóstico está disponible
        try {
          const diagResult = await diagnosticarSistema();
          console.log("Diagnóstico del sistema:", diagResult.data);
          
          if (diagResult.data.database.status !== "Conectada") {
            throw new Error(`Problema de conexión a la base de datos: ${diagResult.data.database.status}`);
          }
        } catch (diagError) {
          console.warn("No se pudo realizar el diagnóstico previo:", diagError);
          // Continuamos con la solicitud aunque el diagnóstico falle
        }
        
        // Realizar la solicitud de recuperación
        const result = await solicitarRecuperacion(values.correo);
        
        if (!result.success) {
          throw result.error;
        }
        
        console.log("Respuesta recibida:", result.data);
        
        // Si llegamos aquí, la solicitud fue exitosa
        setRequestSent(true);
        formik.resetForm();      } catch (err: any) {
        console.error("Error al solicitar recuperación:", err);
        
        // Mostrar detalles del error en consola
        if (err.response) {
          console.error("Detalles del error:", err.response.data);
          console.error("Código de estado:", err.response.status);
          
          // Para errores 500, mostrar los detalles técnicos en la consola
          if (err.response.status === 500 && err.response.data.detail) {
            console.error("Detalles técnicos:", err.response.data.detail);
          }
        }
        
        // Mostrar mensaje apropiado al usuario
        let errorMessage = "No se pudo procesar la solicitud. Intenta nuevamente.";
        
        if (err.response?.data?.mensaje) {
          errorMessage = err.response.data.mensaje;
        } else if (err.response?.data?.error) {
          errorMessage = err.response.data.error;
        } else if (err.message && typeof err.message === 'string' && err.message.includes("Network Error")) {
          errorMessage = "Error de conexión con el servidor. Por favor, verifica tu conexión a internet.";
        }
        
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    }
  });

  return (
    <div className="min-vh-100 d-flex align-items-center bg-light py-5">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-8 col-lg-6">
            <div className="card border-0 shadow-lg">
              <div className="card-body p-4 p-md-5">
                <div className="text-center mb-4">
                  <h2 className="fw-bold">Recuperar Contraseña</h2>
                  <p className="text-muted">
                    Ingresa tu correo electrónico para recuperar tu contraseña
                  </p>
                </div>                {requestSent ? (
                  <div className="text-center">
                    <div className="alert alert-success mb-4" role="alert">
                      <i className="bi bi-check-circle me-2"></i>
                      <p className="mb-0">
                        Hemos enviado las instrucciones de recuperación al correo proporcionado.
                        Por favor, revisa tu bandeja de entrada (y carpeta de spam).
                      </p>
                    </div>
                    <Link 
                      to="/login" 
                      className="btn btn-primary btn-lg"
                    >
                      <i className="bi bi-arrow-left me-2"></i>
                      Volver a inicio de sesión
                    </Link>
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
                      <label htmlFor="correo" className="form-label">
                        Correo Electrónico
                      </label>
                      <input
                        id="correo"
                        name="correo"
                        type="email"
                        placeholder="tu.correo@ejemplo.com"
                        className={`form-control form-control-lg ${
                          formik.touched.correo && formik.errors.correo
                            ? "is-invalid"
                            : ""
                        }`}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        value={formik.values.correo}
                      />
                      {formik.touched.correo && formik.errors.correo && (
                        <div className="invalid-feedback">
                          {formik.errors.correo}
                        </div>
                      )}
                    </div>                    <div className="d-grid gap-2">
                      <button
                        type="submit"
                        className="btn btn-primary btn-lg"
                        disabled={isLoading}
                      >
                        {isLoading ? (
                          <>
                            <span
                              className="spinner-border spinner-border-sm me-2"
                              role="status"
                              aria-hidden="true"
                            ></span>
                            Enviando...
                          </>
                        ) : (
                          "Enviar Instrucciones"
                        )}
                      </button>

                      <Link 
                        to="/login" 
                        className="btn btn-outline-secondary mt-3"
                      >
                        <i className="bi bi-arrow-left me-2"></i>
                        Volver a inicio de sesión
                      </Link>
                    </div>
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

export default RequestPasswordReset;
