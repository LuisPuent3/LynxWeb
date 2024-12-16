import React, { useEffect, useState } from "react";
import api from "../../utils/api";
import ProductCard from "./ProductCard";
import { Producto } from "../../types/types";

// Actualizamos la interfaz para incluir searchTerm
interface ProductListProps {
  addToCart: (producto: Producto) => void;
  searchTerm: string; // Añadimos esta prop
}

const ProductList: React.FC<ProductListProps> = ({ addToCart, searchTerm }) => {
  const [productos, setProductos] = useState<Producto[]>([]);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get("/productos");
        setProductos(response.data);
      } catch (error) {
        console.error("Error al obtener productos:", error);
      }
    };
    fetchProducts();
  }, []);

  // Filtramos los productos basados en searchTerm
  const productosFiltrados = productos.filter(producto =>
    producto.nombre.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="row g-3">
      {productosFiltrados.map((producto) => (
        <div className="col-md-6 col-lg-4" key={producto.id_producto}>
          <ProductCard producto={producto} addToCart={addToCart} />
        </div>
      ))}
      {productosFiltrados.length === 0 && (
        <div className="col-12 text-center py-4">
          <p className="text-muted">No se encontraron productos</p>
        </div>
      )}
    </div>
  );
};

export default ProductList;