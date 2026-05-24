import React, { useState } from 'react';

import { API_BASE } from '../../config';

const PredictorView = () => {
  const [smiles, setSmiles] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const indexNames = {
    "ABC": "Atom-Bond Connectivity Index ABC(G)",
    "GA": "Geometric-Arithmetic Index GA(G)",
    "RI": "Randic Index R(G)",
    "RR": "Reciprocal Randic Index RR(G)",
    "H": "Harmonic Index H(G)",
    "SCI": "Sum Connectivity Index SC(G)",
    "M1": "First Zagreb Index M1(G)",
    "M2": "Second Zagreb Index M2(G)",
    "HM": "Hyper Zagreb Index HM(G)",
    "RM2": "Redefined Second Zagreb Index RM2(G)",
    "F": "Forgotten Index F(G)",
    "HF": "Hyper Forgotten Index HF(G)"
  };

  const handlePredict = async () => {
    if (!smiles.trim()) return;
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const res = await fetch(`${API_BASE}/predict?smiles=${encodeURIComponent(smiles)}`, {
        method: 'POST'
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Prediction failed');
      }
      const data = await res.json();
      setResults(data.indices);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h2 style={{ fontSize: '16px', marginBottom: '8px' }}>In-Silico Predictor</h2>
      <p style={{ color: 'var(--text-dim)', marginBottom: '24px', fontSize: '13px' }}>
        Enter a valid SMILES string to calculate the 10 degree-based topological indices instantly.
      </p>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
        <input 
          className="input-dense mono" 
          placeholder="e.g. CC(=O)OC1=CC=CC=C1C(=O)O" 
          value={smiles}
          onChange={(e) => setSmiles(e.target.value)}
          style={{ flex: 1, maxWidth: '600px' }}
          onKeyDown={(e) => e.key === 'Enter' && handlePredict()}
        />
        <button 
          className="btn btn-primary" 
          onClick={handlePredict} 
          disabled={loading || !smiles.trim()}
        >
          {loading ? 'Calculating...' : 'Calculate Indices'}
        </button>
      </div>

      {error && (
        <div style={{ color: '#ff6b6b', padding: '12px', border: '1px solid #ff6b6b33', borderRadius: '4px', background: '#ff6b6b11', marginBottom: '24px' }}>
          {error}
        </div>
      )}

      {results && (
        <div style={{ flex: 1, overflow: 'auto' }}>
          <h3 style={{ fontSize: '14px', marginBottom: '12px', paddingBottom: '8px', borderBottom: '1px solid var(--border-light)' }}>
            Calculated Topological Indices
          </h3>
          <div className="panel table-panel" style={{ maxWidth: '600px' }}>
            <div className="table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th style={{ width: '80px' }}>Symbol</th>
                    <th>Index Name</th>
                    <th className="text-right">Value</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(results).map(([key, value]) => (
                    <tr key={key}>
                      <td className="mono" style={{ fontWeight: 600 }}>{key}</td>
                      <td>{indexNames[key] || key}</td>
                      <td className="mono text-right">{value.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictorView;
