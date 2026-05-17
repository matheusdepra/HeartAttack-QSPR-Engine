import React, { useState, useEffect } from 'react';

import { API_BASE } from '../../config';

const HistoryView = ({ onViewAnalysis, user }) => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      const res = await fetch(`${API_BASE}/analyses?user_id=${user?.id}`);
      const data = await res.json();
      setAnalyses(data);
    } catch (err) {
      console.error("Failed to fetch analyses:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ marginBottom: '1rem' }}>
        <h1 style={{ margin: 0 }}>Logs & History</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>Previous QSPR snapshots and their generated reports.</p>
      </div>

      <div className="panel" style={{ flex: 1, padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <div style={{ overflowY: 'auto', flex: 1 }}>
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: '40px' }}>ID</th>
                <th>Title</th>
                <th style={{ width: '150px' }}>Status</th>
                <th style={{ width: '180px' }}>Created At</th>
                <th style={{ width: '100px' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    Loading history...
                  </td>
                </tr>
              ) : analyses.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                    No previous analyses found.
                  </td>
                </tr>
              ) : (
                analyses.map((analysis) => (
                  <tr key={analysis.id}>
                    <td className="mono" style={{ color: 'var(--text-dim)' }}>{analysis.id}</td>
                    <td style={{ fontWeight: '500' }}>{analysis.name}</td>
                    <td>
                      <span className={`badge ${analysis.status === 'completed' ? 'badge-source' : 'badge-calc'}`} style={{ 
                        borderColor: analysis.status === 'completed' ? '#238636' : '#bb8009',
                        color: analysis.status === 'completed' ? '#3fb950' : '#e3b341',
                        background: analysis.status === 'completed' ? 'rgba(35, 134, 54, 0.1)' : 'rgba(187, 128, 9, 0.1)'
                      }}>
                        {analysis.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="mono" style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                      {new Date(analysis.created_at).toLocaleString()}
                    </td>
                    <td>
                      <button 
                        className="btn btn-outline" 
                        style={{ fontSize: '11px', padding: '2px 8px' }}
                        onClick={() => onViewAnalysis(analysis.id)}
                      >
                        Open
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default HistoryView;
