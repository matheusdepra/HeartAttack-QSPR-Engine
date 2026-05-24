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

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to permanently delete this analysis? This action cannot be undone.")) {
      return;
    }
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/analyses/${id}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        await fetchAnalyses();
      } else {
        alert("Failed to delete analysis");
      }
    } catch (err) {
      console.error("Failed to delete analysis:", err);
      alert("Error deleting analysis");
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

      <div className="panel table-panel" style={{ flex: 1 }}>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th className="col-center" style={{ width: '48px' }}>ID</th>
                <th>Analysis Title</th>
                <th className="col-center" style={{ width: '140px' }}>Status</th>
                <th className="col-right" style={{ width: '190px' }}>Created At</th>
                <th className="col-center" style={{ width: '140px' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-dim)' }}>
                    Loading history...
                  </td>
                </tr>
              ) : analyses.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-dim)' }}>
                    No previous analyses found.
                  </td>
                </tr>
              ) : (
                analyses.map((analysis) => (
                  <tr key={analysis.id}>
                    <td className="mono col-center" style={{ color: 'var(--text-dim)', fontSize: '12px' }}>{analysis.id}</td>
                    <td style={{ fontWeight: '500', color: '#f8fafc' }}>{analysis.name}</td>
                    <td className="col-center">
                      <span style={{
                        display: 'inline-block',
                        fontSize: '10px',
                        fontWeight: '600',
                        letterSpacing: '0.06em',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        border: `1px solid ${analysis.status === 'completed' ? 'rgba(16,185,129,0.35)' : 'rgba(245,158,11,0.35)'}`,
                        color: analysis.status === 'completed' ? '#10b981' : '#f59e0b',
                        background: analysis.status === 'completed' ? 'rgba(16,185,129,0.08)' : 'rgba(245,158,11,0.08)',
                      }}>
                        {analysis.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="mono col-right" style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                      {new Date(analysis.created_at).toLocaleString()}
                    </td>
                    <td className="col-center">
                      <div style={{ display: 'inline-flex', gap: '6px' }}>
                        <button
                          className="btn btn-outline"
                          style={{ fontSize: '11px', padding: '3px 10px' }}
                          onClick={() => onViewAnalysis(analysis.id)}
                        >
                          Open
                        </button>
                        <button
                          className="btn btn-outline"
                          style={{
                            fontSize: '11px',
                            padding: '3px 10px',
                            borderColor: 'rgba(248, 81, 73, 0.4)',
                            color: '#f85149',
                            background: 'transparent'
                          }}
                          onClick={() => handleDelete(analysis.id)}
                        >
                          Delete
                        </button>
                      </div>
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
