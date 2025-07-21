/**
 * COMPONENTE DE GESTIÓN DE SINÓNIMOS PARA ADMIN PANEL
 * Interfaz orgánica para administrar sinónimos específicos por producto
 * 
 * Funcionalidades:
 * - Visualizar sinónimos existentes
 * - Agregar nuevos sinónimos
 * - Eliminar sinónimos
 * - Ver estadísticas de popularidad
 * - Sugerencias automáticas basadas en métricas
 * 
 * Autor: Sistema LCLN v2.0
 * Fecha: Julio 2025
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Card, 
  Form, 
  Button, 
  Badge, 
  Table, 
  Alert,
  Spinner,
  Row,
  Col,
  ButtonGroup,
  ProgressBar,
  Tooltip,
  OverlayTrigger,
  Modal
} from 'react-bootstrap';

// ================================================
// INTERFACES Y TIPOS
// ================================================

interface Sinonimo {
  id?: number;
  producto_id: number;
  sinonimo: string;
  popularidad: number;
  precision_score: number;
  fuente: 'admin' | 'auto_learning' | 'user_feedback';
  activo: boolean;
  fecha_creacion?: string;
  fecha_ultima_actualizacion?: string;
}

interface SugerenciaSinonimo {
  termino_busqueda: string;
  frecuencia: number;
  promedio_clicks: number;
  ultima_busqueda?: string;
  tipo?: string;
}

interface AtributoProducto {
  id?: number;
  producto_id: number;
  atributo: string;
  valor: boolean;
  intensidad: number;
}

interface SinonimosManagerProps {
  productoId: number;
  productoNombre: string;
  visible?: boolean;
  onClose?: () => void;
  apiBaseUrl?: string;
}

// ================================================
// COMPONENTE PRINCIPAL
// ================================================

const SinonimosManager: React.FC<SinonimosManagerProps> = ({
  productoId,
  productoNombre,
  visible = true,
  onClose,
  apiBaseUrl = '/api/admin/sinonimos'
}) => {
  // Estados principales
  const [sinonimos, setSinonimos] = useState<Sinonimo[]>([]);
  const [atributos, setAtributos] = useState<AtributoProducto[]>([]);
  const [sugerencias, setSugerencias] = useState<SugerenciaSinonimo[]>([]);
  
  // Estados de UI
  const [loading, setLoading] = useState(false);
  const [loadingAdd, setLoadingAdd] = useState(false);
  const [loadingSugerencias, setLoadingSugerencias] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<{show: boolean, sinonimo?: Sinonimo}>({show: false});
  
  // Estados de formulario
  const [nuevoSinonimo, setNuevoSinonimo] = useState('');
  const [formValidation, setFormValidation] = useState<{valid: boolean, message: string}>({valid: true, message: ''});

  // ================================================
  // EFECTOS Y CARGA DE DATOS
  // ================================================

  useEffect(() => {
    if (productoId && visible) {
      cargarDatos();
    }
  }, [productoId, visible]);

  const cargarDatos = useCallback(async () => {
    await Promise.all([
      cargarSinonimos(),
      cargarAtributos(),
      cargarSugerencias()
    ]);
  }, [productoId]);

  // ================================================
  // FUNCIONES DE API - SINÓNIMOS
  // ================================================

  const cargarSinonimos = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiBaseUrl}/producto/${productoId}`);
      
      if (response.ok) {
        const data = await response.json();
        setSinonimos(Array.isArray(data) ? data : []);
      } else {
        const error = await response.json();
        console.error('Error al cargar sinónimos:', error.detail || 'Error desconocido');
        setSinonimos([]);
      }
    } catch (error) {
      console.error('Error de conexión al cargar sinónimos:', error);
      setSinonimos([]);
    } finally {
      setLoading(false);
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
    if (sinonimos.some(s => s.sinonimo.toLowerCase() === sinonimoLower)) {
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
      const response = await fetch(apiBaseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          producto_id: productoId,
          sinonimo: nuevoSinonimo.trim().toLowerCase(),
          fuente: 'admin'
        })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setNuevoSinonimo('');
        setFormValidation({valid: true, message: ''});
        await cargarSinonimos();
        
        // Actualizar sugerencias para remover la agregada
        setSugerencias(prev => prev.filter(s => s.termino_busqueda !== nuevoSinonimo.trim().toLowerCase()));
      } else {
        setFormValidation({valid: false, message: result.detail || result.message || 'Error al agregar sinónimo'});
      }
    } catch (error) {
      setFormValidation({valid: false, message: 'Error de conexión al agregar sinónimo'});
      console.error('Error:', error);
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
      const response = await fetch(`${apiBaseUrl}/${sinonimo.id}`, {
        method: 'DELETE'
      });

      const result = await response.json();

      if (response.ok && result.success) {
        await cargarSinonimos();
      } else {
        console.error('Error al eliminar sinónimo:', result.detail || result.message);
      }
    } catch (error) {
      console.error('Error de conexión al eliminar sinónimo:', error);
    } finally {
      setShowDeleteConfirm({show: false});
    }
  };

  // ================================================
  // FUNCIONES DE API - ATRIBUTOS Y SUGERENCIAS
  // ================================================

  const cargarAtributos = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/producto/${productoId}/atributos`);
      
      if (response.ok) {
        const data = await response.json();
        setAtributos(Array.isArray(data) ? data : []);
      } else {
        setAtributos([]);
      }
    } catch (error) {
      console.error('Error cargando atributos:', error);
      setAtributos([]);
    }
  };

  const cargarSugerencias = async () => {
    try {
      setLoadingSugerencias(true);
      const response = await fetch(`${apiBaseUrl}/sugerencias/producto/${productoId}`);
      
      if (response.ok) {
        const data = await response.json();
        setSugerencias(data.sugerencias || []);
      } else {
        setSugerencias([]);
      }
    } catch (error) {
      console.error('Error cargando sugerencias:', error);
      setSugerencias([]);
    } finally {
      setLoadingSugerencias(false);
    }
  };

  const agregarSugerencia = (termino: string) => {
    setNuevoSinonimo(termino);
  };

  // ================================================
  // CÁLCULOS Y ESTADÍSTICAS
  // ================================================

  const estadisticas = {
    totalSinonimos: sinonimos.length,
    totalBusquedas: sinonimos.reduce((acc, s) => acc + s.popularidad, 0),
    precisionPromedio: sinonimos.length > 0 
      ? Math.round((sinonimos.reduce((acc, s) => acc + s.precision_score, 0) / sinonimos.length) * 100)
      : 0,
    masPopular: sinonimos.length > 0 
      ? sinonimos.reduce((max, s) => s.popularidad > max.popularidad ? s : max, sinonimos[0])
      : null
  };

  // ================================================
  // HELPERS DE RENDER
  // ================================================

  const getBadgeVariant = (fuente: string) => {
    switch (fuente) {
      case 'auto_learning': return 'info';
      case 'user_feedback': return 'warning';
      default: return 'primary';
    }
  };

  const getPopularidadColor = (valor: number) => {
    if (valor > 20) return 'success';
    if (valor > 10) return 'warning';
    if (valor > 0) return 'info';
    return 'secondary';
  };

  const getPrecisionColor = (score: number) => {
    const percentage = Math.round(score * 100);
    if (percentage >= 90) return 'success';
    if (percentage >= 70) return 'warning';
    if (percentage >= 50) return 'info';
    return 'danger';
  };

  // ================================================
  // RENDER CONDICIONAL
  // ================================================

  if (!visible) {
    return null;
  }

  // ================================================
  // RENDER PRINCIPAL
  // ================================================

  return (
    <div className="sinonimos-manager">
      <Card className="mt-3">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <div className="d-flex align-items-center">
            <i className="bi bi-tags me-2 text-primary"></i>
            <span>Sinónimos para: <strong>{productoNombre}</strong></span>
          </div>
          {onClose && (
            <Button variant="outline-secondary" size="sm" onClick={onClose}>
              <i className="bi bi-x"></i> Cerrar
            </Button>
          )}
        </Card.Header>

        <Card.Body>
          {/* SECCIÓN DE ESTADÍSTICAS RÁPIDAS */}
          <Row className="mb-4">
            <Col md={3}>
              <div className="text-center">
                <h4 className="text-primary">{estadisticas.totalSinonimos}</h4>
                <small className="text-muted">
                  <i className="bi bi-tags me-1"></i>
                  Total Sinónimos
                </small>
              </div>
            </Col>
            <Col md={3}>
              <div className="text-center">
                <h4 className="text-info">{estadisticas.totalBusquedas}</h4>
                <small className="text-muted">
                  <i className="bi bi-eye me-1"></i>
                  Búsquedas Totales
                </small>
              </div>
            </Col>
            <Col md={3}>
              <div className="text-center">
                <h4 className="text-success">{estadisticas.precisionPromedio}%</h4>
                <small className="text-muted">
                  <i className="bi bi-trophy me-1"></i>
                  Precisión Promedio
                </small>
              </div>
            </Col>
            <Col md={3}>
              <div className="text-center">
                {estadisticas.masPopular && (
                  <>
                    <h6 className="text-warning">"{estadisticas.masPopular.sinonimo}"</h6>
                    <small className="text-muted">
                      <i className="bi bi-fire me-1"></i>
                      Más Popular
                    </small>
                  </>
                )}
              </div>
            </Col>
          </Row>

          <hr />

          {/* SECCIÓN AGREGAR NUEVO SINÓNIMO */}
          <div className="mb-4">
            <h5 className="mb-3">
              <i className="bi bi-plus-circle me-2"></i>
              Agregar Nuevo Sinónimo
            </h5>
            
            <Form onSubmit={agregarSinonimo}>
              <Row>
                <Col md={8}>
                  <Form.Control
                    type="text"
                    placeholder="Ej: chettos, cheetos mix, doritos nacho"
                    value={nuevoSinonimo}
                    onChange={(e) => setNuevoSinonimo(e.target.value)}
                    isInvalid={!formValidation.valid}
                    className="mb-2"
                  />
                  {!formValidation.valid && (
                    <Form.Control.Feedback type="invalid">
                      {formValidation.message}
                    </Form.Control.Feedback>
                  )}
                </Col>
                <Col md={4}>
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={loadingAdd}
                    className="w-100"
                  >
                    {loadingAdd ? (
                      <>
                        <Spinner as="span" animation="border" size="sm" className="me-2" />
                        Agregando...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-plus me-1"></i>
                        Agregar
                      </>
                    )}
                  </Button>
                </Col>
              </Row>
              <small className="text-muted">
                💡 <strong>Tip:</strong> Agrega términos que los usuarios comúnmente usan para buscar este producto
              </small>
            </Form>
          </div>

          {/* SECCIÓN SUGERENCIAS AUTOMÁTICAS */}
          {(sugerencias.length > 0 || loadingSugerencias) && (
            <div className="mb-4">
              <h5 className="mb-3">
                <i className="bi bi-robot me-2"></i>
                Sugerencias Automáticas
              </h5>
              
              {loadingSugerencias ? (
                <div className="text-center py-3">
                  <Spinner animation="border" size="sm" className="me-2" />
                  Analizando métricas de búsqueda...
                </div>
              ) : (
                <>
                  <Alert variant="info" className="mb-3">
                    <strong>Sugerencias basadas en búsquedas reales de usuarios</strong><br/>
                    <small>Estos términos han sido utilizados por usuarios para encontrar este producto</small>
                  </Alert>
                  
                  <div className="d-flex gap-2 flex-wrap">
                    {sugerencias.map((sugerencia, index) => (
                      <OverlayTrigger
                        key={index}
                        overlay={
                          <Tooltip id={`tooltip-${index}`}>
                            Frecuencia: {sugerencia.frecuencia} | Clicks: {sugerencia.promedio_clicks}
                          </Tooltip>
                        }
                      >
                        <Button
                          variant="outline-warning"
                          size="sm"
                          onClick={() => agregarSugerencia(sugerencia.termino_busqueda)}
                        >
                          <i className="bi bi-lightbulb me-1"></i>
                          + {sugerencia.termino_busqueda}
                        </Button>
                      </OverlayTrigger>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}

          <hr />

          {/* SECCIÓN TABLA DE SINÓNIMOS */}
          <div>
            <h5 className="mb-3">
              <i className="bi bi-tags me-2"></i>
              Sinónimos Configurados
            </h5>
            
            {loading ? (
              <div className="text-center py-4">
                <Spinner animation="border" />
                <p className="mt-2 text-muted">Cargando sinónimos...</p>
              </div>
            ) : sinonimos.length === 0 ? (
              <div className="text-center py-4 text-muted">
                <i className="bi bi-inbox display-4 d-block mb-3"></i>
                <h6>No hay sinónimos configurados</h6>
                <small>¡Agrega el primero arriba!</small>
              </div>
            ) : (
              <div className="table-responsive">
                <Table striped hover className="mb-0">
                  <thead>
                    <tr>
                      <th>Sinónimo</th>
                      <th className="text-center">Popularidad</th>
                      <th className="text-center">Precisión</th>
                      <th className="text-center">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sinonimos
                      .sort((a, b) => b.popularidad - a.popularidad)
                      .map((sinonimo) => (
                      <tr key={sinonimo.id}>
                        <td>
                          <div className="d-flex align-items-center">
                            <i className="bi bi-tag me-2 text-primary"></i>
                            <strong>{sinonimo.sinonimo}</strong>
                            <Badge 
                              bg={getBadgeVariant(sinonimo.fuente)} 
                              className="ms-2"
                              style={{fontSize: '0.7em'}}
                            >
                              {sinonimo.fuente === 'auto_learning' ? 'Auto' : 
                               sinonimo.fuente === 'user_feedback' ? 'Usuario' : 'Admin'}
                            </Badge>
                          </div>
                        </td>
                        <td className="text-center">
                          <Badge bg={getPopularidadColor(sinonimo.popularidad)}>
                            {sinonimo.popularidad > 20 && <i className="bi bi-fire me-1"></i>}
                            {sinonimo.popularidad > 10 && sinonimo.popularidad <= 20 && <i className="bi bi-trophy me-1"></i>}
                            {sinonimo.popularidad > 0 && sinonimo.popularidad <= 10 && <i className="bi bi-eye me-1"></i>}
                            {sinonimo.popularidad}
                          </Badge>
                        </td>
                        <td className="text-center">
                          <Badge bg={getPrecisionColor(sinonimo.precision_score)}>
                            {Math.round(sinonimo.precision_score * 100)}%
                          </Badge>
                        </td>
                        <td className="text-center">
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => confirmarEliminarSinonimo(sinonimo)}
                            title="Eliminar sinónimo"
                          >
                            <i className="bi bi-trash"></i>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            )}
          </div>

          {/* SECCIÓN INFORMACIÓN DE ATRIBUTOS */}
          {atributos.length > 0 && (
            <>
              <hr />
              <div>
                <h5 className="mb-3">
                  <i className="bi bi-fire me-2"></i>
                  Atributos del Producto
                </h5>
                
                <div className="d-flex gap-2 flex-wrap mb-3">
                  {atributos.map((attr, index) => (
                    <Badge
                      key={index}
                      bg={attr.valor ? 'success' : 'danger'}
                      className="p-2"
                    >
                      {attr.valor ? '✓' : '✗'} {attr.atributo}
                      {attr.intensidad > 1 && ` (${attr.intensidad}/10)`}
                    </Badge>
                  ))}
                </div>
                
                <small className="text-muted">
                  💡 Estos atributos se usan para búsquedas como "sin picante" o "con azúcar"
                </small>
              </div>
            </>
          )}
        </Card.Body>
      </Card>

      {/* MODAL DE CONFIRMACIÓN DE ELIMINACIÓN */}
      <Modal 
        show={showDeleteConfirm.show} 
        onHide={() => setShowDeleteConfirm({show: false})}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-exclamation-triangle me-2 text-warning"></i>
            Confirmar Eliminación
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {showDeleteConfirm.sinonimo && (
            <p>
              ¿Estás seguro de que deseas eliminar el sinónimo <strong>"{showDeleteConfirm.sinonimo.sinonimo}"</strong>?
              <br/>
              <small className="text-muted">Esta acción no se puede deshacer.</small>
            </p>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={() => setShowDeleteConfirm({show: false})}
          >
            Cancelar
          </Button>
          <Button 
            variant="danger" 
            onClick={eliminarSinonimo}
          >
            <i className="bi bi-trash me-1"></i>
            Eliminar
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default SinonimosManager;