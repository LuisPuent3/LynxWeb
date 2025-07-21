import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AdminProductList from '../components/products/AdminProductList';
import api from '../utils/api';
import { Producto } from '../types/types';
import ImageUploader from '../components/products/ImageUploader';
import SimpleImageUploader from '../components/products/SimpleImageUploader';
import SinonimosManager from '../components/admin/SinonimosManager';

interface FormData {
  id_producto: number;
  nombre: string;
  precio: string | number;
  cantidad: number;
  id_categoria: number;
  imagen: string;
}

const AdminProductsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSinonimosManager, setShowSinonimosManager] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    id_producto: 0,
    nombre: '',
    precio: '',
    cantidad: 0,
    id_categoria: 1,
    imagen: 'default.jpg'
  });
  
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // Manejadores de formulario
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'precio' || name === 'cantidad' || name === 'id_categoria' 
        ? Number(value) 
        : value
    });
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      if (isEditing) {
        // Actualizar producto existente
        await api.put(`/productos/${formData.id_producto}`, formData);
        alert('Producto actualizado con éxito');
      } else {
        // Crear nuevo producto
        await api.post('/productos', formData);
        alert('Producto creado con éxito');
      }
      
      // Resetear formulario y actualizar lista
      setFormData({
        id_producto: 0,
        nombre: '',
        precio: '',
        cantidad: 0,
        id_categoria: 1,
        imagen: 'default.jpg'
      });
      setShowForm(false);
      setIsEditing(false);
      setRefreshTrigger(prev => prev + 1);
    } catch (err: any) {
      console.error('Error al guardar producto:', err);
      setError(err.response?.data?.mensaje || 'Error al guardar el producto');
    } finally {
      setLoading(false);
    }
  };
  
  const handleEdit = (producto: Producto) => {
    setFormData({
      id_producto: producto.id_producto,
      nombre: producto.nombre,
      precio: producto.precio,
      cantidad: producto.cantidad,
      id_categoria: producto.id_categoria,
      imagen: producto.imagen || 'default.jpg'
    });
    setIsEditing(true);
    setShowForm(true);
    window.scrollTo(0, 0);
  };
  
  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Estás seguro de eliminar este producto?')) {
      return;
    }
    
    try {
      setLoading(true);
      await api.delete(`/productos/${id}`);
      alert('Producto eliminado con éxito');
      setRefreshTrigger(prev => prev + 1);
    } catch (err: any) {
      console.error('Error al eliminar producto:', err);
      alert(err.response?.data?.mensaje || 'Error al eliminar el producto');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="admin-products-page bg-light min-vh-100">
      {/* Barra superior administrativa */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
        <div className="container-fluid">
          <a className="navbar-brand" href="#">
            <i className="bi bi-shop me-2"></i>
            LynxShop Admin
          </a>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#adminNavbar">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="adminNavbar">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <li className="nav-item">
                <a 
                  className="nav-link" 
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    navigate('/admin/dashboard');
                  }}
                >
                  Dashboard
                </a>
              </li>
              <li className="nav-item">
                <a 
                  className="nav-link active" 
                  href="#"
                >
                  Productos
                </a>
              </li>
              <li className="nav-item">
                <a 
                  className="nav-link" 
                  href="#"
                >
                  Pedidos
                </a>
              </li>
            </ul>
            <div className="d-flex">
              <button className="btn btn-outline-light me-2" onClick={() => navigate('/')}>
                <i className="bi bi-shop me-1"></i>
                Ir a Tienda
              </button>
              <div className="dropdown">
                <button className="btn btn-primary dropdown-toggle" type="button" id="userDropdown" data-bs-toggle="dropdown">
                  <i className="bi bi-person-circle me-1"></i>
                  {user?.nombre?.split(' ')[0] || 'Admin'}
                </button>
                <ul className="dropdown-menu dropdown-menu-end">
                  <li><a className="dropdown-item" href="#"><i className="bi bi-person me-2"></i>Perfil</a></li>
                  <li><a className="dropdown-item" href="#"><i className="bi bi-gear me-2"></i>Configuración</a></li>
                  <li><hr className="dropdown-divider" /></li>
                  <li><a className="dropdown-item" href="#"><i className="bi bi-box-arrow-right me-2"></i>Cerrar sesión</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </nav>
      
      {/* Contenido principal */}
      <div className="container py-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1 className="h3 mb-0">Gestión de Productos</h1>
          <button 
            className="btn btn-primary"
            onClick={() => {
              setFormData({
                id_producto: 0,
                nombre: '',
                precio: '',
                cantidad: 0,
                id_categoria: 1,
                imagen: 'default.jpg'
              });
              setIsEditing(false);
              setShowForm(!showForm);
            }}
          >
            {showForm ? (
              <>
                <i className="bi bi-x-lg me-1"></i>
                Cancelar
              </>
            ) : (
              <>
                <i className="bi bi-plus-lg me-1"></i>
                Nuevo Producto
              </>
            )}
          </button>
        </div>
        
        {/* Formulario de producto */}
        {showForm && (
          <div className="card mb-4 shadow-sm">
            <div className="card-header bg-white py-3">
              <h5 className="mb-0">{isEditing ? 'Editar Producto' : 'Nuevo Producto'}</h5>
            </div>
            <div className="card-body">
              {error && (
                <div className="alert alert-danger">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  {error}
                </div>
              )}
              
              <form onSubmit={handleSubmit}>
                <div className="row g-3">
                  <div className="col-md-6">
                    <label className="form-label">Nombre del Producto</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      name="nombre" 
                      value={formData.nombre}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  
                  <div className="col-md-3">
                    <label className="form-label">Precio ($)</label>
                    <input 
                      type="number" 
                      className="form-control" 
                      name="precio" 
                      value={formData.precio}
                      onChange={handleInputChange}
                      min="0"
                      step="0.01"
                      required
                    />
                  </div>
                  
                  <div className="col-md-3">
                    <label className="form-label">Cantidad en Stock</label>
                    <input 
                      type="number" 
                      className="form-control" 
                      name="cantidad" 
                      value={formData.cantidad}
                      onChange={handleInputChange}
                      min="0"
                      required
                    />
                  </div>
                  
                  <div className="col-md-6">
                    <label className="form-label">Categoría</label>
                    <select 
                      className="form-select" 
                      name="id_categoria"
                      value={formData.id_categoria}
                      onChange={handleInputChange}
                      required
                    >
                      <option value={1}>Bebidas</option>
                      <option value={2}>Snacks</option>
                      <option value={3}>Abarrotes</option>
                      <option value={4}>Frutas</option>
                      <option value={5}>Verduras</option>
                    </select>
                  </div>
                  
                  <div className="col-md-6">
                    <label className="form-label">Imagen del producto</label>
                    <div className="bg-light p-3 rounded">
                      <SimpleImageUploader
                        initialFilename={formData.imagen}
                        onImageSelected={(filename) => {
                          setFormData({
                            ...formData,
                            imagen: filename
                          });
                        }}
                      />
                    </div>
                  </div>
                  
                  {/* Sección de Gestión de Sinónimos - Solo para productos existentes */}
                  {isEditing && formData.id_producto > 0 && (
                    <div className="col-12 mt-3">
                      <div className="border-top pt-3">
                        <h6 className="text-muted mb-3">
                          <i className="bi bi-tags me-2"></i>
                          Gestión de Sinónimos
                        </h6>
                        <p className="text-muted small mb-3">
                          Los sinónimos ayudan a los usuarios a encontrar este producto más fácilmente.
                        </p>
                        <button 
                          type="button" 
                          className="btn btn-outline-info w-100"
                          onClick={() => setShowSinonimosManager(true)}
                        >
                          <i className="bi bi-tags me-2"></i>
                          Gestionar Sinónimos del Producto
                        </button>
                      </div>
                    </div>
                  )}
                  
                  <div className="col-12 mt-4">
                    <button 
                      type="submit" 
                      className="btn btn-primary"
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Guardando...
                        </>
                      ) : isEditing ? (
                        'Actualizar Producto'
                      ) : (
                        'Crear Producto'
                      )}
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-outline-secondary ms-2"
                      onClick={() => setShowForm(false)}
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        )}
        
        {/* Buscador */}
        <div className="card mb-4 shadow-sm">
          <div className="card-body">
            <div className="input-group">
              <span className="input-group-text bg-white border-end-0">
                <i className="bi bi-search text-muted"></i>
              </span>
              <input 
                type="text" 
                className="form-control border-start-0" 
                placeholder="Buscar productos por nombre..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              {searchTerm && (
                <button 
                  className="btn btn-outline-secondary border-start-0" 
                  type="button"
                  onClick={() => setSearchTerm('')}
                >
                  <i className="bi bi-x"></i>
                </button>
              )}
            </div>
          </div>
        </div>
        
        {/* Lista de productos */}
        <AdminProductList 
          onEdit={handleEdit}
          onDelete={handleDelete}
          searchTerm={searchTerm}
          refreshTrigger={refreshTrigger}
        />
        
        {/* Modal de Gestión de Sinónimos */}
        {showSinonimosManager && (
          <div className="modal fade show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
            <div className="modal-dialog modal-lg modal-dialog-scrollable">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">
                    <i className="bi bi-tags me-2"></i>
                    Gestión de Sinónimos
                  </h5>
                  <button 
                    type="button" 
                    className="btn-close" 
                    onClick={() => setShowSinonimosManager(false)}
                  ></button>
                </div>
                <div className="modal-body p-0">
                  <SinonimosManager
                    productoId={formData.id_producto}
                    productoNombre={formData.nombre}
                    visible={showSinonimosManager}
                    onClose={() => setShowSinonimosManager(false)}
                    apiBaseUrl="/api/admin/sinonimos"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminProductsPage; 