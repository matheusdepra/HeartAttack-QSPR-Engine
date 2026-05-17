import React from 'react';

const GlassCard = ({ children, className = '', title, subtitle }) => {
  return (
    <div className={`glass-card ${className}`}>
      {(title || subtitle) && (
        <div style={{ marginBottom: '1.25rem', borderBottom: '1px solid var(--border-light)', paddingBottom: '1rem' }}>
          {title && <h3 style={{ fontSize: '1.1rem', marginBottom: '0.25rem' }}>{title}</h3>}
          {subtitle && <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{subtitle}</p>}
        </div>
      )}
      {children}
    </div>
  );
};

export default GlassCard;
