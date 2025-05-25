import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Producto } from '../../types/types';

interface OrderConfirmationProps {
  isProcessing: boolean;
  isCompleted: boolean;
  orderId?: number | null;
  cartItems: Array<Producto & { cantidad: number }>;
  total: number;
  discount?: number;
  onViewOrders?: () => void;
  onContinueShopping?: () => void;
}

const OrderConfirmation: React.FC<OrderConfirmationProps> = ({
  isProcessing,
  isCompleted,
  orderId,
  cartItems,
  total,
  discount = 0,
  onViewOrders,
  onContinueShopping
}) => {
  const navigate = useNavigate();

  // Handler para ver pedidos
  const handleViewOrders = () => {
    if (onViewOrders) {
      onViewOrders();
    } else {
      navigate('/pedidos');
    }
  };

  // Handler para continuar comprando
  const handleContinueShopping = () => {
    if (onContinueShopping) {
      onContinueShopping();
    } else {
      navigate('/');
    }
  };

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-10 col-lg-8">
          {/* Tarjeta principal */}
          <div className="card border-0 shadow-sm rounded-3 overflow-hidden">
            {/* Encabezado de la tarjeta */}
            <div className="card-header bg-primary text-white py-4 border-0">
              <h4 className="mb-0 d-flex align-items-center">
                <i className="bi bi-cart-check-fill me-2"></i>
                {isProcessing 
                  ? 'Procesando su pedido...' 
                  : isCompleted 
                    ? '¡Pedido Confirmado!' 
                    : 'Resumen de Pedido'}
              </h4>
            </div>
            
            {/* Cuerpo de la tarjeta */}
            <div className="card-body p-4">
              {/* Estado de carga */}
              {isProcessing && (
                <div className="text-center py-5">
                  <div className="spinner-border text-primary" style={{ width: '3rem', height: '3rem' }} role="status">
                    <span className="visually-hidden">Cargando...</span>
                  </div>
                  <h5 className="mt-4 text-muted">Procesando su pedido, por favor espere...</h5>
                  <div className="progress mt-4" style={{ height: '6px' }}>
                    <div className="progress-bar progress-bar-striped progress-bar-animated bg-primary" 
                      role="progressbar" 
                      style={{ width: '100%' }}>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Confirmación completada */}
              {!isProcessing && isCompleted && (
                <div className="text-center py-4">
                  <div className="bg-success bg-opacity-10 text-success p-3 rounded-circle mx-auto mb-4" style={{ width: '90px', height: '90px' }}>
                    <i className="bi bi-check-circle-fill fs-1"></i>
                  </div>
                  <h4 className="mb-2 text-success">Pedido Realizado con Éxito</h4>                  <p className="text-muted mb-1">Su pedido #{orderId} ha sido confirmado</p>
                  <p className="text-muted">Gracias por comprar en LynxShop</p>
                  <p className="text-info mb-4">
                    <small>
                      <i className="bi bi-info-circle me-1"></i>
                      El inventario se actualizará cuando su pedido sea entregado
                    </small>
                  </p>
                  
                  <div className="d-flex justify-content-center gap-3 mt-4">
                    <button 
                      className="btn btn-outline-primary px-4 py-2"
                      onClick={handleViewOrders}
                    >
                      <i className="bi bi-list-ul me-2"></i>
                      Ver mis pedidos
                    </button>
                    <button 
                      className="btn btn-primary px-4 py-2"
                      onClick={handleContinueShopping}
                    >
                      <i className="bi bi-cart me-2"></i>
                      Seguir comprando
                    </button>
                  </div>
                </div>
              )}
              
              {/* Detalles del pedido (siempre visible) */}
              {(!isProcessing || !isCompleted) && (
                <>
                  <h5 className="mb-3 border-bottom pb-2">
                    <i className="bi bi-box me-2 text-primary"></i>
                    Productos en su pedido
                  </h5>
                  <div className="table-responsive mb-4">
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
                        {cartItems.map((item) => (
                          <tr key={item.id_producto}>
                            <td>
                              <div className="d-flex align-items-center">
                                {item.imagen ? (                                  <img
                                    src={`/uploads/${item.imagen}?v=${item.id_producto}`}
                                    alt={item.nombre}
                                    className="img-fluid rounded shadow-sm me-3"
                                    style={{ 
                                      width: '100%', 
                                      height: 'auto',
                                      maxWidth: '50px',
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
                    </table>
                  </div>
                  
                  {/* Resumen de totales */}
                  <div className="bg-light p-4 rounded mb-3">
                    <div className="d-flex justify-content-between mb-2">
                      <span>Subtotal</span>
                      <span>${total.toFixed(2)}</span>
                    </div>
                    
                    {discount > 0 && (
                      <div className="d-flex justify-content-between mb-2 text-success">
                        <span>Descuento</span>
                        <span>-${((total * discount) / 100).toFixed(2)}</span>
                      </div>
                    )}
                    
                    <div className="d-flex justify-content-between border-top pt-2 mt-2">
                      <span className="fw-bold">Total</span>
                      <span className="fw-bold text-primary fs-5">
                        ${(total - (total * discount / 100)).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </>
              )}
            </div>
              {/* Footer con información adicional */}
            {isCompleted && (
              <div className="card-footer bg-light py-3 border-0">
                <div className="small text-muted text-center">
                  <i className="bi bi-info-circle me-1"></i>
                  Recibirá un correo electrónico con los detalles de su compra (próximamente)
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderConfirmation;