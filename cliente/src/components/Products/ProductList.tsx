import React, { useEffect, useState } from "react";
import api from "../../utils/api"; // Asegúrate de que el archivo exista
import ProductCard from "./ProductCard";

// Definir el tipo para los productos
interface Producto {
  id_producto: number;
  nombre: string;
  precio: number;
  cantidad: number;
  imagen: string; // Asumiendo que siempre hay imagen; si no, usa `imagen?: string`
}

// Definir el tipo para las props
interface ProductListProps {
  addToCart: (producto: Producto) => void; // Función que recibe un producto
}

const ProductList: React.FC<ProductListProps> = ({ addToCart }) => {
  const [productos, setProductos] = useState<Producto[]>([]);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        // Usamos api directamente en lugar de escribir la URL completa
        const response = await api.get("/productos");
        setProductos(response.data);
      } catch (error) {
        console.error("Error al obtener productos:", error);
      }
    };
    fetchProducts();
  }, []);

  return (
    <div className="container mt-5">
      <h2>Productos Disponibles</h2>
      <div className="row">
        {productos.map((producto) => (
          <div className="col-md-4" key={producto.id_producto}>
            <ProductCard producto={producto} addToCart={addToCart} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductList;
