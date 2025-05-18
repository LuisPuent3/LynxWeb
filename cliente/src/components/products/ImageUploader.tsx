import React, { useState, useEffect } from 'react';
import api from '../../utils/api';

interface ImageUploaderProps {
  productId: number;
  currentImage: string | null;
  onImageUpdated: (filename: string) => void;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({
  productId,
  currentImage,
  onImageUpdated
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imgError, setImgError] = useState(false);
  
  // Limpiar previsualizaciones cuando cambia el producto
  useEffect(() => {
    setPreview(null);
    setImgError(false);
  }, [productId, currentImage]);

  // Construir URL una sola vez con parámetro para evitar caché
  const imageUrl = currentImage 
    ? `http://localhost:5000/uploads/${currentImage}?v=${Date.now()}` 
    : '';

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validar tipo de archivo
    if (!file.type.startsWith('image/')) {
      setError('Solo se permiten archivos de imagen');
      return;
    }

    // Validar tamaño (5MB máximo)
    if (file.size > 5 * 1024 * 1024) {
      setError('La imagen no puede superar los 5MB');
      return;
    }

    setError(null);
    setSelectedFile(file);
    setImgError(false);

    // Crear previsualización
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Selecciona una imagen primero');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('imagen', selectedFile);

      // Si es un producto nuevo, usamos una ruta temporal
      // De lo contrario, actualizamos la imagen del producto existente
      const uploadEndpoint = productId 
        ? `/productos/${productId}/imagen` 
        : '/uploads/temp';

      const response = await api.post(uploadEndpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setLoading(false);
      setSelectedFile(null);
      onImageUpdated(response.data.filename);
      alert('Imagen actualizada con éxito');
    } catch (err: any) {
      console.error('Error al subir imagen:', err);
      setError(err.response?.data?.mensaje || 'Error al subir la imagen');
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-3 d-flex justify-content-center">
        <div 
          className="border rounded" 
          style={{ width: '150px', height: '150px', overflow: 'hidden' }}
        >
          {preview ? (
            <img 
              src={preview} 
              alt="Vista previa" 
              className="img-fluid" 
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          ) : currentImage && !imgError ? (
            <img 
              src={imageUrl} 
              alt="Imagen actual" 
              className="img-fluid" 
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              loading="lazy"
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="d-flex align-items-center justify-content-center h-100 bg-light">
              <i className="bi bi-image text-secondary" style={{ fontSize: '2rem' }}></i>
            </div>
          )}
        </div>
      </div>
      
      <div className="mb-3">
        <input 
          type="file" 
          className="form-control form-control-sm" 
          id={`productImage-${productId || 'new'}`}
          accept="image/*"
          onChange={handleFileChange}
        />
        <div className="form-text small">Formatos: JPG, PNG, GIF. Máx: 5MB</div>
      </div>
      
      {error && (
        <div className="alert alert-danger py-2 small" role="alert">
          {error}
        </div>
      )}
      
      <button 
        className="btn btn-primary btn-sm" 
        onClick={handleUpload}
        disabled={!selectedFile || loading}
      >
        {loading ? (
          <>
            <span className="spinner-border spinner-border-sm me-1" role="status"></span>
            Subiendo...
          </>
        ) : 'Subir imagen'}
      </button>
    </div>
  );
};

export default ImageUploader; 