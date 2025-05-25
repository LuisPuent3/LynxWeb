import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import { formatDate, mapOrderStatus } from '../utils/helpers';
// Importar datos de ejemplo
import mockOrders from '../components/MockOrderData';

interface OrderItem {
  id_producto: number;
  nombre: string;
  cantidad: number;
  precio: number;
  imagen?: string;
}

interface Order {
  id_pedido: number;
  fecha: string;
  estado: 'pendiente' | 'aceptado' | 'procesando' | 'enviado' | 'entregado' | 'cancelado';
  total: number;
  metodo_pago: string;
  productos: OrderItem[];
  tracking_code?: string;
}

const OrderHistoryPage: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>('todos');
  const [expandedOrder, setExpandedOrder] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isGuest, setIsGuest] = useState(false);

  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    // Comprobar si es usuario invitado
    const guestMode = localStorage.getItem('guestMode') === 'true';
    setIsGuest(guestMode);
    
    fetchOrders();
  }, [isAuthenticated, navigate]);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No token available');
      
      // Obtener el ID de usuario del contexto o localStorage
      const userId = user?.id_usuario || 
                   (localStorage.getItem('usuario') ? 
                     JSON.parse(localStorage.getItem('usuario') || '{}').id_usuario : 
                     null);
      
      console.log('ID de usuario actual:', userId);
      
      if (!userId) {
        setError('No se pudo determinar el ID de usuario');
        setLoading(false);
        return;
      }
      
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Usar la URL correcta con el ID de usuario
      const url = `/pedidos/usuario/${userId}`;
      console.log('Consultando URL:', url);
      
      const response = await api.get(url);
      
      if (response.data && Array.isArray(response.data)) {
        // Mapear los estados desde la DB a los valores enum de nuestro frontend
        const processedOrders = response.data.map((order: Order) => ({
          ...order,
          estado: mapOrderStatus(order.estado)
        }));
        setOrders(processedOrders);
        console.log('Pedidos recibidos:', processedOrders.length);
      } else {
        setOrders([]);
        console.log('No se recibieron pedidos o formato incorrecto');
      }
      setError(null);
    } catch (err) {
      console.error('Error fetching orders:', err);
      
      // Mostrar información más detallada sobre el error
      if (err.response) {
        // Error de respuesta del servidor
        console.error('Error de servidor:', err.response.status, err.response.data);
        setError(`Error del servidor: ${err.response.status}. ${err.response.data?.error || ''}`);
      } else if (err.request) {
        // No se recibió respuesta
        console.error('No se recibió respuesta del servidor');
        setError('No se pudo conectar con el servidor. Verifica tu conexión.');
      } else {
        // Error de configuración
        setError(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const getOrderStatusBadge = (status: string) => {
    // Mapear el estado a un valor conocido primero
    const mappedStatus = mapOrderStatus(status);
    
    switch (mappedStatus) {
      case 'pendiente':
        return <span className="badge bg-warning text-dark">Pendiente</span>;
      case 'aceptado':
        return <span className="badge bg-info">Aceptado</span>;
      case 'entregado':
        return <span className="badge bg-success">Entregado</span>;
      case 'cancelado':
        return <span className="badge bg-danger">Cancelado</span>;
      default:
        return <span className="badge bg-secondary">{status || 'Desconocido'}</span>;
    }
  };

  const getOrderStatusClass = (status: string) => {
    // Mapear el estado a un valor conocido primero
    const mappedStatus = mapOrderStatus(status);
    
    switch (mappedStatus) {
      case 'pendiente': return 'border-warning';
      case 'aceptado': return 'border-info';  
      case 'entregado': return 'border-success';
      case 'cancelado': return 'border-danger';
      default: return 'border-secondary';
    }
  };

  const getOrderProgressValue = (status: string) => {
    // Mapear el estado a un valor conocido primero
    const mappedStatus = mapOrderStatus(status);
    
    switch (mappedStatus) {
      case 'pendiente': return 25;
      case 'aceptado': return 50;
      case 'entregado': return 100;
      case 'cancelado': return 0;
      default: return 0;
    }
  };

  const getOrderProgressClass = (status: string) => {
    // Mapear el estado a un valor conocido primero
    const mappedStatus = mapOrderStatus(status);
    
    switch (mappedStatus) {
      case 'pendiente': return 'bg-warning';
      case 'aceptado': return 'bg-info';
      case 'entregado': return 'bg-success';
      case 'cancelado': return 'bg-danger';
      default: return 'bg-secondary';
    }
  };

  const handleOrderClick = (orderId: number) => {
    setExpandedOrder(expandedOrder === orderId ? null : orderId);
  };

  const filterOrders = () => {
    let filtered = [...orders];
    
    // Aplicar filtro por estado
    if (activeFilter !== 'todos') {
      filtered = filtered.filter(order => {
        // Mapear el estado de la BD al estado interno para asegurar compatibilidad
        const mappedStatus = mapOrderStatus(order.estado);
        return mappedStatus === activeFilter;
      });
    }
    
    // Aplicar búsqueda
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(order => 
        order.id_pedido.toString().includes(search) || 
        order.productos.some(p => p.nombre.toLowerCase().includes(search))
      );
    }
    
    return filtered.sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime());
  };

  const filteredOrders = filterOrders();

  const cancelOrder = async (orderId: number) => {
    if (!window.confirm('¿Estás seguro de que deseas cancelar este pedido?')) {
      return;
    }
    
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No token available');
      
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      const response = await api.put(`/pedidos/${orderId}/estado`, {
        estado: 'cancelado'
      });
      
      if (response.status === 200) {
        // Update the order in the state
        setOrders(prevOrders => 
          prevOrders.map(order => 
            order.id_pedido === orderId 
              ? { ...order, estado: 'cancelado' } 
              : order
          )
        );
        
        alert('Pedido cancelado con éxito');
      }
    } catch (error) {
      console.error('Error al cancelar el pedido:', error);
      alert('No se pudo cancelar el pedido. Inténtalo nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const repeatOrder = async (order: Order) => {
    try {
      // Add the products to the cart
      const cartItems = order.productos.map(item => ({
        ...item,
        id_producto: item.id_producto,
        precio: item.precio,
        cantidad: item.cantidad
      }));
      
      // Store the cart items in localStorage
      localStorage.setItem('tempCarrito', JSON.stringify(cartItems));
      
      // Navigate to the cart page
      navigate('/cart');
    } catch (error) {
      console.error('Error al repetir el pedido:', error);
      alert('No se pudo repetir el pedido. Inténtalo nuevamente.');
    }
  };

  const downloadInvoice = (order: Order) => {
    // Since we don't have a real PDF generator, we'll create a simple text version for demo
    const fileName = `factura-pedido-${order.id_pedido}.txt`;
    
    let invoiceContent = `
===============================================
            FACTURA - LYNX SHOP
===============================================

Fecha: ${formatDate(order.fecha)}
No. Pedido: ${order.id_pedido}
Estado: ${mapOrderStatus(order.estado)}
Método de pago: ${order.metodo_pago}

-----------------------------------------------
PRODUCTOS:
`;
    
    order.productos.forEach(product => {
      invoiceContent += `
${product.nombre}
Cantidad: ${product.cantidad} x $${product.precio.toFixed(2)}
Subtotal: $${(product.cantidad * product.precio).toFixed(2)}
-----------------------------------------------`;
    });
    
    invoiceContent += `
TOTAL: $${order.total.toFixed(2)}
===============================================
Gracias por tu compra!
`;
    
    // Create a blob and download link
    const blob = new Blob([invoiceContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  };

  if (loading) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
        <p className="mt-3 text-muted">Cargando tu historial de pedidos...</p>
      </div>
    );
  }

  return (
    <div className="container py-5">
      <div className="row mb-4">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h1 className="display-6 fw-bold text-primary mb-0">Mi Historial de Pedidos</h1>
            <button 
              className="btn btn-outline-primary" 
              onClick={() => navigate('/')}
            >
              <i className="bi bi-house-door me-1"></i>
              Regresar a Inicio
            </button>
          </div>
          <p className="text-muted mb-4">
            Consulta el estado y detalles de todos tus pedidos realizados en LynxShop
          </p>
          
          {/* Banner informativo para usuarios invitados */}
          {isGuest && (
            <div className="card border-warning mb-4">
              <div className="card-body">
                <h5 className="d-flex align-items-center">
                  <i className="bi bi-exclamation-triangle text-warning me-2"></i>
                  Modo Invitado
                </h5>
                <p className="mb-3">Tu historial solo estará disponible en este dispositivo mientras no cierres sesión.</p>
                <div className="d-flex">
                  <button 
                    className="btn btn-warning me-2"
                    onClick={() => navigate('/register')}
                  >
                    <i className="bi bi-person-plus me-1"></i>
                    Crear cuenta permanente
                  </button>
                  <button className="btn btn-outline-secondary btn-sm">
                    <i className="bi bi-question-circle me-1"></i>
                    Más información
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>      {/* Filtros y búsqueda */}
      <div className="row mb-4">
        <div className="col-md-8">
          <div className="btn-group" role="group" aria-label="Filtros de pedidos">
            <button 
              type="button" 
              className={`btn ${activeFilter === 'todos' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setActiveFilter('todos')}
            >
              Todos
            </button>
            <button 
              type="button" 
              className={`btn ${activeFilter === 'pendiente' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setActiveFilter('pendiente')}
            >
              Pendientes
            </button>
            <button 
              type="button" 
              className={`btn ${activeFilter === 'aceptado' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setActiveFilter('aceptado')}
            >
              Aceptados
            </button>
            <button 
              type="button" 
              className={`btn ${activeFilter === 'entregado' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setActiveFilter('entregado')}
            >
              Entregados
            </button>
            <button 
              type="button" 
              className={`btn ${activeFilter === 'cancelado' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setActiveFilter('cancelado')}
            >
              Cancelados
            </button>
          </div>
        </div>
        <div className="col-md-4 mt-3 mt-md-0">
          <div className="input-group">
            <span className="input-group-text bg-white border-end-0">
              <i className="bi bi-search text-muted"></i>
            </span>
            <input 
              type="text" 
              className="form-control border-start-0" 
              placeholder="Buscar por # de pedido o producto"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {error}
        </div>
      )}

      {filteredOrders.length === 0 ? (
        <div className="text-center py-5 my-4 bg-light rounded-3">
          <div className="mb-4">
            <i className="bi bi-bag text-muted" style={{ fontSize: '3rem' }}></i>
          </div>
          <h3>No encontramos pedidos</h3>
          <p className="text-muted mb-4">
            {activeFilter !== 'todos' 
              ? `No tienes pedidos con el estado: ${activeFilter}` 
              : searchTerm 
                ? 'No hay resultados para tu búsqueda' 
                : 'Aún no has realizado ningún pedido'}
          </p>
          <button 
            className="btn btn-primary px-4 py-2"
            onClick={() => navigate('/')}
          >
            <i className="bi bi-cart me-2"></i>
            Ir a comprar
          </button>
        </div>
      ) : (
        <div className="row">
          <div className="col-12">
            {filteredOrders.map(order => (
              <div 
                key={order.id_pedido} 
                className={`card mb-4 border-start-0 border-end-0 border-bottom-0 border-top-4 ${getOrderStatusClass(order.estado)}`}
                style={{ borderTopWidth: '4px', cursor: 'pointer' }}
                onClick={() => handleOrderClick(order.id_pedido)}
              >
                <div className="card-body p-4">
                  <div className="row align-items-center">
                    <div className="col-md-2 text-center text-md-start mb-3 mb-md-0">
                      <span className="badge bg-secondary bg-opacity-10 text-secondary p-2 rounded-pill mb-2 d-inline-block">
                        <i className="bi bi-hash"></i> Pedido #{order.id_pedido}
                      </span>
                      <div className="small text-muted">
                        {formatDate(order.fecha)}
                      </div>
                    </div>
                    <div className="col-md-3 text-center text-md-start mb-3 mb-md-0">
                      <div className="d-flex align-items-center justify-content-center justify-content-md-start">
                        <div className="me-2">
                          {getOrderStatusBadge(order.estado)}
                        </div>
                        {order.tracking_code && (
                          <span className="badge bg-light text-dark border">
                            <i className="bi bi-truck me-1"></i>
                            {order.tracking_code}
                          </span>
                        )}
                      </div>
                      <div className="progress mt-2" style={{ height: '6px' }}>
                        <div 
                          className={`progress-bar ${getOrderProgressClass(order.estado)}`} 
                          role="progressbar" 
                          style={{ width: `${getOrderProgressValue(order.estado)}%` }}
                          aria-valuenow={getOrderProgressValue(order.estado)} 
                          aria-valuemin={0} 
                          aria-valuemax={100}
                        ></div>
                      </div>
                    </div>
                    <div className="col-md-4 text-center text-md-start mb-3 mb-md-0">
                      <div className="text-truncate small">
                        {order.productos.slice(0, 2).map(item => item.nombre).join(', ')}
                        {order.productos.length > 2 && ` y ${order.productos.length - 2} más`}
                      </div>
                      <div className="small text-muted mt-1">
                        <i className="bi bi-box me-1"></i>
                        {order.productos.reduce((sum, item) => sum + item.cantidad, 0)} productos
                      </div>
                    </div>
                    <div className="col-md-2 text-center text-md-start mb-3 mb-md-0">
                      <span className="fw-bold text-primary fs-5">${Number(order.total).toFixed(2)}</span>
                      <div className="small text-muted">
                        <i className="bi bi-credit-card me-1"></i>
                        {order.metodo_pago === 'efectivo' ? 'Efectivo' : order.metodo_pago}
                      </div>
                    </div>
                    <div className="col-md-1 text-end">
                      <i className={`bi ${expandedOrder === order.id_pedido ? 'bi-chevron-up' : 'bi-chevron-down'} fs-5 text-muted`}></i>
                    </div>
                  </div>

                  {/* Detalles expandibles del pedido */}
                  {expandedOrder === order.id_pedido && (
                    <div className="mt-4 pt-3 border-top">
                      <h6 className="mb-3 fw-bold">
                        <i className="bi bi-box-seam me-2 text-primary"></i>
                        Detalle del Pedido
                      </h6>
                      
                      {/* Productos del pedido */}
                      <div className="table-responsive mb-3">
                        <table className="table table-hover">
                          <thead className="table-light">
                            <tr>
                              <th>Producto</th>
                              <th>Cantidad</th>
                              <th>Precio</th>
                              <th className="text-end">Subtotal</th>
                            </tr>
                          </thead>
                          <tbody>
                            {order.productos.map(item => (
                              <tr key={item.id_producto}>
                                <td>
                                  <div className="d-flex align-items-center">
                                    {item.imagen ? (                                      <img 
                                        src={`/uploads/${item.imagen}?v=${item.id_producto}`}
                                        alt={item.nombre}
                                        className="img-fluid rounded shadow-sm me-3"
                                        style={{ 
                                          width: '100%', 
                                          height: 'auto',
                                          maxWidth: '40px',
                                          aspectRatio: '1/1',
                                          objectFit: 'cover',
                                          objectPosition: 'center'
                                        }}
                                        onError={(e) => {
                                          // Si hay error al cargar la imagen, mostrar el icono
                                          e.currentTarget.style.display = 'none';
                                          e.currentTarget.parentElement?.querySelector('.fallback-icon')?.classList.remove('d-none');
                                        }}
                                      />
                                    ) : (
                                      <div className="bg-light rounded p-2 me-3">
                                        <i className="bi bi-box text-primary"></i>
                                      </div>
                                    )}
                                    <div className="fallback-icon d-none bg-light rounded p-2 me-3">
                                      <i className="bi bi-box text-primary"></i>
                                    </div>
                                    <div>
                                      <h6 className="mb-0">{item.nombre}</h6>
                                      <small className="text-muted">SKU: PRD-{item.id_producto}</small>
                                    </div>
                                  </div>
                                </td>
                                <td>{item.cantidad}</td>
                                <td>${Number(item.precio).toFixed(2)}</td>
                                <td className="text-end fw-bold">${(Number(item.precio) * item.cantidad).toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                          <tfoot className="table-light">
                            <tr>
                              <td colSpan={3} className="text-end fw-bold">Total</td>
                              <td className="text-end fw-bold">${Number(order.total).toFixed(2)}</td>
                            </tr>
                          </tfoot>
                        </table>
                      </div>
                      
                      {/* Estado del pedido */}
                      <div className="card bg-light mb-3">
                        <div className="card-body p-3">
                          <h6 className="card-title mb-3">
                            <i className="bi bi-truck me-2 text-primary"></i>
                            Seguimiento del Pedido
                          </h6>
                          <div className="position-relative pb-3">
                            <div className="position-absolute top-0 start-0 bottom-0" style={{ width: '1px', backgroundColor: '#dee2e6', left: '11px' }}></div>
                            
                            <div className="d-flex mb-3 position-relative">
                              <div className={`rounded-circle p-1 ${order.estado !== 'cancelado' ? 'bg-success' : 'bg-secondary'} text-white me-3`} style={{ width: '22px', height: '22px', zIndex: 1 }}>
                                <i className="bi bi-check-lg" style={{ fontSize: '0.8rem' }}></i>
                              </div>
                              <div>
                                <p className="mb-0 fw-medium">Pedido confirmado</p>
                                <p className="text-muted small mb-0">{formatDate(order.fecha)}</p>
                              </div>
                            </div>
                            
                            <div className="d-flex mb-3 position-relative">
                              <div className={`rounded-circle p-1 ${['aceptado', 'entregado'].includes(mapOrderStatus(order.estado)) ? 'bg-success' : 'bg-secondary'} text-white me-3`} style={{ width: '22px', height: '22px', zIndex: 1 }}>
                                {['aceptado', 'entregado'].includes(mapOrderStatus(order.estado)) ? (
                                  <i className="bi bi-check-lg" style={{ fontSize: '0.8rem' }}></i>
                                ) : (
                                  <i className="bi bi-clock" style={{ fontSize: '0.8rem' }}></i>
                                )}
                              </div>
                              <div>
                                <p className="mb-0 fw-medium">Pedido aceptado</p>
                                <p className="text-muted small mb-0">
                                  {['aceptado', 'entregado'].includes(mapOrderStatus(order.estado)) 
                                    ? 'Tu pedido ha sido aceptado' 
                                    : 'Pendiente'}
                                </p>
                              </div>
                            </div>
                            
                            <div className="d-flex position-relative">
                              <div className={`rounded-circle p-1 ${mapOrderStatus(order.estado) === 'entregado' ? 'bg-success' : 'bg-secondary'} text-white me-3`} style={{ width: '22px', height: '22px', zIndex: 1 }}>
                                {mapOrderStatus(order.estado) === 'entregado' ? (
                                  <i className="bi bi-check-lg" style={{ fontSize: '0.8rem' }}></i>
                                ) : (
                                  <i className="bi bi-clock" style={{ fontSize: '0.8rem' }}></i>
                                )}
                              </div>
                              <div>
                                <p className="mb-0 fw-medium">Entregado</p>
                                <p className="text-muted small mb-0">
                                  {mapOrderStatus(order.estado) === 'entregado' 
                                    ? 'Tu pedido ha sido entregado con éxito' 
                                    : 'Pendiente'}
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      {/* Botones de acción */}
                      <div className="d-flex justify-content-end mt-3">
                        <button 
                          className="btn btn-primary me-2"
                          onClick={(e) => {
                            e.stopPropagation();
                            repeatOrder(order);
                          }}
                        >
                          <i className="bi bi-arrow-repeat me-1"></i>
                          Repetir pedido
                        </button>
                        <button 
                          className="btn btn-outline-secondary position-relative"
                          disabled={true}
                          title="Proximamente"
                        >
                          <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-warning text-dark px-2" style={{ fontSize: '0.65rem' }}>
                            Próximamente
                          </span>
                          <i className="bi bi-download me-1"></i>
                          Descargar factura
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderHistoryPage;