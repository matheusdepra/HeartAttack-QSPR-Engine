import React from 'react';

const LoadingOverlay = ({ message = 'Executing...' }) => {
  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(13, 17, 23, 0.7)',
      backdropFilter: 'blur(2px)',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '1rem'
    }}>
      <div className="panel" style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '16px 24px', border: '1px solid var(--border-light)', boxShadow: '0 4px 12px rgba(0,0,0,0.5)' }}>
        <div style={{
          width: '24px',
          height: '24px',
          border: '2px solid var(--border-light)',
          borderTopColor: 'var(--primary)',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontWeight: '600', color: 'var(--text-primary)', fontSize: '13px' }}>{message}</span>
          <span style={{ color: 'var(--text-dim)', fontSize: '11px', fontFamily: 'monospace' }}>Please wait. Do not close the window.</span>
        </div>
      </div>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingOverlay;
