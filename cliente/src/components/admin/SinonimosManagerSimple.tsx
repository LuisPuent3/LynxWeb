import React, { useState, useEffect, useCallback } from 'react';
import { 
  Card, 
  Form, 
  Button, 
  Alert,
  Spinner,
  Modal
} from 'react-bootstrap';
import api from '../../utils/api';

// ================================================
// INTERFACES Y TIPOS
// ================================================

interface Sinonimo {
  id?: number;
  producto_id: number;
  sinonimo: string;
  popularidad?: number;
  precision_score?: number;
  fuente: string;
  activo?: boolean;
  fecha_creacion?: string;
  fecha_ultima_actualizacion?: string;
}

interface SugerenciaSinonimo {
  termino_busqueda: string;
  frecuencia: number;
  promedio_clicks: number;
  ultima_busqueda: string;
  tipo: string;
}

interface SinonimosManagerProps {
  productoId: number;
  productoNombre: string;
  visible?: boolean;
  onClose?: () => void;
}

// ================================================
// COMPONENTE PRINCIPAL
// ================================================

const SinonimosManager: React.FC<SinonimosManagerProps> = ({
  productoId,
  productoNombre,
  visible = true,
  onClose
}) => {
  // Estados principales
  const [sinonimos, setSinonimos] = useState<Sinonimo[]>([]);
  const [sugerencias, setSugerencias] = useState<SugerenciaSinonimo[]>([]);
  
  // Estados del formulario
  const [nuevoSinonimo, setNuevoSinonimo] = useState('');
  const [formValidation, setFormValidation] = useState({valid: true, message: ''});
  
  // Estados de carga
  const [loading, setLoading] = useState(false);
  const [loadingAdd, setLoadingAdd] = useState(false);
  
  // Estados del modal
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<{show: boolean, sinonimo?: Sinonimo}>({show: false});

  // ================================================
  // EFECTOS
  // ================================================

  useEffect(() => {
    if (visible && productoId) {
      cargarDatos();
    }
  }, [visible, productoId]);

  const cargarDatos = useCallback(async () => {
    await Promise.all([
      cargarSinonimos(),
      cargarSugerencias()
    ]);
  }, [productoId]);

  // ================================================
  // FUNCIONES DE API
  // ================================================

  const cargarSinonimos = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/admin/sinonimos/producto/${productoId}`);
      
      if (response.data) {
        setSinonimos(Array.isArray(response.data) ? response.data : []);
      } else {
        setSinonimos([]);
      }
    } catch (error: any) {
      console.error('Error al cargar sinónimos:', error.response?.data?.detail || error.message);
      setSinonimos([]);
    } finally {
      setLoading(false);
    }
  };

  const cargarSugerencias = async () => {
    try {
      const response = await api.get(`/admin/sinonimos/sugerencias/producto/${productoId}`);
      
      if (response.data) {
        setSugerencias(response.data.sugerencias || []);
      } else {
        setSugerencias([]);
      }
    } catch (error: any) {
      console.error('Error al cargar sugerencias:', error.response?.data || error.message);
      setSugerencias([]);
    }
  };

  const validarSinonimo = (sinonimo: string): {valid: boolean, message: string} => {
    if (!sinonimo.trim()) {
      return {valid: false, message: 'Ingrese un sinónimo válido'};
    }

    if (sinonimo.length < 2) {
      return {valid: false, message: 'El sinónimo debe tener al menos 2 caracteres'};
    }

    if (!/^[a-záéíóúñ\s]+$/i.test(sinonimo)) {
      return {valid: false, message: 'El sinónimo solo puede contener letras y espacios'};
    }

    // Verificar duplicados locales
    const sinonimoLower = sinonimo.trim().toLowerCase();
    if (sinonimos.some(s => s.sinonimo && s.sinonimo.toLowerCase() === sinonimoLower)) {
      return {valid: false, message: 'Este sinónimo ya existe para este producto'};
    }

    return {valid: true, message: ''};
  };

  const agregarSinonimo = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const validation = validarSinonimo(nuevoSinonimo);
    setFormValidation(validation);
    
    if (!validation.valid) {
      return;
    }

    try {
      setLoadingAdd(true);
      const response = await api.post('/admin/sinonimos', {
        producto_id: productoId,
        sinonimo: nuevoSinonimo.trim().toLowerCase(),
        fuente: 'admin'
      });

      if (response.data && response.data.success) {
        setNuevoSinonimo('');
        setFormValidation({valid: true, message: ''});
        await cargarSinonimos();
        
        // Actualizar sugerencias para remover la agregada
        setSugerencias(prev => prev.filter(s => s.termino_busqueda !== nuevoSinonimo.trim().toLowerCase()));
      } else {
        setFormValidation({valid: false, message: response.data?.detail || response.data?.message || 'Error al agregar sinónimo'});
      }
    } catch (error: any) {
      setFormValidation({valid: false, message: error.response?.data?.message || 'Error de conexión al agregar sinónimo'});
      console.error('Error:', error.response?.data || error.message);
    } finally {
      setLoadingAdd(false);
    }
  };

  const confirmarEliminarSinonimo = (sinonimo: Sinonimo) => {
    setShowDeleteConfirm({show: true, sinonimo});
  };

  const eliminarSinonimo = async () => {
    const sinonimo = showDeleteConfirm.sinonimo;
    if (!sinonimo) return;

    try {
      const response = await api.delete(`/admin/sinonimos/${sinonimo.id}`);

      if (response.data && response.data.success) {
        await cargarSinonimos();
      } else {
        console.error('Error al eliminar sinónimo:', response.data?.detail || response.data?.message);
      }
    } catch (error: any) {
      console.error('Error de conexión al eliminar sinónimo:', error.response?.data || error.message);
    } finally {
      setShowDeleteConfirm({show: false});
    }
  };

  // ================================================
  // RENDER
  // ================================================

  if (!visible) {
    return null;
  }

  return (
    <div className="sinonimos-manager">
      <Card className="mt-3 border-0 shadow-sm">
        <Card.Header className="bg-primary text-white d-flex justify-content-between align-items-center">
          <div>
            <h5 className="mb-0">
              <i className="bi bi-tags me-2"></i>
              Sinónimos: {productoNombre}
            </h5>
          </div>
          {onClose && (
            <Button variant="link" className="text-white p-0" onClick={onClose}>
              <i className="bi bi-x-lg"></i>
            </Button>
          )}
        </Card.Header>
        
        <Card.Body className="p-4">
          {/* FORMULARIO SIMPLE */}
          <div className="mb-4">
            <Form onSubmit={agregarSinonimo}>
              <div className="d-flex gap-2">
                <Form.Control
                  type="text"
                  placeholder="Agregar nuevo sinónimo (ej: gaseosa, refresco, bebida)"
                  value={nuevoSinonimo}
                  onChange={(e) => setNuevoSinonimo(e.target.value)}
                  disabled={loadingAdd}
                />
                <Button 
                  type="submit" 
                  variant="primary" 
                  disabled={loadingAdd || !nuevoSinonimo.trim()}
                >
                  {loadingAdd ? <Spinner size="sm" /> : 'Agregar'}
                </Button>
              </div>
              {!formValidation.valid && (
                <div className="text-danger mt-2 small">
                  <i className="bi bi-exclamation-triangle me-1"></i>
                  {formValidation.message}
                </div>
              )}
            </Form>
          </div>

          {/* LISTA DE SINÓNIMOS ACTUALES */}
          <div>
            <h6 className="text-muted mb-3">
              Sinónimos actuales ({sinonimos.length})
            </h6>
            
            {loading ? (
              <div className="text-center py-3">
                <Spinner animation="border" size="sm" className="me-2" />
                Cargando sinónimos...
              </div>
            ) : sinonimos.length === 0 ? (
              <Alert variant="light" className="text-center py-4">
                <i className="bi bi-tags text-muted" style={{fontSize: '2rem'}}></i>
                <div className="mt-2">No hay sinónimos configurados</div>
                <small className="text-muted">Agrega el primer sinónimo para este producto</small>
              </Alert>
            ) : (
              <div className="d-flex flex-wrap gap-2">
                {sinonimos.map((sinonimo) => (
                  <div 
                    key={sinonimo.id} 
                    className="d-flex align-items-center bg-light rounded-pill px-3 py-2"
                    style={{border: '1px solid #dee2e6'}}
                  >
                    <span className="me-2">{sinonimo.sinonimo}</span>
                    <Button
                      variant="link"
                      size="sm"
                      className="text-danger p-0 ms-1"
                      style={{fontSize: '0.8rem', lineHeight: 1}}
                      onClick={() => confirmarEliminarSinonimo(sinonimo)}
                      title="Eliminar sinónimo"
                    >
                      <i className="bi bi-x-circle"></i>
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* SUGERENCIAS RÁPIDAS */}
          {sugerencias.length > 0 && (
            <div className="mt-4">
              <h6 className="text-muted mb-2">
                <i className="bi bi-lightbulb text-warning me-1"></i>
                Sugerencias rápidas
              </h6>
              <div className="d-flex flex-wrap gap-2">
                {sugerencias.slice(0, 5).map((sugerencia, index) => (
                  <Button
                    key={index}
                    variant="outline-warning"
                    size="sm"
                    onClick={() => {
                      setNuevoSinonimo(sugerencia.termino_busqueda);
                    }}
                    title={`Frecuencia: ${sugerencia.frecuencia} búsquedas`}
                  >
                    + {sugerencia.termino_busqueda}
                  </Button>
                ))}
              </div>
            </div>
          )}
        </Card.Body>
      </Card>

      {/* MODAL DE CONFIRMACIÓN PARA ELIMINAR */}
      <Modal show={showDeleteConfirm.show} onHide={() => setShowDeleteConfirm({show: false})}>
        <Modal.Header closeButton>
          <Modal.Title>Confirmar eliminación</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          ¿Estás seguro que deseas eliminar el sinónimo <strong>"{showDeleteConfirm.sinonimo?.sinonimo}"</strong>?
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteConfirm({show: false})}>
            Cancelar
          </Button>
          <Button variant="danger" onClick={eliminarSinonimo}>
            Eliminar
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default SinonimosManager;
