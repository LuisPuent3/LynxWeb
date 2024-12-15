import React, { useState, useEffect } from "react";
import api from "../../utils/api";

const UserManagement = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [formData, setFormData] = useState({
    nombre: "",
    apellidoP: "",
    apellidoM: "",
    correo: "",
    telefono: "",
    contraseña: "",
    id_rol: 1,
  });

  useEffect(() => {
    const fetchUsuarios = async () => {
      try {
        const response = await api.get("/usuarios");
        setUsuarios(response.data);
      } catch (error) {
        console.error("Error al obtener usuarios:", error);
      }
    };
    fetchUsuarios();
  }, []);

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post("/usuarios", formData);
      alert(response.data.mensaje);
      setFormData({
        nombre: "",
        apellidoP: "",
        apellidoM: "",
        correo: "",
        telefono: "",
        contraseña: "",
        id_rol: 1,
      });
      const usuariosActualizados = await api.get("/usuarios");
      setUsuarios(usuariosActualizados.data);
    } catch (error) {
      console.error("Error al crear usuario:", error);
      alert("No se pudo crear el usuario.");
    }
  };

  return (
    <div className="container mt-5">
      <h2>Gestión de Usuarios</h2>
      <form onSubmit={handleSubmit} className="mb-5">
        <div className="row">
          <div className="col-md-4">
            <input
              type="text"
              name="nombre"
              placeholder="Nombre"
              value={formData.nombre}
              onChange={handleInputChange}
              className="form-control"
            />
          </div>
          <div className="col-md-4">
            <input
              type="text"
              name="apellidoP"
              placeholder="Apellido Paterno"
              value={formData.apellidoP}
              onChange={handleInputChange}
              className="form-control"
            />
          </div>
          <div className="col-md-4">
            <input
              type="text"
              name="apellidoM"
              placeholder="Apellido Materno"
              value={formData.apellidoM}
              onChange={handleInputChange}
              className="form-control"
            />
          </div>
        </div>
        <div className="row mt-3">
          <div className="col-md-4">
            <input
              type="email"
              name="correo"
              placeholder="Correo Electrónico"
              value={formData.correo}
              onChange={handleInputChange}
              className="form-control"
            />
          </div>
          <div className="col-md-4">
            <input
              type="text"
              name="telefono"
              placeholder="Teléfono"
              value={formData.telefono}
              onChange={handleInputChange}
              className="form-control"
            />
          </div>
          <div className="col-md-4">
            <select
              name="id_rol"
              value={formData.id_rol}
              onChange={handleInputChange}
              className="form-control"
            >
              <option value={1}>Cliente</option>
              <option value={2}>Administrador</option>
              <option value={3}>Invitado</option>
            </select>
          </div>
        </div>
        <div className="row mt-3">
          <div className="col-md-12">
            <input
              type="password"
              name="contraseña"
              placeholder="Contraseña"
              value={formData.contraseña}
              onChange={handleInputChange}
              className="form-control"
            />
          </div>
        </div>
        <button type="submit" className="btn btn-primary mt-3">
          Crear Usuario
        </button>
      </form>

      <h3>Lista de Usuarios</h3>
      <ul className="list-group">
        {usuarios.map((usuario) => (
          <li key={usuario.id_usuario} className="list-group-item">
            {usuario.nombre} {usuario.apellidoP} {usuario.apellidoM} - {usuario.rol}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UserManagement;