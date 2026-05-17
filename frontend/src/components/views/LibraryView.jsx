import React, { useState } from 'react';

const LibraryView = ({ drugs, syncStatus, loadDefaults, handleAddDrug, isStarting, onUpdateDrug, onResync }) => {
  const [editingDrug, setEditingDrug] = useState(null);

  const handleSave = async () => {
    if (!editingDrug) return;
    await onUpdateDrug(editingDrug.id, editingDrug);
    setEditingDrug(null);
  };

  const handleChange = (field, value) => {
    setEditingDrug(prev => ({ ...prev, [field]: value === '' ? null : parseFloat(value) || value }));
  };

  return (
    <div style={{ display: 'flex', gap: '1rem', height: '100%', overflow: 'hidden' }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Header Actions */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h1 style={{ margin: 0 }}>Molecular Database</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>{drugs.length} entities loaded. Synchronize from PubChem to add more.</p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn btn-outline" onClick={loadDefaults} disabled={syncStatus.active}>
              Load Baseline Dataset
            </button>
            <button className="btn btn-primary" onClick={handleAddDrug} disabled={syncStatus.active}>
              + Add Compound
            </button>
          </div>
        </div>

        {isStarting && (
          <div style={{ color: 'var(--text-secondary)', padding: '1rem', border: '1px solid var(--border-light)', borderRadius: '6px' }}>
            Querying local database...
          </div>
        )}

        {/* Main Data Table */}
        {!isStarting && (
          <div className="panel" style={{ flex: 1, padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div style={{ overflowY: 'auto', flex: 1 }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th style={{ width: '40px' }}>ID</th>
                    <th style={{ width: '150px' }}>Compound</th>
                    <th>SMILES String</th>
                    <th style={{ width: '80px' }}>BP</th>
                    <th style={{ width: '80px' }}>VP</th>
                    <th style={{ width: '80px' }}>MR</th>
                    <th style={{ width: '80px' }}>MW</th>
                    <th style={{ width: '80px' }}>Comp</th>
                    <th style={{ width: '80px' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {drugs.map((drug) => (
                    <tr key={drug.id} style={{ background: editingDrug?.id === drug.id ? 'var(--bg-hover)' : 'transparent' }}>
                      <td className="mono" style={{ color: 'var(--text-dim)' }}>{drug.id}</td>
                      <td style={{ fontWeight: '500' }}>{drug.name}</td>
                      <td className="mono" style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                        <div style={{ maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={drug.smiles}>
                          {drug.smiles || 'N/A'}
                        </div>
                      </td>
                      <td className="mono">{drug.bp !== null ? drug.bp.toFixed(1) : '-'}</td>
                      <td className="mono">{drug.vp !== null ? drug.vp.toExponential(1) : '-'}</td>
                      <td className="mono">{drug.mr !== null ? drug.mr.toFixed(2) : '-'}</td>
                      <td className="mono">{drug.mw !== null ? drug.mw.toFixed(1) : '-'}</td>
                      <td className="mono">{drug.complexity !== null ? drug.complexity.toFixed(0) : '-'}</td>
                      <td>
                        <button className="btn btn-outline" style={{ fontSize: '11px', padding: '2px 8px' }} onClick={() => setEditingDrug({ ...drug })}>
                          Edit
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Side Editor Panel */}
      {editingDrug && (
        <div className="panel" style={{ width: '320px', display: 'flex', flexDirection: 'column', gap: '1rem', borderLeft: '1px solid var(--border-light)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ fontSize: '14px', margin: 0 }}>Edit Compound</h2>
            <button className="btn btn-outline" style={{ padding: '2px 6px' }} onClick={() => setEditingDrug(null)}>✕</button>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', overflowY: 'auto', flex: 1, paddingRight: '4px' }}>
            <div>
              <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>Molecule Name</label>
              <input className="input-dense" value={editingDrug.name} onChange={(e) => handleChange('name', e.target.value)} />
            </div>
            <div>
              <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>SMILES String</label>
              <textarea className="input-dense mono" style={{ height: '60px', resize: 'none' }} value={editingDrug.smiles || ''} onChange={(e) => handleChange('smiles', e.target.value)} />
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>BP (°C)</label>
                <input className="input-dense mono" type="number" value={editingDrug.bp || ''} onChange={(e) => handleChange('bp', e.target.value)} />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>VP (mmHg)</label>
                <input className="input-dense mono" type="number" value={editingDrug.vp || ''} onChange={(e) => handleChange('vp', e.target.value)} />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>EV (kJ/mol)</label>
                <input className="input-dense mono" type="number" value={editingDrug.ev || ''} onChange={(e) => handleChange('ev', e.target.value)} />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>FP (°C)</label>
                <input className="input-dense mono" type="number" value={editingDrug.fp || ''} onChange={(e) => handleChange('fp', e.target.value)} />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>MR</label>
                <input className="input-dense mono" type="number" value={editingDrug.mr || ''} onChange={(e) => handleChange('mr', e.target.value)} />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>ST (dyn/cm)</label>
                <input className="input-dense mono" type="number" value={editingDrug.st || ''} onChange={(e) => handleChange('st', e.target.value)} />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>MV (cm³/mol)</label>
                <input className="input-dense mono" type="number" value={editingDrug.mv || ''} onChange={(e) => handleChange('mv', e.target.value)} />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>MW (g/mol)</label>
                <input className="input-dense mono" type="number" value={editingDrug.mw || ''} onChange={(e) => handleChange('mw', e.target.value)} />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>Complexity</label>
                <input className="input-dense mono" type="number" value={editingDrug.complexity || ''} onChange={(e) => handleChange('complexity', e.target.value)} />
              </div>
            </div>
          </div>

          <div style={{ borderTop: '1px solid var(--border-light)', paddingTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn btn-outline" style={{ flex: 1 }} onClick={() => setEditingDrug(null)}>Cancel</button>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleSave}>Save Changes</button>
            </div>
            <button 
              className="btn btn-outline" 
              style={{ width: '100%', borderColor: 'var(--primary)', color: 'var(--primary)', fontSize: '11px' }}
              onClick={async () => {
                await onResync(editingDrug.id);
                setEditingDrug(null);
              }}
            >
              🔄 Refresh Missing Data from PubChem
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LibraryView;
