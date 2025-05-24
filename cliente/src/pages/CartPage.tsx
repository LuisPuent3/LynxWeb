import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import { Producto } from '../types/types';
import { Modal } from 'react-bootstrap';
import AuthModal from '../components/auth/AuthModal';

interface CartItem extends Producto {
  cantidad: number;
}

interface LocationState {
  cartItems?: CartItem[];
  total?: number;
}

const CartPage: React.FC = () => {
  const [carrito, setCarrito] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingOrder, setProcessingOrder] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('efectivo');
  const [couponCode, setCouponCode] = useState('');
  const [couponApplied, setCouponApplied] = useState(false);
  const [discount, setDiscount] = useState(0);
  const [showAuthModal, setShowAuthModal] = useState(false);

  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const locationState = location.state as LocationState;

  useEffect(() => {
    // Añadir refresh forzado para resolver problemas de congelamiento con invitados
    const forceRefresh = () => {
      // Verificar si estamos en una recarga mediante un parámetro de URL
      const urlParams = new URLSearchParams(window.location.search);
      const hasReloaded = urlParams.get('reloaded') === 'true';
      
      // Si ya estamos en una recarga o no es usuario invitado, no recargar
      if (hasReloaded || localStorage.getItem("guestMode") !== "true") {
        return false;
      }
      
      // Solo refrescar una vez agregando un parámetro a la URL
      console.log("Forzando recarga para invitado en CartPage");
      const newUrl = window.location.pathname + '?reloaded=true' + window.location.hash;
      window.location.href = newUrl;
      return true; // Indicar que se hizo refresh
    };
    
    // Si se hizo refresh, no continuar con la carga normal
    if (forceRefresh()) return;

    // Primero verificar si hay items en location state (viniendo de handleLoginSuccess)
    if (locationState?.cartItems && locationState.cartItems.length > 0) {
      console.log("Received cart items from navigation state:", locationState.cartItems);
      setCarrito(locationState.cartItems);
    } else {
      // Si no, cargar el carrito desde localStorage
      const savedCarrito = localStorage.getItem('tempCarrito');
      if (savedCarrito) {
        setCarrito(JSON.parse(savedCarrito));
      }
    }
    setLoading(false);
  }, [locationState]);

  // Guardar cambios en el carrito al localStorage
  useEffect(() => {
    if (carrito.length > 0) {
      localStorage.setItem('tempCarrito', JSON.stringify(carrito));
    }
  }, [carrito]);

  const updateQuantity = (id: number, newQuantity: number) => {
    if (newQuantity < 1) return;
    
    // Buscar el producto en el carrito
    const productoEnCarrito = carrito.find(item => item.id_producto === id);
    if (!productoEnCarrito) return;
    
    // Verificar si hay suficiente stock disponible
    if (newQuantity > productoEnCarrito.cantidad) {
      // Buscar el stock actual del producto en tiempo real
      api.get(`/productos/${id}`)
        .then(response => {
          const stockActual = response.data.cantidad;
          
          if (newQuantity > stockActual) {
            alert(`No es posible agregar ${newQuantity} unidades. Solo hay ${stockActual} unidades disponibles.`);
            
            // Actualizar al máximo disponible
            setCarrito(prevCart => 
              prevCart.map(item => 
                item.id_producto === id 
                  ? { ...item, cantidad: Math.min(newQuantity, stockActual) } 
                  : item
              )
            );
          } else {
            // Si hay suficiente stock, actualizar normalmente
            setCarrito(prevCart => 
              prevCart.map(item => 
                item.id_producto === id 
                  ? { ...item, cantidad: newQuantity } 
                  : item
              )
            );
          }
        })
        .catch(error => {
          console.error('Error al verificar stock disponible:', error);
          // En caso de error, permitir la actualización pero mostrar advertencia
          alert('No se pudo verificar el stock disponible. La cantidad podría ser ajustada al procesar el pedido.');
          
          setCarrito(prevCart => 
            prevCart.map(item => 
              item.id_producto === id 
                ? { ...item, cantidad: newQuantity } 
                : item
            )
          );
        });
    } else {
      // Si la cantidad solicitada es menor o igual a la que ya tenía en el carrito, actualizar sin verificar
      setCarrito(prevCart => 
        prevCart.map(item => 
          item.id_producto === id 
            ? { ...item, cantidad: newQuantity } 
            : item
        )
      );
    }
  };

  const removeItem = (id: number) => {
    setCarrito(prevCart => prevCart.filter(item => item.id_producto !== id));
    // Si el carrito queda vacío, eliminar del localStorage
    if (carrito.length === 1) {
      localStorage.removeItem('tempCarrito');
    }
  };

  const calculateSubtotal = (): number => {
    return carrito.reduce((total, item) => 
      total + (Number(item.precio) * item.cantidad), 0);
  };

  const calculateTotal = (): number => {
    const subtotal = calculateSubtotal();
    const discountAmount = couponApplied ? subtotal * (discount / 100) : 0;
    return subtotal - discountAmount;
  };

  const handleApplyCoupon = () => {
    // En un caso real, esto verificaría el cupón con el backend
    if (couponCode.toLowerCase() === 'lynx10') {
      setCouponApplied(true);
      setDiscount(10);
      alert('¡Cupón aplicado! 10% de descuento.');
    } else {
      setCouponApplied(false);
      setDiscount(0);
      alert('Cupón no válido.');
    }
  };

  const procesarPedido = async (userId?: string | number) => {
    try {
      // Guardar los items del carrito antes de procesarlo
      const itemsToConfirm = [...carrito];
      const totalToConfirm = calculateTotal();
      const discountToConfirm = couponApplied ? discount : 0;
      
      // Preparar datos del pedido según el formato esperado por el backend
      const pedidoData = {
        carrito: carrito.map(item => ({
          id_producto: Number(item.id_producto),
          cantidad: Number(item.cantidad),
          precio: Number(item.precio)
        })),
        id_usuario: userId || user?.id_usuario,
        metodo_pago: paymentMethod,
        descuento: couponApplied ? discount : 0,
        total: calculateTotal()
      };

      // Enviar pedido al backend
      const token = localStorage.getItem('token');
      if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await api.post('/pedidos', pedidoData);
      
      if (response.data && response.data.id_pedido) {
        // Pedido creado exitosamente
        // Vaciar el carrito
        vaciarCarrito();
        
        // Navegamos a la página de confirmación con los datos necesarios
        navigate('/order/confirmation', {
          state: {
            cartItems: itemsToConfirm,
            orderId: response.data.id_pedido,
            total: totalToConfirm,
            discount: discountToConfirm
          }
        });
      } else {
        throw new Error('No se recibió confirmación del pedido');
      }
    } catch (error) {
      console.error('Error al procesar el pedido:', error);
      alert('Hubo un problema al procesar tu pedido. Por favor intenta nuevamente.');
      setProcessingOrder(false);
    }
  };

  const vaciarCarrito = () => {
    setCarrito([]);
    localStorage.removeItem('tempCarrito');
  };

  const handleCheckout = async () => {
    if (carrito.length === 0) {
      alert('Tu carrito está vacío');
      return;
    }

    if (!isAuthenticated) {
      // Mostrar modal de autenticación en lugar de la alerta
      setShowAuthModal(true);
      return;
    }

    // For guest users, navigate to order summary page
    // For authenticated regular users, process the order directly
    if (localStorage.getItem("guestMode") === "true") {
      // Asegurarse de pasar los datos completos del carrito al navegar
      const calculatedTotal = calculateTotal();
      navigate('/order/summary', {
        state: {
          cartItems: [...carrito], // Hacer una copia del carrito para evitar referencias
          total: calculatedTotal,
          discount: couponApplied ? discount : 0,
          paymentMethod: paymentMethod
        }
      });
    } else {
      // For regular authenticated users, process order directly
      setProcessingOrder(true);
      await procesarPedido();
    }
  };

  const handleModalLogin = async () => {
    // Esta función se llamará después de un login exitoso desde el modal
    await procesarPedido();
  };

  if (loading) {
    return (
      <div className="container-fluid py-3 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-5">
      {/* Modal de Autenticación */}
      <Modal 
        show={showAuthModal} 
        onHide={() => setShowAuthModal(false)}
        centered
        size="lg"
      >
        <AuthModal 
          isOpen={showAuthModal} 
          onClose={() => setShowAuthModal(false)}
          onLogin={handleModalLogin}
          onGuestCheckout={() => procesarPedido()}
          vaciarCarrito={vaciarCarrito}
        />
      </Modal>

      {/* Encabezado */}
      <div className="pb-4 text-center">
        <h1 className="display-5 fw-bold text-primary mb-2">Tu Carrito</h1>
        <p className="lead text-muted">
          {carrito.length 
            ? `Tienes ${carrito.length} ${carrito.length === 1 ? 'producto' : 'productos'} en tu carrito` 
            : 'Tu carrito está vacío'}
        </p>
        <div className="progress" style={{ height: '3px', maxWidth: '400px', margin: '0 auto' }}>
          <div className="progress-bar bg-primary" role="progressbar" style={{ width: '100%' }}></div>
        </div>
      </div>

      {carrito.length > 0 ? (
        <div className="row g-5">
          {/* Productos en el carrito */}
          <div className="col-lg-8">
            <div className="card border-0 shadow-sm mb-4 rounded-3 overflow-hidden">
              <div className="card-header bg-white py-3 border-bottom">
                <h5 className="mb-0 d-flex align-items-center">
                  <i className="bi bi-cart3 me-2 text-primary"></i>
                  Productos en tu carrito
                </h5>
              </div>
              <div className="card-body p-0">
                {carrito.map((item, index) => (
                  <div key={item.id_producto} className={`p-4 ${index !== carrito.length - 1 ? 'border-bottom' : ''}`}>
                    <div className="row align-items-center">
                      <div className="col-md-2">
                        {item.imagen ? (
                          <img 
                            src={`http://localhost:5000/uploads/${item.imagen}?v=${item.id_producto}`}
                            alt={item.nombre}
                            className="img-fluid rounded shadow-sm"
                            style={{ 
                              width: '100%', 
                              height: 'auto',
                              maxWidth: '80px',
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
                          <div className="bg-light rounded p-2 text-center">
                            <i className="bi bi-box text-primary fs-1"></i>
                          </div>
                        )}
                      </div>
                      <div className="col-md-3 d-flex align-items-center">
                        <div>
                          <h6 className="text-primary mb-1 fw-semibold">{item.nombre}</h6>
                          <p className="small text-muted mb-0">SKU: PRD-{item.id_producto}</p>
                        </div>
                      </div>
                      <div className="col-md-3 d-flex align-items-center">
                        <div className="d-flex align-items-center">
                          <button 
                            className="btn btn-sm btn-outline-secondary rounded-pill"
                            onClick={() => updateQuantity(item.id_producto, item.cantidad - 1)}
                          >
                            <i className="bi bi-dash"></i>
                          </button>
                          <input 
                            type="number" 
                            className="form-control form-control-sm mx-2 text-center" 
                            style={{ 
                              width: '50px',
                              minWidth: '50px',
                              height: '38px',
                              padding: '2px 4px',
                              border: '1px solid #ced4da',
                              fontSize: '16px',
                              fontWeight: 'bold',
                              zIndex: 1 // Ensure it's above any potential overlapping elements
                            }}
                            value={item.cantidad} 
                            min="1"
                            onChange={(e) => updateQuantity(item.id_producto, parseInt(e.target.value) || 1)}
                          />
                          <button 
                            className="btn btn-sm btn-outline-secondary rounded-pill"
                            onClick={() => updateQuantity(item.id_producto, item.cantidad + 1)}
                          >
                            <i className="bi bi-plus"></i>
                          </button>
                        </div>
                      </div>
                      <div className="col-md-2 d-flex align-items-center">
                        <div>
                          <p className="fw-bold mb-0 text-primary">${Number(item.precio).toFixed(2)}</p>
                          <p className="text-muted small mb-0">Precio unitario</p>
                        </div>
                      </div>
                      <div className="col-md-2 d-flex align-items-center justify-content-end">
                        <div className="text-end">
                          <p className="fw-bold mb-2 fs-5">${(Number(item.precio) * item.cantidad).toFixed(2)}</p>
                          <button 
                            className="btn btn-sm btn-outline-danger rounded-pill"
                            onClick={() => removeItem(item.id_producto)}
                          >
                            <i className="bi bi-trash me-1"></i>
                            Eliminar
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                <div className="text-end p-4 bg-light">
                  <button 
                    className="btn btn-outline-primary rounded-pill"
                    onClick={() => navigate('/')}
                  >
                    <i className="bi bi-arrow-left me-2"></i>
                    Seguir comprando
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Resumen y opciones de pago */}
          <div className="col-lg-4">
            <div className="card border-0 shadow-sm rounded-3 sticky-top" style={{ top: "80px" }}>
              <div className="card-header bg-primary bg-gradient text-white py-3 border-0">
                <h5 className="mb-0 d-flex align-items-center">
                  <i className="bi bi-receipt me-2"></i>
                  Resumen de compra
                </h5>
              </div>
              <div className="card-body p-4">
                <div className="d-flex justify-content-between mb-3">
                  <span className="text-muted">Subtotal</span>
                  <span className="fw-bold">${calculateSubtotal().toFixed(2)}</span>
                </div>
                
                {couponApplied && (
                  <div className="d-flex justify-content-between mb-3 text-success">
                    <span>Descuento ({discount}%)</span>
                    <span className="fw-bold">-${(calculateSubtotal() * (discount / 100)).toFixed(2)}</span>
                  </div>
                )}
                
                <div className="d-flex justify-content-between fw-bold mb-3 border-top border-bottom py-3">
                  <span>Total</span>
                  <span className="fs-5 text-primary">${calculateTotal().toFixed(2)}</span>
                </div>
                
                {/* Cupón */}
                <div className="mb-4">
                  <label className="form-label fw-medium">Cupón de descuento</label>
                  <div className="input-group mb-2">
                    <input 
                      type="text" 
                      className="form-control form-control-sm rounded-start border-0 bg-light"
                      placeholder="Ingresa un cupón"
                      value={couponCode}
                      onChange={(e) => setCouponCode(e.target.value)}
                    />
                    <button 
                      className="btn btn-outline-primary btn-sm"
                      onClick={handleApplyCoupon}
                    >
                      Aplicar
                    </button>
                  </div>
                  <div className="form-text">
                    <i className="bi bi-tag-fill me-1 text-primary"></i>
                    Prueba con: LYNX10
                  </div>
                </div>

                {/* Método de pago */}
                <div className="mb-4">
                  <label className="form-label fw-medium">Método de pago</label>
                  <div className="d-flex flex-wrap gap-2">
                    <div 
                      className={`p-2 border rounded text-center flex-grow-1 position-relative ${paymentMethod === 'card' ? 'border-secondary bg-light' : 'border-secondary bg-light'}`}
                      style={{ cursor: 'not-allowed', opacity: '0.7' }}
                    >
                      <div className="position-absolute top-0 end-0 badge bg-warning text-dark m-1" style={{ fontSize: '0.6rem' }}>
                        Próximamente
                      </div>
                      <i className="bi bi-credit-card fs-4 d-block mb-1"></i>
                      <small>Tarjeta</small>
                    </div>
                    <div 
                      className={`p-2 border rounded text-center flex-grow-1 position-relative ${paymentMethod === 'transfer' ? 'border-secondary bg-light' : 'border-secondary bg-light'}`}
                      style={{ cursor: 'not-allowed', opacity: '0.7' }}
                    >
                      <div className="position-absolute top-0 end-0 badge bg-warning text-dark m-1" style={{ fontSize: '0.6rem' }}>
                        Próximamente
                      </div>
                      <i className="bi bi-bank fs-4 d-block mb-1"></i>
                      <small>Transferencia</small>
                    </div>
                    <div 
                      className={`p-2 border rounded text-center flex-grow-1 cursor-pointer ${paymentMethod === 'efectivo' ? 'border-primary bg-primary bg-opacity-10' : ''}`}
                      onClick={() => setPaymentMethod('efectivo')}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="position-absolute top-0 end-0 badge bg-success m-1" style={{ fontSize: '0.6rem' }}>
                        Disponible
                      </div>
                      <i className="bi bi-cash fs-4 d-block mb-1"></i>
                      <small>Efectivo</small>
                    </div>
                  </div>
                  <div className="form-text text-center mt-2">
                    <i className="bi bi-info-circle me-1"></i>
                    Actualmente solo aceptamos pagos en efectivo
                  </div>
                </div>

                <button 
                  className="btn btn-primary w-100 py-3 rounded-pill fw-bold"
                  onClick={handleCheckout}
                  disabled={processingOrder || carrito.length === 0 || paymentMethod !== 'efectivo'}
                >
                  {processingOrder ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Procesando...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-lock-fill me-2"></i>
                      Finalizar Compra
                    </>
                  )}
                </button>
                
                <div className="alert alert-info mt-3 mb-2 p-2 text-center small">
                  <i className="bi bi-info-circle-fill me-1"></i>
                  <strong>Información importante:</strong> Por el momento, solo aceptamos pagos en efectivo.
                  Las opciones de tarjeta y transferencia estarán disponibles próximamente.
                </div>
                
                <div className="d-flex justify-content-center gap-3 mt-3">
                  <i className="bi bi-shield-lock text-primary"></i>
                  <i className="bi bi-credit-card text-primary"></i>
                  <i className="bi bi-truck text-primary"></i>
                </div>
                <p className="text-center text-muted small mt-2">
                  Pago seguro garantizado
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-3">
          <p className="mb-0">Tu carrito está vacío</p>
        </div>
      )}
    </div>
  );
};

export default CartPage;