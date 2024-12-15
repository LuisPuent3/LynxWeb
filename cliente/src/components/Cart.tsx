// src/components/Cart.tsx
import React, { useState, useEffect } from "react";
import api from "../utils/api.tsx";

// Interfaz para los productos del carrito
interface ProductoCarrito {
  id_detalle: number;
  nombre: string;
  cantidad: number;
  subtotal: number;
}

interface CartProps {
  userId: number;
}

const Cart: React.FC<CartProps> = ({ userId }) => {
  const [carrito, setCarrito] = useState<ProductoCarrito[]>([]);

  useEffect(() => {
    const fetchCarrito = async () => {
      try {
        const response = await api.get(`/carrito/${userId}`);
        setCarrito(response.data);
      } catch (error) {
        console.error("Error al obtener el carrito:", error);
      }
    };

    fetchCarrito();
  }, [userId]);

  const eliminarProducto = async (idDetalle: number) => {
    try {
      const response = await api.delete(`/carrito/${idDetalle}`);
      alert(response.data.mensaje);
      setCarrito(carrito.filter((item) => item.id_detalle !== idDetalle));
    } catch (error) {
      console.error("Error al eliminar producto:", error);
    }
  };

  return (
    <div className="container mt-5">
      <h2>Carrito de Compras</h2>
      <ul className="list-group">
        {carrito.map((item) => (
          <li key={item.id_detalle} className="list-group-item">
            {item.nombre} - {item.cantidad} unidades - ${item.subtotal.toFixed(2)}
            <button
              onClick={() => eliminarProducto(item.id_detalle)}
              className="btn btn-danger btn-sm float-end">
              Eliminar
            </button>
            <button
              onClick={() => eliminarProducto(item.id_detalle)}
              className="btn btn-danger btn-sm float-end">
              Eliminar
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Cart;
