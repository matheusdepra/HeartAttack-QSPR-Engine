import React, { useState } from 'react';

export default function LoginView({ apiBase, onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!username.trim() || !password.trim()) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);
    try {
      // Login account
      const res = await fetch(`${apiBase}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), password: password.trim() })
      });
      const data = await res.json();
      if (res.ok) {
        onLoginSuccess(data);
      } else {
        setError(data.detail || 'Invalid credentials or pending approval.');
      }
    } catch (err) {
      setError('Connection error with the backend server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(circle at top right, #1d2b44 0%, #0c101b 100%)',
      fontFamily: '"Outfit", sans-serif',
      position: 'fixed',
      top: 0,
      left: 0,
      zIndex: 9999,
      overflow: 'hidden'
    }}>
      {/* Decorative blurred background lights */}
      <div style={{
        position: 'absolute',
        width: '400px',
        height: '400px',
        background: 'rgba(56, 189, 248, 0.15)',
        borderRadius: '50%',
        filter: 'blur(100px)',
        top: '10%',
        right: '15%'
      }}></div>
      <div style={{
        position: 'absolute',
        width: '350px',
        height: '350px',
        background: 'rgba(236, 72, 153, 0.1)',
        borderRadius: '50%',
        filter: 'blur(100px)',
        bottom: '10%',
        left: '10%'
      }}></div>

      {/* Main Glass Container */}
      <div style={{
        width: '420px',
        padding: '40px',
        borderRadius: '16px',
        background: 'rgba(255, 255, 255, 0.03)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        backdropFilter: 'blur(16px)',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
        color: '#fff',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'stretch'
      }}>
        {/* Title / Logo */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{
            fontSize: '28px',
            fontWeight: 800,
            letterSpacing: '-0.5px',
            margin: 0,
            background: 'linear-gradient(135deg, #38bdf8 0%, #ec4899 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            display: 'inline-block'
          }}>
            CardioQSPR
          </h1>
        </div>

        {/* Form alerts */}
        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            color: '#fca5a5',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '12px',
            marginBottom: '20px',
            lineHeight: '1.4'
          }}>
            {error}
          </div>
        )}

        {/* Inputs */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label style={{
              display: 'block',
              fontSize: '11px',
              color: '#94a3b8',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '6px'
            }}>
              Username
            </label>
            <input
              type="text"
              placeholder="Enter your username..."
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%',
                boxSizing: 'border-box',
                padding: '12px 16px',
                borderRadius: '8px',
                background: 'rgba(0, 0, 0, 0.2)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                color: '#fff',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#38bdf8'}
              onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.08)'}
            />
          </div>

          <div>
            <label style={{
              display: 'block',
              fontSize: '11px',
              color: '#94a3b8',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '6px'
            }}>
              Password
            </label>
            <input
              type="password"
              placeholder="Enter your password..."
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                boxSizing: 'border-box',
                padding: '12px 16px',
                borderRadius: '8px',
                background: 'rgba(0, 0, 0, 0.2)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                color: '#fff',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#38bdf8'}
              onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.08)'}
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '14px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #38bdf8 0%, #0369a1 100%)',
              color: '#fff',
              border: 'none',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              marginTop: '12px',
              transition: 'opacity 0.2s, transform 0.1s',
              boxShadow: '0 4px 12px rgba(56, 189, 248, 0.2)'
            }}
            onMouseOver={(e) => e.target.style.opacity = '0.95'}
            onMouseOut={(e) => e.target.style.opacity = '1'}
            onMouseDown={(e) => e.target.style.transform = 'scale(0.99)'}
            onMouseUp={(e) => e.target.style.transform = 'scale(1)'}
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
