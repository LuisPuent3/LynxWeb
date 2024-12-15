const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const productRoutes = require('./routes/productRoutes');
const orderRoutes = require('./routes/orderRoutes');

dotenv.config();
const app = express();

app.use(cors({
  origin: 'http://localhost:5173', // URL de tu frontend
  credentials: true
}));

app.use(express.json());

// Rutas
app.use('/api/productos', productRoutes);
app.use('/api/pedidos', orderRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en el puerto ${PORT}`);
});