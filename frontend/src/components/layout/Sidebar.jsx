import React from 'react';

const Sidebar = ({ activeView, setView, user }) => {
  const menuItems = [
    { id: 'library', label: 'Database & Library', icon: '⛁' },
    { id: 'wizard', label: 'Analysis Workspace', icon: '📊' },
    { id: 'predictor', label: 'In-Silico Predictor', icon: '⚡' },
    { id: 'history', label: 'Logs & History', icon: '📄' },
    { id: 'docs', label: 'Documentation', icon: '📖' },
  ];

  if (user && user.role === 'admin') {
    menuItems.push({ id: 'users', label: 'User Management', icon: '👥' });
  }

  return (
    <aside className="app-sidebar">
      <div style={{ padding: '12px 16px', fontSize: '11px', fontWeight: '600', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        Explorer
      </div>
      
      <nav style={{ display: 'flex', flexDirection: 'column' }}>
        {menuItems.map(item => (
          <button
            key={item.id}
            onClick={() => setView(item.id)}
            style={{
              padding: '6px 16px',
              border: 'none',
              background: activeView === item.id ? 'var(--bg-hover)' : 'transparent',
              color: activeView === item.id ? 'var(--text-primary)' : 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              cursor: 'pointer',
              textAlign: 'left',
              fontFamily: 'inherit',
              fontSize: '13px',
              borderLeft: activeView === item.id ? '2px solid var(--primary)' : '2px solid transparent'
            }}
          >
            <span style={{ fontSize: '14px', width: '16px', textAlign: 'center' }}>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
