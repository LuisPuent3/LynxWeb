import React, { useState, useEffect } from "react";
import ProductList from "../components/Products/ProductList";
import api from "../utils/api"; // Asegúrate de que la ruta a tu API sea la correcta
import { useNavigate } from "react-router-dom";

// Definir las interfaces para los productos
interface Producto {
  id_producto: number;
  nombre: string;
  precio: number;
  cantidad: number;
  imagen?: string; // Si no todas las propiedades son necesarias, usa el signo ? para hacerlas opcionales
}

const Home = () => {
  const [carrito, setCarrito] = useState<Producto[]>([]);
  const navigate = useNavigate();

  // Función para agregar productos al carrito
  const addToCart = (producto: Producto) => {
   
    // Si está autenticado, agregamos el producto al carrito
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

  // Función para eliminar productos del carrito
  const removeFromCart = (id_producto: number) => {
    setCarrito(carrito.filter((item) => item.id_producto !== id_producto));
  };

  // Función para vaciar el carrito
  const vaciarCarrito = () => {
    setCarrito([]);
  };

  // Función para confirmar el pedido
  const confirmarPedido = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");  // Redirige a login si no está autenticado
      return;
    }

    try {
      const id_usuario = 10; // Cambiar por el ID del usuario autenticado (debería venir del token)
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

  return (
    <div className="container">
      <h1>Bienvenido a LynxShop</h1>
      <ProductList addToCart={addToCart} />
      <div className="mt-5">
        <h2>Carrito de Compras</h2>
        {carrito.length === 0 ? (
          <p>El carrito está vacío</p>
        ) : (
          <div>
            {carrito.map((item) => (
              <div key={item.id_producto} className="d-flex justify-content-between">
                <span>
                  {item.nombre} - {item.cantidad} x ${item.precio}
                </span>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => removeFromCart(item.id_producto)}>
                  Eliminar
                </button>
              </div>
            ))}
            <button className="btn btn-warning mt-3" onClick={vaciarCarrito}>
              Vaciar Carrito
            </button>
            <button className="btn btn-success mt-3" onClick={confirmarPedido}>
              Confirmar Pedido
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
