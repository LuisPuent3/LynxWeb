import React, { useState } from "react";
import api from "../../utils/api";  // Asegúrate de importar correctamente

const Register = () => {
  const [nombre, setNombre] = useState<string>("");  // Definir tipo para el state
  const [correo, setCorreo] = useState<string>("");  // Definir tipo para el state
  const [telefono, setTelefono] = useState<string>("");  // Definir tipo para el state
  const [contraseña, setContraseña] = useState<string>("");  // Definir tipo para el state
  const [mensaje, setMensaje] = useState<string>("");

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await api.post("/auth/register", { nombre, correo, telefono, contraseña });
      setMensaje("Registro exitoso. Ahora puedes iniciar sesión.");
    } catch (err) {
      setMensaje("Error al registrar. Intenta nuevamente.");
    }
  };

  return (
    <div className="container mt-5">
      <h2>Registro</h2>
      {mensaje && <div className="alert alert-info">{mensaje}</div>}
      <form onSubmit={handleRegister}>
        <div className="mb-3">
          <label>Nombre</label>
          <input
            type="text"
            className="form-control"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label>Correo electrónico</label>
          <input
            type="email"
            className="form-control"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label>Teléfono</label>
          <input
            type="tel"
            className="form-control"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label>Contraseña</label>
          <input
            type="password"
            className="form-control"
            value={contraseña}
            onChange={(e) => setContraseña(e.target.value)}
          />
        </div>
        <button type="submit" className="btn btn-primary">Registrar</button>
      </form>
    </div>
  );
};

export default Register;
