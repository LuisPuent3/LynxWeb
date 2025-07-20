import React, { useEffect, useState } from "react";
import api from "../../utils/api";
import ProductCard from "./ProductCard";
import { Producto } from "../../types/types";
import { useRecommendations } from "../../hooks/useRecommendations";

// Actualizamos la interfaz para incluir productos NLP
interface ProductListProps {
  addToCart: (producto: Producto) => void;
  searchTerm: string;
  categoryFilter: number | null;
  nlpProducts?: Producto[];  // Productos sugeridos por NLP
  isUsingNLP?: boolean;      // Indica si se están usando resultados NLP
}

const ProductList: React.FC<ProductListProps> = ({ 
  addToCart, 
  searchTerm, 
  categoryFilter, 
  nlpProducts = [], 
  isUsingNLP = false 
}) => {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const { sortProductsByRecommendation, loading: loadingRecommendations } = useRecommendations();

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await api.get("/productos");
        setProductos(response.data);
      } catch (error) {
        console.error("Error al obtener productos:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);
  // Determinar qué productos mostrar
  const productosAMostrar = isUsingNLP && nlpProducts.length > 0 ? nlpProducts : productos;

  // Filtramos los productos basados en searchTerm y categoryFilter
  const productosFiltrados = productosAMostrar.filter(producto => {
    // Si estamos usando NLP, no aplicar filtros adicionales ya que NLP ya los procesó
    if (isUsingNLP && nlpProducts.length > 0) {
      return true;
    }
    
    // Verificar si cumple con la condición de búsqueda
    const matchesSearch = producto.nombre.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Verificar si cumple con el filtro de categoría (si hay alguno seleccionado)
    const matchesCategory = categoryFilter === null || producto.id_categoria === categoryFilter;
    
    // El producto debe cumplir con ambas condiciones para ser incluido
    return matchesSearch && matchesCategory;
  });

  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
        <p className="mt-2">Cargando productos...</p>
      </div>
    );
  }
  // Ordenar productos filtrados basados en recomendaciones
  const productosOrdenados = loadingRecommendations 
    ? productosFiltrados 
    : sortProductsByRecommendation(productosFiltrados);
  return (
    <div>
      {/* Indicador de búsqueda NLP */}
      {isUsingNLP && nlpProducts.length > 0 && (
        <div className="alert alert-info border-0 mb-3 d-flex align-items-center">
          <i className="bi bi-brain me-2 text-primary"></i>
          <div>
            <strong>Resultados de búsqueda inteligente LYNX</strong>
            <div className="small text-muted">
              Mostrando {productosFiltrados.length} productos sugeridos por inteligencia artificial
            </div>
          </div>
        </div>
      )}
      
      <div className="row g-3">
        {productosOrdenados.map((producto) => (
          <div className="col-md-6 col-lg-4" key={producto.id_producto}>
            <ProductCard producto={producto} addToCart={addToCart} />
          </div>
        ))}
        {productosFiltrados.length === 0 && (
          <div className="col-12 text-center py-4">
            <i className="bi bi-search display-4 text-muted"></i>
            <p className="text-muted mt-2">
              {isUsingNLP 
                ? "La búsqueda inteligente no encontró productos para esta consulta"
                : searchTerm && categoryFilter 
                  ? "No se encontraron productos con los filtros seleccionados" 
                  : searchTerm 
                    ? "No se encontraron productos con ese término de búsqueda"
                    : categoryFilter
                      ? "No hay productos en esta categoría"
                      : "No hay productos disponibles"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ProductList;