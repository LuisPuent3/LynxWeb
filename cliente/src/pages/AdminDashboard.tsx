import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import Dashboard from '../components/admin/Dashboard';

interface Producto {
  id_producto: number;
  nombre: string;
  precio: string | number;
  cantidad: number;
  id_categoria: number;
  imagen: string;
}

interface Categoria {
  id_categoria: number;
  nombre: string;
  descripcion: string;
}

interface Pedido {
  id_pedido: number;
  id_usuario: number;
  fecha: string;
  estado: string;
  total?: number;
  nombre_cliente?: string;
}

const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [productos, setProductos] = useState<Producto[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Estado para el formulario de producto
  const [formData, setFormData] = useState<Producto>({
    id_producto: 0,
    nombre: '',
    precio: '',
    cantidad: 0,
    id_categoria: 1,
    imagen: 'default.jpg'
  });
  
  // Estado para edición
  const [isEditing, setIsEditing] = useState(false);
  
  const { user } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Cargar productos
        const productosRes = await api.get('/productos');
        setProductos(productosRes.data);
        
        // Cargar categorías
        const categoriasRes = await api.get('/categorias');
        setCategorias(categoriasRes.data);
        
        // Cargar pedidos
        const pedidosRes = await api.get('/pedidos');
        setPedidos(pedidosRes.data);
        
        setLoading(false);
      } catch (err) {
        console.error('Error al cargar datos:', err);
        setError('Error al cargar los datos. Por favor, intenta de nuevo.');
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  // Manejadores para el CRUD de productos
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'precio' || name === 'cantidad' || name === 'id_categoria' 
        ? Number(value) 
        : value
    }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isEditing) {
        // Actualizar producto
        await api.put(`/productos/${formData.id_producto}`, formData);
        // Actualizar la lista de productos
        setProductos(productos.map(p => 
          p.id_producto === formData.id_producto ? {...formData} : p
        ));
      } else {
        // Crear nuevo producto
        const response = await api.post('/productos', formData);
        setProductos([...productos, response.data]);
      }
      
      // Resetear formulario
      setFormData({
        id_producto: 0,
        nombre: '',
        precio: '',
        cantidad: 0,
        id_categoria: 1,
        imagen: 'default.jpg'
      });
      setIsEditing(false);
    } catch (err) {
      console.error('Error al guardar producto:', err);
      setError('Error al guardar el producto. Por favor, intenta de nuevo.');
    }
  };
  
  const handleEdit = (producto: Producto) => {
    setFormData({
      id_producto: producto.id_producto,
      nombre: producto.nombre,
      precio: producto.precio,
      cantidad: producto.cantidad,
      id_categoria: producto.id_categoria,
      imagen: producto.imagen
    });
    setIsEditing(true);
    setActiveTab('products-form');
  };
  
  const handleDelete = async (id: number) => {
    if (window.confirm('¿Estás seguro de eliminar este producto?')) {
      try {
        await api.delete(`/productos/${id}`);
        setProductos(productos.filter(p => p.id_producto !== id));
      } catch (err) {
        console.error('Error al eliminar producto:', err);
        setError('Error al eliminar el producto. Por favor, intenta de nuevo.');
      }
    }
  };
  
  // Cambiar estado de pedido
  const handleOrderStatus = async (id: number, newStatus: string) => {
    try {
      await api.put(`/pedidos/${id}`, { estado: newStatus });
      setPedidos(pedidos.map(p => 
        p.id_pedido === id ? {...p, estado: newStatus} : p
      ));
    } catch (err) {
      console.error('Error al actualizar pedido:', err);
      setError('Error al actualizar el estado del pedido.');
    }
  };

  return (
    <div className="admin-dashboard">
      {/* Barra de navegación admin */}
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
                  className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`} 
                  href="#" 
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveTab('dashboard');
                  }}
                >
                  Dashboard
                </a>
              </li>
              <li className="nav-item">
                <a 
                  className={`nav-link ${activeTab === 'products' ? 'active' : ''}`} 
                  href="#" 
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveTab('products');
                  }}
                >
                  Productos
                </a>
              </li>
              <li className="nav-item">
                <a 
                  className={`nav-link ${activeTab === 'categories' ? 'active' : ''}`} 
                  href="#" 
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveTab('categories');
                  }}
                >
                  Categorías
                </a>
              </li>
              <li className="nav-item">
                <a 
                  className={`nav-link ${activeTab === 'orders' ? 'active' : ''}`} 
                  href="#" 
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveTab('orders');
                  }}
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

      <div className="container-fluid py-4">
        {loading ? (
          <div className="text-center p-5">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Cargando...</span>
            </div>
          </div>
        ) : error ? (
          <div className="alert alert-danger">{error}</div>
        ) : (
          <>
            {/* Dashboard */}
            {activeTab === 'dashboard' && <Dashboard />}
            
            {/* Productos */}
            {activeTab === 'products' && (
              <div className="card">
                <div className="card-header bg-white d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Gestión de Productos</h5>
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
                      setActiveTab('products-form');
                    }}
                  >
                    <i className="bi bi-plus-circle me-1"></i>
                    Nuevo Producto
                  </button>
                </div>
                <div className="card-body p-0">
                  <div className="table-responsive">
                    <table className="table table-hover align-middle">
                      <thead className="table-light">
                        <tr>
                          <th>ID</th>
                          <th>Producto</th>
                          <th>Precio</th>
                          <th>Stock</th>
                          <th>Categoría</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {productos.map(producto => (
                          <tr key={producto.id_producto}>
                            <td>{producto.id_producto}</td>
                            <td>
                              <div className="d-flex align-items-center">
                                <div className="me-3 bg-light rounded p-2 text-center" style={{width: "50px", height: "50px"}}>
                                  <i className="bi bi-box text-primary" style={{fontSize: "1.5rem"}}></i>
                                </div>
                                <div>
                                  <h6 className="mb-0">{producto.nombre}</h6>
                                  <small className="text-muted">SKU: PRD-{producto.id_producto}</small>
                                </div>
                              </div>
                            </td>
                            <td>${typeof producto.precio === 'string' ? parseFloat(producto.precio).toFixed(2) : producto.precio.toFixed(2)}</td>
                            <td>
                              <span className={`badge ${
                                producto.cantidad > 10 ? 'bg-success' :
                                producto.cantidad > 5 ? 'bg-warning' :
                                'bg-danger'
                              }`}>
                                {producto.cantidad}
                              </span>
                            </td>
                            <td>
                              {categorias.find(c => c.id_categoria === producto.id_categoria)?.nombre || 'Sin categoría'}
                            </td>
                            <td>
                              <div className="btn-group">
                                <button 
                                  className="btn btn-sm btn-outline-primary"
                                  onClick={() => handleEdit(producto)}
                                >
                                  <i className="bi bi-pencil"></i>
                                </button>
                                <button 
                                  className="btn btn-sm btn-outline-danger"
                                  onClick={() => handleDelete(producto.id_producto)}
                                >
                                  <i className="bi bi-trash"></i>
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
            
            {/* Formulario de productos */}
            {activeTab === 'products-form' && (
              <div className="card">
                <div className="card-header bg-white">
                  <h5 className="mb-0">{isEditing ? 'Editar Producto' : 'Nuevo Producto'}</h5>
                </div>
                <div className="card-body">
                  <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                      <label className="form-label">Nombre del producto</label>
                      <input 
                        type="text" 
                        className="form-control" 
                        name="nombre" 
                        value={formData.nombre}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                    
                    <div className="row mb-3">
                      <div className="col-md-6">
                        <label className="form-label">Precio ($)</label>
                        <input 
                          type="number" 
                          className="form-control" 
                          name="precio" 
                          value={formData.precio}
                          onChange={handleInputChange}
                          step="0.01"
                          min="0"
                          required
                        />
                      </div>
                      <div className="col-md-6">
                        <label className="form-label">Cantidad en stock</label>
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
                    </div>
                    
                    <div className="mb-3">
                      <label className="form-label">Categoría</label>
                      <select 
                        className="form-select" 
                        name="id_categoria" 
                        value={formData.id_categoria}
                        onChange={handleInputChange}
                        required
                      >
                        {categorias.map(categoria => (
                          <option key={categoria.id_categoria} value={categoria.id_categoria}>
                            {categoria.nombre}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    <div className="mb-3">
                      <label className="form-label">Imagen</label>
                      <input 
                        type="text" 
                        className="form-control" 
                        name="imagen" 
                        value={formData.imagen}
                        onChange={handleInputChange}
                        placeholder="default.jpg"
                      />
                      <small className="text-muted">
                        Nota: La carga de imágenes estará disponible próximamente.
                      </small>
                    </div>
                    
                    <div className="d-flex gap-2">
                      <button type="submit" className="btn btn-primary">
                        {isEditing ? 'Actualizar Producto' : 'Crear Producto'}
                      </button>
                      <button 
                        type="button" 
                        className="btn btn-secondary"
                        onClick={() => setActiveTab('products')}
                      >
                        Cancelar
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}
            
            {/* Categorías */}
            {activeTab === 'categories' && (
              <div className="card">
                <div className="card-header bg-white d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Gestión de Categorías</h5>
                  <button className="btn btn-primary">
                    <i className="bi bi-plus-circle me-1"></i>
                    Nueva Categoría
                  </button>
                </div>
                <div className="card-body">
                  <div className="alert alert-info">
                    <i className="bi bi-info-circle me-1"></i>
                    La gestión completa de categorías estará disponible próximamente.
                  </div>
                  <div className="table-responsive">
                    <table className="table">
                      <thead className="table-light">
                        <tr>
                          <th>ID</th>
                          <th>Nombre</th>
                          <th>Descripción</th>
                          <th>Productos</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {categorias.map(categoria => (
                          <tr key={categoria.id_categoria}>
                            <td>{categoria.id_categoria}</td>
                            <td>{categoria.nombre}</td>
                            <td>{categoria.descripcion || 'Sin descripción'}</td>
                            <td>
                              <span className="badge bg-primary rounded-pill">
                                {productos.filter(p => p.id_categoria === categoria.id_categoria).length}
                              </span>
                            </td>
                            <td>
                              <div className="btn-group">
                                <button className="btn btn-sm btn-outline-primary">
                                  <i className="bi bi-pencil"></i>
                                </button>
                                <button className="btn btn-sm btn-outline-danger">
                                  <i className="bi bi-trash"></i>
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
            
            {/* Pedidos */}
            {activeTab === 'orders' && (
              <div className="card">
                <div className="card-header bg-white">
                  <h5 className="mb-0">Gestión de Pedidos</h5>
                </div>
                <div className="card-body p-0">
                  <div className="table-responsive">
                    <table className="table">
                      <thead className="table-light">
                        <tr>
                          <th>ID</th>
                          <th>Cliente</th>
                          <th>Fecha</th>
                          <th>Total</th>
                          <th>Estado</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {pedidos.map(pedido => (
                          <tr key={pedido.id_pedido}>
                            <td>{pedido.id_pedido}</td>
                            <td>{pedido.nombre_cliente || `Cliente #${pedido.id_usuario}`}</td>
                            <td>{new Date(pedido.fecha).toLocaleDateString()}</td>
                            <td>${pedido.total ? Number(pedido.total).toFixed(2) : '0.00'}</td>
                            <td>
                              <span className={`badge ${
                                pedido.estado === 'Entregado' ? 'bg-success' :
                                pedido.estado === 'Cancelado' ? 'bg-danger' :
                                'bg-warning'
                              }`}>
                                {pedido.estado}
                              </span>
                            </td>
                            <td>
                              <div className="btn-group">
                                <button className="btn btn-sm btn-outline-primary">
                                  <i className="bi bi-eye"></i>
                                </button>
                                <button className="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                                  Estado
                                </button>
                                <ul className="dropdown-menu">
                                  <li>
                                    <a 
                                      className="dropdown-item" 
                                      href="#"
                                      onClick={(e) => {
                                        e.preventDefault();
                                        handleOrderStatus(pedido.id_pedido, 'Pendiente');
                                      }}
                                    >Pendiente</a>
                                  </li>
                                  <li>
                                    <a 
                                      className="dropdown-item" 
                                      href="#"
                                      onClick={(e) => {
                                        e.preventDefault();
                                        handleOrderStatus(pedido.id_pedido, 'Entregado');
                                      }}
                                    >Entregado</a>
                                  </li>
                                  <li>
                                    <a 
                                      className="dropdown-item" 
                                      href="#"
                                      onClick={(e) => {
                                        e.preventDefault();
                                        handleOrderStatus(pedido.id_pedido, 'Cancelado');
                                      }}
                                    >Cancelado</a>
                                  </li>
                                </ul>
                              </div>
                            </td>
                          </tr>
                        ))}
                        {pedidos.length === 0 && (
                          <tr>
                            <td colSpan={6} className="text-center py-3">No hay pedidos disponibles</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
