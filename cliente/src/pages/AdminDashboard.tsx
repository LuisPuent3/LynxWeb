import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import Dashboard from '../components/admin/Dashboard';
import SimpleImageUploader from '../components/products/SimpleImageUploader';

// Utilidad para obtener teléfonos de usuarios conocidos
const obtenerTelefonoUsuario = async (idUsuario: number, email?: string): Promise<string> => {
  // Mapeo de IDs de usuario a teléfonos conocidos
  const telefonosConocidos: {[key: number]: string} = {
    // Administradores
    68: "5551234567",
    3: "5551234568",
    // Usuarios regulares
    72: "5552345678",
    11: "5553456789",
    19: "5559876543",
    // Añadir más usuarios aquí según sea necesario
  };
  
  // Mapeo de correos a teléfonos (para casos donde conocemos el email pero no el ID)
  const telefonosPorEmail: {[key: string]: string} = {
    "admin@lynxshop.com": "5554567890",
    "emergencia@test.com": "5557654321",
    "emergencia2@test.com": "5558765432",
    // Añadir más emails conocidos aquí
  };
  
  try {
    // Primero intentar obtener desde la API
    const response = await api.get(`/auth/telefono/${idUsuario}`);
    console.log(`Teléfono obtenido desde API para usuario ${idUsuario}:`, response.data);
    return response.data.telefono || "No disponible";
  } catch (error) {
    console.error(`Error al obtener teléfono desde la API para usuario ${idUsuario}:`, error);
    
    // Si falla la API, intentar obtener por ID desde nuestro fallback
    if (telefonosConocidos[idUsuario]) {
      return telefonosConocidos[idUsuario];
    }
    
    // Si no se encuentra por ID, intentar por email
    if (email && telefonosPorEmail[email]) {
      return telefonosPorEmail[email];
    }
    
    // Valor por defecto si no se encuentra
    return "No disponible";
  }
};

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
  correo?: string;
  esClienteRegistrado?: boolean;
  nombre_usuario?: string;
  telefono_usuario?: string;
  correo_usuario?: string;
  rol?: string;
  id_rol?: number;
  telefono?: string;
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
  id_rol?: number;
  fecha_registro: string;
}

// Componente separado para el modal de detalles del pedido
const OrderDetailModal: React.FC<{
  selectedOrder: Pedido | null;
  isLoading: boolean;
  isLoadingUserData: boolean;
  onClose: () => void;
  onStatusChange: (id: number, status: string) => void;
}> = ({ selectedOrder, isLoading, isLoadingUserData, onClose, onStatusChange }) => {
  if (!selectedOrder) return null;

  // Definir estilo CSS para la animación del modal
  const fadeInAnimation = {
    animation: 'fadeIn 0.3s',
    WebkitAnimation: 'fadeIn 0.3s'
  };
  
  console.log('Modal - Datos del pedido completo:', selectedOrder);
  
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
                <h5 className="modal-title">
                  <i className="bi bi-info-circle me-2"></i>
                  Detalles del Pedido #{selectedOrder.id_pedido}
                </h5>
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
                    {/* Información del pedido y cliente */}
                    <div className="card border mb-3">
                      <div className="card-header bg-light py-2">
                        <h6 className="mb-0">
                          <i className="bi bi-card-checklist me-2"></i>
                          Información General
                        </h6>
                      </div>
                      <div className="card-body">
                        <div className="row">
                          {/* Información del pedido - Columna izquierda */}
                          <div className="col-md-6">
                            <h6 className="border-bottom pb-2 mb-3">
                              <i className="bi bi-box me-2"></i>
                              Datos del Pedido
                            </h6>
                            <p>
                              <strong><i className="bi bi-hash me-1"></i>ID Pedido:</strong> {selectedOrder.id_pedido}
                            </p>
                            <p>
                              <strong><i className="bi bi-calendar me-1"></i>Fecha:</strong> {new Date(selectedOrder.fecha).toLocaleDateString()} {new Date(selectedOrder.fecha).toLocaleTimeString()}
                            </p>                            <p>
                              <strong><i className="bi bi-tag me-1"></i>Estado:</strong> 
                              <span className={`badge ms-2 ${
                                selectedOrder.estado === 'pendiente' ? 'bg-warning' :
                                selectedOrder.estado === 'aceptado' ? 'bg-info' :
                                selectedOrder.estado === 'entregado' ? 'bg-success' :
                                selectedOrder.estado === 'cancelado' ? 'bg-danger' : 'bg-secondary'
                              }`}>
                                {selectedOrder.estado_nombre || selectedOrder.estado}
                              </span>
                            </p>
                            <p><strong><i className="bi bi-credit-card me-1"></i>Método de Pago:</strong> {selectedOrder.metodo_pago || 'Efectivo'}</p>
                            <p><strong><i className="bi bi-info-circle me-1"></i>Información adicional:</strong> {selectedOrder.informacion_adicional || 'N/A'}</p>
                          </div>
                          
                          {/* Información del cliente - Columna derecha */}
                          <div className="col-md-6">
                            <h6 className="border-bottom pb-2 mb-3">
                              <i className="bi bi-person me-2"></i>
                              Datos del Cliente
                            </h6>
                            
                            {/* ID Usuario */}
                            <p>
                              <strong><i className="bi bi-person-badge me-1"></i>ID Usuario:</strong> {selectedOrder.id_usuario}
                            </p>
                            
                            {/* Rol/Tipo de usuario si está disponible */}
                            {(selectedOrder.rol || selectedOrder.id_rol) && (
                              <p>
                                <strong><i className="bi bi-person-check me-1"></i>Rol:</strong> {selectedOrder.rol || `ID Rol: ${selectedOrder.id_rol}`}
                              </p>
                            )}
                            
                            {/* Nombre - de tabla usuarios o del pedido */}
                            <p>
                              <strong><i className="bi bi-person-circle me-1"></i>Nombre:</strong> {selectedOrder.nombre_usuario || 'No disponible'}
                            </p>
                            
                            {/* Correo electrónico */}
                            <p>
                              <strong><i className="bi bi-envelope me-1"></i>Correo:</strong> {selectedOrder.correo_usuario || selectedOrder.correo || selectedOrder.usuario || 'No disponible'}
                            </p>
                            
                            {/* Mostrar teléfono de la tabla usuarios siempre */}
                            <p>
                              <strong><i className="bi bi-telephone me-1"></i>Teléfono:</strong> {
                                isLoadingUserData ? (
                                  <span>
                                    <small className="spinner-border spinner-border-sm text-secondary me-1" role="status">
                                      <span className="visually-hidden">Cargando...</span>
                                    </small>
                                    Obteniendo...
                                  </span>
                                ) : (
                                  selectedOrder.telefono_usuario || 'No disponible'
                                )
                              } 
                            </p>
                            
                            {/* Teléfono de contacto del pedido */}
                            {selectedOrder.telefono_contacto && (
                              <p>
                                <strong><i className="bi bi-phone me-1"></i>Teléfono Invitado:</strong> {selectedOrder.telefono_contacto}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <h6 className="border-bottom pb-2 mb-3">
                      <i className="bi bi-cart me-2"></i>
                      Productos
                    </h6>
                    <div className="table-responsive">
                      <table className="table table-sm table-hover">
                        <thead className="table-light">
                          <tr>
                            <th><i className="bi bi-bag me-1"></i>Producto</th>
                            <th><i className="bi bi-123 me-1"></i>Cantidad</th>
                            <th><i className="bi bi-currency-dollar me-1"></i>Precio</th>
                            <th><i className="bi bi-calculator me-1"></i>Subtotal</th>
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
                                <i className="bi bi-inbox text-secondary me-2"></i>
                                No hay productos en este pedido
                              </td>
                            </tr>
                          ) : (
                            selectedOrder.productos.map((producto, index) => (
                              <tr key={index}>
                                <td><i className="bi bi-box text-primary me-1"></i>{producto.nombre}</td>
                                <td>{producto.cantidad}</td>
                                <td>${typeof producto.precio === 'number' ? producto.precio.toFixed(2) : producto.precio}</td>
                                <td className="fw-bold">${(producto.cantidad * (typeof producto.precio === 'number' ? producto.precio : parseFloat(String(producto.precio)))).toFixed(2)}</td>
                              </tr>
                            ))
                          )}
                        </tbody>
                        <tfoot className="table-light">
                          <tr>
                            <th colSpan={3} className="text-end"><i className="bi bi-wallet2 me-1"></i>Total:</th>
                            <th className="text-primary">${typeof selectedOrder.total === 'number' ? selectedOrder.total.toFixed(2) : selectedOrder.total || '(calculando)'}</th>
                          </tr>
                        </tfoot>
                      </table>
                    </div>
                  </div>
                )}
              </div>              {selectedOrder.estado === 'pendiente' && !isLoading && (
                <div className="alert alert-info mb-0 mt-3" role="alert">
                  <i className="bi bi-info-circle me-2"></i>
                  <small>Al entregar se actualizará el inventario de productos. El stock se descuenta únicamente cuando el pedido se marca como entregado.</small>
                </div>
              )}              <div className="modal-footer" style={{ borderTop: '1px solid #dee2e6', backgroundColor: '#f8f9fa' }}>
                <button type="button" className="btn btn-outline-secondary" onClick={onClose}>
                  <i className="bi bi-x-circle me-1"></i>
                  Cerrar
                </button>
                {selectedOrder.estado === 'pendiente' && !isLoading && (
                  <>
                    <button 
                      type="button"
                      className="btn btn-info"
                      onClick={() => onStatusChange(selectedOrder.id_pedido, 'aceptado')}
                    >
                      <i className="bi bi-check2-circle me-1"></i>
                      Aceptar Pedido
                    </button>
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
  const [searchProductId, setSearchProductId] = useState<string>(""); // Estado para búsqueda de productos por ID
  const [searchOrderId, setSearchOrderId] = useState<string>(""); // Estado para búsqueda de pedidos por ID
  const [searchPhoneNumber, setSearchPhoneNumber] = useState<string>(""); // Estado para búsqueda de pedidos por teléfono
  const [loadingOrderDetails, setLoadingOrderDetails] = useState<boolean>(false);
  const [orderDetailsCache, setOrderDetailsCache] = useState<{[key: number]: boolean}>({});
  const [selectedOrder, setSelectedOrder] = useState<Pedido | null>(null);
  const [showDetailModal, setShowDetailModal] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [loadingUserData, setLoadingUserData] = useState<boolean>(false);
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
  
  // Agregar nuevo estado para rastrear si la imagen ha sido subida
  const [isImageUploaded, setIsImageUploaded] = useState(false);
  
  // Nuevo estado para el filtro de categoría en productos
  const [categoryFilter, setCategoryFilter] = useState<number | null>(null);
  
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
        console.log('Pedidos recibidos de la API:', pedidosRes.data);
        
        // Simplemente guardar los pedidos tal como vienen
        setPedidos(pedidosRes.data);
        setPedidosFiltrados(pedidosRes.data);
        
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
      setError(null);
      
      // Verificar que la imagen ha sido subida
      if (!isImageUploaded && !isEditing) {
        setError('Debes subir una imagen antes de guardar el producto');
        return;
      }
      
      if (isEditing) {
        // Actualizar producto
        await api.put(`/productos/${formData.id_producto}`, formData);
        // Actualizar la lista de productos
        setProductos(productos.map(p => 
          p.id_producto === formData.id_producto ? {...formData} : p
        ));
        setSuccessMessage('¡Producto actualizado correctamente!');
      } else {
        // Crear nuevo producto
        const response = await api.post('/productos', formData);
        setProductos([...productos, response.data]);
        setSuccessMessage('¡Producto creado correctamente!');
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
      setIsImageUploaded(false);
      
      // Cambiar a la pestaña de productos para ver el resultado
      setActiveTab('products');
      
      // Limpiar el mensaje después de 3 segundos
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err: any) {
      console.error('Error al guardar producto:', err);
      
      // Manejar errores específicos de la API
      if (err.response) {
        const statusCode = err.response.status;
        const errorData = err.response.data;
        
        if (statusCode === 400) {
          // Error de validación
          if (errorData.code === 'DUPLICATE_NAME') {
            setError('Ya existe un producto con este nombre. Por favor, usa un nombre diferente.');
          } else {
            setError(errorData.error || 'Error de validación en los datos del producto.');
          }
        } else {
          // Otros errores
          setError('Error al guardar el producto. Por favor, intenta de nuevo.');
        }
      } else if (err.request) {
        // Error de conexión
        setError('No se pudo conectar con el servidor. Verifica tu conexión a internet.');
      } else {
        // Error inesperado
        setError('Error al guardar el producto. Por favor, intenta de nuevo.');
      }
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
    setIsImageUploaded(true); // Asumimos que el producto existente ya tiene imagen
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
    }  };
  
  // Cambiar estado de pedido
  const handleOrderStatus = async (id: number, status: string) => {
    try {
      // Determinar el id_estado basado en el status
      const id_estado = 
        status === 'entregado' ? 2 : 
        status === 'cancelado' ? 3 : 
        status === 'aceptado' ? 4 : 1; // 1 = pendiente, 2 = entregado, 3 = cancelado, 4 = aceptado
      
      // Mostrar mensaje de carga para operaciones que pueden tardar
      if (status === 'entregado') {
        setSuccessMessage("Actualizando inventario, por favor espere...");
      } else if (status === 'aceptado') {
        setSuccessMessage("Aceptando pedido, por favor espere...");
      }
      
      const response = await api.put(`/pedidos/${id}`, { estado: status, id_estado });
      
      // Actualizar el estado en la lista de pedidos
      const updatedPedidos = pedidos.map(p => 
        p.id_pedido === id ? {...p, estado: status, estado_nombre: status} : p
      );
      
      setPedidos(updatedPedidos);
      // También actualizar los pedidos filtrados
      setPedidosFiltrados(
        filtroEstado === 'todos'
          ? updatedPedidos
          : updatedPedidos.filter(p => p.estado === filtroEstado)
      );
        // Mostrar mensaje de éxito específico
      setError(null);
      const successMsg = status === 'entregado' 
        ? 'Pedido marcado como entregado y stock actualizado.' 
        : status === 'aceptado'
        ? 'Pedido aceptado correctamente.'
        : `Pedido marcado como ${status}.`;
      
      setSuccessMessage(successMsg);
      
      // Limpiar el mensaje de éxito después de 3 segundos
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err: any) {
      console.error('Error al actualizar pedido:', err);
      
      // Mostrar mensaje de error más específico
      if (err.code === 'ECONNABORTED') {
        setError('La operación tardó demasiado tiempo. Intente nuevamente.');
      } else if (err.response && err.response.data && err.response.data.error) {
        setError(`Error: ${err.response.data.error}`);
      } else {
        setError('Error al actualizar el estado del pedido. Intente nuevamente.');
      }
    }
  };

  // Función para manejar el filtro de pedidos
  const handleOrderFilter = useCallback((filtro: string) => {
    setFiltroEstado(filtro);
    
    // Filtrar por estado seleccionado
    const pedidosFiltradosPorEstado = filtro === 'todos' 
      ? pedidos 
      : pedidos.filter(p => 
          p.estado?.toLowerCase() === filtro || 
          p.estado_nombre?.toLowerCase() === filtro
        );
    
    setPedidosFiltrados(pedidosFiltradosPorEstado);
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
        // Mostrar mensaje de éxito
        setSuccessMessage(`¡La categoría "${categoriaForm.nombre}" ha sido actualizada correctamente!`);
      } else {
        // Crear nueva categoría
        const response = await api.post('/categorias', categoriaForm);
        setCategorias([...categorias, response.data]);
        // Mostrar mensaje de éxito
        setSuccessMessage(`¡La categoría "${categoriaForm.nombre}" ha sido creada correctamente!`);
      }
      
      // Resetear formulario
      setCategoriaForm({
        id_categoria: 0,
        nombre: '',
        descripcion: ''
      });
      setIsEditingCategoria(false);
      
      // Redirigir a la vista de categorías
      setActiveTab('categories');
      
      // Configurar un temporizador para quitar el mensaje después de unos segundos
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err) {
      console.error('Error al guardar categoría:', err);
      setError('Error al guardar la categoría. Por favor, intenta de nuevo.');
      
      // Configurar un temporizador para quitar el mensaje de error
      setTimeout(() => {
        setError(null);
      }, 3000);
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
      
      // Configurar un temporizador para quitar el mensaje de error
      setTimeout(() => {
        setError(null);
      }, 3000);
      return;
    }
    
    if (window.confirm('¿Estás seguro de eliminar esta categoría?')) {
      try {
        // Encontrar el nombre de la categoría antes de eliminarla
        const categoriaAEliminar = categorias.find(c => c.id_categoria === id);
        const nombreCategoria = categoriaAEliminar?.nombre || 'La categoría';
        
        await api.delete(`/categorias/${id}`);
        setCategorias(categorias.filter(c => c.id_categoria !== id));
        
        // Mostrar mensaje de éxito
        setSuccessMessage(`${nombreCategoria} ha sido eliminada correctamente`);
        
        // Configurar un temporizador para quitar el mensaje
        setTimeout(() => {
          setSuccessMessage(null);
        }, 3000);
      } catch (err) {
        console.error('Error al eliminar categoría:', err);
        setError('Error al eliminar la categoría. Por favor, intenta de nuevo.');
        
        // Configurar un temporizador para quitar el mensaje de error
        setTimeout(() => {
          setError(null);
        }, 3000);
      }
    }
  };

  // Función para cerrar el modal
  const closeDetailModal = () => {
    setSelectedOrder(null);
    setShowDetailModal(false);
  };

  // Función para cargar los detalles de un pedido
  const handleViewOrderDetails = async (id: number) => {
    try {
      // Si ya tenemos los detalles completos en caché, solo mostrarlos
      if (orderDetailsCache[id]) {
        const order = pedidos.find(p => p.id_pedido === id);
        if (order) {
          setSelectedOrder(order);
          setShowDetailModal(true);
          return;
        }
      }

      // Necesitamos cargar los detalles, mostrar loading
      setLoadingOrderDetails(true);
      setShowDetailModal(true);
      
      try {
        // Obtener detalles del pedido
        const { data } = await api.get(`/pedidos/detalle/${id}`);
        
        if (!data) {
          throw new Error('No se recibieron datos del pedido');
        }
        
        console.log('Respuesta API - Detalles del pedido:', data);
        
        // Extraer datos básicos
        const order = data;
        
        // Nombre completo para mostrar - Intentar usar el nombre completo del pedido primero
        let nombreUsuario = order.nombre_completo || '';
        
        // Si no hay nombre en el pedido, intentar usar el nombre del usuario si existe
        if (!nombreUsuario && order.usuario) {
          nombreUsuario = order.usuario.split('@')[0];
        }
        
        // Preparar objeto con detalles completos
        let completeOrderDetails = {
          ...order,
          // Asignar campos específicos para la información de usuario
          nombre_usuario: nombreUsuario,
          correo_usuario: order.usuario || order.correo || 'No disponible'
        };
        
        console.log('Datos detallados del pedido:', completeOrderDetails);
        
        // Si tiene un id_usuario, identificar su rol y obtener datos del usuario
        if (order.id_usuario && order.id_usuario > 0) {
          // Determinar el rol basado en el usuario - Según la base de datos:
          // id_rol = 1: Cliente, id_rol = 2: Usuario, id_rol = 3: Administrador
          let rol = 'Cliente';
          let idRol = 1;
          
          // Admin tiene correo admin@lynxshop.com o id_rol = 3
          if (order.id_rol === 3 || order.usuario === 'admin@lynxshop.com') {
            rol = 'Administrador';
            idRol = 3;
          } 
          // Guest users tienen correo que empieza con guest_
          else if (order.usuario?.includes('guest_')) {
            rol = 'Invitado';
            idRol = 2;
          }
          
          // Activar estado de carga para datos de usuario
          setLoadingUserData(true);
          
          try {
            // Obtener teléfono del usuario desde nuestra utilidad
            const telefonoUsuario = await obtenerTelefonoUsuario(order.id_usuario, order.usuario);
            
            completeOrderDetails = {
              ...completeOrderDetails,
              id_rol: order.id_rol || idRol,
              rol: rol,
              // Cada teléfono en su lugar correspondiente
              telefono_usuario: telefonoUsuario,
              // Mantenemos el teléfono de contacto tal como viene del pedido
              telefono_contacto: order.telefono_contacto || 'No proporcionado'
            };
            
            console.log('Datos finales con rol y teléfono:', {
              rol: rol,
              id_rol: idRol,
              telefono: telefonoUsuario
            });
          } catch (phoneError) {
            console.error('Error al obtener teléfono desde la API:', phoneError);
            
            completeOrderDetails = {
              ...completeOrderDetails,
              id_rol: order.id_rol || idRol,
              rol: rol,
              telefono_usuario: 'No disponible',
              telefono_contacto: order.telefono_contacto || 'No proporcionado'
            };
          } finally {
            // Desactivar estado de carga para datos de usuario
            setLoadingUserData(false);
          }
        }
        
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
        
        // Actualizar el pedido seleccionado
        setSelectedOrder(completeOrderDetails);
        
        // Marcar como cargado en caché
        setOrderDetailsCache(prev => ({...prev, [id]: true}));
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
                ) : error ? (          <div className="alert alert-danger">{error}</div>        ) : successMessage ? (          <div className="alert alert-success">{successMessage}</div>        ) : (
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
                              {pedidos.slice(0, 5).map((pedido) => (                                <tr key={pedido.id_pedido}>
                                  <td>#{pedido.id_pedido}</td>
                                  <td>{pedido.usuario || pedido.nombre_completo || 'Usuario'}</td>
                                  <td>{new Date(pedido.fecha).toLocaleDateString()}</td>
                                  <td>
                                    <span className={`badge ${
                                      pedido.estado === 'pendiente' ? 'bg-warning' :
                                      pedido.estado === 'aceptado' ? 'bg-info' :
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
                <div className="card-header bg-white d-flex justify-content-between align-items-center py-2">
                  <h5 className="mb-0">Gestión de Productos</h5>
                  <div className="d-flex gap-2">
                    <div className="input-group input-group-sm" style={{ maxWidth: '400px' }}>
                      <input
                        type="text"
                        className="form-control form-control-sm"
                        placeholder="ID..."
                        value={searchProductId}
                        onChange={(e) => setSearchProductId(e.target.value)}
                        style={{ height: '31px' }}
                      />
                      <select 
                        className="form-select form-select-sm"
                        style={{ height: '31px', fontSize: '0.875rem' }}
                        onChange={(e) => setCategoryFilter(e.target.value === "all" ? null : Number(e.target.value))}
                        value={categoryFilter === null ? "all" : categoryFilter}
                      >
                        <option value="all">Todas las categorías</option>
                        {categorias.map(cat => (
                          <option key={cat.id_categoria} value={cat.id_categoria}>
                            {cat.nombre}
                          </option>
                        ))}
                      </select>
                    </div>                    <button 
                      className="btn btn-primary btn-sm"
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
                        setIsImageUploaded(false);
                        setActiveTab('products-form');
                      }}
                      style={{ fontSize: '0.85rem', padding: '0.25rem 0.6rem' }}
                    >
                      <i className="bi bi-plus-circle me-1"></i>
                      Nuevo Producto
                    </button>
                  </div>
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
                        {productos
                          .filter(producto => 
                            // Filtrar por ID si hay texto en la búsqueda
                            (searchProductId === "" || producto.id_producto.toString().includes(searchProductId)) &&
                            // Filtrar por categoría si hay una seleccionada
                            (categoryFilter === null || producto.id_categoria === categoryFilter)
                          )
                          .map(producto => (
                          <tr key={producto.id_producto}>
                            <td>{producto.id_producto}</td>
                            <td>
                              <div className="d-flex align-items-center">
                                <div className="me-3 bg-light rounded p-2 text-center" style={{width: "50px", height: "50px", overflow: "hidden"}}>
                                  {producto.imagen && producto.imagen !== 'default.jpg' ? (                                    <img 
                                      src={`/uploads/${producto.imagen}`} 
                                      alt={producto.nombre}
                                      style={{width: "100%", height: "100%", objectFit: "cover"}}
                                      onError={(e) => {
                                        (e.target as HTMLImageElement).style.display = 'none';
                                        e.currentTarget.parentElement!.innerHTML = '<i class="bi bi-box text-primary" style="font-size: 1.5rem"></i>';
                                      }}
                                    />
                                  ) : (
                                    <i className="bi bi-box text-primary" style={{fontSize: "1.5rem"}}></i>
                                  )}
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
                          setIsImageUploaded(true);
                        }}
                      />
                    </div>
                    
                    <div className="d-flex gap-2">
                      <button 
                        type="submit" 
                        className="btn btn-primary"
                        disabled={!formData.nombre || !formData.precio || formData.cantidad < 0 || (!isEditing && !isImageUploaded)}
                      >
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
                  <div>
                    <h5 className="card-title mb-1">Gestión de Pedidos</h5>
                    <p className="text-muted small mb-0">
                      <i className="bi bi-info-circle me-1"></i>
                      El inventario se actualiza automáticamente cuando un pedido se marca como "entregado"
                    </p>
                  </div>
                  <div className="d-flex align-items-center gap-2">
                    <div className="input-group input-group-sm" style={{ maxWidth: '350px' }}>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="ID..."
                        value={searchOrderId}
                        onChange={(e) => setSearchOrderId(e.target.value)}
                      />
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Teléfono..."
                        value={searchPhoneNumber}
                        onChange={(e) => setSearchPhoneNumber(e.target.value)}
                      />                      <select className="form-select" 
                        value={filtroEstado}
                        onChange={(e) => handleOrderFilter(e.target.value)}
                      >
                        <option value="todos">Todos</option>
                        <option value="pendiente">Pendiente</option>
                        <option value="aceptado">Aceptado</option>
                        <option value="entregado">Entregado</option>
                        <option value="cancelado">Cancelado</option>
                      </select>
                    </div>
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
                          {pedidosFiltrados
                            .filter(pedido => 
                              // Filtrar por ID de pedido si hay búsqueda
                              (searchOrderId === "" || 
                                pedido.id_pedido.toString().includes(searchOrderId)) &&
                              // Filtrar por número de teléfono (cualquiera de los campos que puedan contener teléfono)
                              (searchPhoneNumber === "" || 
                                (pedido.telefono_contacto && pedido.telefono_contacto.includes(searchPhoneNumber)) ||
                                (pedido.telefono_usuario && pedido.telefono_usuario.includes(searchPhoneNumber)) ||
                                (pedido.telefono && pedido.telefono.includes(searchPhoneNumber)))
                            )
                            .map((pedido) => (
                            <tr key={pedido.id_pedido}>
                              <td>#{pedido.id_pedido}</td>                              <td>{pedido.usuario || pedido.nombre_completo || 'Usuario'}</td>
                              <td>{new Date(pedido.fecha).toLocaleDateString()}</td>
                              <td>
                                <span className={`badge ${
                                  pedido.estado === 'pendiente' ? 'bg-warning' :
                                  pedido.estado === 'aceptado' ? 'bg-info' :
                                  pedido.estado === 'entregado' ? 'bg-success' :
                                  pedido.estado === 'cancelado' ? 'bg-danger' : 'bg-secondary'
                                }`}>
                                  {pedido.estado_nombre || pedido.estado}
                                </span>
                              </td>
                              <td>${typeof pedido.total === 'number' ? pedido.total.toFixed(2) : pedido.total || '(calculando)'}</td>
                              <td>                                <div className="btn-group">
                                  {/* Botón Ver Detalles */}
                                  <button 
                                    className="btn btn-sm btn-outline-primary" 
                                    onClick={() => handleViewOrderDetails(pedido.id_pedido)}
                                  >
                                    <i className="bi bi-eye me-1"></i>
                                    Ver
                                  </button>
                                  {pedido.estado === 'pendiente' && (
                                    <button 
                                      className="btn btn-sm btn-outline-info"
                                      onClick={() => handleOrderStatus(pedido.id_pedido, 'aceptado')}
                                    >
                                      <i className="bi bi-check2-circle me-1"></i>
                                      Aceptar
                                    </button>
                                  )}
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
          isLoadingUserData={loadingUserData}
          onClose={closeDetailModal}
          onStatusChange={handleOrderStatusFromModal}
        />
      )}
    </div>
  );
};

export default AdminDashboard;
