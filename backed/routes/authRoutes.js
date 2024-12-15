const express = require('express');
const router = express.Router();

router.post('/login', async (req, res) => {
  try {
    const { correo, contraseña } = req.body;

    // Aquí la lógica de autenticación
    if (!correo || !contraseña) {
      return res.status(400).json({ message: 'Correo y contraseña requeridos' });
    }

    // Simulación de autenticación (cámbialo según tu lógica)
    const user = await User.findOne({ correo }); // Asegúrate de importar el modelo User
    if (!user) {
      return res.status(401).json({ message: 'Usuario no encontrado' });
    }

    // Verificación de la contraseña (ejemplo)
    const isMatch = await bcrypt.compare(contraseña, user.contraseña);
    if (!isMatch) {
      return res.status(401).json({ message: 'Contraseña incorrecta' });
    }

    const token = 'tu_token_generado_aquí'; // Genera tu token JWT si es necesario
    res.status(200).json({ token });

  } catch (error) {
    console.error('Error en la autenticación:', error);
    res.status(500).json({ message: 'Error en el servidor' });
  }
});

module.exports = router;
