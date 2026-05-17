import React, { useState, useEffect } from 'react';

export default function UserManagementView({ apiBase }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Create User form state
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('user');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/users`);
      if (res.ok) {
        const data = await res.json();
        setUsers(data);
      }
    } catch (err) {
      console.error("Failed to fetch users:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!username.trim() || !password.trim()) {
      setError('Please fill in all fields.');
      return;
    }

    try {
      const res = await fetch(`${apiBase}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: username.trim(),
          password: password.trim(),
          role
        })
      });
      const data = await res.json();
      if (res.ok) {
        setSuccess(`User "${username}" successfully created!`);
        setUsername('');
        setPassword('');
        fetchUsers();
      } else {
        setError(data.detail || 'Error creating user.');
      }
    } catch (err) {
      setError('Error connecting to backend server.');
    }
  };

  const handleApprove = async (id) => {
    try {
      const res = await fetch(`${apiBase}/users/${id}/approve`, { method: 'POST' });
      if (res.ok) {
        fetchUsers();
      }
    } catch (err) {
      alert("Error approving user.");
    }
  };

  const handleToggleRole = async (id) => {
    try {
      const res = await fetch(`${apiBase}/users/${id}/toggle-role`, { method: 'POST' });
      if (res.ok) {
        fetchUsers();
      } else {
        const err = await res.json();
        alert(err.detail);
      }
    } catch (err) {
      alert("Error toggling user role.");
    }
  };

  const handleDelete = async (id, name) => {
    if (!confirm(`Are you sure you want to delete the account of "${name}"?`)) return;
    try {
      const res = await fetch(`${apiBase}/users/${id}`, { method: 'DELETE' });
      if (res.ok) {
        fetchUsers();
      } else {
        const err = await res.json();
        alert(err.detail);
      }
    } catch (err) {
      alert("Error deleting user.");
    }
  };

  return (
    <div className="view-container" style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
      
      {/* Users List Table */}
      <div className="card" style={{ flex: '2', minWidth: '450px', padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0 }}>User Management</h2>
            <p style={{ fontSize: '12px', color: 'var(--text-dim)', margin: '4px 0 0 0' }}>
              Approve access requests and manage administrative roles.
            </p>
          </div>
          <button className="btn btn-outline" style={{ fontSize: '12px', padding: '6px 12px' }} onClick={fetchUsers}>
            Reload
          </button>
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '14px' }}>
            Loading registered users...
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th style={{ width: '60px' }}>ID</th>
                  <th>Username</th>
                  <th style={{ width: '120px' }}>Role</th>
                  <th style={{ width: '120px' }}>Status</th>
                  <th style={{ width: '220px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td className="mono">{u.id}</td>
                    <td>
                      <span style={{ fontWeight: 600, color: '#fff' }}>{u.username}</span>
                    </td>
                    <td>
                      <span style={{
                        fontSize: '11px',
                        fontWeight: 600,
                        padding: '2px 8px',
                        borderRadius: '4px',
                        background: u.role === 'admin' ? 'rgba(236, 72, 153, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                        color: u.role === 'admin' ? '#f472b6' : 'var(--text-dim)',
                        border: u.role === 'admin' ? '1px solid rgba(236, 72, 153, 0.25)' : '1px solid rgba(255, 255, 255, 0.08)'
                      }}>
                        {u.role.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <span style={{
                        fontSize: '11px',
                        fontWeight: 600,
                        padding: '2px 8px',
                        borderRadius: '4px',
                        background: u.is_approved ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                        color: u.is_approved ? '#34d399' : '#fbbf24',
                        border: u.is_approved ? '1px solid rgba(16, 185, 129, 0.25)' : '1px solid rgba(245, 158, 11, 0.25)'
                      }}>
                        {u.is_approved ? 'APPROVED' : 'PENDING'}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                        {!u.is_approved && (
                          <button
                            className="btn btn-primary"
                            style={{ fontSize: '11px', padding: '2px 8px', background: '#059669', color: '#fff' }}
                            onClick={() => handleApprove(u.id)}
                          >
                            Approve
                          </button>
                        )}
                        {u.username !== 'admin' && (
                          <>
                            <button
                              className="btn btn-outline"
                              style={{ fontSize: '11px', padding: '2px 8px' }}
                              onClick={() => handleToggleRole(u.id)}
                            >
                              Toggle Role
                            </button>
                            <button
                              className="btn btn-outline"
                              style={{ fontSize: '11px', padding: '2px 8px', color: '#fca5a5', borderColor: 'rgba(239, 68, 68, 0.2)' }}
                              onClick={() => handleDelete(u.id, u.username)}
                            >
                              Delete
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add User Panel */}
      <div className="card" style={{ flex: '1', minWidth: '300px', padding: '24px', height: 'fit-content' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, margin: '0 0 4px 0' }}>+ Create Approved User</h3>
        <p style={{ fontSize: '12px', color: 'var(--text-dim)', marginBottom: '20px' }}>
          Directly create a new active account with granted access.
        </p>

        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            color: '#fca5a5',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '12px',
            marginBottom: '16px'
          }}>
            {error}
          </div>
        )}
        {success && (
          <div style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            color: '#a7f3d0',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '12px',
            marginBottom: '16px'
          }}>
            {success}
          </div>
        )}

        <form onSubmit={handleCreateUser} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '6px', fontWeight: 600 }}>
              Username
            </label>
            <input
              className="input-dense"
              type="text"
              placeholder="e.g., smith"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{ width: '100%', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '6px', fontWeight: 600 }}>
              Initial Password
            </label>
            <input
              className="input-dense"
              type="password"
              placeholder="Enter password..."
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: '100%', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '6px', fontWeight: 600 }}>
              Role / Access Level
            </label>
            <select
              className="input-dense"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              style={{ width: '100%', boxSizing: 'border-box', background: 'var(--bg-input)', color: '#fff', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '6px 10px', outline: 'none' }}
            >
              <option value="user">Scientific User (Viewer/Predictor)</option>
              <option value="admin">Administrator (Full + Moderation)</option>
            </select>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{
              padding: '10px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              marginTop: '8px',
              background: 'linear-gradient(135deg, #38bdf8 0%, #0284c7 100%)',
              color: '#fff',
              border: 'none',
              borderRadius: '6px'
            }}
          >
            Create User
          </button>
        </form>
      </div>

    </div>
  );
}
