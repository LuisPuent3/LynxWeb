import { describe, it, expect, vi } from "vitest";
import api from "../../utils/api";

describe("LYNX_010: Prueba de Manejo de Errores API", () => {
  it("Debe devolver código 404 al solicitar una ruta inexistente", async () => {
    try {
      await api.get("/ruta-que-no-existe");
      // Si llegamos aquí, la prueba debería fallar porque esperamos un error
      expect(true).toBe(false);
    } catch (error: any) {
      expect(error.response.status).toBe(404);
      console.log("Test de ruta inexistente exitoso");
    }
  });

  it("Debe devolver código 404 al solicitar un producto inexistente", async () => {
    try {
      await api.get("/productos/99999");
      // Si llegamos aquí, la prueba debería fallar porque esperamos un error
      expect(true).toBe(false);
    } catch (error: any) {
      expect(error.response.status).toBe(404);
      console.log("Test de producto inexistente exitoso");
    }
  });

  it("Debe devolver código 401 al acceder a ruta protegida sin token", async () => {
    try {
      await api.get("/admin/usuarios");
      // Si llegamos aquí, la prueba debería fallar porque esperamos un error
      expect(true).toBe(false);
    } catch (error: any) {
      expect(error.response.status).toBe(401);
      console.log("Test de autenticación requerida exitoso");
    }
  });

  it("Debe devolver código 401 al proporcionar un token inválido", async () => {
    try {
      await api.get("/admin/usuarios", {
        headers: {
          Authorization: "Bearer token-invalido"
        }
      });
      // Si llegamos aquí, la prueba debería fallar porque esperamos un error
      expect(true).toBe(false);
    } catch (error: any) {
      expect(error.response.status).toBe(401);
      console.log("Test de token inválido exitoso");
    }
  });

  it("Debe devolver código 400 al enviar datos inválidos en POST", async () => {
    try {
      // Enviar objeto vacío o datos incorrectos para un POST
      await api.post("/productos", {});
      // Si llegamos aquí, la prueba debería fallar porque esperamos un error
      expect(true).toBe(false);
    } catch (error: any) {
      expect(error.response.status).toBe(400);
      console.log("Test de datos inválidos en POST exitoso");
    }
  });

  /**
   * Prueba: Escenario de acción sin permisos suficientes
   * 
   * Objetivo: Verificar que el sistema devuelve un código 403 cuando
   * un usuario intenta realizar una acción para la que no tiene permisos
   */
  it('Debe devolver código 403 al intentar acción sin permisos', async () => {
    try {
      // Intentar realizar una acción que requiere permisos de administrador
      // usando un token de usuario normal
      await api.delete('/usuarios/1', {
        headers: {
          Authorization: 'Bearer user_token_123' // Token de usuario normal (no admin)
        }
      });
      // Si llegamos aquí, la prueba debe fallar
      expect(true).toBe(false);
    } catch (error: any) {
      expect(error.response.status).toBe(403);
      console.log("Test de permisos insuficientes exitoso");
    }
  });
}); 