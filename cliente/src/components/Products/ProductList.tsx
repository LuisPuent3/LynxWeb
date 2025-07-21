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
  // 🧠 PRIORIDAD 1: Mostrar resultados LCLN si están disponibles
  const productosAMostrar = isUsingNLP && nlpProducts.length > 0 ? nlpProducts : productos;

  // Filtrar productos según el motor usado
  const productosFiltrados = productosAMostrar.filter(producto => {
    // 🎯 Si usamos LCLN, mostrar directamente los resultados (ya están procesados inteligentemente)
    if (isUsingNLP && nlpProducts.length > 0) {
      console.log('🧠 Mostrando resultados LCLN procesados:', producto.nombre);
      return true;
    }
    
    // 🔄 Fallback: Búsqueda normal solo si no hay resultados LCLN
    const matchesSearch = searchTerm.length === 0 || producto.nombre.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === null || producto.id_categoria === categoryFilter;
    
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
      {/* Indicador de búsqueda LCLN inteligente */}
      {isUsingNLP && nlpProducts.length > 0 && (
        <div className="alert border-0 mb-3 d-flex align-items-center" style={{
          background: 'linear-gradient(90deg, #e8f4fd 0%, #f0f9ff 100%)',
          border: '1px solid #bee5eb'
        }}>
          <div className="d-flex align-items-center">
            <span className="me-2" style={{ fontSize: '20px' }}>🧠</span>
            <div>
              <strong className="text-primary">Búsqueda Inteligente LCLN Activada</strong>
              <div className="small text-muted">
                🎯 Encontrados {productosFiltrados.length} productos con inteligencia artificial
                {nlpProducts[0]?.match_score && (
                  <span className="badge bg-success ms-2">
                    {Math.round(nlpProducts[0].match_score * 100)}% precisión
                  </span>
                )}
              </div>
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