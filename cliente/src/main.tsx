import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('app') as HTMLElement); // Asegúrate de que 'app' es el ID correcto
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
