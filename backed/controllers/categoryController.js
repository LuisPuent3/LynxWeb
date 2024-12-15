const db = require("../db");

// Crear nueva categoría
exports.createCategory = async (req, res) => {
  const { nombre, descripcion } = req.body;

  try {
    const existingCategory = await db.query(
      "SELECT * FROM Categorias WHERE nombre = ?",
      [nombre]
    );
    if (existingCategory.length) {
      return res.status(400).json({ message: "La categoría ya existe." });
    }

    await db.query(
      "INSERT INTO Categorias (nombre, descripcion) VALUES (?, ?)",
      [nombre, descripcion]
    );

    res.status(201).json({ message: "Categoría creada con éxito." });
  } catch (error) {
    res.status(500).json({ message: "Error creando categoría.", error });
  }
};

// Obtener todas las categorías
exports.getAllCategories = async (req, res) => {
  try {
    const categories = await db.query("SELECT * FROM Categorias");
    res.status(200).json(categories);
  } catch (error) {
    res.status(500).json({ message: "Error obteniendo categorías.", error });
  }
};
