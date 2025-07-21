import React, { useState } from 'react';
import useNLPSearch from '../../hooks/useNLPSearch';

const NLPSearchDemo: React.FC = () => {
  const [query, setQuery] = useState('');
  
  const { 
    isNLPAvailable, 
    isSearching, 
    nlpResults, 
    suggestedProducts,
    performNLPSearch,
    clearNLPResults,
    hasCorrections,
    correctedQuery,
    processingTime
  } = useNLPSearch();

  const handleSearch = async () => {
    if (query.trim()) {
      await performNLPSearch(query.trim());
    }
  };

  const handleClear = () => {
    setQuery('');
    clearNLPResults();
  };

  return (
    <div className="card mt-4">
      <div className="card-header bg-primary text-white">
        <h5 className="mb-0">
          <i className="bi bi-brain me-2"></i>
          LYNX NLP Search Demo
          {isNLPAvailable ? (
            <span className="badge bg-success ms-2">Connected</span>
          ) : (
            <span className="badge bg-warning ms-2">Disconnected</span>
          )}
        </h5>
      </div>
      
      <div className="card-body">
        {/* Search Input */}
        <div className="row mb-3">
          <div className="col">
            <div className="input-group">
              <input
                type="text"
                className="form-control"
                placeholder="Prueba: 'bebidas sin azucar', 'snacks baratos picantes'..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                disabled={isSearching}
              />
              <button 
                className="btn btn-primary" 
                onClick={handleSearch}
                disabled={isSearching || !query.trim() || !isNLPAvailable}
              >
                {isSearching ? (
                  <div className="spinner-border spinner-border-sm" role="status">
                    <span className="visually-hidden">Searching...</span>
                  </div>
                ) : (
                  <i className="bi bi-search"></i>
                )}
              </button>
              <button 
                className="btn btn-outline-secondary" 
                onClick={handleClear}
                disabled={isSearching}
              >
                <i className="bi bi-x"></i>
              </button>
            </div>
          </div>
        </div>

        {/* Quick Test Buttons */}
        <div className="mb-3">
          <small className="text-muted d-block mb-2">Búsquedas de prueba:</small>
          <div className="btn-group-sm" role="group">
            <button 
              className="btn btn-outline-primary btn-sm me-2 mb-1" 
              onClick={() => setQuery('bebidas sin azucar')}
              disabled={isSearching}
            >
              bebidas sin azucar
            </button>
            <button 
              className="btn btn-outline-primary btn-sm me-2 mb-1" 
              onClick={() => setQuery('snacks picantes baratos')}
              disabled={isSearching}
            >
              snacks picantes baratos
            </button>
            <button 
              className="btn btn-outline-primary btn-sm me-2 mb-1" 
              onClick={() => setQuery('productos menos de 20 pesos')}
              disabled={isSearching}
            >
              productos menos de 20 pesos
            </button>
          </div>
        </div>

        {/* Corrections */}
        {hasCorrections && correctedQuery && (
          <div className="alert alert-info">
            <i className="bi bi-magic me-2"></i>
            <strong>Corrección aplicada:</strong> "{query}" → "{correctedQuery}"
          </div>
        )}

        {/* Results */}
        {nlpResults && (
          <div className="mt-3">
            <div className="row mb-3">
              <div className="col">
                <div className="d-flex justify-content-between align-items-center">
                  <h6 className="text-success mb-0">
                    <i className="bi bi-check-circle me-1"></i>
                    Búsqueda exitosa
                  </h6>
                  <small className="text-muted">
                    Procesado en {processingTime}ms
                  </small>
                </div>
              </div>
            </div>

            {/* Interpretation */}
            {nlpResults.interpretation && (
              <div className="mb-3">
                <h6>Interpretación:</h6>
                <div className="row g-2">
                  {nlpResults.interpretation.categoria && (
                    <div className="col-auto">
                      <span className="badge bg-success">
                        <i className="bi bi-folder me-1"></i>
                        {nlpResults.interpretation.categoria}
                      </span>
                    </div>
                  )}
                  {nlpResults.interpretation.atributos && nlpResults.interpretation.atributos.length > 0 && (
                    nlpResults.interpretation.atributos.map((attr: string, idx: number) => (
                      <div className="col-auto" key={idx}>
                        <span className="badge bg-info">
                          <i className="bi bi-tag me-1"></i>
                          {attr}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {/* Products */}
            {suggestedProducts && suggestedProducts.length > 0 ? (
              <div>
                <h6>Productos encontrados ({suggestedProducts.length}):</h6>
                <div className="row g-3">
                  {suggestedProducts.slice(0, 6).map((product) => (
                    <div key={product.id_producto} className="col-md-4">
                      <div className="card border-0 shadow-sm h-100">
                        {product.imagen && (
                          <img 
                            src={`/uploads/${product.imagen}`}
                            alt={product.nombre}
                            className="card-img-top"
                            style={{ height: '120px', objectFit: 'cover' }}
                            onError={(e) => {
                              (e.target as HTMLImageElement).src = '/uploads/default.jpg';
                            }}
                          />
                        )}
                        <div className="card-body">
                          <h6 className="card-title text-primary mb-1" style={{ fontSize: '0.9rem' }}>
                            {product.nombre}
                          </h6>
                          <div className="d-flex justify-content-between align-items-center">
                            <span className="text-success fw-bold">
                              ${product.precio}
                            </span>
                            <small className="text-muted">
                              Stock: {product.cantidad}
                            </small>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                {suggestedProducts.length > 6 && (
                  <div className="text-center mt-3">
                    <small className="text-muted">
                      y {suggestedProducts.length - 6} productos más...
                    </small>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-3">
                <i className="bi bi-search text-muted"></i>
                <p className="text-muted mb-0">No se encontraron productos</p>
              </div>
            )}
          </div>
        )}

        {/* Status */}
        <div className="mt-4 pt-3 border-top">
          <div className="row text-center">
            <div className="col-md-3">
              <div className={`text-${isNLPAvailable ? 'success' : 'warning'}`}>
                <i className={`bi bi-${isNLPAvailable ? 'check-circle' : 'exclamation-triangle'} d-block mb-1`}></i>
                <small>{isNLPAvailable ? 'NLP Conectado' : 'NLP Desconectado'}</small>
              </div>
            </div>
            <div className="col-md-3">
              <div className="text-info">
                <i className="bi bi-database d-block mb-1"></i>
                <small>MySQL Dinámico</small>
              </div>
            </div>
            <div className="col-md-3">
              <div className="text-success">
                <i className="bi bi-images d-block mb-1"></i>
                <small>Con Imágenes</small>
              </div>
            </div>
            <div className="col-md-3">
              <div className="text-primary">
                <i className="bi bi-arrow-clockwise d-block mb-1"></i>
                <small>Auto-Adaptativo</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NLPSearchDemo;
