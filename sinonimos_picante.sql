-- SINÓNIMOS PARA PRODUCTOS PICANTES
-- Añade reconocimiento mejorado para consultas como "botanas picantes", "snacks con flama", etc.
-- Fecha: 2025-07-22

-- Primero identificar los IDs de los productos picantes:
-- Doritos Dinamita 50g - ID a determinar
-- Crujitos Fuego 59g - ID a determinar  
-- Susalia Flama 200g - ID a determinar

-- Para Doritos Dinamita (producto picante)
-- Asumiendo ID basado en el patrón del sistema
INSERT INTO productos_sinonimos (producto_id, sinonimo, popularidad, activo, precision_score, fuente) VALUES

-- Doritos Dinamita - sinónimos de picante
(11, 'picante', 95, 1, 0.95, 'semantic_spicy'),
(11, 'flama', 90, 1, 0.90, 'semantic_spicy'),
(11, 'flamas', 85, 1, 0.85, 'semantic_spicy'),
(11, 'picoso', 90, 1, 0.90, 'semantic_spicy'),
(11, 'ardiente', 85, 1, 0.85, 'semantic_spicy'),
(11, 'chile', 80, 1, 0.80, 'semantic_spicy'),
(11, 'enchilado', 85, 1, 0.85, 'semantic_spicy'),
(11, 'botanita picante', 90, 1, 0.90, 'semantic_spicy'),
(11, 'snack picante', 88, 1, 0.88, 'semantic_spicy'),
(11, 'con chile', 82, 1, 0.82, 'semantic_spicy'),

-- Crujitos Fuego - sinónimos de picante
(14, 'picante', 95, 1, 0.95, 'semantic_spicy'),
(14, 'flama', 92, 1, 0.92, 'semantic_spicy'),
(14, 'flamas', 88, 1, 0.88, 'semantic_spicy'),
(14, 'picoso', 90, 1, 0.90, 'semantic_spicy'),
(14, 'ardiente', 90, 1, 0.90, 'semantic_spicy'),
(14, 'fuego', 95, 1, 0.95, 'semantic_spicy'),
(14, 'chile', 80, 1, 0.80, 'semantic_spicy'),
(14, 'enchilado', 85, 1, 0.85, 'semantic_spicy'),
(14, 'botanita picante', 90, 1, 0.90, 'semantic_spicy'),
(14, 'snack picante', 88, 1, 0.88, 'semantic_spicy'),

-- Susalia Flama - sinónimos de picante
(21, 'picante', 95, 1, 0.95, 'semantic_spicy'),
(21, 'flama', 95, 1, 0.95, 'semantic_spicy'),
(21, 'flamas', 92, 1, 0.92, 'semantic_spicy'),
(21, 'picoso', 90, 1, 0.90, 'semantic_spicy'),
(21, 'ardiente', 85, 1, 0.85, 'semantic_spicy'),
(21, 'chile', 80, 1, 0.80, 'semantic_spicy'),
(21, 'enchilado', 85, 1, 0.85, 'semantic_spicy'),
(21, 'botanita picante', 90, 1, 0.90, 'semantic_spicy'),
(21, 'snack picante', 88, 1, 0.88, 'semantic_spicy'),
(21, 'con chile', 82, 1, 0.82, 'semantic_spicy'),

-- SINÓNIMOS GENÉRICOS PARA BÚSQUEDAS DE "BOTANAS PICANTES"
-- Estos se asocian a todos los productos picantes para búsquedas generales

-- Sinónimos cruzados para mejor reconocimiento
(11, 'takis', 75, 1, 0.75, 'semantic_similar'),  -- Doritos similar a Takis
(11, 'nacho picante', 80, 1, 0.80, 'semantic_similar'),
(14, 'takis fuego', 80, 1, 0.80, 'semantic_similar'), -- Crujitos similar a Takis
(14, 'nacho fuego', 85, 1, 0.85, 'semantic_similar'),
(21, 'botanita flama', 90, 1, 0.90, 'semantic_similar'),

-- Sinónimos para búsquedas negativas "sin picante"
-- Estos ayudan a excluir productos cuando se busca "botanas sin picante"
(11, 'con chile_exclude', 95, 1, 0.95, 'semantic_exclusion'),
(14, 'con chile_exclude', 95, 1, 0.95, 'semantic_exclusion'),
(21, 'con chile_exclude', 95, 1, 0.95, 'semantic_exclusion');

-- COMENTARIOS ADICIONALES:
-- Los IDs (11, 14, 21) son estimados basados en el orden de productos
-- Deberán ajustarse con los IDs reales de la base de datos
-- La fuente 'semantic_spicy' permite identificar estos sinónimos específicamente
-- Los sinónimos de exclusión ayudan con búsquedas como "botanas sin picante"