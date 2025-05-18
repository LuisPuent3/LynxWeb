import React, { useState, useEffect } from 'react';
import api from '../../utils/api';

interface SimpleImageUploaderProps {
  onImageSelected: (filename: string) => void;
  initialFilename?: string;
}

const SimpleImageUploader: React.FC<SimpleImageUploaderProps> = ({
  onImageSelected,
  initialFilename = ''
}) => {
  const [filename, setFilename] = useState(initialFilename);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploaded, setUploaded] = useState(false);

  // Actualizar el nombre si cambia initialFilename
  useEffect(() => {
    setFilename(initialFilename);
  }, [initialFilename]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setUploaded(false);

    // Conservar el nombre original del archivo
    setFilename(file.name);
    onImageSelected(file.name);

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

    if (!filename.trim()) {
      setError('El nombre de archivo no puede estar vacío');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('imagen', selectedFile);
      formData.append('customFilename', filename);

      await api.post('/api/uploads/custom', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setLoading(false);
      setUploaded(true);
      alert('Imagen subida correctamente');
    } catch (err: any) {
      console.error('Error al subir imagen:', err);
      setError(err.response?.data?.error || 'Error al subir la imagen');
      setLoading(false);
    }
  };

  return (
    <div className="row">
      <div className="col-12 mb-2">
        <input
          type="text"
          className="form-control"
          placeholder="Nombre de la imagen"
          value={filename}
          onChange={(e) => {
            setFilename(e.target.value);
            onImageSelected(e.target.value);
            setUploaded(false);
          }}
          required
        />
      </div>
      
      <div className="col-12">
        {preview && (
          <div className="mb-2 border rounded p-1" style={{ maxWidth: '120px' }}>
            <img 
              src={preview} 
              alt="Vista previa" 
              className="img-fluid" 
            />
          </div>
        )}
        
        <div className="input-group mb-2">
          <input 
            type="file" 
            className="form-control" 
            accept="image/*"
            onChange={handleFileChange}
          />
          <button
            className="btn btn-primary"
            type="button"
            onClick={handleUpload}
            disabled={!selectedFile || loading || uploaded}
          >
            {loading ? (
              <span className="spinner-border spinner-border-sm" role="status"></span>
            ) : uploaded ? (
              <i className="bi bi-check"></i>
            ) : (
              <i className="bi bi-upload"></i>
            )}
          </button>
        </div>
        
        {error && (
          <div className="alert alert-danger py-1 small" role="alert">
            {error}
          </div>
        )}
        
        {uploaded && (
          <div className="alert alert-success py-1 small" role="alert">
            Imagen subida correctamente
          </div>
        )}
        
        <div className="form-text small">
          Primero sube la imagen, luego guarda el producto
        </div>
      </div>
    </div>
  );
};

export default SimpleImageUploader; 