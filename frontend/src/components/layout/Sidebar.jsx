import React from 'react';
import { FRONTEND_APP_NAME, FRONTEND_APP_SHORT_NAME, FRONTEND_APP_VERSION } from '../../config';

const Sidebar = ({ activeView, setView, user, syncStatus, onLogout, collapsed, onToggleCollapsed }) => {
  // Initials for avatar
  const initials = user?.username ? user.username.substring(0, 2).toUpperCase() : 'US';

  const menuItems = [
    { 
      id: 'library', 
      label: 'Database & Library', 
      icon: (
        <svg style={{ width: '16px', height: '16px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
          <path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"></path>
        </svg>
      )
    },
    { 
      id: 'wizard', 
      label: 'Analysis Workspace', 
      icon: (
        <svg style={{ width: '16px', height: '16px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="18" y1="20" x2="18" y2="10"></line>
          <line x1="12" y1="20" x2="12" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
      )
    },
    { 
      id: 'predictor', 
      label: 'In-Silico Predictor', 
      icon: (
        <svg style={{ width: '16px', height: '16px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
        </svg>
      )
    },
    { 
      id: 'history', 
      label: 'Logs & History', 
      icon: (
        <svg style={{ width: '16px', height: '16px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 8v4l3 3M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.72 2.78L21 8"></path>
          <polyline points="21 3 21 8 16 8"></polyline>
        </svg>
      )
    },
    { 
      id: 'docs', 
      label: 'Documentation', 
      icon: (
        <svg style={{ width: '16px', height: '16px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
        </svg>
      )
    },
  ];

  if (user && user.role === 'admin') {
    menuItems.push({ 
      id: 'users', 
      label: 'User Management', 
      icon: (
        <svg style={{ width: '16px', height: '16px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
          <circle cx="9" cy="7" r="4"></circle>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
        </svg>
      )
    });
  }

  return (
    <aside className="app-sidebar" style={{ width: collapsed ? '78px' : '250px', display: 'flex', flexDirection: 'column', height: '100%', borderRight: '1px solid var(--border-light)', transition: 'width 0.18s ease' }}>
      {/* Brand Header */}
      <div style={{ padding: collapsed ? '18px 12px 14px' : '24px 20px 16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: collapsed ? 'center' : 'space-between', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
            <span style={{ 
              fontWeight: '750', 
              fontSize: '15px', 
              letterSpacing: '0.05em', 
              background: 'linear-gradient(135deg, #38bdf8 0%, #a78bfa 100%)', 
              WebkitBackgroundClip: 'text', 
              WebkitTextFillColor: 'transparent',
              textTransform: 'uppercase'
            }}>
              {collapsed ? FRONTEND_APP_SHORT_NAME : FRONTEND_APP_NAME}
            </span>
            {!collapsed && (
              <span style={{ 
                fontSize: '9px', 
                fontWeight: '600', 
                background: 'rgba(56, 189, 248, 0.1)', 
                color: '#38bdf8', 
                padding: '1px 5px', 
                borderRadius: '4px', 
                border: '1px solid rgba(56, 189, 248, 0.2)' 
              }}>
                {FRONTEND_APP_VERSION}
              </span>
            )}
          </div>
          {!collapsed && (
            <button
              onClick={onToggleCollapsed}
              style={{
                background: 'transparent',
                border: '1px solid var(--border-light)',
                color: 'var(--text-dim)',
                cursor: 'pointer',
                width: '28px',
                height: '28px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              title="Collapse sidebar"
            >
              <svg style={{ width: '14px', height: '14px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
            </button>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: collapsed ? 'center' : 'flex-start', gap: '6px', fontSize: '10px', color: 'var(--text-dim)' }}>
          <span style={{ 
            width: '6px', 
            height: '6px', 
            borderRadius: '50%', 
            background: '#10b981', 
            display: 'inline-block', 
            boxShadow: '0 0 8px rgba(16, 185, 129, 0.5)' 
          }}></span>
          {!collapsed && <span>Online Engine Connected</span>}
        </div>
        {collapsed && (
          <button
            onClick={onToggleCollapsed}
            style={{
              background: 'transparent',
              border: '1px solid var(--border-light)',
              color: 'var(--text-dim)',
              cursor: 'pointer',
              width: '100%',
              height: '30px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title="Expand sidebar"
          >
            <svg style={{ width: '14px', height: '14px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        )}
      </div>

      {!collapsed && (
        <div style={{ padding: '0 16px 8px', fontSize: '10px', fontWeight: '600', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          Explorer
        </div>
      )}
      
      {/* Navigation Buttons */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
        {menuItems.map(item => (
          <button
            key={item.id}
            onClick={() => setView(item.id)}
            title={collapsed ? item.label : undefined}
            style={{
              padding: collapsed ? '10px' : '8px 12px',
              margin: collapsed ? '2px 10px' : '2px 12px',
              borderRadius: '6px',
              border: 'none',
              background: activeView === item.id ? 'rgba(56, 189, 248, 0.08)' : 'transparent',
              color: activeView === item.id ? '#38bdf8' : 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: collapsed ? 'center' : 'flex-start',
              gap: collapsed ? '0' : '10px',
              cursor: 'pointer',
              textAlign: 'left',
              fontFamily: 'inherit',
              fontSize: '13px',
              fontWeight: activeView === item.id ? '500' : '400',
              transition: 'all 0.15s ease',
              position: 'relative'
            }}
          >
            {activeView === item.id && (
              <span style={{ 
                position: 'absolute', 
                left: '0', 
                top: '8px', 
                bottom: '8px', 
                width: '3px', 
                borderRadius: '0 2px 2px 0', 
                background: '#38bdf8' 
              }}></span>
            )}
            <span style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              color: activeView === item.id ? '#38bdf8' : 'var(--text-dim)',
              transition: 'color 0.15s' 
            }}>
              {item.icon}
            </span>
            {!collapsed && item.label}
          </button>
        ))}
      </nav>

      {/* Profile & Status Bottom Dock */}
      <div style={{ 
        marginTop: 'auto', 
        borderTop: '1px solid var(--border-light)', 
        background: 'rgba(10, 13, 20, 0.5)',
        padding: collapsed ? '14px 10px 18px' : '16px 16px 20px', 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '12px' 
      }}>
        {/* Dynamic Sync Banner */}
        {syncStatus?.active && !collapsed && (
          <div style={{ 
            background: 'rgba(56, 189, 248, 0.04)', 
            border: '1px solid rgba(56, 189, 248, 0.15)', 
            borderRadius: '6px', 
            padding: '6px 10px',
            display: 'flex',
            flexDirection: 'column',
            gap: '4px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ 
                width: '6px', 
                height: '6px', 
                borderRadius: '50%', 
                background: '#38bdf8', 
                display: 'inline-block',
                boxShadow: '0 0 6px #38bdf8'
              }}></span>
              <span style={{ fontSize: '10px', color: '#38bdf8', fontWeight: '600', letterSpacing: '0.05em' }}>SYNC IN PROGRESS</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }} title={syncStatus.label}>
              {syncStatus.label} ({syncStatus.current}/{syncStatus.total})
            </div>
          </div>
        )}

        {/* Database Connection Engine Tag */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: collapsed ? 'center' : 'space-between', fontSize: '11px', color: 'var(--text-dim)' }}>
          {!collapsed && <span>Engine: <strong>Local (SQLite)</strong></span>}
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }}></span>
            {!collapsed && <span style={{ fontSize: '9px', fontWeight: '600', color: '#10b981' }}>SQLITE</span>}
          </div>
        </div>

        {/* User Card Row & Logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: collapsed ? 'center' : 'space-between', flexDirection: collapsed ? 'column' : 'row' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
            <div style={{ 
              width: '32px', 
              height: '32px', 
              borderRadius: '50%', 
              background: 'linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)', 
              color: '#fff', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              fontSize: '12px', 
              fontWeight: '600',
              boxShadow: '0 4px 12px rgba(14, 165, 233, 0.2)'
            }}>
              {initials}
            </div>
            {!collapsed && (
              <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <span style={{ fontWeight: '600', color: '#fff', fontSize: '12px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={user?.username}>
                {user?.username}
              </span>
              <span style={{ 
                fontSize: '9px', 
                fontWeight: '600', 
                color: user?.role === 'admin' ? '#f472b6' : 'var(--text-dim)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                {user?.role}
              </span>
              </div>
            )}
          </div>

          {/* Integrated Signout */}
          <button 
            onClick={onLogout}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-dim)',
              cursor: 'pointer',
              padding: '4px',
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.15s ease'
            }}
            title="Sign Out"
            onMouseOver={(e) => { e.currentTarget.style.color = '#ef4444'; e.currentTarget.style.background = 'rgba(239, 68, 68, 0.08)'; }}
            onMouseOut={(e) => { e.currentTarget.style.color = 'var(--text-dim)'; e.currentTarget.style.background = 'transparent'; }}
          >
            <svg style={{ width: '16px', height: '16px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
