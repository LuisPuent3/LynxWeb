import React, { useState, useEffect } from 'react';
import api from '../../utils/api';

interface Categoria {
  id_categoria: number;
  nombre: string;
  descripcion: string;
}

const CategoryManager: React.FC = () => {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [formData, setFormData] = useState<Omit<Categoria, 'id_categoria'> & { id_categoria?: number }>({
    nombre: '',
    descripcion: ''
  });
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCategorias();
  }, []);

  const fetchCategorias = async () => {
    try {
      setLoading(true);
      const response = await api.get('/categorias');
      setCategorias(response.data || []);
    } catch (err) {
      console.error('Error al cargar categorías:', err);
      setError('Error al cargar las categorías');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);

      if (isEditing && formData.id_categoria) {
        await api.put(`/categorias/${formData.id_categoria}`, formData);
        alert('Categoría actualizada correctamente');
      } else {
        await api.post('/categorias', formData);
        alert('Categoría creada correctamente');
      }

      // Resetear formulario y recargar datos
      setFormData({ nombre: '', descripcion: '' });
      setIsEditing(false);
      fetchCategorias();
    } catch (err: any) {
      console.error('Error al guardar categoría:', err);
      setError(err.response?.data?.mensaje || 'Error al guardar la categoría');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (categoria: Categoria) => {
    setFormData({
      id_categoria: categoria.id_categoria,
      nombre: categoria.nombre,
      descripcion: categoria.descripcion
    });
    setIsEditing(true);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Estás seguro de eliminar esta categoría? Los productos asociados también se verán afectados.')) {
      return;
    }

    try {
      setLoading(true);
      await api.delete(`/categorias/${id}`);
      alert('Categoría eliminada correctamente');
      fetchCategorias();
    } catch (err: any) {
      console.error('Error al eliminar categoría:', err);
      alert(err.response?.data?.mensaje || 'Error al eliminar la categoría');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="row">
      <div className="col-md-4 mb-4">
        <div className="card shadow-sm">
          <div className="card-header bg-white py-3">
            <h5 className="mb-0">{isEditing ? 'Editar Categoría' : 'Nueva Categoría'}</h5>
          </div>
          <div className="card-body">
            {error && (
              <div className="alert alert-danger">
                <i className="bi bi-exclamation-triangle me-2"></i>
                {error}
              </div>
            )}
            
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="nombre" className="form-label">Nombre</label>
                <input
                  type="text"
                  className="form-control"
                  id="nombre"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="mb-3">
                <label htmlFor="descripcion" className="form-label">Descripción</label>
                <textarea
                  className="form-control"
                  id="descripcion"
                  name="descripcion"
                  rows={3}
                  value={formData.descripcion}
                  onChange={handleInputChange}
                ></textarea>
              </div>
              
              <div className="d-grid gap-2">
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Guardando...
                    </>
                  ) : (
                    isEditing ? 'Actualizar Categoría' : 'Crear Categoría'
                  )}
                </button>
                
                {isEditing && (
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => {
                      setFormData({ nombre: '', descripcion: '' });
                      setIsEditing(false);
                    }}
                  >
                    Cancelar
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <div className="col-md-8">
        <div className="card shadow-sm">
          <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
            <h5 className="mb-0">Categorías</h5>
            <button 
              className="btn btn-sm btn-outline-primary"
              onClick={fetchCategorias}
              disabled={loading}
            >
              <i className="bi bi-arrow-clockwise me-1"></i>
              Actualizar
            </button>
          </div>
          <div className="card-body">
            {loading && categorias.length === 0 ? (
              <div className="text-center py-5">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Cargando...</span>
                </div>
                <p className="mt-2">Cargando categorías...</p>
              </div>
            ) : categorias.length === 0 ? (
              <div className="text-center py-5">
                <i className="bi bi-tags" style={{ fontSize: '3rem', opacity: 0.3 }}></i>
                <p className="mt-3">No hay categorías registradas</p>
                <p className="text-muted">Crea tu primera categoría para organizar tus productos</p>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="table table-hover">
                  <thead className="table-light">
                    <tr>
                      <th>ID</th>
                      <th>Nombre</th>
                      <th>Descripción</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categorias.map((categoria) => (
                      <tr key={categoria.id_categoria}>
                        <td>{categoria.id_categoria}</td>
                        <td>{categoria.nombre}</td>
                        <td>{categoria.descripcion}</td>
                        <td>
                          <div className="btn-group btn-group-sm">
                            <button
                              className="btn btn-outline-primary"
                              onClick={() => handleEdit(categoria)}
                            >
                              <i className="bi bi-pencil"></i>
                            </button>
                            <button
                              className="btn btn-outline-danger"
                              onClick={() => handleDelete(categoria.id_categoria)}
                            >
                              <i className="bi bi-trash"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CategoryManager; 