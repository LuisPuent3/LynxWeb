import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Producto } from '../types/types';
import api from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

interface CartItem extends Producto {
  cantidad: number;
}

interface LocationState {
  cartItems: CartItem[];
  total: number;
  discount: number;
  paymentMethod: string;
}

const OrderSummaryPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [isProcessing, setIsProcessing] = useState(false);
  const [additionalInfo, setAdditionalInfo] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [phoneError, setPhoneError] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [total, setTotal] = useState(0);
  const [discount, setDiscount] = useState(0);
  const [paymentMethod, setPaymentMethod] = useState('efectivo');
  const [isLoading, setIsLoading] = useState(true);

  // Obtener estado de localización
  const locationState = location.state as LocationState;

  useEffect(() => {
    // Primero intentar obtener datos del estado de navegación
    if (locationState && locationState.cartItems && locationState.cartItems.length > 0) {
      setCartItems(locationState.cartItems);
      setTotal(locationState.total);
      setDiscount(locationState.discount || 0);
      setPaymentMethod(locationState.paymentMethod || 'efectivo');
      setIsLoading(false);
    } else {
      // Si no hay datos en el estado de navegación, intentar obtenerlos del localStorage
      const savedCarrito = localStorage.getItem('tempCarrito');
      if (savedCarrito) {
        const parsedCart = JSON.parse(savedCarrito);
        if (parsedCart && parsedCart.length > 0) {
          setCartItems(parsedCart);
          // Calcular el total del carrito
          const calculatedTotal = parsedCart.reduce(
            (sum: number, item: CartItem) => sum + (Number(item.precio) * item.cantidad), 
            0
          );
          setTotal(calculatedTotal);
        } else {
          // Si tampoco hay datos en localStorage, redirigir al carrito
          navigate('/cart');
        }
      } else {
        // Si no hay carrito guardado, redirigir al carrito
        navigate('/cart');
      }
      setIsLoading(false);
    }
  }, [locationState, navigate]);

  useEffect(() => {
    // Solo permitir a usuarios invitados acceder a esta página
    if (!isLoading) {
      if (cartItems.length === 0) {
        navigate('/cart');
        return;
      }

      if (isAuthenticated && localStorage.getItem("guestMode") !== "true") {
        navigate('/cart');
        return;
      }

      if (!isAuthenticated) {
        navigate('/login', { state: { returnToCart: true } });
      }
    }
  }, [cartItems, isAuthenticated, navigate, isLoading]);

  const procesarPedido = async () => {
    try {
      setIsProcessing(true);
      
      // Validar teléfono antes de procesar
      if (!contactPhone) {
        alert('Por favor, ingrese un número de teléfono de contacto.');
        setIsProcessing(false);
        return;
      }
      
      if (!/^[0-9]{10}$/.test(contactPhone)) {
        alert('El teléfono debe tener exactamente 10 dígitos.');
        setIsProcessing(false);
        return;
      }
      
      // Ensure we have a valid user ID
      if (!user || !user.id_usuario) {
        alert('Error: No se pudo identificar al usuario. Inicie sesión nuevamente.');
        navigate('/login', { state: { returnToCart: true } });
        return;
      }
      
      // Ensure user ID is a number
      const userId = typeof user.id_usuario === 'string' 
        ? parseInt(user.id_usuario as string, 10) 
        : user.id_usuario;
      
      // Determinar el nombre completo o usar "Cliente invitado" si no se proporciona
      const nombreCompleto = firstName.trim() || lastName.trim() 
        ? `${firstName} ${lastName}`.trim() 
        : 'Cliente invitado';
      
      // Prepare order data according to backend expectations
      const pedidoData = {
        carrito: cartItems.map(item => ({
          id_producto: Number(item.id_producto),
          cantidad: Number(item.cantidad),
          precio: Number(item.precio)
        })),
        id_usuario: userId,
        metodo_pago: paymentMethod,
        descuento: discount,
        total: total,
        nombre_completo: nombreCompleto,
        telefono_contacto: contactPhone,
        informacion_adicional: additionalInfo
      };

      console.log('Datos a enviar a backend:', pedidoData);

      // Send order to backend
      const token = localStorage.getItem('token');
      if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await api.post('/pedidos', pedidoData);
      
      if (response.data && response.data.id_pedido) {
        // Navigate to confirmation page with necessary data
        navigate('/order/confirmation', {
          state: {
            cartItems: cartItems,
            orderId: response.data.id_pedido,
            total: total,
            discount: discount
          }
        });
        
        // Clear cart from localStorage
        localStorage.removeItem('tempCarrito');
      } else {
        throw new Error('No se recibió confirmación del pedido');
      }
    } catch (error: any) {
      console.error('Error al procesar el pedido:', error);
      
      // Show more detailed error message if available
      if (error.response?.data?.error) {
        alert(`Error: ${error.response.data.error}`);
      } else {
        alert('Hubo un problema al procesar tu pedido. Por favor intenta nuevamente.');
      }
      
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAdditionalInfoChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setAdditionalInfo(e.target.value);
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const phone = e.target.value;
    setContactPhone(phone);
    
    // Validar que tenga exactamente 10 dígitos
    if (phone && !/^[0-9]{10}$/.test(phone)) {
      setPhoneError('El teléfono debe tener exactamente 10 dígitos');
    } else {
      setPhoneError('');
    }
  };

  const handleFirstNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFirstName(e.target.value);
  };

  const handleLastNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLastName(e.target.value);
  };

  if (isLoading) {
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
      <div className="pb-4 mb-4 text-center">
        <h1 className="display-5 fw-bold text-primary mb-2">Resumen del Pedido</h1>
        <p className="lead text-muted">Revisa los detalles antes de confirmar tu compra</p>
        <div className="progress" style={{ height: '3px', maxWidth: '400px', margin: '0 auto' }}>
          <div className="progress-bar bg-primary" role="progressbar" style={{ width: '100%' }}></div>
        </div>
      </div>

      <div className="row g-5">
        {/* Order Details */}
        <div className="col-lg-8">
          <div className="card border-0 shadow-sm mb-4 rounded-3">
            <div className="card-header bg-white py-3">
              <h5 className="mb-0 d-flex align-items-center">
                <i className="bi bi-bag-check me-2 text-primary"></i>
                Productos en tu pedido
              </h5>
            </div>
            <div className="card-body p-0">
              {cartItems.map((item, index) => (
                <div key={item.id_producto} className={`p-4 ${index !== cartItems.length - 1 ? 'border-bottom' : ''}`}>
                  <div className="row align-items-center">
                    <div className="col-md-2">
                      {item.imagen ? (
                        <img 
                          src={`/uploads/${item.imagen}?v=${item.id_producto}`}
                          alt={item.nombre}
                          className="img-fluid rounded shadow-sm"
                          style={{ 
                            width: '100%', 
                            height: 'auto',
                            maxWidth: '70px',
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
                          <i className="bi bi-box text-primary fs-3"></i>
                        </div>
                      )}
                      <div className="fallback-icon d-none bg-light rounded p-2 text-center">
                        <i className="bi bi-box text-primary fs-3"></i>
                      </div>
                    </div>
                    <div className="col-md-5">
                      <h6 className="fw-bold mb-1">{item.nombre}</h6>
                      <p className="small text-muted mb-0">Cantidad: {item.cantidad}</p>
                    </div>
                    <div className="col-md-2 text-center">
                      <p className="mb-0">${Number(item.precio).toFixed(2)}</p>
                      <small className="text-muted">Precio unitario</small>
                    </div>
                    <div className="col-md-3 text-end">
                      <p className="fw-bold fs-5 mb-0">${(Number(item.precio) * item.cantidad).toFixed(2)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Contact Information */}
          <div className="card border-0 shadow-sm mb-4 rounded-3">
            <div className="card-header bg-white py-3">
              <h5 className="mb-0 d-flex align-items-center">
                <i className="bi bi-person me-2 text-primary"></i>
                Información del Cliente
              </h5>
            </div>
            <div className="card-body p-4">
              {/* Teléfono primero */}
              <div className="mb-4">
                <label htmlFor="phone" className="form-label">Teléfono de Contacto <span className="text-danger">*</span></label>
                <input 
                  type="tel" 
                  className={`form-control ${phoneError ? 'is-invalid' : contactPhone && !phoneError ? 'is-valid' : ''}`}
                  id="phone" 
                  placeholder="Ingresa tu número de teléfono" 
                  value={contactPhone}
                  onChange={handlePhoneChange}
                  maxLength={10}
                  pattern="[0-9]{10}"
                  required
                />
                {phoneError && (
                  <div className="invalid-feedback">
                    {phoneError}
                  </div>
                )}
                <div className="form-text">
                  {phoneError ? '' : 'Ingrese exactamente 10 dígitos. Este número es necesario para confirmar su pedido.'}
                </div>
              </div>
              
              <div className="row mb-3">
                <div className="col-md-6 mb-3 mb-md-0">
                  <label htmlFor="firstName" className="form-label">Nombre (Opcional)</label>
                  <input 
                    type="text" 
                    className="form-control" 
                    id="firstName" 
                    placeholder="Ingresa tu nombre" 
                    value={firstName}
                    onChange={handleFirstNameChange}
                  />
                </div>
                <div className="col-md-6">
                  <label htmlFor="lastName" className="form-label">Apellido (Opcional)</label>
                  <input 
                    type="text" 
                    className="form-control" 
                    id="lastName" 
                    placeholder="Ingresa tu apellido" 
                    value={lastName}
                    onChange={handleLastNameChange}
                  />
                </div>
              </div>
              <div className="mb-3">
                <label htmlFor="additionalInfo" className="form-label">Información Adicional (Opcional)</label>
                <textarea 
                  className="form-control" 
                  id="additionalInfo" 
                  rows={3} 
                  placeholder="Instrucciones especiales, comentarios o referencias" 
                  value={additionalInfo}
                  onChange={handleAdditionalInfoChange}
                ></textarea>
              </div>
            </div>
          </div>
        </div>

        {/* Order Summary */}
        <div className="col-lg-4">
          <div className="card border-0 shadow-sm rounded-3 sticky-top" style={{ top: "80px" }}>
            <div className="card-header bg-primary text-white py-3">
              <h5 className="mb-0 d-flex align-items-center">
                <i className="bi bi-receipt me-2"></i>
                Resumen de tu Compra
              </h5>
            </div>
            <div className="card-body p-4">
              <div className="d-flex justify-content-between mb-3">
                <span className="text-muted">Subtotal</span>
                <span className="fw-bold">${total.toFixed(2)}</span>
              </div>
              
              {discount > 0 && (
                <div className="d-flex justify-content-between mb-3 text-success">
                  <span>Descuento ({discount}%)</span>
                  <span className="fw-bold">-${(total * (discount / 100)).toFixed(2)}</span>
                </div>
              )}
              
              <div className="d-flex justify-content-between mb-3 border-bottom pb-3">
                <span className="text-muted">Método de Pago</span>
                <span className="fw-bold">
                  {paymentMethod === 'efectivo' ? (
                    <span><i className="bi bi-cash me-1"></i> Efectivo</span>
                  ) : (
                    <span><i className="bi bi-credit-card me-1"></i> Tarjeta</span>
                  )}
                </span>
              </div>
              
              <div className="d-flex justify-content-between fw-bold mb-4">
                <span className="fs-5">Total</span>
                <span className="fs-4 text-primary">${(total - (discount > 0 ? total * (discount / 100) : 0)).toFixed(2)}</span>
              </div>
              
              <div className="d-grid gap-2">
                <button
                  className="btn btn-outline-secondary"
                  onClick={() => navigate('/cart')}
                >
                  <i className="bi bi-arrow-left me-2"></i>
                  Volver al Carrito
                </button>
                
                <button 
                  className="btn btn-primary py-3 fw-bold"
                  onClick={procesarPedido}
                  disabled={isProcessing || !contactPhone.trim() || phoneError !== ''}
                >
                  {isProcessing ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Procesando...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-check-circle me-2"></i>
                      Confirmar y Pagar
                    </>
                  )}
                </button>
              </div>
              
              <div className="alert alert-info mt-3 p-2 text-center small">
                <i className="bi bi-info-circle-fill me-1"></i>
                <strong>Nota:</strong> Al confirmar, aceptas nuestros términos y condiciones para la entrega.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderSummaryPage; 