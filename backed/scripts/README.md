# Actualización de Contraseñas en la Base de Datos

Este script soluciona el problema con las contraseñas almacenadas como VARBINARY usando AES_ENCRYPT, cambiándolas a VARCHAR con hashes de bcrypt.

## Problema

En la configuración original, las contraseñas se almacenaban como VARBINARY con AES_ENCRYPT, pero el código del backend estaba intentando usar bcrypt para comparar las contraseñas durante el inicio de sesión. Esta incompatibilidad causaba errores de autenticación.

## Solución

El script `update_users_table.sql` realiza los siguientes cambios:

1. Modifica la estructura de la tabla Usuarios para cambiar el tipo de columna de `contraseña` de VARBINARY a VARCHAR
2. Actualiza las contraseñas existentes con valores bcrypt conocidos
3. Agrega un usuario de prueba con credenciales conocidas

## Cómo ejecutar el script

1. Respalda tu base de datos actual:
   ```bash
   mysqldump -u [usuario] -p lynxshop > lynxshop_backup.sql
   ```

2. Ejecuta el script SQL:
   ```bash
   mysql -u [usuario] -p lynxshop < update_users_table.sql
   ```

3. Una vez ejecutado, podrás iniciar sesión con:
   - Correo: test@example.com
   - Contraseña: test123

## Notas importantes

- Después de aplicar este cambio, las contraseñas antiguas no funcionarán y los usuarios deberán restablecer sus contraseñas.
- El controlador de autenticación ha sido actualizado para manejar correctamente el nuevo formato de contraseñas. 