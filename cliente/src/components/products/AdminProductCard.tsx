import React from "react";
import { Producto } from "../../types/types";

interface AdminProductCardProps {
  producto: Producto;
  onEdit: (producto: Producto) => void;
  onDelete: (id: number) => void;
}

const AdminProductCard: React.FC<AdminProductCardProps> = ({ 
  producto, 
  onEdit, 
  onDelete 
}) => {
  // Convertimos el precio a número antes de usar toFixed
  const precioNumerico = typeof producto.precio === 'string' 
    ? parseFloat(producto.precio) 
    : producto.precio;

  return (
    <div className="card h-100 shadow-sm position-relative admin-product-card">
      {/* Etiqueta de admin */}
      <div className="position-absolute top-0 end-0 m-2">
        <div className="dropdown">
          <button 
            className="btn btn-sm btn-dark rounded-circle" 
            type="button" 
            data-bs-toggle="dropdown" 
            aria-expanded="false"
          >
            <i className="bi bi-three-dots"></i>
          </button>
          <ul className="dropdown-menu dropdown-menu-end">
            <li>
              <button 
                className="dropdown-item" 
                onClick={() => onEdit(producto)}
              >
                <i className="bi bi-pencil me-2"></i>
                Editar
              </button>
            </li>
            <li>
              <button 
                className="dropdown-item text-danger" 
                onClick={() => {
                  if (window.confirm('¿Estás seguro de eliminar este producto?')) {
                    onDelete(producto.id_producto);
                  }
                }}
              >
                <i className="bi bi-trash me-2"></i>
                Eliminar
              </button>
            </li>
          </ul>
        </div>
      </div>

      {/* Imagen y badge */}
      <div className="position-relative">
        <div className="admin-product-img-placeholder d-flex align-items-center justify-content-center" style={{ height: '180px', backgroundColor: '#f8f9fa' }}>
          {producto.imagen ? (
            <img
              src={`http://localhost:5000/uploads/${producto.imagen}`}
              className="card-img-top"
              alt={producto.nombre}
              style={{ height: '180px', objectFit: 'cover' }}
            />
          ) : (
            <i className="bi bi-box text-secondary" style={{ fontSize: '3rem' }}></i>
          )}
        </div>
        {producto.cantidad <= 5 && (
          <span className="position-absolute top-0 start-0 badge bg-danger m-2">
            Stock bajo: {producto.cantidad}
          </span>
        )}
      </div>

      {/* Contenido */}
      <div className="card-body d-flex flex-column border-top">
        <div className="d-flex justify-content-between align-items-start mb-2">
          <h5 className="card-title mb-0">{producto.nombre}</h5>
          <span className="badge bg-primary">${isNaN(precioNumerico) ? '0.00' : precioNumerico.toFixed(2)}</span>
        </div>
        
        <div className="mb-2">
          <span className="d-block text-muted small">
            <i className="bi bi-tag me-1"></i>
            Categoría: {producto.id_categoria}
          </span>
          <span className="d-block text-muted small">
            <i className="bi bi-boxes me-1"></i>
            Stock: {producto.cantidad}
          </span>
          <span className="d-block text-muted small">
            <i className="bi bi-key me-1"></i>
            ID: {producto.id_producto}
          </span>
        </div>

        <div className="mt-auto pt-3 border-top d-flex">
          <button
            className="btn btn-sm btn-outline-primary flex-grow-1 me-1"
            onClick={() => onEdit(producto)}
          >
            <i className="bi bi-pencil me-1"></i>
            Editar
          </button>
          <button
            className="btn btn-sm btn-outline-danger flex-grow-1"
            onClick={() => {
              if (window.confirm('¿Estás seguro de eliminar este producto?')) {
                onDelete(producto.id_producto);
              }
            }}
          >
            <i className="bi bi-trash me-1"></i>
            Eliminar
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminProductCard; 