// Servicio de recuperación de contraseña
import api from '../utils/api';

/**
 * Realiza un diagnóstico del sistema de recuperación de contraseña
 * @returns Información sobre el estado del sistema
 */
export const diagnosticarSistema = async () => {
  try {
    const response = await api.get('/password-reset/diagnostico');
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error al diagnosticar el sistema:', error);
    return {
      success: false,
      error
    };
  }
};

/**
 * Solicita la recuperación de contraseña para un correo electrónico
 * @param correo Correo electrónico del usuario
 * @returns Resultado de la operación
 */
export const solicitarRecuperacion = async (correo: string) => {
  try {
    const response = await api.post('/password-reset/request', { correo });
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error al solicitar recuperación:', error);
    return {
      success: false,
      error
    };
  }
};

/**
 * Restablece la contraseña con un token de recuperación
 * @param token Token de recuperación
 * @param nuevaContraseña Nueva contraseña
 * @returns Resultado de la operación
 */
export const restablecerContraseña = async (token: string, nuevaContraseña: string) => {
  try {
    const response = await api.post('/password-reset/reset', { token, nuevaContraseña });
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error al restablecer contraseña:', error);
    return {
      success: false,
      error
    };
  }
};
