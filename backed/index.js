const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const productRoutes = require('./routes/productRoutes');
const pedidoRoutes = require('./routes/pedidoRoutes');

dotenv.config();
const app = express();

app.use(cors());
app.use(express.json());

// Rutas
app.use('/api/productos', productRoutes);
app.use('/api/pedidos', pedidoRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en el puerto ${PORT}`);
});