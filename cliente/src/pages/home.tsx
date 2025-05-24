import React, { useState, useEffect } from "react";
import ProductList from "../components/products/ProductList";
import AuthModal from "../components/auth/AuthModal";
import api from "../utils/api";
import '../styles/Modal.css';
import { useNavigate } from "react-router-dom";
import { Producto } from "../types/types";
import { AxiosError, AxiosResponse } from 'axios';
import { useAuth } from "../contexts/AuthContext";
import { useCategorias } from "../hooks/useCategorias"; // Importar el hook de categorías

interface ApiErrorResponse {
 error?: string;
 mensaje?: string;
}

interface ApiError extends AxiosError {
 response?: AxiosResponse<ApiErrorResponse>; 
}

const Home = () => {
 const [carrito, setCarrito] = useState<Producto[]>(() => {
   const savedCarrito = localStorage.getItem('tempCarrito');
   return savedCarrito ? JSON.parse(savedCarrito) : [];
 });
 const [showAuthModal, setShowAuthModal] = useState(false);
 const [searchTerm, setSearchTerm] = useState("");
 const [categoryFilter, setCategoryFilter] = useState<number | null>(null); // Estado para filtro de categorías
 const navigate = useNavigate();
 const { isAuthenticated, user, logout, login } = useAuth();
 const { categorias, loading: loadingCategorias } = useCategorias(); // Usar el hook

 useEffect(() => {
   localStorage.setItem('tempCarrito', JSON.stringify(carrito));
 }, [carrito]);

 useEffect(() => {
   if (showAuthModal) {
     document.body.style.overflow = 'hidden';
     document.body.classList.add('modal-open');
     console.log("Modal abierto");
   } else {
     document.body.style.overflow = 'unset';
     document.body.classList.remove('modal-open');
     console.log("Modal cerrado");
   }
 }, [showAuthModal]);

 const handleLogout = () => {
   logout();
   navigate('/');
 };

 const addToCart = (producto: Producto) => {
   const existe = carrito.find((item) => item.id_producto === producto.id_producto);
   if (existe) {
     setCarrito(
       carrito.map((item) =>
         item.id_producto === producto.id_producto
           ? { ...item, cantidad: item.cantidad + 1 }
           : item
       )
     );
   } else {
     setCarrito([...carrito, { ...producto, cantidad: 1 }]);
   }
 };

 const removeFromCart = (id_producto: number) => {
   setCarrito(carrito.filter((item) => item.id_producto !== id_producto));
 };

 const vaciarCarrito = () => {
   setCarrito([]);
   localStorage.removeItem('tempCarrito');
 };

 const handleConfirmarPedido = async () => {
   if (carrito.length === 0) {
     alert("El carrito está vacío");
     return;
   }
   
   // Always go to cart page first for all users
   if (isAuthenticated) {
     navigate('/cart');
   } else {
     setShowAuthModal(true);
   }
 };

 const procesarPedido = async () => {
   try {
     const token = localStorage.getItem("token");
     if (!token) {
       setShowAuthModal(true);
       return;
     }
 
     // Get user ID from context instead of using hardcoded values
     if (!user || !user.id_usuario) {
       alert("Error: No se pudo identificar al usuario. Inicie sesión nuevamente.");
       return;
     }

     // Ensure user ID is a number
     const userId = typeof user.id_usuario === 'string' 
       ? parseInt(user.id_usuario as string, 10) 
       : user.id_usuario;

     const pedidoData = {
       carrito: carrito.map(item => ({
         id_producto: Number(item.id_producto),
         cantidad: Number(item.cantidad),
         precio: Number(item.precio)
       })),
       id_usuario: userId // Use numeric user ID
     };
 
     console.log('Datos a enviar:', pedidoData);
     api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
 
     const response = await api.post("/pedidos", pedidoData);
       
     if (response.data.mensaje) {
       navigate('/order/confirmation', { 
         state: { 
           cartItems: carrito,
           orderId: response.data.id_pedido || null,
           total: calculateTotal(),
           discount: 0
         } 
       });
       vaciarCarrito();
     }
   } catch (error) {
     const apiError = error as ApiError;
     console.error("Error completo:", apiError);
     console.error("Detalles del error:", apiError.response?.data);

     // More detailed error handling
     if (apiError.response?.status === 500) {
       const errorMsg = apiError.response.data?.error || "Error interno del servidor";
       
       // Check for foreign key error
       if (errorMsg.includes("foreign key")) {
         alert("Error: El ID de usuario no es válido. Por favor, inicie sesión nuevamente.");
         localStorage.removeItem("token");
         logout();
         setShowAuthModal(true);
       } else {
         alert(`Error del servidor: ${errorMsg}`);
       }
     } else if (apiError.response?.status === 401) {
       localStorage.removeItem("token");
       setShowAuthModal(true);
     } else if (apiError.response?.data?.error) {
       alert(apiError.response.data.error);
     } else {
       alert("Error al procesar el pedido");
     }
   }
 };

 const handleGuestCheckout = async () => {
  try {
    const guestData = {
      nombre: `Guest_${Date.now()}`,
      correo: `guest_${Date.now()}@lynxshop.com`,
      telefono: `000${Date.now().toString().slice(-7)}`,
      contraseña: `guest${Date.now()}`
    };

    console.log('Registrando usuario invitado:', guestData);
    const response = await api.post("/auth/register", guestData);
    
    console.log('Respuesta de registro de invitado:', response.data);
    
    if (response.data.token && response.data.usuario) {
      localStorage.setItem("token", response.data.token);
      localStorage.setItem("guestMode", "true");
      
      console.log('Usuario invitado creado:', response.data.usuario);
      
      // Store the user data from the response
      await login(response.data.token, response.data.usuario);
      setShowAuthModal(false);
      
      // Navigate to cart page for review instead of processing directly
      navigate('/cart');
    } else {
      throw new Error("El registro como invitado falló: no se recibieron datos de usuario");
    }
  } catch (error) {
    console.error("Error al procesar como invitado:", error);
    alert("Error al procesar como invitado. Por favor intente nuevamente.");
  }
};

 const handleLoginSuccess = () => {
   setShowAuthModal(false);
   navigate('/cart');
 };

 // Add event listener for login success
 useEffect(() => {
   const handleLoginSuccessEvent = () => {
     console.log("Login success event received");
     handleLoginSuccess();
   };
   
   document.addEventListener('loginSuccess', handleLoginSuccessEvent);
   
   return () => {
     document.removeEventListener('loginSuccess', handleLoginSuccessEvent);
   };
 }, [handleLoginSuccess]);

 const calculateTotal = (): number => {
   const total = carrito.reduce((total, item) => {
     const precio = Number(item.precio);
     return total + (precio * item.cantidad);
   }, 0);
   
   return Number(total.toFixed(2));
 };

 return (
   <>
     <nav className="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
       <div className="container">
         <a className="navbar-brand d-flex align-items-center" href="/" style={{ 
           color: "white", 
           fontWeight: "bold",
           textShadow: "1px 1px 2px rgba(0,0,0,0.3)",
           fontSize: "1.25rem",
           transition: "all 0.3s ease"
         }}
         onMouseEnter={(e) => e.currentTarget.style.textShadow = "1px 1px 4px rgba(0,0,0,0.5)"}
         onMouseLeave={(e) => e.currentTarget.style.textShadow = "1px 1px 2px rgba(0,0,0,0.3)"}
         >
           <i className="bi bi-shop me-2" style={{ fontSize: "1.4rem" }}></i>
           LynxShop
         </a>
         <button
           className="navbar-toggler"
           type="button"
           data-bs-toggle="collapse"
           data-bs-target="#navbarContent"
         >
           <span className="navbar-toggler-icon"></span>
         </button>
         <div className="collapse navbar-collapse" id="navbarContent">
           <form className="d-flex mx-auto mt-2 mt-lg-0 col-12 col-lg-6">
             <div className="input-group">
               <input
                 type="search"
                 className="form-control"
                 placeholder="Buscar productos..."
                 value={searchTerm}
                 onChange={(e) => setSearchTerm(e.target.value)}
               />
               <button className="btn btn-light" type="submit">
                 <i className="bi bi-search"></i>
               </button>
             </div>
           </form>
           <div className="ms-auto mt-2 mt-lg-0 d-flex align-items-center">
             {isAuthenticated ? (
               <>
                 {/* Botón de Admin Dashboard para administradores */}
                 {user && user.rol === 'Administrador' && (
                   <button
                     className="btn btn-warning me-3"
                     onClick={() => navigate('/admin/dashboard')}
                   >
                     <i className="bi bi-speedometer2 me-1"></i>
                     <span className="d-none d-md-inline">Panel Admin</span>
                   </button>
                 )}
                 <div className="dropdown me-3">
                   <button 
                     className="btn btn-primary dropdown-toggle d-flex align-items-center" 
                     type="button" 
                     id="userMenuDropdown" 
                     data-bs-toggle="dropdown" 
                     aria-expanded="false"
                   >
                     <i className="bi bi-person-circle me-1"></i>
                     <span className="d-none d-md-inline">
                       {user?.nombre || 'Usuario'}
                       {localStorage.getItem("guestMode") === "true" && (
                         <span className="badge bg-warning text-dark ms-1" style={{ fontSize: '0.65rem' }}>Invitado</span>
                       )}
                     </span>
                   </button>
                   <ul className="dropdown-menu dropdown-menu-end" aria-labelledby="userMenuDropdown">
                     <li>
                       <button 
                         className="dropdown-item d-flex align-items-center" 
                         onClick={() => navigate('/pedidos')}
                         disabled={localStorage.getItem("guestMode") === "true"}
                       >
                         <i className="bi bi-bag me-2"></i>
                         Mis Pedidos
                         {localStorage.getItem("guestMode") === "true" && (
                           <span className="badge bg-secondary ms-2" style={{ fontSize: '0.65rem' }}>No disponible</span>
                         )}
                       </button>
                     </li>
                     <li><hr className="dropdown-divider" /></li>
                     <li>
                       <button 
                         className="dropdown-item d-flex align-items-center text-danger" 
                         onClick={handleLogout}
                       >
                         <i className="bi bi-box-arrow-right me-2"></i>
                         Cerrar sesión
                       </button>
                     </li>
                   </ul>
                 </div>
                 <button 
                   className="btn btn-outline-light" 
                   onClick={() => navigate('/pedidos')}
                   onMouseEnter={(e) => {
                     e.currentTarget.classList.remove('btn-outline-light');
                     e.currentTarget.classList.add('btn-white');
                     e.currentTarget.style.backgroundColor = "#ffffff";
                     e.currentTarget.style.color = "#0d6efd";
                   }}
                   onMouseLeave={(e) => {
                     e.currentTarget.classList.remove('btn-white');
                     e.currentTarget.classList.add('btn-outline-light');
                     e.currentTarget.style.backgroundColor = "";
                     e.currentTarget.style.color = "";
                   }}
                 >
                   <i className="bi bi-bag me-1"></i>
                   Pedidos
                 </button>
               </>
             ) : (
               <>
                 <button 
                   className="btn btn-outline-light me-2" 
                   onClick={() => navigate("/login")}
                 >
                   <i className="bi bi-person me-1"></i>
                   Iniciar Sesión
                 </button>
                 <button 
                   className="btn btn-light" 
                   onClick={() => navigate("/register")}
                 >
                   <i className="bi bi-person-plus me-1"></i>
                   Registrarse
                 </button>
               </>
             )}
           </div>
         </div>
       </div>
     </nav>

     <div className="container py-4">
       <div className="bg-light p-4 rounded-3 shadow-sm mb-4">
         <div className="row align-items-center">
           <div className="col-md-8">
             <h1 className="display-5 fw-bold text-primary mb-2">Bienvenido a LynxShop</h1>
             <p className="lead mb-0">Encuentra todo lo que necesitas para tu día a día escolar</p>
           </div>
           <div className="col-md-4 text-end d-none d-md-block">
             <i className="bi bi-bag-check display-1 text-primary opacity-50"></i>
           </div>
         </div>
       </div>

       <div className="row">
         <div className="col-lg-8 mb-4">
           <div className="card shadow-sm">
             <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
               <h5 className="card-title mb-0">Productos Disponibles</h5>
               <div className="dropdown">
                 <button className="btn btn-outline-primary btn-sm dropdown-toggle" type="button" id="dropdownCategorias" data-bs-toggle="dropdown" aria-expanded="false">
                   <i className="bi bi-filter me-1"></i>
                   {categoryFilter ? categorias.find(c => c.id_categoria === categoryFilter)?.nombre : 'Todas las categorías'}
                 </button>
                 <ul className="dropdown-menu dropdown-menu-end shadow-sm" aria-labelledby="dropdownCategorias">
                   <li>
                     <button className="dropdown-item d-flex align-items-center" onClick={() => setCategoryFilter(null)}>
                       <i className="bi bi-grid me-2 text-primary"></i>
                       Todas las categorías
                     </button>
                   </li>
                   <li><hr className="dropdown-divider" /></li>
                   {categorias.map(categoria => (
                     <li key={categoria.id_categoria}>
                       <button 
                         className={`dropdown-item d-flex align-items-center ${categoryFilter === categoria.id_categoria ? 'active' : ''}`}
                         onClick={() => setCategoryFilter(categoria.id_categoria)}
                       >
                         <i className="bi bi-tag me-2"></i>
                         {categoria.nombre}
                       </button>
                     </li>
                   ))}
                 </ul>
               </div>
             </div>
             <div className="card-body">
               <ProductList addToCart={addToCart} searchTerm={searchTerm} categoryFilter={categoryFilter} />
             </div>
           </div>
         </div>

         <div className="col-lg-4">
           <div className="card shadow-sm sticky-top" style={{ top: "80px" }}>
             <div className="card-header bg-white py-3">
               <h5 className="card-title mb-0 d-flex align-items-center">
                 <i className="bi bi-cart3 me-2"></i>
                 Carrito de Compras
               </h5>
             </div>
             <div className="card-body">
               {carrito.length === 0 ? (
                 <div className="text-center py-4">
                   <i className="bi bi-cart-x display-4 text-muted"></i>
                   <p className="text-muted mt-2">El carrito está vacío</p>
                 </div>
               ) : (
                 <div>
                   {carrito.map((item) => (
                     <div
                       key={item.id_producto}
                       className="d-flex justify-content-between align-items-center p-2 border-bottom"
                     >
                       <div>
                         <h6 className="mb-0">{item.nombre}</h6>
                         <small className="text-muted">
                           {item.cantidad} x ${item.precio}
                         </small>
                       </div>
                       <button
                         className="btn btn-outline-danger btn-sm"
                         onClick={() => removeFromCart(item.id_producto)}
                       >
                         <i className="bi bi-trash"></i>
                       </button>
                     </div>
                   ))}

                   <div className="mt-3">
                     <h5 className="text-end mb-3">
                       Total: ${calculateTotal().toFixed(2)}
                     </h5>
                     <div className="d-grid gap-2">
                       <button
                         className="btn btn-outline-danger"
                         onClick={vaciarCarrito}
                       >
                         <i className="bi bi-trash me-2"></i>
                         Vaciar Carrito
                       </button>
                       <button
                         className="btn btn-primary"
                         onClick={handleConfirmarPedido}
                       >
                         <i className="bi bi-check-circle me-2"></i>
                         Confirmar Pedido
                       </button>
                     </div>
                   </div>
                 </div>
               )}
             </div>
           </div>
         </div>
       </div>
     </div>

     {showAuthModal && (
       <div className="modal-container">
         <div 
           className="modal"
           style={{ 
             display: 'block',
           }}
         >
           <div className="modal-dialog modal-dialog-centered modal-lg">
             <div className="modal-content border-0 shadow-lg rounded-3 overflow-hidden">
               <div 
                 className="modal-header border-0 text-white py-4"
                 style={{
                   background: 'linear-gradient(135deg, #0d6efd, #0dcaf0)'
                 }}
               >
                 <h5 className="modal-title fs-4 d-flex align-items-center">
                   <i className="bi bi-cart-check-fill me-2"></i>
                   Finalizar tu Compra
                 </h5>
                 <button 
                   type="button" 
                   className="btn-close btn-close-white" 
                   onClick={() => setShowAuthModal(false)}
                   aria-label="Cerrar"
                 />
               </div>
               
               <div className="modal-body p-5 bg-light">
                 <div className="text-center mb-4">
                   <h4 className="text-primary fw-bold mb-2">Elige cómo continuar</h4>
                   <p className="text-muted">Selecciona una opción para completar tu pedido</p>
                 </div>
                 
                 <div className="row g-4">
                   {/* Opción de Iniciar Sesión */}
                   <div className="col-md-4">
                     <div className="card h-100 border-0 shadow-sm hover-card">
                       <div className="card-body text-center p-4">
                         <div className="icon-circle bg-primary bg-opacity-10 text-primary mx-auto mb-3">
                           <i className="bi bi-person-fill fs-3"></i>
                         </div>
                         <h5 className="card-title mb-2">Iniciar Sesión</h5>
                         <p className="card-text text-muted small mb-3">Accede a tu cuenta para gestionar tus pedidos</p>
                         <button 
                           className="btn btn-primary w-100 py-2"
                           onClick={() => {
                             setShowAuthModal(false);
                             navigate("/login");
                           }}
                         >
                           <i className="bi bi-box-arrow-in-right me-2"></i>
                           Ingresar
                         </button>
                       </div>
                     </div>
                   </div>

                   {/* Opción de Comprar como Invitado */}
                   <div className="col-md-4">
                     <div className="card h-100 border-0 shadow-sm hover-card">
                       <div className="card-body text-center p-4">
                         <div className="icon-circle bg-success bg-opacity-10 text-success mx-auto mb-3">
                           <i className="bi bi-person-badge fs-3"></i>
                         </div>
                         <h5 className="card-title mb-2">Comprar como Invitado</h5>
                         <p className="card-text text-muted small mb-3">Realiza tu compra sin crear una cuenta</p>
                         <button 
                           className="btn btn-success w-100 py-2"
                           onClick={handleGuestCheckout}
                         >
                           <i className="bi bi-cart-check me-2"></i>
                           Continuar
                         </button>
                       </div>
                     </div>
                   </div>

                   {/* Opción de Registrarse */}
                   <div className="col-md-4">
                     <div className="card h-100 border-0 shadow-sm hover-card">
                       <div className="card-body text-center p-4">
                         <div className="icon-circle bg-info bg-opacity-10 text-info mx-auto mb-3">
                           <i className="bi bi-person-plus-fill fs-3"></i>
                         </div>
                         <h5 className="card-title mb-2">Registrarse</h5>
                         <p className="card-text text-muted small mb-3">Crea una cuenta para gestionar tus compras</p>
                         <button 
                           className="btn btn-info text-white w-100 py-2"
                           onClick={() => navigate("/register")}
                         >
                           <i className="bi bi-pencil-square me-2"></i>
                           Crear Cuenta
                         </button>
                       </div>
                     </div>
                   </div>
                 </div>
               </div>
             </div>
           </div>
         </div>
         <div className="modal-backdrop fade show" style={{opacity: 0.6}} />
       </div>
     )}
  </>
 );
};
export default Home;