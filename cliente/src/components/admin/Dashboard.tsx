import React from 'react';

const metrics = [
  {
    title: 'Usuarios registrados',
    value: 128,
    icon: 'bi-people',
    color: 'primary',
  },
  {
    title: 'Órdenes completadas',
    value: 56,
    icon: 'bi-bag-check',
    color: 'success',
  },
  {
    title: 'Productos activos',
    value: 42,
    icon: 'bi-box-seam',
    color: 'info',
  },
  {
    title: 'Pendientes de envío',
    value: 7,
    icon: 'bi-truck',
    color: 'warning',
  },
];

const quickLinks = [
  {
    label: 'Gestionar usuarios',
    icon: 'bi-person-lines-fill',
    href: '/admin/users',
    color: 'primary',
  },
  {
    label: 'Ver productos',
    icon: 'bi-box',
    href: '/admin/products',
    color: 'info',
  },
  {
    label: 'Órdenes',
    icon: 'bi-receipt',
    href: '/admin/orders',
    color: 'success',
  },
  {
    label: 'Reportes',
    icon: 'bi-bar-chart',
    href: '/admin/reports',
    color: 'warning',
  },
];

const Dashboard: React.FC = () => {
  return (
    <div className="container py-4 fade-in">
      <h1 className="mb-4 fw-bold text-primary">Panel de Administración</h1>
      <div className="row g-4 mb-4">
        {metrics.map((m, idx) => (
          <div className="col-12 col-md-6 col-lg-3" key={idx}>
            <div className="dashboard-card text-center shadow-hover h-100">
              <div className={`icon mx-auto mb-2 bg-${m.color} bg-opacity-10 text-${m.color}`}
                   style={{ fontSize: 32 }}>
                <i className={`bi ${m.icon}`}></i>
              </div>
              <div className="title text-muted small mb-1">{m.title}</div>
              <div className="value fs-3 fw-semibold">{m.value}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="card p-4 mb-4 shadow-sm">
        <h5 className="mb-3 fw-semibold">Accesos rápidos</h5>
        <div className="row g-3">
          {quickLinks.map((link, idx) => (
            <div className="col-6 col-md-3" key={idx}>
              <a href={link.href} className={`btn btn-${link.color} w-100 d-flex align-items-center gap-2 py-3 shadow-hover`}>
                <i className={`bi ${link.icon} fs-5`}></i>
                <span className="fw-medium">{link.label}</span>
              </a>
            </div>
          ))}
        </div>
      </div>

      <div className="card p-4 shadow-sm">
        <h5 className="mb-3 fw-semibold">Bienvenido Administrador 👋</h5>
        <p className="mb-0 text-muted">
          Desde este panel puedes gestionar usuarios, productos, órdenes y visualizar reportes de tu tienda. Utiliza los accesos rápidos para navegar fácilmente.
        </p>
      </div>
    </div>
  );
};

export default Dashboard; 