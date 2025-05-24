# Sistema de Recuperación de Contraseña - LynxShop

## Descripción
Este sistema permite a los usuarios recuperar su contraseña a través de un enlace enviado por correo electrónico. El enlace genera un token JWT temporal (válido por 10 minutos) que permite al usuario establecer una nueva contraseña.

## Características
- Tokens JWT seguros con expiración de 10 minutos
- No requiere modificación de la base de datos
- Validación de contraseñas seguras
- Protección contra ataques de fuerza bruta (limitando la validez del token)
- UX amigable con mensajes descriptivos

## Configuración del Correo Electrónico

Para configurar el envío de correos electrónicos, edita el archivo `.env` en la carpeta `backed`:

```
# Configuración de correo electrónico
EMAIL_HOST=smtp.tuproveedor.com
EMAIL_PORT=465
EMAIL_SECURE=true
EMAIL_USER=tu-correo@tudominio.com
EMAIL_PASS=tu-contraseña-segura
FRONTEND_URL=http://localhost:5173
```

### Prueba del envío de correos

Para probar la configuración del correo electrónico, puedes ejecutar el script:

```
cd backed
node scripts/test-email.js
```

Antes de ejecutarlo, asegúrate de modificar el destinatario en el script (variable `testEmail`).

## Flujo de Recuperación de Contraseña

1. El usuario accede a la página de inicio de sesión y selecciona "Olvidaste tu contraseña"
2. El usuario ingresa su correo electrónico registrado
3. El sistema envía un correo con un enlace que contiene un token JWT
4. El usuario hace clic en el enlace y establece una nueva contraseña
5. El sistema verifica el token (validez y expiración) y actualiza la contraseña en la base de datos

## Seguridad

- El token JWT contiene el ID del usuario y está firmado con una clave secreta
- El token tiene una duración limitada (10 minutos) para reducir el riesgo de uso no autorizado
- Se utiliza bcrypt para el hash de la nueva contraseña
- Los mensajes de error no revelan información sensible (como si un correo existe en la base de datos)

## Rutas API

- `POST /api/password-reset/request`: Solicitar recuperación de contraseña
  - Cuerpo: `{ "correo": "usuario@ejemplo.com" }`
  
- `POST /api/password-reset/reset`: Restablecer contraseña con token
  - Cuerpo: `{ "token": "jwt-token", "nuevaContraseña": "contraseña-nueva" }`

## Componentes Frontend

- `RequestPasswordReset.tsx`: Formulario para solicitar recuperación
- `ResetPassword.tsx`: Formulario para establecer nueva contraseña
