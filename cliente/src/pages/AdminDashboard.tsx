import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import Dashboard from '../components/admin/Dashboard';
import SimpleImageUploader from '../components/products/SimpleImageUploader';

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
  estado_nombre?: string;
  total?: number;
  nombre_completo?: string;
  nombre_cliente?: string;
  usuario?: string;
  telefono_contacto?: string;
  informacion_adicional?: string;
  metodo_pago?: string;
  productos?: Array<{
    id_producto: number;
    nombre: string;
    cantidad: number;
    precio: number | string;
    subtotal?: number;
  }>;
}

interface User {
  id_usuario: number;
  nombre: string;
  correo: string;
  telefono: string;
  rol: string;
  fecha_registro: string;
}

// Componente separado para el modal de detalles del pedido
const OrderDetailModal: React.FC<{
  selectedOrder: Pedido | null;
  isLoading: boolean;
  onClose: () => void;
  onStatusChange: (id: number, status: string) => void;
}> = ({ selectedOrder, isLoading, onClose, onStatusChange }) => {
  if (!selectedOrder) return null;

  // Definir estilo CSS para la animación del modal
  const fadeInAnimation = {
    animation: 'fadeIn 0.3s',
    WebkitAnimation: 'fadeIn 0.3s'
  };

  return (
    <>
      {/* Reglas CSS para la animación */}
      <style>
        {`
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-50px); }
            to { opacity: 1; transform: translateY(0); }
          }
          
          @-webkit-keyframes fadeIn {
            from { opacity: 0; transform: translateY(-50px); }
            to { opacity: 1; transform: translateY(0); }
          }
        `}
      </style>
      
      <div className="modal-backdrop show" style={{ 
        display: 'block', 
        zIndex: 1050, 
        backgroundColor: 'rgba(0,0,0,0.5)',
        opacity: 1,
        transition: 'opacity 0.3s ease-in-out'
      }}>
        <div className="modal show" style={{ 
          display: 'block', 
          zIndex: 1051, 
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          overflow: 'auto'
        }} id="orderDetailModal">
          <div className="modal-dialog modal-lg" style={{ 
            margin: '1.75rem auto',
            transform: 'translateY(0)',
            transition: 'transform 0.3s ease-out',
            ...fadeInAnimation
          }}>
            <div className="modal-content" style={{ 
              backgroundColor: 'white', 
              opacity: 1,
              boxShadow: '0 0.5rem 1rem rgba(0, 0, 0, 0.15)'
            }}>
              <div className="modal-header">
                <h5 className="modal-title">Detalles del Pedido #{selectedOrder.id_pedido}</h5>
                <button type="button" className="btn-close" onClick={onClose}></button>
              </div>
              <div className="modal-body" style={{ opacity: 1, backgroundColor: 'white' }}>
                {isLoading ? (
                  <div className="text-center py-5">
                    <div className="spinner-border text-primary" role="status">
                      <span className="visually-hidden">Cargando...</span>
                    </div>
                    <p className="mt-2">Cargando detalles del pedido...</p>
                  </div>
                ) : (
                  <div className="order-details-container">
                    <div className="row mb-3">
                      <div className="col-md-6">
                        <p><strong>Cliente:</strong> {selectedOrder.usuario || selectedOrder.nombre_completo || 'Usuario'}</p>
                        <p><strong>Fecha:</strong> {new Date(selectedOrder.fecha).toLocaleDateString()}</p>
                        <p><strong>Método de Pago:</strong> {selectedOrder.metodo_pago || 'Efectivo'}</p>
                      </div>
                      <div className="col-md-6">
                        <p>
                          <strong>Estado:</strong> 
                          <span className={`badge ms-2 ${
                            selectedOrder.estado === 'pendiente' ? 'bg-warning' :
                            selectedOrder.estado === 'entregado' ? 'bg-success' :
                            selectedOrder.estado === 'cancelado' ? 'bg-danger' : 'bg-secondary'
                          }`}>
                            {selectedOrder.estado_nombre || selectedOrder.estado}
                          </span>
                        </p>
                        <p><strong>Teléfono:</strong> {selectedOrder.telefono_contacto || 'No proporcionado'}</p>
                        <p><strong>Información adicional:</strong> {selectedOrder.informacion_adicional || 'N/A'}</p>
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
                          {!selectedOrder.productos ? (
                            <tr>
                              <td colSpan={4} className="text-center py-3">
                                <div className="d-flex justify-content-center align-items-center">
                                  <div className="spinner-border spinner-border-sm text-primary me-2" role="status">
                                    <span className="visually-hidden">Cargando...</span>
                                  </div>
                                  <span>Cargando detalles de productos...</span>
                                </div>
                              </td>
                            </tr>
                          ) : selectedOrder.productos.length === 0 ? (
                            <tr>
                              <td colSpan={4} className="text-center py-3">
                                No hay productos en este pedido
                              </td>
                            </tr>
                          ) : (
                            selectedOrder.productos.map((producto, index) => (
                              <tr key={index}>
                                <td>{producto.nombre}</td>
                                <td>{producto.cantidad}</td>
                                <td>${typeof producto.precio === 'number' ? producto.precio.toFixed(2) : producto.precio}</td>
                                <td>${(producto.cantidad * (typeof producto.precio === 'number' ? producto.precio : parseFloat(String(producto.precio)))).toFixed(2)}</td>
                              </tr>
                            ))
                          )}
                        </tbody>
                        <tfoot className="table-light">
                          <tr>
                            <th colSpan={3} className="text-end">Total:</th>
                            <th>${typeof selectedOrder.total === 'number' ? selectedOrder.total.toFixed(2) : selectedOrder.total || '(calculando)'}</th>
                          </tr>
                        </tfoot>
                      </table>
                    </div>
                  </div>
                )}
              </div>
              <div className="modal-footer" style={{ borderTop: '1px solid #dee2e6', backgroundColor: '#f8f9fa' }}>
                <button type="button" className="btn btn-secondary" onClick={onClose}>Cerrar</button>
                {selectedOrder.estado === 'pendiente' && !isLoading && (
                  <>
                    <button 
                      type="button"
                      className="btn btn-success"
                      onClick={() => onStatusChange(selectedOrder.id_pedido, 'entregado')}
                    >
                      <i className="bi bi-check-circle me-1"></i>
                      Marcar como Entregado
                    </button>
                    <button 
                      type="button"
                      className="btn btn-danger"
                      onClick={() => onStatusChange(selectedOrder.id_pedido, 'cancelado')}
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
      </div>
    </>
  );
};

const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [productos, setProductos] = useState<Producto[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [pedidosFiltrados, setPedidosFiltrados] = useState<Pedido[]>([]);
  const [filtroEstado, setFiltroEstado] = useState<string>('todos');
  const [loadingOrderDetails, setLoadingOrderDetails] = useState<boolean>(false);
  const [orderDetailsCache, setOrderDetailsCache] = useState<{[key: number]: boolean}>({});
  const [selectedOrder, setSelectedOrder] = useState<Pedido | null>(null);
  // Eliminada la gestión de usuarios  // const [usuarios, setUsuarios] = useState<User[]>([]);
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
  
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  // Referencia para acceder a modales desde useEffect 
  const modalRefs = useRef<{[key: number]: HTMLElement | null}>({});

  // Efecto para evitar conflictos entre React y Bootstrap en modales
  useEffect(() => {
    // Este efecto se ejecuta una vez cuando la página se carga
    const handleHideModal = (e: Event) => {
      // Evitar re-renders innecesarios que pueden causar parpadeo
      e.stopPropagation();
    };

    // Añadir el evento a cada modal cuando se inicializa
    document.querySelectorAll('.modal').forEach(modal => {
      modal.addEventListener('hidden.bs.modal', handleHideModal);
    });

    // Limpiar eventos cuando el componente se desmonte
    return () => {
      document.querySelectorAll('.modal').forEach(modal => {
        modal.removeEventListener('hidden.bs.modal', handleHideModal);
      });
    };
  }, []);

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
        console.log('Pedidos cargados:', pedidosRes.data);
        setPedidos(pedidosRes.data);
        setPedidosFiltrados(pedidosRes.data);
        
                // Eliminada la carga de usuarios
        
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
      // Determinar el id_estado basado en el newStatus
      const id_estado = 
        newStatus === 'entregado' ? 2 : 
        newStatus === 'cancelado' ? 3 : 1; // Por defecto 1 (pendiente)
      
      await api.put(`/pedidos/${id}`, { estado: newStatus, id_estado });
      
      // Actualizar el estado en la lista de pedidos
      const updatedPedidos = pedidos.map(p => 
        p.id_pedido === id ? {...p, estado: newStatus, estado_nombre: newStatus} : p
      );
      
      setPedidos(updatedPedidos);
      // También actualizar los pedidos filtrados
      setPedidosFiltrados(
        filtroEstado === 'todos'
          ? updatedPedidos
          : updatedPedidos.filter(p => p.estado === filtroEstado)
      );
      
      // Mostrar mensaje de éxito
      setError(null);
    } catch (err) {
      console.error('Error al actualizar pedido:', err);
      setError('Error al actualizar el estado del pedido.');
    }
  };

  // Función para manejar el filtro de pedidos
  const handleOrderFilter = useCallback((filtro: string) => {
    setFiltroEstado(filtro);
    if (filtro === 'todos') {
      setPedidosFiltrados(pedidos);
    } else {
      setPedidosFiltrados(pedidos.filter(p => 
        p.estado?.toLowerCase() === filtro || 
        p.estado_nombre?.toLowerCase() === filtro
      ));
    }
  }, [pedidos]);

  // Actualizar los pedidos filtrados cuando cambian los pedidos
  useEffect(() => {
    handleOrderFilter(filtroEstado);
  }, [pedidos, filtroEstado, handleOrderFilter]);

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

  // Función para cerrar el modal
  const closeDetailModal = () => {
    setSelectedOrder(null);
  };

  // Función simplificada para cargar los detalles de un pedido
  const handleViewOrderDetails = async (id: number) => {
    try {
      // Buscar el pedido en la lista
      const order = pedidos.find(p => p.id_pedido === id);
      if (!order) {
        console.error(`No se encontró el pedido con ID: ${id}`);
        setError(`No se encontró información para el pedido #${id}`);
        return;
      }
      
      console.log('Pedido seleccionado:', order);
      
      // Siempre mostrar el modal, incluso mientras se cargan los detalles
      setSelectedOrder({...order});
      
      // Si ya tenemos los productos, no es necesario cargarlos de nuevo
      if (order.productos && order.productos.length > 0) {
        console.log('El pedido ya tiene productos:', order.productos);
        return;
      }
      
      if (orderDetailsCache[id]) {
        console.log('Usando caché para el pedido:', id);
        return;
      }
      
      // Cargar los detalles completos del pedido
      console.log('Cargando detalles para el pedido:', id);
      setLoadingOrderDetails(true);
      
      try {
        // Hacer la petición al endpoint específico para detalles
        const response = await api.get(`/pedidos/detalle/${id}`);
        const orderDetails = response.data;
        console.log('Detalles recibidos del servidor:', orderDetails);
        
        if (orderDetails) {
          // Verificar si tiene productos
          if (!orderDetails.productos || orderDetails.productos.length === 0) {
            console.warn('El pedido no tiene productos en la respuesta de la API');
            setError('Este pedido no tiene productos asociados.');
          } else {
            console.log('Productos recibidos:', orderDetails.productos);
          }
          
          // Crear una nueva copia del objeto completo combinando datos
          const completeOrderDetails = {
            ...order,
            ...orderDetails,
            productos: orderDetails.productos || []
          };
          
          // Actualizar el pedido en la lista
          const updatedPedidos = pedidos.map(p => 
            p.id_pedido === id ? completeOrderDetails : p
          );
          
          setPedidos(updatedPedidos);
          setPedidosFiltrados(
            filtroEstado === 'todos'
              ? updatedPedidos
              : updatedPedidos.filter(p => 
                  p.estado?.toLowerCase() === filtroEstado || 
                  p.estado_nombre?.toLowerCase() === filtroEstado
                )
          );
          
          // Actualizar también el pedido seleccionado (con los productos)
          setSelectedOrder(completeOrderDetails);
          
          // Marcar como cargado en caché
          setOrderDetailsCache(prev => ({...prev, [id]: true}));
        }
      } catch (error) {
        console.error('Error al cargar detalles del pedido:', error);
        setError('No se pudieron cargar los detalles del pedido');
      } finally {
        setLoadingOrderDetails(false);
      }
    } catch (error) {
      console.error('Error general:', error);
      setError('Ocurrió un error al procesar la solicitud');
    }
  };

  // Wrapper para manejar el estado del pedido desde el modal
  const handleOrderStatusFromModal = async (id: number, newStatus: string) => {
    await handleOrderStatus(id, newStatus);
    closeDetailModal();
  };

  // Función para manejar el cierre de sesión
  const handleLogout = () => {
    logout();
    navigate('/');
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
              <div className="ms-auto">
                <div className="dropdown">
                  <button className="btn btn-primary dropdown-toggle" type="button" id="userDropdown" data-bs-toggle="dropdown">
                    <i className="bi bi-person-circle me-1"></i>
                    {user?.nombre?.split(' ')[0] || 'Admin'}
                  </button>
                  <ul className="dropdown-menu dropdown-menu-end">
                    <li><a className="dropdown-item" href="#" onClick={handleLogout}><i className="bi bi-box-arrow-right me-2"></i>Cerrar sesión</a></li>
                  </ul>
                </div>
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
                                    {/* Sección de Clientes eliminada */}
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
                            <td>${typeof producto.precio === 'number' ? producto.precio.toFixed(2) : parseFloat(String(producto.precio)).toFixed(2)}</td>
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
                    <select className="form-select form-select-sm" 
                      value={filtroEstado}
                      onChange={(e) => handleOrderFilter(e.target.value)}
                    >
                      <option value="todos">Todos los estados</option>
                      <option value="pendiente">Pendiente</option>
                      <option value="entregado">Entregado</option>
                      <option value="cancelado">Cancelado</option>
                    </select>
                  </div>
                </div>
                <div className="card-body">
                  {pedidosFiltrados.length === 0 ? (
                    <div className="text-center py-4">
                      <i className="bi bi-inbox display-4 text-muted"></i>
                      <p className="text-muted mt-2">
                        {filtroEstado !== 'todos' 
                          ? `No hay pedidos con estado "${filtroEstado}"` 
                          : "No hay pedidos registrados"}
                      </p>
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
                          {pedidosFiltrados.map((pedido) => (
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
                              <td>${typeof pedido.total === 'number' ? pedido.total.toFixed(2) : pedido.total || '(calculando)'}</td>
                              <td>
                                <div className="btn-group">
                                  {/* Botón Ver Detalles */}
                                  <button 
                                    className="btn btn-sm btn-outline-primary" 
                                    onClick={() => handleViewOrderDetails(pedido.id_pedido)}
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
          </>
        )}
      </div>
      
      {/* Modal de detalles del pedido - Renderizado fuera del ciclo principal */}
      {selectedOrder && (
        <OrderDetailModal
          selectedOrder={selectedOrder}
          isLoading={loadingOrderDetails}
          onClose={closeDetailModal}
          onStatusChange={handleOrderStatusFromModal}
        />
      )}
    </div>
  );
};

export default AdminDashboard;
