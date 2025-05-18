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
  const [uploaded, setUploaded] = useState(!!initialFilename);
  const [imageExists, setImageExists] = useState(false);

  // Actualizar el nombre si cambia initialFilename
  useEffect(() => {
    setFilename(initialFilename);
    // Mostrar preview de imagen existente si hay un nombre inicial
    if (initialFilename) {
      const imageUrl = `http://localhost:5000/uploads/${initialFilename}?v=${Date.now()}`;
      fetch(imageUrl)
        .then(response => {
          if (!response.ok) throw new Error('La imagen no existe');
          setImageExists(true);
          return response.blob();
        })
        .then(blob => {
          const reader = new FileReader();
          reader.onloadend = () => {
            setPreview(reader.result as string);
          };
          reader.readAsDataURL(blob);
          setUploaded(true);
        })
        .catch(error => {
          console.error('Error al cargar la imagen existente:', error);
          setImageExists(false);
          setUploaded(false);
        });
    }
  }, [initialFilename]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setUploaded(false);
    setError(null);
    
    // Crear previsualización
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
    
    // Si no hay nombre de archivo, usar el nombre del archivo subido
    if (!filename.trim()) {
      setFilename(file.name);
    }
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

    // Verificar si el nombre tiene una extensión válida
    const validExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp'];
    let currentFilename = filename;
    let hasValidExtension = false;
    
    // Comprobar si el nombre ya tiene una extensión válida
    for (const ext of validExtensions) {
      if (currentFilename.toLowerCase().endsWith(ext)) {
        hasValidExtension = true;
        break;
      }
    }
    
    // Si no tiene extensión, añadir la del archivo seleccionado
    if (!hasValidExtension && selectedFile) {
      const fileExt = selectedFile.name.substring(selectedFile.name.lastIndexOf('.'));
      currentFilename = `${currentFilename}${fileExt}`;
      setFilename(currentFilename);
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('imagen', selectedFile);
      formData.append('customFilename', currentFilename);

      // Log para depuración
      console.log('Subiendo imagen con nombre personalizado:', currentFilename);
      
      // Datos completos del FormData (para depuración)
      for (const [key, value] of formData.entries()) {
        console.log(`FormData: ${key} = ${value instanceof File ? value.name : value}`);
      }

      // Usar la ruta correcta sin duplicar '/api'
      const response = await api.post('/uploads/custom', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Log para depuración
      console.log('Respuesta del servidor:', response.data);

      // Obtener el nombre del archivo que realmente se guardó
      const savedFilename = response.data.filename;
      
      // Si el nombre guardado no coincide con el esperado, mostrar advertencia
      if (savedFilename !== currentFilename) {
        console.warn(`Advertencia: El nombre del archivo guardado (${savedFilename}) no coincide con el solicitado (${currentFilename})`);
      }

      setLoading(false);
      setUploaded(true);
      setImageExists(true);
      
      // Actualizar el nombre del archivo con el que se guardó realmente
      setFilename(savedFilename);
      
      // Notificar al componente padre con el nombre guardado
      onImageSelected(savedFilename);
      
      console.log('Imagen subida correctamente como:', savedFilename);
    } catch (err: any) {
      console.error('Error al subir imagen:', err);
      setError(err.response?.data?.error || 'Error al subir la imagen');
      setLoading(false);
      setUploaded(false);
      setImageExists(false);
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
            // No actualizar el componente padre hasta que se suba la imagen
            setUploaded(false);
            setImageExists(false);
          }}
          required
        />
        <div className="form-text small">
          <i className="bi bi-info-circle me-1"></i>
          El nombre que escribas será exactamente el nombre del archivo guardado
        </div>
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
        
        {uploaded && imageExists && (
          <div className="alert alert-success py-1 small" role="alert">
            Imagen subida correctamente como: {filename}
          </div>
        )}
        
        {!uploaded && (
          <div className="form-text small text-danger">
            <strong>Importante:</strong> Debes subir una imagen antes de guardar el producto
          </div>
        )}
        
        {uploaded && (
          <div className="form-text small text-success">
            <i className="bi bi-check-circle me-1"></i>
            Imagen lista para guardar con el producto
          </div>
        )}
      </div>
    </div>
  );
};

export default SimpleImageUploader; 