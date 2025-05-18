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

interface User {
  id_usuario: number;
  nombre: string;
  correo: string;
  telefono: string;
  rol: string;
  fecha_registro: string;
}

const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [productos, setProductos] = useState<Producto[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [usuarios, setUsuarios] = useState<User[]>([]);
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
  
  // Estado para el formulario de categorías
  const [categoriaForm, setCategoriaForm] = useState<Categoria>({
    id_categoria: 0,
    nombre: '',
    descripcion: ''
  });
  
  // Estado para edición
  const [isEditing, setIsEditing] = useState(false);
  const [isEditingCategoria, setIsEditingCategoria] = useState(false);
  
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
        
        // Cargar usuarios
        try {
          const usuariosRes = await api.get('/auth/users');
          setUsuarios(usuariosRes.data);
        } catch (userErr) {
          console.error("Error al cargar usuarios:", userErr);
          // No impedir la carga del resto de datos si falla usuarios
        }
        
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

  // Manejadores para el CRUD de categorías
  const handleCategoriaInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setCategoriaForm(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleCategoriaSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isEditingCategoria) {
        // Actualizar categoría
        await api.put(`/categorias/${categoriaForm.id_categoria}`, categoriaForm);
        // Actualizar la lista de categorías
        setCategorias(categorias.map(c => 
          c.id_categoria === categoriaForm.id_categoria ? {...categoriaForm} : c
        ));
      } else {
        // Crear nueva categoría
        const response = await api.post('/categorias', categoriaForm);
        setCategorias([...categorias, response.data]);
      }
      
      // Resetear formulario
      setCategoriaForm({
        id_categoria: 0,
        nombre: '',
        descripcion: ''
      });
      setIsEditingCategoria(false);
    } catch (err) {
      console.error('Error al guardar categoría:', err);
      setError('Error al guardar la categoría. Por favor, intenta de nuevo.');
    }
  };
  
  const handleEditCategoria = (categoria: Categoria) => {
    setCategoriaForm({
      id_categoria: categoria.id_categoria,
      nombre: categoria.nombre,
      descripcion: categoria.descripcion
    });
    setIsEditingCategoria(true);
    setActiveTab('categories-form');
  };
  
  const handleDeleteCategoria = async (id: number) => {
    // Verificar si hay productos usando esta categoría
    const productos_en_categoria = productos.filter(p => p.id_categoria === id);
    
    if (productos_en_categoria.length > 0) {
      setError(`No se puede eliminar la categoría porque hay ${productos_en_categoria.length} productos asociados a ella.`);
      return;
    }
    
    if (window.confirm('¿Estás seguro de eliminar esta categoría?')) {
      try {
        await api.delete(`/categorias/${id}`);
        setCategorias(categorias.filter(c => c.id_categoria !== id));
      } catch (err) {
        console.error('Error al eliminar categoría:', err);
        setError('Error al eliminar la categoría. Por favor, intenta de nuevo.');
      }
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
              <li className="nav-item">
                <a 
                  className={`nav-link ${activeTab === 'users' ? 'active' : ''}`} 
                  href="#" 
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveTab('users');
                  }}
                >
                  Clientes
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
            {activeTab === 'dashboard' && (
              <>
                <div className="row mb-4">
                  <div className="col-md-3">
                    <div className="card border-0 shadow-sm h-100">
                      <div className="card-body">
                        <div className="d-flex align-items-center mb-3">
                          <div className="icon-circle bg-primary bg-opacity-10 text-primary me-3">
                            <i className="bi bi-cart-check fs-4"></i>
                          </div>
                          <h6 className="card-title mb-0">Pedidos Totales</h6>
                        </div>
                        <h2 className="display-6 fw-bold text-primary mb-0">{pedidos.length}</h2>
                        <p className="text-muted small mt-2">
                          <i className="bi bi-arrow-up-short"></i> Desde el inicio
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="card border-0 shadow-sm h-100">
                      <div className="card-body">
                        <div className="d-flex align-items-center mb-3">
                          <div className="icon-circle bg-success bg-opacity-10 text-success me-3">
                            <i className="bi bi-box-seam fs-4"></i>
                          </div>
                          <h6 className="card-title mb-0">Productos</h6>
                        </div>
                        <h2 className="display-6 fw-bold text-success mb-0">{productos.length}</h2>
                        <p className="text-muted small mt-2">
                          En {categorias.length} categorías
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="card border-0 shadow-sm h-100">
                      <div className="card-body">
                        <div className="d-flex align-items-center mb-3">
                          <div className="icon-circle bg-warning bg-opacity-10 text-warning me-3">
                            <i className="bi bi-people fs-4"></i>
                          </div>
                          <h6 className="card-title mb-0">Clientes</h6>
                        </div>
                        <h2 className="display-6 fw-bold text-warning mb-0">{usuarios.filter(u => u.rol === 'Cliente').length}</h2>
                        <p className="text-muted small mt-2">
                          {usuarios.filter(u => u.rol === 'Invitado').length} invitados
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="card border-0 shadow-sm h-100">
                      <div className="card-body">
                        <div className="d-flex align-items-center mb-3">
                          <div className="icon-circle bg-info bg-opacity-10 text-info me-3">
                            <i className="bi bi-hourglass-split fs-4"></i>
                          </div>
                          <h6 className="card-title mb-0">Pendientes</h6>
                        </div>
                        <h2 className="display-6 fw-bold text-info mb-0">
                          {pedidos.filter(p => p.estado === 'pendiente').length}
                        </h2>
                        <p className="text-muted small mt-2">
                          Por entregar
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="row">
                  <div className="col-md-8 mb-4">
                    <div className="card border-0 shadow-sm">
                      <div className="card-header bg-white py-3">
                        <h5 className="card-title mb-0">Últimos Pedidos</h5>
                      </div>
                      <div className="card-body p-0">
                        <div className="table-responsive">
                          <table className="table mb-0">
                            <thead className="table-light">
                              <tr>
                                <th>ID</th>
                                <th>Cliente</th>
                                <th>Fecha</th>
                                <th>Estado</th>
                                <th>Total</th>
                              </tr>
                            </thead>
                            <tbody>
                              {pedidos.slice(0, 5).map((pedido) => (
                                <tr key={pedido.id_pedido}>
                                  <td>#{pedido.id_pedido}</td>
                                  <td>{pedido.usuario || pedido.nombre_completo || 'Usuario'}</td>
                                  <td>{new Date(pedido.fecha).toLocaleDateString()}</td>
                                  <td>
                                    <span className={`badge ${
                                      pedido.estado === 'pendiente' ? 'bg-warning' :
                                      pedido.estado === 'entregado' ? 'bg-success' :
                                      pedido.estado === 'cancelado' ? 'bg-danger' : 'bg-secondary'
                                    }`}>
                                      {pedido.estado_nombre || pedido.estado}
                                    </span>
                                  </td>
                                  <td>${pedido.total || '(calculando)'}</td>
                                </tr>
                              ))}
                              {pedidos.length === 0 && (
                                <tr>
                                  <td colSpan={5} className="text-center py-3">No hay pedidos disponibles</td>
                                </tr>
                              )}
                            </tbody>
                          </table>
                        </div>
                      </div>
                      <div className="card-footer bg-white text-end border-0 pt-0">
                        <button 
                          className="btn btn-sm btn-link text-decoration-none"
                          onClick={() => setActiveTab('orders')}
                        >
                          Ver todos los pedidos
                          <i className="bi bi-arrow-right ms-1"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  <div className="col-md-4 mb-4">
                    <div className="card border-0 shadow-sm h-100">
                      <div className="card-header bg-white py-3">
                        <h5 className="card-title mb-0">Productos con Bajo Stock</h5>
                      </div>
                      <div className="card-body">
                        {productos.filter(p => p.cantidad < 10).length === 0 ? (
                          <div className="text-center py-4">
                            <i className="bi bi-check-circle-fill text-success display-4"></i>
                            <p className="text-muted mt-2">Todos los productos tienen stock suficiente</p>
                          </div>
                        ) : (
                          <ul className="list-group list-group-flush">
                            {productos
                              .filter(p => p.cantidad < 10)
                              .sort((a, b) => a.cantidad - b.cantidad)
                              .slice(0, 5)
                              .map(producto => (
                                <li key={producto.id_producto} className="list-group-item px-0 py-3 d-flex justify-content-between align-items-center">
                                  <div>
                                    <h6 className="mb-0">{producto.nombre}</h6>
                                    <p className="text-muted small mb-0">
                                      {categorias.find(c => c.id_categoria === producto.id_categoria)?.nombre || 'Sin categoría'}
                                    </p>
                                  </div>
                                  <span className={`badge bg-${producto.cantidad <= 5 ? 'danger' : 'warning'}`}>
                                    {producto.cantidad} unidades
                                  </span>
                                </li>
                              ))}
                          </ul>
                        )}
                      </div>
                      <div className="card-footer bg-white text-end border-0">
                        <button 
                          className="btn btn-sm btn-link text-decoration-none"
                          onClick={() => setActiveTab('products')}
                        >
                          Ver todos los productos
                          <i className="bi bi-arrow-right ms-1"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}
            
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
              <div className="card shadow-sm">
                <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                  <h5 className="card-title mb-0">Gestión de Categorías</h5>
                  <button 
                    className="btn btn-sm btn-primary" 
                    onClick={() => {
                      setCategoriaForm({
                        id_categoria: 0,
                        nombre: '',
                        descripcion: ''
                      });
                      setIsEditingCategoria(false);
                      setActiveTab('categories-form');
                    }}
                  >
                    <i className="bi bi-plus-circle me-1"></i>
                    Nueva Categoría
                  </button>
                </div>
                <div className="card-body">
                  {categorias.length === 0 ? (
                    <div className="text-center py-4">
                      <i className="bi bi-tags display-4 text-muted"></i>
                      <p className="text-muted mt-2">No hay categorías registradas</p>
                    </div>
                  ) : (
                    <div className="table-responsive">
                      <table className="table table-hover align-middle">
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
                          {categorias.map((categoria) => {
                            const productosEnCategoria = productos.filter(p => p.id_categoria === categoria.id_categoria).length;
                            return (
                              <tr key={categoria.id_categoria}>
                                <td>{categoria.id_categoria}</td>
                                <td>{categoria.nombre}</td>
                                <td>{categoria.descripcion || '-'}</td>
                                <td>
                                  <span className="badge bg-info">{productosEnCategoria}</span>
                                </td>
                                <td>
                                  <div className="btn-group">
                                    <button 
                                      className="btn btn-sm btn-outline-primary"
                                      onClick={() => handleEditCategoria(categoria)}
                                    >
                                      <i className="bi bi-pencil me-1"></i>
                                      Editar
                                    </button>
                                    <button 
                                      className="btn btn-sm btn-outline-danger"
                                      onClick={() => handleDeleteCategoria(categoria.id_categoria)}
                                      disabled={productosEnCategoria > 0}
                                    >
                                      <i className="bi bi-trash me-1"></i>
                                      Eliminar
                                    </button>
                                  </div>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* Formulario de Categoría */}
            {activeTab === 'categories-form' && (
              <div className="card shadow-sm">
                <div className="card-header bg-white py-3">
                  <h5 className="card-title mb-0">
                    {isEditingCategoria ? 'Editar Categoría' : 'Nueva Categoría'}
                  </h5>
                </div>
                <div className="card-body">
                  <form onSubmit={handleCategoriaSubmit}>
                    <div className="mb-3">
                      <label htmlFor="nombre" className="form-label">Nombre de la Categoría</label>
                      <input
                        type="text"
                        className="form-control"
                        id="nombre"
                        name="nombre"
                        value={categoriaForm.nombre}
                        onChange={handleCategoriaInputChange}
                        required
                      />
                    </div>
                    <div className="mb-3">
                      <label htmlFor="descripcion" className="form-label">Descripción</label>
                      <textarea
                        className="form-control"
                        id="descripcion"
                        name="descripcion"
                        rows={3}
                        value={categoriaForm.descripcion}
                        onChange={handleCategoriaInputChange}
                      ></textarea>
                    </div>
                    <div className="d-flex gap-2">
                      <button type="submit" className="btn btn-primary">
                        {isEditingCategoria ? 'Actualizar' : 'Guardar'}
                      </button>
                      <button 
                        type="button" 
                        className="btn btn-outline-secondary"
                        onClick={() => setActiveTab('categories')}
                      >
                        Cancelar
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}
            
            {/* Pedidos */}
            {activeTab === 'orders' && (
              <div className="card shadow-sm">
                <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                  <h5 className="card-title mb-0">Gestión de Pedidos</h5>
                  <div>
                    <select className="form-select form-select-sm" onChange={(e) => {
                      const filtro = e.target.value;
                      // Filtro por estado
                    }}>
                      <option value="todos">Todos los estados</option>
                      <option value="pendiente">Pendiente</option>
                      <option value="entregado">Entregado</option>
                      <option value="cancelado">Cancelado</option>
                    </select>
                  </div>
                </div>
                <div className="card-body">
                  {pedidos.length === 0 ? (
                    <div className="text-center py-4">
                      <i className="bi bi-inbox display-4 text-muted"></i>
                      <p className="text-muted mt-2">No hay pedidos registrados</p>
                    </div>
                  ) : (
                    <div className="table-responsive">
                      <table className="table table-hover align-middle">
                        <thead className="table-light">
                          <tr>
                            <th>ID</th>
                            <th>Cliente</th>
                            <th>Fecha</th>
                            <th>Estado</th>
                            <th>Total</th>
                            <th>Acciones</th>
                          </tr>
                        </thead>
                        <tbody>
                          {pedidos.map((pedido) => (
                            <tr key={pedido.id_pedido}>
                              <td>#{pedido.id_pedido}</td>
                              <td>{pedido.usuario || pedido.nombre_completo || 'Usuario'}</td>
                              <td>{new Date(pedido.fecha).toLocaleDateString()}</td>
                              <td>
                                <span className={`badge ${
                                  pedido.estado === 'pendiente' ? 'bg-warning' :
                                  pedido.estado === 'entregado' ? 'bg-success' :
                                  pedido.estado === 'cancelado' ? 'bg-danger' : 'bg-secondary'
                                }`}>
                                  {pedido.estado_nombre || pedido.estado}
                                </span>
                              </td>
                              <td>${pedido.total || '(calculando)'}</td>
                              <td>
                                <div className="btn-group">
                                  <button 
                                    className="btn btn-sm btn-outline-primary" 
                                    data-bs-toggle="modal" 
                                    data-bs-target={`#detallesPedido${pedido.id_pedido}`}
                                  >
                                    <i className="bi bi-eye me-1"></i>
                                    Ver
                                  </button>
                                  <button 
                                    className="btn btn-sm btn-outline-success"
                                    onClick={() => handleOrderStatus(pedido.id_pedido, 'entregado')}
                                    disabled={pedido.estado === 'entregado' || pedido.estado === 'cancelado'}
                                  >
                                    <i className="bi bi-check-circle me-1"></i>
                                    Entregar
                                  </button>
                                  <button 
                                    className="btn btn-sm btn-outline-danger"
                                    onClick={() => handleOrderStatus(pedido.id_pedido, 'cancelado')}
                                    disabled={pedido.estado === 'entregado' || pedido.estado === 'cancelado'}
                                  >
                                    <i className="bi bi-x-circle me-1"></i>
                                    Cancelar
                                  </button>
                                </div>
                                
                                {/* Modal para detalles del pedido */}
                                <div className="modal fade" id={`detallesPedido${pedido.id_pedido}`} tabIndex={-1} aria-hidden="true">
                                  <div className="modal-dialog modal-lg">
                                    <div className="modal-content">
                                      <div className="modal-header">
                                        <h5 className="modal-title">Detalles del Pedido #{pedido.id_pedido}</h5>
                                        <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                      </div>
                                      <div className="modal-body">
                                        <div className="row mb-3">
                                          <div className="col-md-6">
                                            <p><strong>Cliente:</strong> {pedido.usuario || pedido.nombre_completo || 'Usuario'}</p>
                                            <p><strong>Fecha:</strong> {new Date(pedido.fecha).toLocaleString()}</p>
                                            <p><strong>Método de Pago:</strong> {pedido.metodo_pago || 'Efectivo'}</p>
                                          </div>
                                          <div className="col-md-6">
                                            <p><strong>Estado:</strong> {pedido.estado_nombre || pedido.estado}</p>
                                            <p><strong>Teléfono:</strong> {pedido.telefono_contacto || 'No proporcionado'}</p>
                                            <p><strong>Información adicional:</strong> {pedido.informacion_adicional || 'N/A'}</p>
                                          </div>
                                        </div>
                                        
                                        <h6 className="border-bottom pb-2 mb-3">Productos</h6>
                                        <div className="table-responsive">
                                          <table className="table table-sm">
                                            <thead className="table-light">
                                              <tr>
                                                <th>Producto</th>
                                                <th>Cantidad</th>
                                                <th>Precio</th>
                                                <th>Subtotal</th>
                                              </tr>
                                            </thead>
                                            <tbody>
                                              {pedido.productos ? (
                                                pedido.productos.map((producto, index) => (
                                                  <tr key={index}>
                                                    <td>{producto.nombre}</td>
                                                    <td>{producto.cantidad}</td>
                                                    <td>${producto.precio}</td>
                                                    <td>${(producto.cantidad * producto.precio).toFixed(2)}</td>
                                                  </tr>
                                                ))
                                              ) : (
                                                <tr>
                                                  <td colSpan={4} className="text-center">
                                                    Detalles no disponibles
                                                  </td>
                                                </tr>
                                              )}
                                            </tbody>
                                            <tfoot className="table-light">
                                              <tr>
                                                <th colSpan={3} className="text-end">Total:</th>
                                                <th>${pedido.total || '(calculando)'}</th>
                                              </tr>
                                            </tfoot>
                                          </table>
                                        </div>
                                      </div>
                                      <div className="modal-footer">
                                        <button type="button" className="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                                        {pedido.estado === 'pendiente' && (
                                          <>
                                            <button 
                                              className="btn btn-success"
                                              onClick={() => {
                                                handleOrderStatus(pedido.id_pedido, 'entregado');
                                                document.getElementById(`detallesPedido${pedido.id_pedido}`)?.classList.remove('show');
                                                document.body.classList.remove('modal-open');
                                                document.querySelector('.modal-backdrop')?.remove();
                                              }}
                                            >
                                              <i className="bi bi-check-circle me-1"></i>
                                              Marcar como Entregado
                                            </button>
                                            <button 
                                              className="btn btn-danger"
                                              onClick={() => {
                                                handleOrderStatus(pedido.id_pedido, 'cancelado');
                                                document.getElementById(`detallesPedido${pedido.id_pedido}`)?.classList.remove('show');
                                                document.body.classList.remove('modal-open');
                                                document.querySelector('.modal-backdrop')?.remove();
                                              }}
                                            >
                                              <i className="bi bi-x-circle me-1"></i>
                                              Cancelar Pedido
                                            </button>
                                          </>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* Usuarios/Clientes */}
            {activeTab === 'users' && (
              <div className="card shadow-sm">
                <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                  <h5 className="card-title mb-0">Gestión de Clientes</h5>
                  <div>
                    <select className="form-select form-select-sm" onChange={(e) => {
                      // Filtrar por rol
                    }}>
                      <option value="todos">Todos los roles</option>
                      <option value="Cliente">Clientes</option>
                      <option value="Administrador">Administradores</option>
                      <option value="Invitado">Invitados</option>
                    </select>
                  </div>
                </div>
                <div className="card-body">
                  {usuarios.length === 0 ? (
                    <div className="text-center py-4">
                      <i className="bi bi-people display-4 text-muted"></i>
                      <p className="text-muted mt-2">No hay usuarios registrados</p>
                    </div>
                  ) : (
                    <div className="table-responsive">
                      <table className="table table-hover align-middle">
                        <thead className="table-light">
                          <tr>
                            <th>ID</th>
                            <th>Nombre</th>
                            <th>Correo</th>
                            <th>Teléfono</th>
                            <th>Rol</th>
                            <th>Registro</th>
                            <th>Pedidos</th>
                            <th>Acciones</th>
                          </tr>
                        </thead>
                        <tbody>
                          {usuarios.map((usuario) => {
                            const pedidosUsuario = pedidos.filter(p => p.id_usuario === usuario.id_usuario).length;
                            return (
                              <tr key={usuario.id_usuario}>
                                <td>{usuario.id_usuario}</td>
                                <td>{usuario.nombre || 'Sin nombre'}</td>
                                <td>{usuario.correo}</td>
                                <td>{usuario.telefono || 'No registrado'}</td>
                                <td>
                                  <span className={`badge ${
                                    usuario.rol === 'Administrador' ? 'bg-primary' :
                                    usuario.rol === 'Cliente' ? 'bg-success' :
                                    'bg-secondary'
                                  }`}>
                                    {usuario.rol}
                                  </span>
                                </td>
                                <td>{new Date(usuario.fecha_registro).toLocaleDateString()}</td>
                                <td>
                                  <span className="badge bg-info">{pedidosUsuario}</span>
                                </td>
                                <td>
                                  <div className="btn-group">
                                    <button 
                                      className="btn btn-sm btn-outline-primary"
                                      onClick={() => {
                                        // Ver historial de pedidos del usuario
                                        // Esta funcionalidad se puede implementar más adelante
                                      }}
                                    >
                                      <i className="bi bi-bag me-1"></i>
                                      Pedidos
                                    </button>
                                    <button 
                                      className="btn btn-sm btn-outline-secondary"
                                      data-bs-toggle="modal"
                                      data-bs-target={`#detalleUsuario${usuario.id_usuario}`}
                                    >
                                      <i className="bi bi-eye me-1"></i>
                                      Ver
                                    </button>
                                  </div>
                                  
                                  {/* Modal para detalles del usuario */}
                                  <div className="modal fade" id={`detalleUsuario${usuario.id_usuario}`} tabIndex={-1} aria-hidden="true">
                                    <div className="modal-dialog">
                                      <div className="modal-content">
                                        <div className="modal-header">
                                          <h5 className="modal-title">Detalles del Cliente</h5>
                                          <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                        </div>
                                        <div className="modal-body">
                                          <div className="mb-3 text-center">
                                            <div className="avatar mb-3">
                                              <div className="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" style={{width: '80px', height: '80px', fontSize: '2rem'}}>
                                                {usuario.nombre ? usuario.nombre.charAt(0).toUpperCase() : 'U'}
                                              </div>
                                            </div>
                                            <h4>{usuario.nombre || 'Usuario sin nombre'}</h4>
                                            <p className="text-muted">{usuario.correo}</p>
                                            <span className={`badge ${
                                              usuario.rol === 'Administrador' ? 'bg-primary' :
                                              usuario.rol === 'Cliente' ? 'bg-success' :
                                              'bg-secondary'
                                            }`}>
                                              {usuario.rol}
                                            </span>
                                          </div>
                                          
                                          <hr/>
                                          
                                          <div className="mb-3">
                                            <h6 className="fw-bold">Información de contacto</h6>
                                            <p><strong>Teléfono:</strong> {usuario.telefono || 'No registrado'}</p>
                                            <p><strong>Correo:</strong> {usuario.correo}</p>
                                          </div>
                                          
                                          <div className="mb-3">
                                            <h6 className="fw-bold">Información de cuenta</h6>
                                            <p><strong>ID:</strong> {usuario.id_usuario}</p>
                                            <p><strong>Fecha de registro:</strong> {new Date(usuario.fecha_registro).toLocaleString()}</p>
                                            <p><strong>Total pedidos:</strong> {pedidosUsuario}</p>
                                          </div>
                                        </div>
                                        <div className="modal-footer">
                                          <button type="button" className="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                                          <button 
                                            type="button" 
                                            className="btn btn-primary"
                                            onClick={() => {
                                              // Ir al historial de pedidos del usuario
                                              // Esta funcionalidad se puede implementar más adelante
                                            }}
                                          >
                                            <i className="bi bi-bag me-1"></i>
                                            Ver Pedidos
                                          </button>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
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
