import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';

const Login = () => {
 const [correo, setCorreo] = useState('');
 const [contraseña, setContraseña] = useState('');
 const [error, setError] = useState('');
 const [success, setSuccess] = useState('');
 const navigate = useNavigate();

 const handleLogin = async (e: React.FormEvent) => {
  e.preventDefault();
  try {
    console.log('Intentando login con:', { correo, contraseña });
    const response = await api.post('/auth/login', {
      correo,
      contraseña
    });
    console.log('Respuesta del servidor:', response.data);
    
    if (response.data.token) {
      setSuccess('Login exitoso!');
      localStorage.setItem('token', response.data.token);
      // Agrega un delay para ver el mensaje
      await new Promise(resolve => setTimeout(resolve, 2000));
      navigate('/cart');
    } else {
      setError('Credenciales inválidas');
    }

  } catch (err: any) {
    console.error('Error completo:', err);
    setError(err.response?.data?.error || 'Error en el login');
    // Mantén el mensaje de error visible por más tiempo
    await new Promise(resolve => setTimeout(resolve, 10000));
  }
};

 return (
   <div className="container mt-5">
     <div className="row justify-content-center">
       <div className="col-md-6">
         <div className="card">
           <div className="card-header">
             <h3 className="text-center">Iniciar Sesión</h3>
           </div>
           <div className="card-body">
             {error && <div className="alert alert-danger">{error}</div>}
             {success && <div className="alert alert-success">{success}</div>}
             <form onSubmit={handleLogin}>
               <div className="mb-3">
                 <label htmlFor="correo" className="form-label">Correo Electrónico</label>
                 <input
                   type="email"
                   className="form-control"
                   id="correo"
                   value={correo}
                   onChange={(e) => setCorreo(e.target.value)}
                   required
                 />
               </div>
               <div className="mb-3">
                 <label htmlFor="contraseña" className="form-label">Contraseña</label>
                 <input
                   type="password"
                   className="form-control"
                   id="contraseña"
                   value={contraseña}
                   onChange={(e) => setContraseña(e.target.value)}
                   required
                 />
               </div>
               <button type="submit" className="btn btn-primary w-100">
                 Iniciar Sesión
               </button>
             </form>
           </div>
         </div>
       </div>
     </div>
   </div>
 );
};

export default Login;