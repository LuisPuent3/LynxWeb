import React, { useState, useEffect } from "react";
import ProductList from "../components/products/ProductList";
import AuthModal from "../components/auth/AuthModal";
import api from "../utils/api";
import { useNavigate } from "react-router-dom";
import { Producto } from "../types/types";
import { AxiosError, AxiosResponse } from 'axios';

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
  const navigate = useNavigate();

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

    const token = localStorage.getItem("token");
    console.log("Verificando token:", token);
    
    if (!token) {
      console.log("No hay token, mostrando modal");
      setShowAuthModal(true);
      return;
    }
    
    try {
      await procesarPedido();
    } catch (error) {
      const apiError = error as ApiError;
      console.error("Error al procesar pedido:", apiError);
      if (apiError.response?.status === 401) {
        localStorage.removeItem("token");
        console.log("Token inválido, mostrando modal");
        setShowAuthModal(true);
      }
    }
  };

  const procesarPedido = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setShowAuthModal(true);
        return;
      }

      // Estructura simplificada que espera el backend
      const pedidoData = {
        productos: carrito.map(item => ({
          id_producto: Number(item.id_producto),
          cantidad: Number(item.cantidad),
          precio: Number(item.precio)
        }))
      };

      console.log('Datos a enviar:', pedidoData);

      // Configurar el token en los headers
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      const response = await api.post<ApiErrorResponse>("/pedidos", pedidoData);
      
      if (response.data.mensaje) {
        alert(response.data.mensaje);
        vaciarCarrito();
      }
    } catch (error) {
      const apiError = error as ApiError;
      console.error("Error completo:", apiError);
      console.error("Detalles del error:", apiError.response?.data);

      if (apiError.response?.status === 401) {
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
      console.log("Iniciando checkout como invitado");
      const response = await api.post("/auth/guest");
      
      if (response.data.token) {
        localStorage.setItem("token", response.data.token);
        console.log("Token de invitado obtenido");
        setShowAuthModal(false);
        await procesarPedido();
      } else {
        throw new Error("No se recibió token de invitado");
      }
    } catch (error) {
      console.error("Error en checkout invitado:", error);
      alert("Error al procesar como invitado. Por favor intente nuevamente.");
    }
  };

  const handleLoginSuccess = () => {
    setShowAuthModal(false);
    procesarPedido();
  };

  const calculateTotal = (): number => {
    const total = carrito.reduce((total, item) => {
      const precio = Number(item.precio);
      return total + (precio * item.cantidad);
    }, 0);
    
    return Number(total.toFixed(2));
  };

  return (
    <>
      {/* Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
        <div className="container">
          <a className="navbar-brand d-flex align-items-center" href="/">
            <i className="bi bi-shop me-2"></i>
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
            <div className="ms-auto mt-2 mt-lg-0">
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
            </div>
          </div>
        </div>
      </nav>

      <div className="container py-4">
        {/* Hero Section */}
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
          {/* Lista de Productos */}
          <div className="col-lg-8 mb-4">
            <div className="card shadow-sm">
              <div className="card-header bg-white py-3">
                <h5 className="card-title mb-0">Productos Disponibles</h5>
              </div>
              <div className="card-body">
                <ProductList addToCart={addToCart} searchTerm={searchTerm} />
              </div>
            </div>
          </div>

          {/* Carrito */}
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

      {/* Modal de Autenticación */}
      <div
        className={`modal fade ${showAuthModal ? 'show' : ''}`}
        style={{ display: showAuthModal ? 'block' : 'none' }}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
      >
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            <AuthModal
              isOpen={true}
              onClose={() => {
                console.log("Cerrando modal");
                setShowAuthModal(false);
              }}
              onLogin={handleLoginSuccess}
              onGuestCheckout={handleGuestCheckout}
              vaciarCarrito={vaciarCarrito}
            />
          </div>
        </div>
      </div>

      {/* Backdrop */}
      {showAuthModal && (
        <div 
          className="modal-backdrop fade show" 
          style={{ display: 'block' }}
        />
      )}
    </>
  );
};

export default Home;