import React from 'react';

// Datos de ejemplo para pedidos
export const mockOrders = [
  {
    id_pedido: 1,
    fecha: new Date().toISOString(),
    estado: 'pendiente',
    metodo_pago: 'efectivo',
    tracking_code: '',
    total: 1500,
    productos: [
      {
        id_producto: 1,
        nombre: 'Coca-Cola',
        cantidad: 2,
        precio: 15.50
      },
      {
        id_producto: 2,
        nombre: 'Doritos',
        cantidad: 3,
        precio: 25.00
      }
    ]
  },
  {
    id_pedido: 2,
    fecha: new Date(Date.now() - 86400000).toISOString(), // Ayer
    estado: 'aceptado',
    metodo_pago: 'efectivo',
    tracking_code: '',
    total: 750,
    productos: [
      {
        id_producto: 3,
        nombre: 'Arroz',
        cantidad: 1,
        precio: 10.00
      },
      {
        id_producto: 4,
        nombre: 'Manzana',
        cantidad: 5,
        precio: 12.00
      }
    ]
  },
  {
    id_pedido: 3,
    fecha: new Date(Date.now() - 172800000).toISOString(), // Hace 2 días
    estado: 'aceptado',
    metodo_pago: 'efectivo',
    tracking_code: '',
    total: 356,
    productos: [
      {
        id_producto: 5,
        nombre: 'Lechuga',
        cantidad: 2,
        precio: 8.00
      },
      {
        id_producto: 1,
        nombre: 'Coca-Cola',
        cantidad: 1,
        precio: 15.50
      }
    ]
  },
  {
    id_pedido: 4,
    fecha: new Date(Date.now() - 345600000).toISOString(), // Hace 4 días
    estado: 'entregado',
    metodo_pago: 'efectivo',
    tracking_code: 'TRK789012',
    total: 860,
    productos: [
      {
        id_producto: 2,
        nombre: 'Doritos',
        cantidad: 4,
        precio: 25.00
      },
      {
        id_producto: 3,
        nombre: 'Arroz',
        cantidad: 2,
        precio: 10.00
      }
    ]
  },
  {
    id_pedido: 5,
    fecha: new Date(Date.now() - 172800000).toISOString(), // Hace 2 días
    estado: 'cancelado',
    metodo_pago: 'efectivo',
    tracking_code: '',
    total: 120,
    productos: [
      {
        id_producto: 4,
        nombre: 'Manzana',
        cantidad: 10,
        precio: 12.00
      }
    ]
  }
];

export default mockOrders;
