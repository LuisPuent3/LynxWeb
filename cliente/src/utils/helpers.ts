/**
 * Funciones de utilidad para formatear datos
 */

/**
 * Formatea una fecha ISO a un formato legible
 * @param dateString - String de fecha en formato ISO
 * @returns Fecha formateada en español
 */
export const formatDate = (dateString: string): string => {
  if (!dateString) return 'Fecha no disponible';
  
  const options: Intl.DateTimeFormatOptions = { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', options);
  } catch (error) {
    console.error('Error formateando fecha:', error);
    return dateString;
  }
};

/**
 * Formatea un número a moneda
 * @param amount - Cantidad a formatear
 * @returns Cadena formateada como moneda
 */
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
    minimumFractionDigits: 2
  }).format(amount);
};

/**
 * Mapea el nombre del estado de pedido desde la DB al tipo usado en el frontend
 * @param estadoDB - Nombre del estado del pedido en la base de datos
 * @returns Estado tipado para el frontend
 */
export const mapOrderStatus = (estadoDB: string): 'pendiente' | 'entregado' | 'cancelado' | 'aceptado' => {
  // Convertir a minúsculas para hacer la comparación insensible a mayúsculas/minúsculas
  const estado = estadoDB?.toLowerCase() || '';
  
  // Mapeo básico para los estados principales
  if (estado.includes('pendiente')) return 'pendiente';
  if (estado.includes('acept')) return 'aceptado';
  if (estado.includes('entreg')) return 'entregado';
  if (estado.includes('cancel')) return 'cancelado';
  
  // Estado por defecto si no hay coincidencia
  return 'pendiente';
};