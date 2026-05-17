import React from 'react';

const Navbar = ({ syncStatus, user, onLogout }) => {
  return (
    <header className="app-navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '220px' }}>
        <div style={{ fontWeight: '600', color: '#fff', fontSize: '14px', letterSpacing: '0.02em' }}>
          CardioQSPR <span style={{ color: 'var(--text-dim)', fontWeight: '400' }}>Platform</span>
        </div>
      </div>
      
      <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
        {syncStatus.active && (
          <div style={{ 
            display: 'flex', alignItems: 'center', gap: '8px', 
            background: 'var(--bg-hover)', padding: '4px 12px', borderRadius: '4px', border: '1px solid var(--border-light)' 
          }}>
            <span style={{ fontSize: '11px', color: 'var(--primary)', fontWeight: '500' }}>PROCESSING</span>
            <span style={{ fontSize: '12px', fontFamily: 'monospace' }}>{syncStatus.label} ({syncStatus.current}/{syncStatus.total})</span>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '12px' }}>
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderRight: '1px solid var(--border-color)', paddingRight: '16px' }}>
            <span style={{ color: 'var(--text-dim)' }}>User: <strong style={{ color: '#fff' }}>{user.username}</strong></span>
            <span style={{
              fontSize: '10px',
              fontWeight: 600,
              padding: '1px 6px',
              borderRadius: '4px',
              background: user.role === 'admin' ? 'rgba(236, 72, 153, 0.15)' : 'rgba(255, 255, 255, 0.05)',
              color: user.role === 'admin' ? '#f472b6' : 'var(--text-dim)',
              border: user.role === 'admin' ? '1px solid rgba(236, 72, 153, 0.25)' : '1px solid rgba(255, 255, 255, 0.08)'
            }}>
              {user.role.toUpperCase()}
            </span>
          </div>
        )}
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ color: 'var(--text-dim)' }}>Engine: <strong>Local (SQLite)</strong></span>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#238636' }}></span>
        </div>

        {user && (
          <button 
            onClick={onLogout}
            style={{
              background: 'transparent',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#fca5a5',
              padding: '4px 10px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '11px',
              fontWeight: 500,
              transition: 'all 0.2s',
              marginLeft: '8px'
            }}
            onMouseOver={(e) => { e.target.style.background = 'rgba(239, 68, 68, 0.1)'; }}
            onMouseOut={(e) => { e.target.style.background = 'transparent'; }}
          >
            Logout
          </button>
        )}
      </div>
    </header>
  );
};

export default Navbar;
