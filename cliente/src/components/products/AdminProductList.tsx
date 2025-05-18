import React, { useEffect, useState } from "react";
import api from "../../utils/api";
import AdminProductCard from "./AdminProductCard";
import { Producto } from "../../types/types";

interface AdminProductListProps {
  onEdit: (producto: Producto) => void;
  onDelete: (id: number) => void;
  searchTerm: string;
  refreshTrigger?: number; // Para forzar actualización de la lista
}

const AdminProductList: React.FC<AdminProductListProps> = ({ 
  onEdit, 
  onDelete, 
  searchTerm,
  refreshTrigger = 0
}) => {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [categorias, setCategorias] = useState<{[key: number]: string}>({});
  
  // Filtrado
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState<number | null>(null);
  const [ordenamiento, setOrdenamiento] = useState<string>("nombre-asc");

  useEffect(() => {
    const fetchProductsAndCategories = async () => {
      try {
        setLoading(true);
        
        // Obtener productos
        const productosResponse = await api.get("/productos");
        setProductos(productosResponse.data);
        
        // Obtener categorías
        const categoriasResponse = await api.get("/categorias");
        const categoriasMap: {[key: number]: string} = {};
        categoriasResponse.data.forEach((cat: any) => {
          categoriasMap[cat.id_categoria] = cat.nombre;
        });
        setCategorias(categoriasMap);
        
        setLoading(false);
      } catch (error) {
        console.error("Error al cargar productos:", error);
        setError("No se pudieron cargar los productos. Por favor, intente de nuevo.");
        setLoading(false);
      }
    };

    fetchProductsAndCategories();
  }, [refreshTrigger]); // Dependencia para refrescar la lista cuando cambia

  // Actualizar cuando cambia el ordenamiento
  const productosFiltrados = productos
    .filter(producto => {
      // Filtrar por búsqueda
      const matchesSearch = producto.nombre.toLowerCase().includes(searchTerm.toLowerCase());
      
      // Filtrar por categoría si hay una seleccionada
      const matchesCategoria = categoriaSeleccionada === null || 
                              producto.id_categoria === categoriaSeleccionada;
      
      return matchesSearch && matchesCategoria;
    })
    .sort((a, b) => {
      // Ordenar según la selección
      const [campo, direccion] = ordenamiento.split('-');
      
      if (campo === 'nombre') {
        return direccion === 'asc' 
          ? a.nombre.localeCompare(b.nombre)
          : b.nombre.localeCompare(a.nombre);
      } else if (campo === 'precio') {
        const precioA = typeof a.precio === 'string' ? parseFloat(a.precio) : a.precio;
        const precioB = typeof b.precio === 'string' ? parseFloat(b.precio) : b.precio;
        return direccion === 'asc' ? precioA - precioB : precioB - precioA;
      } else if (campo === 'stock') {
        return direccion === 'asc' ? a.cantidad - b.cantidad : b.cantidad - a.cantidad;
      }
      
      return 0;
    });

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Cargando productos...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        <i className="bi bi-exclamation-triangle-fill me-2"></i>
        {error}
      </div>
    );
  }

  return (
    <div>
      {/* Opciones de filtrado y ordenamiento */}
      <div className="d-flex flex-wrap gap-2 mb-4 align-items-center">
        <div className="me-auto">
          <span className="text-muted">
            {productosFiltrados.length} producto{productosFiltrados.length !== 1 ? 's' : ''} encontrado{productosFiltrados.length !== 1 ? 's' : ''}
          </span>
        </div>
        
        <div className="d-flex gap-2">
          <select 
            className="form-select form-select-sm"
            value={categoriaSeleccionada === null ? '' : categoriaSeleccionada}
            onChange={(e) => setCategoriaSeleccionada(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">Todas las categorías</option>
            {Object.entries(categorias).map(([id, nombre]) => (
              <option key={id} value={id}>
                {nombre}
              </option>
            ))}
          </select>
          
          <select 
            className="form-select form-select-sm"
            value={ordenamiento}
            onChange={(e) => setOrdenamiento(e.target.value)}
          >
            <option value="nombre-asc">Nombre (A-Z)</option>
            <option value="nombre-desc">Nombre (Z-A)</option>
            <option value="precio-asc">Precio (menor a mayor)</option>
            <option value="precio-desc">Precio (mayor a menor)</option>
            <option value="stock-asc">Stock (menor a mayor)</option>
            <option value="stock-desc">Stock (mayor a menor)</option>
          </select>
        </div>
      </div>
      
      {/* Lista de productos */}
      <div className="row g-4">
        {productosFiltrados.length > 0 ? (
          productosFiltrados.map((producto) => (
            <div className="col-sm-6 col-md-4 col-lg-3" key={producto.id_producto}>
              <AdminProductCard 
                producto={{
                  ...producto,
                  id_categoria: producto.id_categoria
                }} 
                onEdit={onEdit} 
                onDelete={onDelete} 
              />
            </div>
          ))
        ) : (
          <div className="col-12 text-center py-5">
            <div className="py-5">
              <i className="bi bi-search fs-1 text-muted"></i>
              <p className="mt-3 text-muted">No se encontraron productos que coincidan con la búsqueda.</p>
              <button 
                className="btn btn-outline-primary mt-2"
                onClick={() => {
                  setCategoriaSeleccionada(null);
                }}
              >
                Mostrar todos los productos
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminProductList; 