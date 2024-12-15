import React, { useEffect, useState } from "react";
import api from "../../utils/api";
import ProductCard from "./ProductCard";

// Interfaces
interface Producto {
 id_producto: number;
 nombre: string;
 precio: number;
 cantidad: number;
 imagen: string;
 id_categoria: number;
}

interface ProductListProps {
 addToCart: (producto: Producto) => void;
}

const ProductList: React.FC<ProductListProps> = ({ addToCart }) => {
 const [productos, setProductos] = useState<Producto[]>([]);
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState<string | null>(null);

 useEffect(() => {
   const fetchProducts = async () => {
     try {
       setLoading(true);
       const response = await api.get("/productos");
       setProductos(response.data);
       setError(null);
     } catch (error) {
       console.error("Error al obtener productos:", error);
       setError("Error al cargar los productos. Por favor, intente más tarde.");
     } finally {
       setLoading(false);
     }
   };

   fetchProducts();
 }, []);

 if (loading) {
   return <div className="text-center mt-5">Cargando productos...</div>;
 }

 if (error) {
   return <div className="alert alert-danger mt-5">{error}</div>;
 }

 if (productos.length === 0) {
   return <div className="alert alert-info mt-5">No hay productos disponibles.</div>;
 }

 return (
   <div className="container mt-5">
     <h2 className="mb-4">Productos Disponibles</h2>
     <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
       {productos.map((producto) => (
         <div className="col" key={producto.id_producto}>
           <ProductCard 
             producto={producto} 
             addToCart={addToCart}
           />
         </div>
       ))}
     </div>
   </div>
 );
};

export default ProductList;