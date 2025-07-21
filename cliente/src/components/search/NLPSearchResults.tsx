import React from 'react';
import { NLPSearchResponse } from '../../services/nlpService';

interface NLPSearchResultsProps {
  nlpResults: NLPSearchResponse | null;
  isSearching: boolean;
  onDismiss: () => void;
}

const NLPSearchResults: React.FC<NLPSearchResultsProps> = ({ 
  nlpResults, 
  isSearching,
  onDismiss 
}) => {
  if (!nlpResults && !isSearching) {
    return null;
  }

  return (
    <div className="nlp-search-overlay position-fixed w-100 h-100" 
         style={{ 
           top: 0, 
           left: 0, 
           zIndex: 1050, 
           backgroundColor: 'rgba(0,0,0,0.5)' 
         }}
         onClick={onDismiss}>
      <div className="container py-4">
        <div className="row justify-content-center">
          <div className="col-lg-10">
            <div className="card shadow-lg border-0" onClick={(e) => e.stopPropagation()}>
              <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <div>
                  <h5 className="mb-0 d-flex align-items-center">
                    <i className="bi bi-brain me-2"></i>
                    LYNX - Búsqueda Inteligente
                  </h5>
                  {nlpResults && (
                    <small className="opacity-75">
                      Procesado en {nlpResults.processing_time_ms}ms
                    </small>
                  )}
                </div>
                <button 
                  className="btn btn-link text-white p-0" 
                  onClick={onDismiss}
                  style={{ fontSize: '1.5rem' }}
                >
                  <i className="bi bi-x"></i>
                </button>
              </div>

              <div className="card-body">
                {isSearching ? (
                  // Estado de carga
                  <div className="text-center py-4">
                    <div className="spinner-border text-primary mb-3" role="status">
                      <span className="visually-hidden">Analizando consulta...</span>
                    </div>
                    <p className="text-muted">Analizando tu consulta con inteligencia artificial...</p>
                  </div>
                ) : nlpResults ? (
                  <div>
                    {/* Correcciones ortográficas */}
                    {nlpResults.corrections?.applied && (
                      <div className="alert alert-info border-0 mb-3">
                        <div className="d-flex align-items-center">
                          <i className="bi bi-magic text-info me-2"></i>
                          <div>
                            <strong>¿Quisiste decir?</strong>
                            <div className="mt-1">
                              <span className="text-muted">"{nlpResults.query}" → </span>
                              <span className="fw-bold text-success">"{nlpResults.corrections.corrected_query}"</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Interpretación del sistema */}
                    <div className="mb-4">
                      <h6 className="text-primary mb-3">
                        <i className="bi bi-lightbulb me-1"></i>
                        Interpretación de tu búsqueda
                      </h6>
                      <div className="row g-2">
                        {nlpResults.interpretation.producto && (
                          <div className="col-auto">
                            <span className="badge bg-primary">
                              <i className="bi bi-box me-1"></i>
                              Producto: {nlpResults.interpretation.producto}
                            </span>
                          </div>
                        )}
                        {nlpResults.interpretation.categoria && (
                          <div className="col-auto">
                            <span className="badge bg-success">
                              <i className="bi bi-folder me-1"></i>
                              Categoría: {nlpResults.interpretation.categoria}
                            </span>
                          </div>
                        )}
                        {nlpResults.interpretation.atributos && nlpResults.interpretation.atributos.length > 0 && (
                          nlpResults.interpretation.atributos.map((attr, index) => (
                            <div className="col-auto" key={index}>
                              <span className="badge bg-info">
                                <i className="bi bi-tag me-1"></i>
                                {attr}
                              </span>
                            </div>
                          ))
                        )}
                        {nlpResults.interpretation.filtros?.precio && (
                          <div className="col-auto">
                            <span className="badge bg-warning text-dark">
                              <i className="bi bi-currency-dollar me-1"></i>
                              {nlpResults.interpretation.filtros.precio.tendency === 'low' ? 'Precio bajo' : 'Filtro precio'}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Mensaje del sistema */}
                    {nlpResults.user_message && (
                      <div className="alert alert-light border mb-3">
                        <i className="bi bi-chat-dots text-primary me-2"></i>
                        {nlpResults.user_message}
                      </div>
                    )}

                    {/* Resultados */}
                    <h6 className="text-primary mb-3">
                      <i className="bi bi-search me-1"></i>
                      Productos encontrados ({nlpResults.recommendations.length})
                    </h6>
                    
                    {nlpResults.recommendations.length > 0 ? (
                      <div className="row g-3">                        {nlpResults.recommendations.slice(0, 6).map((product, index) => (
                          <div className="col-md-6 col-lg-4" key={product.id_producto || product.id || index}>
                            <div className={`card h-100 border-0 shadow-sm ${index === 0 ? 'border-primary border-2' : ''}`}>
                              {index === 0 && (
                                <div className="position-absolute top-0 start-0 m-2">
                                  <span className="badge bg-primary">
                                    <i className="bi bi-star me-1"></i>
                                    Mejor resultado
                                  </span>
                                </div>
                              )}                              <div className="card-body">
                                <h6 className="card-title text-primary">
                                  {product.nombre || product.name}
                                </h6>
                                <div className="d-flex justify-content-between align-items-center mb-2">
                                  <span className="h6 text-success mb-0">
                                    ${(product.precio || product.price || 0).toFixed(2)}
                                  </span>
                                  <span className="badge bg-light text-dark">
                                    {product.categoria_nombre || product.category}
                                  </span>
                                </div>
                                <div className="mb-2">
                                  <div className="progress" style={{ height: '4px' }}>
                                    <div 
                                      className="progress-bar bg-success" 
                                      style={{ width: `${(product.match_score || product.relevance || 0.8) * 100}%` }}
                                    ></div>
                                  </div>
                                  <small className="text-muted">
                                    Relevancia: {Math.round((product.match_score || product.relevance || 0.8) * 100)}%
                                  </small>
                                </div>
                                {/* Mostrar imagen del producto */}
                                {(product.imagen || product.image) && (
                                  <div className="mb-2 text-center">
                                    <img 
                                      src={`/uploads/${product.imagen || product.image}`} 
                                      alt={product.nombre || product.name}
                                      className="img-fluid rounded"
                                      style={{ maxHeight: '100px', objectFit: 'cover' }}
                                      onError={(e) => {
                                        e.currentTarget.src = '/uploads/default.jpg';
                                      }}
                                    />
                                  </div>
                                )}
                                {(product.match_reasons || []).length > 0 && (
                                  <div className="mt-2">
                                    <small className="text-muted d-block mb-1">Por qué coincide:</small>
                                    {(product.match_reasons || []).slice(0, 2).map((reason, idx) => (
                                      <span key={idx} className="badge bg-secondary me-1 mb-1" style={{ fontSize: '0.7em' }}>
                                        {reason}
                                      </span>
                                    ))}
                                  </div>
                                )}
                                <div className="mt-3 d-flex justify-content-between align-items-center">
                                  {/* Stock info */}
                                  <div>
                                    <small className="text-muted">Stock: </small>
                                    <span className={`badge ${(product.cantidad || product.stock || 0) > 0 ? 'bg-success' : 'bg-danger'}`}>
                                      {product.cantidad || product.stock || 0}
                                    </span>
                                  </div>
                                  {/* Availability */}
                                  <div>
                                    {(product.available !== false && (product.cantidad || product.stock || 0) > 0) ? (
                                      <span className="badge bg-success">
                                        <i className="bi bi-check-circle me-1"></i>
                                        Disponible
                                      </span>
                                    ) : (
                                      <span className="badge bg-danger">
                                        <i className="bi bi-x-circle me-1"></i>
                                        Agotado
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-4">
                        <i className="bi bi-search display-4 text-muted"></i>
                        <p className="text-muted mt-2">No se encontraron productos para esta búsqueda</p>
                      </div>
                    )}

                    {/* SQL Query para debug (solo en desarrollo) */}
                    {process.env.NODE_ENV === 'development' && nlpResults.sql_query && (
                      <div className="mt-4">
                        <details>
                          <summary className="text-muted" style={{ cursor: 'pointer' }}>
                            <small>
                              <i className="bi bi-code me-1"></i>
                              Ver consulta generada (Debug)
                            </small>
                          </summary>
                          <div className="mt-2">
                            <code className="text-muted small d-block bg-light p-2 rounded">
                              {nlpResults.sql_query}
                            </code>
                          </div>
                        </details>
                      </div>
                    )}

                    {/* Botones de acción */}
                    <div className="mt-4 d-flex justify-content-between">
                      <button 
                        className="btn btn-outline-primary"
                        onClick={onDismiss}
                      >
                        <i className="bi bi-arrow-left me-1"></i>
                        Usar estos resultados
                      </button>
                      
                      {nlpResults.recommendations.length > 6 && (
                        <small className="text-muted align-self-center">
                          y {nlpResults.recommendations.length - 6} productos más...
                        </small>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <i className="bi bi-exclamation-triangle display-4 text-warning"></i>
                    <p className="text-muted mt-2">Error al procesar la búsqueda</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NLPSearchResults;
