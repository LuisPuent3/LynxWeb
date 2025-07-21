---

# 🚀 SISTEMA LCLN INTELIGENTE CON SINÓNIMOS DINÁMICOS
## Extensión Avanzada del Sistema Base

---

## 8. ARQUITECTURA MEJORADA CON SINÓNIMOS ESPECÍFICOS

### 8.1 Flujo Inteligente con Prioridades

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     FLUJO MEJORADO CON SINÓNIMOS DINÁMICOS               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Entrada: "chettos picantes baratos"                                     │
│     ↓                                                                    │
│  🥇 [PRIORIDAD 1] BÚSQUEDA EXACTA + SINÓNIMOS ESPECÍFICOS              │
│     • Buscar "chettos" en tabla producto_sinonimos                      │
│     • Encontrado: "chettos" → Producto ID 15 (Cheetos Mix)             │
│     • Match directo con producto real en BD                              │
│     ↓                                                                    │
│  🥈 [PRIORIDAD 2] ANÁLISIS DE ATRIBUTOS + NEGACIONES                   │
│     • "picantes" → ATRIBUTO_SABOR                                       │
│     • "baratos" → ATRIBUTO_PRECIO                                       │
│     • "sin picante" → NEGACIÓN + ATRIBUTO                              │
│     ↓                                                                    │
│  🥉 [PRIORIDAD 3] CORRECCIÓN ORTOGRÁFICA (Solo como apoyo)              │
│     • Se ejecuta solo si no hay matches en prioridades anteriores       │
│     • "votana" → "botana" → buscar en sinónimos                        │
│     ↓                                                                    │
│  📊 [RANKING INTELIGENTE] ORDENAMIENTO POR POPULARIDAD                  │
│     • Productos con más clicks/ventas primero                           │
│     • Boost por coincidencias exactas                                   │
│     • Penalización por distancia semántica                              │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Estructura de Base de Datos Extendida

```sql
-- ================================================
-- TABLAS PARA SISTEMA DE SINÓNIMOS INTELIGENTES
-- ================================================

-- Sinónimos específicos por producto
CREATE TABLE producto_sinonimos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    sinonimo VARCHAR(255) NOT NULL COLLATE utf8mb4_general_ci,
    popularidad INT DEFAULT 0,
    precision_score DECIMAL(3,2) DEFAULT 1.00,
    creado_por INT,
    fuente ENUM('admin', 'auto_learning', 'user_feedback') DEFAULT 'admin',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (producto_id) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (creado_por) REFERENCES usuarios(id) ON DELETE SET NULL,
    
    UNIQUE KEY unique_producto_sinonimo (producto_id, sinonimo),
    INDEX idx_sinonimo_activo (sinonimo, activo),
    INDEX idx_producto_activo (producto_id, activo),
    INDEX idx_popularidad (popularidad DESC),
    FULLTEXT idx_sinonimo_fulltext (sinonimo)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Métricas de búsqueda para aprendizaje automático
CREATE TABLE busqueda_metricas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    termino_busqueda VARCHAR(255) NOT NULL,
    producto_id INT,
    usuario_id INT,
    clicks INT DEFAULT 0,
    tiempo_en_pagina INT DEFAULT 0, -- en segundos
    conversiones INT DEFAULT 0, -- compras realizadas
    rating_utilidad TINYINT CHECK (rating_utilidad BETWEEN 1 AND 5),
    fecha_busqueda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100),
    
    FOREIGN KEY (producto_id) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    
    INDEX idx_termino_fecha (termino_busqueda, fecha_busqueda),
    INDEX idx_producto_metricas (producto_id, conversiones DESC, clicks DESC),
    INDEX idx_fecha_session (fecha_busqueda, session_id)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Atributos específicos de productos para negaciones
CREATE TABLE producto_atributos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    atributo VARCHAR(100) NOT NULL,
    valor BOOLEAN DEFAULT TRUE,
    intensidad TINYINT DEFAULT 5 CHECK (intensidad BETWEEN 1 AND 10),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (producto_id) REFERENCES productos(id_producto) ON DELETE CASCADE,
    
    UNIQUE KEY unique_producto_atributo (producto_id, atributo),
    INDEX idx_atributo_valor (atributo, valor)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Ejemplos de datos iniciales
INSERT INTO producto_atributos (producto_id, atributo, valor, intensidad) VALUES
(8, 'picante', TRUE, 8),    -- Doritos Dinamita - muy picante
(20, 'picante', TRUE, 6),   -- Crujitos Fuego - moderadamente picante
(2, 'picante', FALSE, 0),   -- Coca Cola - no picante
(3, 'azucar', FALSE, 0),    -- Coca Cola Sin Azúcar - sin azúcar
(2, 'azucar', TRUE, 8);     -- Coca Cola normal - con azúcar
```

### 8.3 Casos de Uso Específicos del Sistema Mejorado

#### **CASO 1: "chettos picantes" - Sinónimo Específico**
```json
{
  "entrada": "chettos picantes",
  "proceso": {
    "paso_1": {
      "busqueda_sinonimos": "SELECT producto_id FROM producto_sinonimos WHERE sinonimo='chettos' AND activo=1",
      "resultado": "producto_id: 15 (Cheetos Mix 50g)"
    },
    "paso_2": {
      "filtro_atributos": "SELECT * FROM producto_atributos WHERE producto_id=15 AND atributo='picante'",
      "verificacion": "Producto ya es picante (intensidad: 7)"
    }
  },
  "respuesta": {
    "productos_encontrados": 1,
    "match_type": "exact_synonym",
    "confidence": 0.95,
    "mensaje": "Encontrado: Cheetos Mix 50g (picante)"
  }
}
```

#### **CASO 2: "sin picante barato" - Manejo de Negaciones**
```json
{
  "entrada": "sin picante barato",
  "proceso": {
    "paso_1": {
      "detectar_negacion": "Token 'sin' detectado",
      "atributo_negado": "picante"
    },
    "paso_2": {
      "query_negacion": "SELECT p.* FROM productos p LEFT JOIN producto_atributos pa ON p.id_producto = pa.producto_id AND pa.atributo = 'picante' WHERE (pa.valor = FALSE OR pa.valor IS NULL) AND p.precio < (SELECT AVG(precio) FROM productos)"
    }
  },
  "respuesta": {
    "productos_encontrados": 12,
    "match_type": "attribute_negation",
    "filtros_aplicados": ["precio_bajo", "no_picante"],
    "mensaje": "Productos económicos sin picante"
  }
}
```

#### **CASO 3: "votana bara" - Corrección + Sinónimo**
```json
{
  "entrada": "votana bara",
  "proceso": {
    "paso_1": {
      "correccion_ortografica": {
        "votana": "botana",
        "bara": "barata"
      }
    },
    "paso_2": {
      "busqueda_sinonimos": "SELECT producto_id FROM producto_sinonimos WHERE sinonimo='botana'",
      "mapeo_categoria": "botana → categoria: snacks"
    },
    "paso_3": {
      "filtro_precio": "productos.precio < AVG(precio) WHERE categoria='snacks'"
    }
  },
  "respuesta": {
    "productos_encontrados": 8,
    "match_type": "corrected_category_search",
    "correcciones_aplicadas": true,
    "mensaje": "Mostrando snacks económicos (se corrigió: votana→botana, bara→barata)"
  }
}
```

---

## 9. INTEGRACIÓN EN ADMIN PANEL

### 9.1 Componente de Gestión de Sinónimos

#### **Ubicación:** Sección de edición de productos existente

```tsx
// components/admin/SinonimosManager.tsx
import React, { useState, useEffect } from 'react';
import { Badge, Input, Button, Table, Modal, message } from 'antd';
import { PlusOutlined, DeleteOutlined, RobotOutlined } from '@ant-design/icons';

interface SinonimoItem {
  id?: number;
  producto_id: number;
  sinonimo: string;
  popularidad: number;
  precision_score: number;
  fuente: 'admin' | 'auto_learning' | 'user_feedback';
  activo: boolean;
}

interface SinonimosManagerProps {
  productoId: number;
  productoNombre: string;
  onSinonimosChange: (sinonimos: SinonimoItem[]) => void;
}

const SinonimosManager: React.FC<SinonimosManagerProps> = ({
  productoId,
  productoNombre,
  onSinonimosChange
}) => {
  const [sinonimos, setSinonimos] = useState<SinonimoItem[]>([]);
  const [nuevoSinonimo, setNuevoSinonimo] = useState('');
  const [sugerenciasAuto, setSugerenciasAuto] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  // Cargar sinónimos existentes
  useEffect(() => {
    if (productoId) {
      cargarSinonimos();
      cargarSugerenciasAutomaticas();
    }
  }, [productoId]);

  const cargarSinonimos = async () => {
    try {
      const response = await fetch(`/api/admin/productos/${productoId}/sinonimos`);
      const data = await response.json();
      setSinonimos(data.sinonimos || []);
    } catch (error) {
      message.error('Error al cargar sinónimos');
    }
  };

  const cargarSugerenciasAutomaticas = async () => {
    try {
      const response = await fetch(`/api/admin/productos/${productoId}/sinonimos/sugerencias`);
      const data = await response.json();
      setSugerenciasAuto(data.sugerencias || []);
    } catch (error) {
      console.error('Error al cargar sugerencias:', error);
    }
  };

  const agregarSinonimo = async (sinonimo: string, fuente: string = 'admin') => {
    if (!sinonimo.trim()) return;

    try {
      setLoading(true);
      const response = await fetch(`/api/admin/productos/${productoId}/sinonimos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sinonimo: sinonimo.trim().toLowerCase(),
          fuente,
          activo: true
        })
      });

      if (response.ok) {
        message.success('Sinónimo agregado correctamente');
        setNuevoSinonimo('');
        cargarSinonimos();
        onSinonimosChange([...sinonimos, { 
          producto_id: productoId,
          sinonimo: sinonimo.trim().toLowerCase(),
          popularidad: 0,
          precision_score: 1.0,
          fuente: fuente as any,
          activo: true
        }]);
      } else {
        const error = await response.json();
        message.error(error.message || 'Error al agregar sinónimo');
      }
    } catch (error) {
      message.error('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const eliminarSinonimo = async (sinonimoId: number) => {
    try {
      const response = await fetch(`/api/admin/sinonimos/${sinonimoId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        message.success('Sinónimo eliminado');
        cargarSinonimos();
      }
    } catch (error) {
      message.error('Error al eliminar sinónimo');
    }
  };

  const columns = [
    {
      title: 'Sinónimo',
      dataIndex: 'sinonimo',
      key: 'sinonimo',
      render: (text: string, record: SinonimoItem) => (
        <span>
          {text}
          {record.fuente === 'auto_learning' && (
            <Badge 
              count={<RobotOutlined style={{ color: '#1890ff' }} />} 
              style={{ marginLeft: 8 }}
              title="Aprendido automáticamente"
            />
          )}
        </span>
      )
    },
    {
      title: 'Popularidad',
      dataIndex: 'popularidad',
      key: 'popularidad',
      render: (valor: number) => (
        <Badge 
          count={valor} 
          style={{ 
            backgroundColor: valor > 10 ? '#52c41a' : valor > 5 ? '#faad14' : '#d9d9d9' 
          }} 
        />
      )
    },
    {
      title: 'Precisión',
      dataIndex: 'precision_score',
      key: 'precision_score',
      render: (score: number) => `${(score * 100).toFixed(0)}%`
    },
    {
      title: 'Acciones',
      key: 'actions',
      render: (_, record: SinonimoItem) => (
        <Button
          type="text"
          danger
          size="small"
          icon={<DeleteOutlined />}
          onClick={() => eliminarSinonimo(record.id!)}
        />
      )
    }
  ];

  return (
    <div style={{ marginTop: 16 }}>
      <h4>Gestión de Sinónimos para: {productoNombre}</h4>
      
      {/* Agregar nuevo sinónimo */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <Input
          placeholder="Escribir sinónimo (ej: chettos, cheetos mix)"
          value={nuevoSinonimo}
          onChange={(e) => setNuevoSinonimo(e.target.value)}
          onPressEnter={() => agregarSinonimo(nuevoSinonimo)}
        />
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          loading={loading}
          onClick={() => agregarSinonimo(nuevoSinonimo)}
        >
          Agregar
        </Button>
      </div>

      {/* Sugerencias automáticas */}
      {sugerenciasAuto.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <p><RobotOutlined /> Sugerencias basadas en búsquedas de usuarios:</p>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {sugerenciasAuto.map((sugerencia, index) => (
              <Button
                key={index}
                size="small"
                type="dashed"
                onClick={() => agregarSinonimo(sugerencia, 'auto_learning')}
              >
                + {sugerencia}
              </Button>
            ))}
          </div>
        </div>
      )}

      {/* Tabla de sinónimos existentes */}
      <Table
        columns={columns}
        dataSource={sinonimos}
        size="small"
        rowKey="id"
        pagination={false}
        locale={{ emptyText: 'Sin sinónimos configurados' }}
      />

      {/* Métricas rápidas */}
      <div style={{ marginTop: 16, padding: 12, background: '#f5f5f5', borderRadius: 6 }}>
        <p style={{ margin: 0, fontSize: 12, color: '#666' }}>
          📊 Total sinónimos: {sinonimos.length} | 
          🔍 Búsquedas últimos 30 días: {sinonimos.reduce((acc, s) => acc + s.popularidad, 0)} |
          🎯 Precisión promedio: {sinonimos.length > 0 ? Math.round((sinonimos.reduce((acc, s) => acc + s.precision_score, 0) / sinonimos.length) * 100) : 0}%
        </p>
      </div>
    </div>
  );
};

export default SinonimosManager;
```

### 9.2 API Backend para Gestión de Sinónimos

```javascript
// routes/admin/sinonimos.js
const express = require('express');
const router = express.Router();
const mysql = require('mysql2/promise');
const { verificarAdmin } = require('../../middlewares/auth');

// Obtener sinónimos de un producto
router.get('/productos/:productoId/sinonimos', verificarAdmin, async (req, res) => {
  try {
    const { productoId } = req.params;
    
    const [sinonimos] = await db.query(`
      SELECT ps.*, u.nombre as creado_por_nombre
      FROM producto_sinonimos ps
      LEFT JOIN usuarios u ON ps.creado_por = u.id
      WHERE ps.producto_id = ? AND ps.activo = 1
      ORDER BY ps.popularidad DESC, ps.precision_score DESC
    `, [productoId]);

    res.json({ 
      success: true, 
      sinonimos,
      total: sinonimos.length 
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Obtener sugerencias automáticas basadas en métricas de búsqueda
router.get('/productos/:productoId/sinonimos/sugerencias', verificarAdmin, async (req, res) => {
  try {
    const { productoId } = req.params;
    
    // Obtener términos de búsqueda que resultaron en clicks a este producto
    const [sugerencias] = await db.query(`
      SELECT bm.termino_busqueda, COUNT(*) as frecuencia, 
             AVG(bm.conversiones) as conversion_rate
      FROM busqueda_metricas bm
      WHERE bm.producto_id = ? 
        AND bm.clicks > 0
        AND bm.fecha_busqueda > DATE_SUB(NOW(), INTERVAL 30 DAY)
        AND bm.termino_busqueda NOT IN (
          SELECT sinonimo FROM producto_sinonimos 
          WHERE producto_id = ? AND activo = 1
        )
      GROUP BY bm.termino_busqueda
      HAVING frecuencia >= 3 AND conversion_rate > 0.1
      ORDER BY frecuencia DESC, conversion_rate DESC
      LIMIT 10
    `, [productoId, productoId]);

    const terminosSugeridos = sugerencias
      .filter(s => s.termino_busqueda.length > 2)
      .map(s => s.termino_busqueda);

    res.json({ 
      success: true, 
      sugerencias: terminosSugeridos 
    });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

// Agregar nuevo sinónimo
router.post('/productos/:productoId/sinonimos', verificarAdmin, async (req, res) => {
  try {
    const { productoId } = req.params;
    const { sinonimo, fuente = 'admin' } = req.body;
    const userId = req.user.id;

    // Validaciones
    if (!sinonimo || sinonimo.trim().length < 2) {
      return res.status(400).json({ 
        success: false, 
        message: 'El sinónimo debe tener al menos 2 caracteres' 
      });
    }

    // Verificar que el producto existe
    const [producto] = await db.query('SELECT id_producto FROM productos WHERE id_producto = ?', [productoId]);
    if (producto.length === 0) {
      return res.status(404).json({ 
        success: false, 
        message: 'Producto no encontrado' 
      });
    }

    // Verificar que el sinónimo no existe ya
    const [existente] = await db.query(
      'SELECT id FROM producto_sinonimos WHERE producto_id = ? AND sinonimo = ?',
      [productoId, sinonimo.trim().toLowerCase()]
    );

    if (existente.length > 0) {
      return res.status(409).json({ 
        success: false, 
        message: 'Este sinónimo ya existe para este producto' 
      });
    }

    // Insertar nuevo sinónimo
    const [resultado] = await db.query(`
      INSERT INTO producto_sinonimos (producto_id, sinonimo, fuente, creado_por, activo)
      VALUES (?, ?, ?, ?, 1)
    `, [productoId, sinonimo.trim().toLowerCase(), fuente, userId]);

    res.json({ 
      success: true, 
      message: 'Sinónimo agregado correctamente',
      id: resultado.insertId 
    });

  } catch (error) {
    if (error.code === 'ER_DUP_ENTRY') {
      res.status(409).json({ 
        success: false, 
        message: 'Este sinónimo ya existe' 
      });
    } else {
      res.status(500).json({ success: false, message: error.message });
    }
  }
});

// Eliminar sinónimo
router.delete('/sinonimos/:sinonimoId', verificarAdmin, async (req, res) => {
  try {
    const { sinonimoId } = req.params;
    
    const [resultado] = await db.query(
      'UPDATE producto_sinonimos SET activo = 0 WHERE id = ?',
      [sinonimoId]
    );

    if (resultado.affectedRows === 0) {
      return res.status(404).json({ 
        success: false, 
        message: 'Sinónimo no encontrado' 
      });
    }

    res.json({ 
      success: true, 
      message: 'Sinónimo eliminado correctamente' 
    });

  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

module.exports = router;
```

---

## 10. MOTOR DE BÚSQUEDA INTELIGENTE MEJORADO

### 10.1 Clase Principal del Sistema Mejorado

```python
# sistema_lcln_inteligente.py
import mysql.connector
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import re
from corrector_ortografico import CorrectorOrtografico

class SistemaLCLNInteligente:
    """
    Sistema LCLN Inteligente con sinónimos dinámicos y prioridades
    """
    
    def __init__(self):
        # Configuración de base de datos
        self.mysql_config = {
            'host': 'localhost',
            'database': 'lynxshop',
            'user': 'root',
            'password': '12345678',
            'charset': 'utf8mb4'
        }
        
        # Componentes del sistema
        self.corrector = CorrectorOrtografico()
        self.analizador_negaciones = AnalizadorNegaciones()
        
        # Cache para optimización
        self._cache_sinonimos = {}
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=10)
        
        # Configuración de scoring
        self.pesos_scoring = {
            'exact_synonym': 1.0,      # Sinónimo exacto
            'direct_product': 0.9,     # Producto directo
            'category_match': 0.7,     # Coincidencia de categoría
            'attribute_match': 0.6,    # Coincidencia de atributo
            'price_range': 0.4,        # Rango de precio
            'popularity_boost': 0.3,   # Boost por popularidad
            'spelling_correction': 0.5  # Corrección ortográfica
        }

    def buscar_inteligente(self, consulta: str, limit: int = 20, user_id: int = None) -> Dict:
        """
        Búsqueda inteligente con sistema de prioridades
        """
        inicio = datetime.now()
        consulta_original = consulta
        
        # Análizar consulta inicial
        analisis_inicial = self._analizar_consulta_completa(consulta)
        
        resultados_finales = []
        estrategia_usada = []
        correcciones_aplicadas = False
        
        # 🥇 PRIORIDAD 1: Búsqueda exacta + sinónimos específicos
        resultados_exactos = self._buscar_por_sinonimos_exactos(analisis_inicial['terminos'])
        if resultados_exactos:
            resultados_finales.extend(resultados_exactos[:limit])
            estrategia_usada.append("sinonimos_exactos")
        
        # 🥈 PRIORIDAD 2: Búsqueda por categoría + atributos + negaciones
        if len(resultados_finales) < limit:
            resultados_categoria = self._buscar_por_categoria_atributos(
                analisis_inicial, 
                limit - len(resultados_finales)
            )
            if resultados_categoria:
                resultados_finales.extend(resultados_categoria)
                estrategia_usada.append("categoria_atributos")
        
        # 🥉 PRIORIDAD 3: Corrección ortográfica + fallback
        if len(resultados_finales) < max(3, limit // 3):  # Al menos 3 resultados
            resultado_correcciones = self.corrector.corregir_consulta(consulta)
            if resultado_correcciones.get('applied', False):
                correcciones_aplicadas = True
                consulta_corregida = resultado_correcciones.get('corrected_query', consulta)
                
                # Repetir búsqueda con consulta corregida
                analisis_corregido = self._analizar_consulta_completa(consulta_corregida)
                
                resultados_corregidos = self._buscar_por_sinonimos_exactos(analisis_corregido['terminos'])
                if not resultados_corregidos:
                    resultados_corregidos = self._buscar_por_categoria_atributos(
                        analisis_corregido, 
                        limit - len(resultados_finales)
                    )
                
                if resultados_corregidos:
                    resultados_finales.extend(resultados_corregidos)
                    estrategia_usada.append("correccion_ortografica")
        
        # Aplicar scoring y ranking inteligente
        resultados_rankeados = self._aplicar_scoring_inteligente(
            resultados_finales, 
            analisis_inicial,
            correcciones_aplicadas
        )
        
        # Registrar métricas para aprendizaje automático
        if user_id:
            self._registrar_busqueda_metricas(consulta_original, resultados_rankeados, user_id)
        
        tiempo_total = (datetime.now() - inicio).total_seconds() * 1000
        
        return {
            'success': True,
            'processing_time_ms': round(tiempo_total, 2),
            'original_query': consulta_original,
            'corrections': {
                'applied': correcciones_aplicadas,
                'details': resultado_correcciones if correcciones_aplicadas else {}
            },
            'interpretation': {
                'terminos_detectados': analisis_inicial['terminos'],
                'negaciones': analisis_inicial['negaciones'],
                'filtros_precio': analisis_inicial['filtros_precio'],
                'estrategias_usadas': estrategia_usada
            },
            'recommendations': resultados_rankeados[:limit],
            'products_found': len(resultados_rankeados),
            'user_message': self._generar_mensaje_usuario(analisis_inicial, estrategia_usada, len(resultados_rankeados)),
            'metadata': {
                'search_type': 'intelligent_lcln',
                'has_synonyms': any('sinonimos' in est for est in estrategia_usada),
                'has_corrections': correcciones_aplicadas,
                'priority_levels_used': len(estrategia_usada)
            }
        }

    def _buscar_por_sinonimos_exactos(self, terminos: List[str]) -> List[Dict]:
        """
        Búsqueda por sinónimos específicos en la base de datos
        """
        if not terminos:
            return []
        
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor(dictionary=True)
            
            # Construir query para buscar sinónimos
            placeholders = ','.join(['%s'] * len(terminos))
            query = f"""
            SELECT DISTINCT p.*, ps.sinonimo, ps.popularidad,
                   ps.precision_score, c.nombre as categoria
            FROM productos p
            INNER JOIN producto_sinonimos ps ON p.id_producto = ps.producto_id
            INNER JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE ps.sinonimo IN ({placeholders}) 
              AND ps.activo = 1 
              AND p.activo = 1
            ORDER BY ps.popularidad DESC, ps.precision_score DESC, p.precio ASC
            """
            
            cursor.execute(query, terminos)
            resultados = cursor.fetchall()
            
            # Procesar resultados
            productos_encontrados = []
            for row in resultados:
                producto = {
                    'id': row['id_producto'],
                    'nombre': row['nombre'],
                    'precio': float(row['precio']),
                    'categoria': row['categoria'],
                    'descripcion': row['descripcion'] or '',
                    'imagen': row['imagen'] or 'default.jpg',
                    'cantidad': row['cantidad'],
                    'available': row['cantidad'] > 0,
                    'match_score': 0.95 + (row['precision_score'] * 0.05),
                    'match_type': 'exact_synonym',
                    'match_details': {
                        'sinonimo_usado': row['sinonimo'],
                        'popularidad': row['popularidad'],
                        'precision': row['precision_score']
                    },
                    'source': 'sinonimos_especificos'
                }
                productos_encontrados.append(producto)
            
            return productos_encontrados
            
        except Exception as e:
            print(f"Error en búsqueda por sinónimos: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def _buscar_por_categoria_atributos(self, analisis: Dict, limit: int) -> List[Dict]:
        """
        Búsqueda por categoría, atributos y manejo de negaciones
        """
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor(dictionary=True)
            
            # Construir query base
            query_base = """
            SELECT DISTINCT p.*, c.nombre as categoria
            FROM productos p
            INNER JOIN categorias c ON p.id_categoria = c.id_categoria
            LEFT JOIN producto_atributos pa ON p.id_producto = pa.producto_id
            WHERE p.activo = 1
            """
            
            condiciones = []
            parametros = []
            
            # Filtros de categoría inferida
            if analisis.get('categoria_inferida'):
                condiciones.append("c.nombre = %s")
                parametros.append(analisis['categoria_inferida'])
            
            # Manejo de negaciones
            for negacion in analisis.get('negaciones', []):
                condiciones.append("""
                    (pa.atributo = %s AND pa.valor = FALSE) 
                    OR (pa.atributo = %s AND pa.producto_id IS NULL)
                """)
                parametros.extend([negacion['atributo'], negacion['atributo']])
            
            # Filtros de precio
            if analisis.get('filtros_precio'):
                filtro_precio = analisis['filtros_precio']
                if filtro_precio.get('max'):
                    condiciones.append("p.precio <= %s")
                    parametros.append(filtro_precio['max'])
                if filtro_precio.get('min'):
                    condiciones.append("p.precio >= %s")
                    parametros.append(filtro_precio['min'])
            
            # Filtros de atributos positivos
            for atributo in analisis.get('atributos_positivos', []):
                condiciones.append("(pa.atributo = %s AND pa.valor = TRUE)")
                parametros.append(atributo)
            
            # Construir query final
            if condiciones:
                query_final = query_base + " AND " + " AND ".join(condiciones)
            else:
                query_final = query_base
            
            query_final += " ORDER BY p.precio ASC LIMIT %s"
            parametros.append(limit)
            
            cursor.execute(query_final, parametros)
            resultados = cursor.fetchall()
            
            # Procesar resultados
            productos_encontrados = []
            for row in resultados:
                producto = {
                    'id': row['id_producto'],
                    'nombre': row['nombre'],
                    'precio': float(row['precio']),
                    'categoria': row['categoria'],
                    'descripcion': row['descripcion'] or '',
                    'imagen': row['imagen'] or 'default.jpg',
                    'cantidad': row['cantidad'],
                    'available': row['cantidad'] > 0,
                    'match_score': 0.8,
                    'match_type': 'category_attributes',
                    'match_details': {
                        'filtros_aplicados': list(analisis.keys()),
                        'negaciones_aplicadas': len(analisis.get('negaciones', []))
                    },
                    'source': 'categoria_atributos'
                }
                productos_encontrados.append(producto)
            
            return productos_encontrados
            
        except Exception as e:
            print(f"Error en búsqueda por categoría: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def _analizar_consulta_completa(self, consulta: str) -> Dict:
        """
        Análisis completo de la consulta con detección de negaciones, 
        filtros de precio y categorías
        """
        terminos = consulta.lower().split()
        
        analisis = {
            'terminos': terminos,
            'negaciones': [],
            'atributos_positivos': [],
            'filtros_precio': {},
            'categoria_inferida': None
        }
        
        # Detectar negaciones
        negaciones_detectadas = self.analizador_negaciones.detectar_negaciones(consulta)
        analisis['negaciones'] = negaciones_detectadas
        
        # Detectar filtros de precio
        filtros_precio = self._detectar_filtros_precio(consulta)
        if filtros_precio:
            analisis['filtros_precio'] = filtros_precio
        
        # Detectar atributos positivos
        atributos_conocidos = ['picante', 'dulce', 'salado', 'grande', 'pequeño']
        for termino in terminos:
            if termino in atributos_conocidos and not any(neg['atributo'] == termino for neg in negaciones_detectadas):
                analisis['atributos_positivos'].append(termino)
        
        # Inferir categoría
        categoria = self._inferir_categoria(terminos)
        if categoria:
            analisis['categoria_inferida'] = categoria
        
        return analisis

    def _detectar_filtros_precio(self, consulta: str) -> Dict:
        """
        Detectar filtros de precio en la consulta
        """
        filtros = {}
        
        # Patrones para detectar precios
        patron_menor = r'(?:menor|menos)\s+(?:de|a)\s+(\d+)'
        patron_mayor = r'(?:mayor|mas|más)\s+(?:de|a)\s+(\d+)'
        patron_entre = r'entre\s+(\d+)\s+y\s+(\d+)'
        patron_barato = r'\b(?:barato|barata|económico|económica)\b'
        
        # Menor que
        match_menor = re.search(patron_menor, consulta.lower())
        if match_menor:
            filtros['max'] = int(match_menor.group(1))
        
        # Mayor que  
        match_mayor = re.search(patron_mayor, consulta.lower())
        if match_mayor:
            filtros['min'] = int(match_mayor.group(1))
        
        # Entre rango
        match_entre = re.search(patron_entre, consulta.lower())
        if match_entre:
            filtros['min'] = int(match_entre.group(1))
            filtros['max'] = int(match_entre.group(2))
        
        # Términos de precio bajo
        if re.search(patron_barato, consulta.lower()):
            # Si no hay precio específico, usar precio promedio como referencia
            if not filtros:
                filtros['tendency'] = 'low'
        
        return filtros if filtros else {}

    def _inferir_categoria(self, terminos: List[str]) -> Optional[str]:
        """
        Inferir categoría basada en términos de la consulta
        """
        mapeo_categorias = {
            'botana': 'snacks',
            'snack': 'snacks', 
            'papas': 'snacks',
            'doritos': 'snacks',
            'cheetos': 'snacks',
            'bebida': 'bebidas',
            'refresco': 'bebidas',
            'coca': 'bebidas',
            'agua': 'bebidas',
            'galleta': 'panaderia',
            'pan': 'panaderia',
            'fruta': 'frutas',
            'manzana': 'frutas',
            'naranja': 'frutas'
        }
        
        for termino in terminos:
            if termino in mapeo_categorias:
                return mapeo_categorias[termino]
        
        return None

    def _aplicar_scoring_inteligente(self, productos: List[Dict], analisis: Dict, correcciones_aplicadas: bool) -> List[Dict]:
        """
        Aplicar scoring inteligente basado en relevancia y popularidad
        """
        for producto in productos:
            score_final = producto.get('match_score', 0.5)
            
            # Boost por tipo de match
            match_type = producto.get('match_type', 'unknown')
            if match_type == 'exact_synonym':
                score_final += self.pesos_scoring['exact_synonym'] * 0.1
            elif match_type == 'category_attributes':
                score_final += self.pesos_scoring['category_match'] * 0.1
            
            # Boost por disponibilidad
            if producto.get('available', False):
                score_final += 0.05
            
            # Penalización por corrección ortográfica
            if correcciones_aplicadas and match_type != 'exact_synonym':
                score_final -= self.pesos_scoring['spelling_correction'] * 0.1
            
            # Boost por precio en rango solicitado
            if analisis.get('filtros_precio', {}).get('tendency') == 'low':
                precio = producto.get('precio', 999)
                if precio < 20:  # Precio considerado bajo
                    score_final += 0.1
            
            producto['match_score'] = min(score_final, 1.0)
        
        # Ordenar por score final
        return sorted(productos, key=lambda x: x['match_score'], reverse=True)

    def _generar_mensaje_usuario(self, analisis: Dict, estrategias: List[str], total_resultados: int) -> str:
        """
        Generar mensaje descriptivo para el usuario
        """
        mensajes = []
        
        if 'sinonimos_exactos' in estrategias:
            mensajes.append("Encontrados productos específicos")
        
        if analisis.get('negaciones'):
            negaciones_texto = ', '.join([f"sin {neg['atributo']}" for neg in analisis['negaciones']])
            mensajes.append(f"Aplicando filtros: {negaciones_texto}")
        
        if analisis.get('filtros_precio'):
            filtro = analisis['filtros_precio']
            if filtro.get('max'):
                mensajes.append(f"precio menor a ${filtro['max']}")
            elif filtro.get('tendency') == 'low':
                mensajes.append("productos económicos")
        
        if 'correccion_ortografica' in estrategias:
            mensajes.append("(con corrección ortográfica aplicada)")
        
        mensaje_base = f"Encontrados {total_resultados} productos"
        if mensajes:
            mensaje_base += f" - {', '.join(mensajes)}"
        
        return mensaje_base

    def _registrar_busqueda_metricas(self, consulta: str, resultados: List[Dict], user_id: int):
        """
        Registrar métricas de búsqueda para aprendizaje automático
        """
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor()
            
            session_id = f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
            
            # Registrar cada resultado para análisis futuro
            for producto in resultados[:5]:  # Solo los primeros 5
                cursor.execute("""
                    INSERT INTO busqueda_metricas 
                    (termino_busqueda, producto_id, usuario_id, session_id, fecha_busqueda)
                    VALUES (%s, %s, %s, %s, %s)
                """, [
                    consulta, 
                    producto.get('id'), 
                    user_id, 
                    session_id,
                    datetime.now()
                ])
            
            conn.commit()
            
        except Exception as e:
            print(f"Error registrando métricas: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()


class AnalizadorNegaciones:
    """
    Clase especializada en detectar y manejar negaciones
    """
    
    def __init__(self):
        self.palabras_negacion = ['sin', 'no', 'libre', 'zero', 'sin', 'ningún', 'ninguna']
        self.atributos_comunes = [
            'picante', 'azucar', 'azúcar', 'gluten', 'lactosa', 
            'sal', 'grasa', 'conservantes', 'artificiales'
        ]
    
    def detectar_negaciones(self, consulta: str) -> List[Dict]:
        """
        Detectar patrones de negación en la consulta
        """
        negaciones_encontradas = []
        tokens = consulta.lower().split()
        
        for i, token in enumerate(tokens):
            if token in self.palabras_negacion:
                # Buscar el siguiente token que sea un atributo conocido
                for j in range(i + 1, min(i + 3, len(tokens))):  # Buscar hasta 2 tokens adelante
                    if tokens[j] in self.atributos_comunes:
                        negaciones_encontradas.append({
                            'palabra_negacion': token,
                            'atributo': tokens[j],
                            'posicion': i,
                            'confianza': 0.9
                        })
                        break
        
        return negaciones_encontradas

# Instancia global del sistema
sistema_lcln_inteligente = SistemaLCLNInteligente()
```

---

## 11. CONCLUSIONES Y TRABAJO FUTURO

### 11.1 Logros del Sistema Base
- ✅ Resolución efectiva de ambigüedades mediante AFD multi-nivel
- ✅ Corrección ortográfica con alta precisión para español
- ✅ Sistema de recomendaciones inteligente
- ✅ Integración transparente con LYNX
- ✅ Performance optimizado con cache

### 11.2 Mejoras del Sistema Inteligente
- ✅ **Sinónimos específicos** por producto en base de datos
- ✅ **Sistema de prioridades** jerárquico para búsquedas
- ✅ **Manejo inteligente de negaciones** ("sin picante", "libre de gluten")
- ✅ **Integración orgánica** en admin panel existente
- ✅ **Aprendizaje automático** basado en métricas de usuario
- ✅ **Sugerencias automáticas** de sinónimos basadas en datos reales

### 11.3 Métricas de Éxito Esperadas
- 📈 **Precisión de búsqueda**: 85% → 95%
- ⚡ **Tiempo de respuesta**: <100ms en 95% de casos
- 🎯 **Satisfacción de usuario**: 70% → 90%
- 🔍 **Cobertura de consultas**: 60% → 85%
- 🤖 **Aprendizaje automático**: 50+ sinónimos/mes autodescubiertos

### 11.4 Roadmap Futuro

#### **Fase 1: Implementación Base (Sprint 1-2)**
- [ ] Crear tablas de sinónimos y métricas
- [ ] Integrar componente admin de gestión de sinónimos
- [ ] Implementar motor de búsqueda con prioridades
- [ ] Sistema básico de negaciones

#### **Fase 2: Inteligencia Avanzada (Sprint 3-4)**
- [ ] Algoritmo de aprendizaje automático para sinónimos
- [ ] Sistema de scoring inteligente con métricas reales
- [ ] Dashboard de analytics para admin
- [ ] Optimizaciones de performance

#### **Fase 3: Características Avanzadas (Sprint 5-6)**
- [ ] Búsqueda por voz con procesamiento NLP
- [ ] Recomendaciones contextuales por ubicación/hora
- [ ] Sistema de feedback de usuario integrado
- [ ] API pública para desarrolladores

---

## 📚 ANEXOS

### A.1 Queries SQL de Configuración Inicial

```sql
-- Poblar datos iniciales de sinónimos más comunes
INSERT INTO producto_sinonimos (producto_id, sinonimo, popularidad, fuente) VALUES
(2, 'coca', 15, 'admin'),
(2, 'coca-cola', 25, 'admin'),
(2, 'coka', 8, 'admin'),
(8, 'doritos', 20, 'admin'),
(8, 'dorito', 12, 'admin'),
(20, 'crujitos', 10, 'admin'),
(20, 'cheetos', 18, 'admin'),
(20, 'chettos', 22, 'admin');

-- Configurar atributos iniciales de productos
INSERT INTO producto_atributos (producto_id, atributo, valor, intensidad) VALUES
(2, 'azucar', TRUE, 8),
(3, 'azucar', FALSE, 0),
(8, 'picante', TRUE, 7),
(20, 'picante', TRUE, 6),
(21, 'picante', TRUE, 5);
```

### A.2 Configuración de Índices para Performance

```sql
-- Índices optimizados para búsquedas rápidas
CREATE INDEX idx_sinonimos_busqueda ON producto_sinonimos (sinonimo, activo, popularidad DESC);
CREATE INDEX idx_productos_categoria_precio ON productos (id_categoria, precio ASC, activo);
CREATE INDEX idx_atributos_busqueda ON producto_atributos (atributo, valor, producto_id);
CREATE FULLTEXT INDEX idx_productos_fulltext ON productos (nombre, descripcion);
```

---

**Documento Técnico Completo - Sistema LCLN Inteligente v2.0**  
*Actualizado: Julio 2025*

