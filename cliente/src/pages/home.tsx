import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import ProductList from "../components/Products/ProductList";
import api from "../utils/api";
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

interface Producto {
  id_producto: number;
  nombre: string;
  precio: number;
  cantidad: number;
  imagen?: string;
}

const Home = () => {
  const [carrito, setCarrito] = useState<Producto[]>([]);
  const navigate = useNavigate();

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
  };

  const confirmarPedido = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }

    try {
      const id_usuario = 10;
      const response = await api.post("/pedidos", {
        carrito,
        id_usuario,
      });
      alert(response.data.mensaje);
      vaciarCarrito();
    } catch (error) {
      console.error("Error al confirmar pedido:", error);
      alert("No se pudo confirmar el pedido.");
    }
  };

  const calculateTotal = () => {
    return carrito.reduce((total, item) => total + item.precio * item.cantidad, 0);
  };

  return (
    <div className="container py-4">
      {/* Hero Section */}
      <div className="bg-light p-5 rounded-lg mb-4">
        <h1 className="display-4">Bienvenido a LynxShop</h1>
        <p className="lead">
          Encuentra todos los productos que necesitas para tu día a día escolar
        </p>
      </div>

      <div className="row">
        {/* Products Section */}
        <div className="col-lg-8 mb-4">
          <div className="card h-100">
            <div className="card-header">
              <h5 className="card-title mb-0">Productos Disponibles</h5>
            </div>
            <div className="card-body">
              <ProductList addToCart={addToCart} />
            </div>
          </div>
        </div>

        {/* Cart Section */}
        <div className="col-lg-4">
          <div className="card">
            <div className="card-header d-flex align-items-center">
              <i className="bi bi-cart me-2"></i>
              <h5 className="card-title mb-0">Carrito de Compras</h5>
            </div>
            <div className="card-body">
              {carrito.length === 0 ? (
                <p className="text-muted text-center py-3">El carrito está vacío</p>
              ) : (
                <div>
                  {carrito.map((item) => (
                    <div key={item.id_producto} className="d-flex justify-content-between align-items-center p-2 border-bottom">
                      <div>
                        <h6 className="mb-0">{item.nombre}</h6>
                        <small className="text-muted">
                          {item.cantidad} x ${item.precio}
                        </small>
                      </div>
                      <button
                        onClick={() => removeFromCart(item.id_producto)}
                        className="btn btn-outline-danger btn-sm"
                      >
                        <i className="bi bi-trash"></i>
                      </button>
                    </div>
                  ))}
                  
                  <div className="mt-3">
                    <h5 className="mb-3">Total: ${calculateTotal().toFixed(2)}</h5>
                    <div className="d-grid gap-2">
                      <button 
                        onClick={vaciarCarrito}
                        className="btn btn-warning"
                      >
                        <i className="bi bi-trash me-2"></i>
                        Vaciar Carrito
                      </button>
                      <button 
                        onClick={confirmarPedido}
                        className="btn btn-success"
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
  );
};

export default Home;