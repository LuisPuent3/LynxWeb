import React, { useState, useRef, useEffect } from 'react';
import useNLPSearch from '../../hooks/useNLPSearch';

interface SmartSearchBarProps {
  searchTerm: string;
  onSearchChange: (term: string) => void;
  onSearchSubmit: (term: string) => void;
  placeholder?: string;
  className?: string;
}

const SmartSearchBar: React.FC<SmartSearchBarProps> = ({
  searchTerm,
  onSearchChange,
  onSearchSubmit,
  placeholder = "Buscar productos...",
  className = ""
}) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const suggestionsTimeoutRef = useRef<NodeJS.Timeout>();

  const { isNLPAvailable, isSearching } = useNLPSearch();

  // Sugerencias estáticas mejoradas (en producción vendrían del servidor)
  const staticSuggestions = [
    'bebidas sin azúcar',
    'snacks picantes baratos',
    'productos menos de 20 pesos',
    'coca cola grande',
    'papitas sabritas',
    'leche deslactosada',
    'dulces para niños',
    'botanas saladas',
    'galletas de chocolate',
    'agua natural',
    'cereales integrales',
    'frutas frescas',
    'yogurt natural',
    'pan integral'
  ];

  // Generar sugerencias basadas en el texto actual
  const generateSuggestions = (input: string): string[] => {
    if (input.length < 2) return [];
    
    const filtered = staticSuggestions.filter(suggestion =>
      suggestion.toLowerCase().includes(input.toLowerCase())
    );
    
    return filtered.slice(0, 5);
  };

  // Manejar cambios en el input
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onSearchChange(value);
    
    setIsTyping(true);
    
    // Clear previous timeout
    if (suggestionsTimeoutRef.current) {
      clearTimeout(suggestionsTimeoutRef.current);
    }
    
    // Generate suggestions after brief delay
    suggestionsTimeoutRef.current = setTimeout(() => {
      const newSuggestions = generateSuggestions(value);
      setSuggestions(newSuggestions);
      setShowSuggestions(newSuggestions.length > 0 && value.length >= 2);
      setIsTyping(false);
    }, 300);
  };

  // Manejar submit del formulario
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      setShowSuggestions(false);
      onSearchSubmit(searchTerm.trim());
    }
  };

  // Manejar selección de sugerencia
  const handleSuggestionClick = (suggestion: string) => {
    onSearchChange(suggestion);
    setShowSuggestions(false);
    onSearchSubmit(suggestion);
    searchInputRef.current?.blur();
  };

  // Cerrar sugerencias al hacer click fuera
  const handleBlur = () => {
    // Delay para permitir click en sugerencias
    setTimeout(() => {
      setShowSuggestions(false);
    }, 150);
  };

  // Limpiar timeout al desmontar
  useEffect(() => {
    return () => {
      if (suggestionsTimeoutRef.current) {
        clearTimeout(suggestionsTimeoutRef.current);
      }
    };
  }, []);

  // Manejar teclas especiales
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      setShowSuggestions(false);
      searchInputRef.current?.blur();
    }
  };

  return (
    <div className={`smart-search-container position-relative ${className}`}>
      <form onSubmit={handleSubmit} className="d-flex">
        <div className="input-group">
          {/* Indicador NLP */}
          <span className="input-group-text bg-white border-end-0">
            {isNLPAvailable ? (
              <i 
                className="bi bi-brain text-primary" 
                title="Búsqueda inteligente LYNX activada"
              ></i>
            ) : (
              <i 
                className="bi bi-search text-muted" 
                title="Búsqueda básica"
              ></i>
            )}
          </span>
          
          {/* Input principal */}
          <input
            ref={searchInputRef}
            type="search"
            className="form-control border-start-0 border-end-0"
            placeholder={isNLPAvailable ? `${placeholder} (con IA)` : placeholder}
            value={searchTerm}
            onChange={handleInputChange}
            onFocus={() => {
              if (searchTerm.length >= 2) {
                const newSuggestions = generateSuggestions(searchTerm);
                setSuggestions(newSuggestions);
                setShowSuggestions(newSuggestions.length > 0);
              }
            }}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            disabled={isSearching}
          />
          
          {/* Botón de búsqueda */}
          <button 
            className="btn btn-primary" 
            type="submit"
            disabled={isSearching || !searchTerm.trim()}
          >
            {isSearching ? (
              <div className="spinner-border spinner-border-sm" role="status">
                <span className="visually-hidden">Buscando...</span>
              </div>
            ) : (
              <i className="bi bi-search"></i>
            )}
          </button>
        </div>
      </form>

      {/* Sugerencias dropdown */}
      {showSuggestions && (suggestions.length > 0 || isTyping) && (
        <div className="suggestions-dropdown position-absolute w-100 mt-1 bg-white border rounded shadow-lg" 
             style={{ zIndex: 1000, maxHeight: '300px', overflowY: 'auto' }}>
          
          {isTyping ? (
            <div className="px-3 py-2 text-muted d-flex align-items-center">
              <div className="spinner-border spinner-border-sm me-2" role="status"></div>
              <small>Generando sugerencias...</small>
            </div>
          ) : (
            <>
              {suggestions.length > 0 && (
                <div className="px-3 py-2 bg-light border-bottom">
                  <small className="text-muted d-flex align-items-center">
                    {isNLPAvailable ? (
                      <>
                        <i className="bi bi-lightbulb me-1"></i>
                        Sugerencias inteligentes
                      </>
                    ) : (
                      <>
                        <i className="bi bi-list me-1"></i>
                        Sugerencias
                      </>
                    )}
                  </small>
                </div>
              )}
              
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="suggestion-item px-3 py-2 border-bottom cursor-pointer d-flex align-items-center"
                  onMouseDown={() => handleSuggestionClick(suggestion)}
                  style={{ cursor: 'pointer' }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f8f9fa';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                  }}
                >
                  <i className="bi bi-search text-muted me-2"></i>
                  <span>{suggestion}</span>
                  {isNLPAvailable && (
                    <i className="bi bi-magic ms-auto text-primary" title="Con procesamiento IA"></i>
                  )}
                </div>
              ))}
            </>
          )}
        </div>
      )}

      {/* Indicador de estado NLP */}
      {isNLPAvailable && (
        <div className="position-absolute top-100 start-0 mt-1">
          <small className="text-success d-flex align-items-center">
            <i className="bi bi-check-circle-fill me-1"></i>
            <span>LYNX IA conectado</span>
          </small>
        </div>
      )}
    </div>
  );
};

export default SmartSearchBar;
