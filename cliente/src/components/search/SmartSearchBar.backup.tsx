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
}) => {  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const suggestionsTimeoutRef = useRef<NodeJS.Timeout>();
  const { isNLPAvailable, isSearching } = useNLPSearch();
  
  // Emojis de comida para alternar con la lupa
  const foodEmojis = ['🍟', '🍿', '🥤', '🍭', '🍪', '🥨', '🧃', '🍇', '🍊', '🥯'];
  const [currentIcon, setCurrentIcon] = useState('🔍');  // Debug: Mostrar estado NLP
  console.log('🐛 SmartSearchBar Debug - isNLPAvailable:', isNLPAvailable);
  
  // Patrón inteligente: Lupa (3s) → Emoji random (2s) → Lupa (3s) → ...
  useEffect(() => {
    console.log('🐛 useEffect triggered - isNLPAvailable:', isNLPAvailable);
    
    if (!isNLPAvailable) {
      console.log('🐛 NLP no disponible, usando lupa fija');
      setCurrentIcon('🔍');
      return;
    }
    
    console.log('🐛 NLP disponible, iniciando rotación de emojis');
    let timeoutId: NodeJS.Timeout;
    
    // Estado para controlar si estamos en modo lupa o emoji
    let showingMagnifier = true;
    
    const switchIcon = () => {
      console.log('🐛 switchIcon called - showingMagnifier:', showingMagnifier);
      if (showingMagnifier) {
        // Mostrar emoji aleatorio
        const randomEmoji = foodEmojis[Math.floor(Math.random() * foodEmojis.length)];
        setCurrentIcon(randomEmoji);
        console.log('🔄 Cambio a emoji:', randomEmoji); // Debug
        showingMagnifier = false;
        timeoutId = setTimeout(switchIcon, 2000); // 2 segundos con emoji
      } else {
        // Mostrar lupa
        setCurrentIcon('🔍');
        console.log('🔄 Cambio a lupa'); // Debug
        showingMagnifier = true;
        timeoutId = setTimeout(switchIcon, 3000); // 3 segundos con lupa
      }
    };
    
    // Comenzar con lupa
    setCurrentIcon('🔍');
    console.log('🔄 Iniciando con lupa'); // Debug
    
    // Iniciar el primer cambio después de 3 segundos
    timeoutId = setTimeout(switchIcon, 3000);
    console.log('🐛 Timeout iniciado para primer cambio');
      return () => {
      console.log('🐛 Cleanup useEffect');
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [isNLPAvailable]); // Solo depende de isNLPAvailable, no de foodEmojis

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
      <form onSubmit={handleSubmit} className="d-flex">        <div className="input-group shadow-sm">
          {/* Input principal mejorado */}
          <input
            ref={searchInputRef}
            type="search"
            className="form-control px-3"
            style={{ 
              borderColor: '#dee2e6',
              fontSize: '16px',
              height: '46px',
              boxShadow: 'none',
              backgroundColor: '#f5f5f5'
            }}            placeholder={isNLPAvailable ? 
              `${placeholder} 🤖` : 
              placeholder
            }
            value={searchTerm}
            onChange={handleInputChange}
            onFocus={(e) => {
              e.target.style.borderColor = '#0d6efd';
              e.target.style.outline = 'none';
              e.target.style.backgroundColor = '#ffffff';
              if (searchTerm.length >= 2) {
                const newSuggestions = generateSuggestions(searchTerm);
                setSuggestions(newSuggestions);
                setShowSuggestions(newSuggestions.length > 0);
              }
            }}
            onBlur={(e) => {
              e.target.style.borderColor = '#dee2e6';
              e.target.style.backgroundColor = '#f5f5f5';
              handleBlur();
            }}
            onKeyDown={handleKeyDown}
            disabled={isSearching}
          />            {/* Botón de búsqueda con patrón inteligente lupa+emoji */}
          <button 
            type="submit"
            disabled={isSearching || !searchTerm.trim()}
            style={{ 
              border: '1px solid #dee2e6',
              color: '#6c757d',
              height: '46px',
              minWidth: '50px',
              padding: '0 12px',
              backgroundColor: 'white',
              backgroundImage: 'none',
              boxShadow: 'none',
              borderRadius: '0 0.375rem 0.375rem 0',
              outline: 'none',
              cursor: (isSearching || !searchTerm.trim()) ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            onMouseEnter={(e) => {
              if (!isSearching && searchTerm.trim()) {
                e.currentTarget.style.setProperty('background-color', '#0d6efd', 'important');
                e.currentTarget.style.setProperty('border-color', '#0d6efd', 'important');
                e.currentTarget.style.setProperty('color', 'white', 'important');
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.setProperty('background-color', 'white', 'important');
              e.currentTarget.style.setProperty('border-color', '#dee2e6', 'important');
              e.currentTarget.style.setProperty('color', '#6c757d', 'important');
            }}
            onFocus={(e) => {
              e.currentTarget.style.setProperty('outline', 'none', 'important');
              e.currentTarget.style.setProperty('box-shadow', 'none', 'important');
            }}
          >
            {isSearching ? (
              <div className="spinner-border spinner-border-sm" role="status">
                <span className="visually-hidden">Buscando...</span>
              </div>
            ) : isNLPAvailable ? (
              <span 
                style={{ 
                  fontSize: '16px',
                  transition: 'transform 0.3s ease',
                  display: 'inline-block'
                }}                title="Búsqueda inteligente LCLN"
              >
                {currentIcon}
              </span>
            ) : (
              <i className="bi bi-search"></i>
            )}
          </button>
        </div>
      </form>      {/* Sugerencias dropdown mejoradas */}
      {showSuggestions && (suggestions.length > 0 || isTyping) && (
        <div className="suggestions-dropdown position-absolute w-100 mt-2 bg-white border-0 rounded-3 shadow-lg" 
             style={{ zIndex: 1000, maxHeight: '320px', overflowY: 'auto', border: '1px solid #e9ecef' }}>
          
          {isTyping ? (
            <div className="px-4 py-3 text-muted d-flex align-items-center">
              <div className="spinner-border spinner-border-sm me-3" role="status"></div>
              <span style={{ fontSize: '14px' }}>Generando sugerencias...</span>
            </div>
          ) : (
            <>
              {suggestions.length > 0 && (
                <div className="px-4 py-2 bg-light rounded-top-3 border-bottom" style={{ borderColor: '#f1f3f4' }}>
                  <small className="text-muted d-flex align-items-center" style={{ fontSize: '12px', fontWeight: '500' }}>                    {isNLPAvailable ? (
                      <>
                        <span className="me-2">{currentIcon}</span>
                        Sugerencias inteligentes
                      </>
                    ) : (
                      <>
                        <i className="bi bi-list me-2"></i>
                        Sugerencias
                      </>
                    )}
                  </small>
                </div>
              )}
              
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="suggestion-item px-4 py-3 border-bottom cursor-pointer d-flex align-items-center justify-content-between"
                  onMouseDown={() => handleSuggestionClick(suggestion)}
                  style={{ 
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    borderColor: '#f1f3f4',
                    fontSize: '15px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f8f9fa';
                    e.currentTarget.style.transform = 'translateX(2px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.transform = 'translateX(0px)';
                  }}
                >
                  <div className="d-flex align-items-center">
                    <i className="bi bi-search text-muted me-3" style={{ fontSize: '14px' }}></i>
                    <span style={{ color: '#495057' }}>{suggestion}</span>
                  </div>
                  
                  {isNLPAvailable && (
                    <span className="text-muted" style={{ fontSize: '12px' }}>
                      <i className="bi bi-magic"></i>
                    </span>
                  )}
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default SmartSearchBar;
