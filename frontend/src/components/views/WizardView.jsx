import React, { useState } from 'react';
import ResultsGallery from './ResultsGallery';

const WizardView = ({ 
  wizardStep, 
  setWizardStep,
  drugs, 
  selectedDrugIds, 
  setSelectedDrugIds, 
  startAnalysis, 
  analysisItems, 
  handleOverwrite, 
  runFinalAnalysis, 
  currentAnalysis,
  setView,
  resetWizard
}) => {
  const steps = ['Selection', 'Data Override', 'Analysis Viewer'];
  const [analysisName, setAnalysisName] = useState('');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header & Breadcrumb */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h1 style={{ margin: 0 }}>Analysis Workspace</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-dim)' }}>
          {steps.map((label, idx) => (
            <React.Fragment key={idx}>
              <span 
                onClick={() => (idx + 1 < wizardStep) && setWizardStep(idx + 1)}
                style={{ 
                  color: wizardStep === idx + 1 ? 'var(--text-primary)' : (idx + 1 < wizardStep ? 'var(--primary)' : 'inherit'),
                  fontWeight: wizardStep === idx + 1 ? '600' : 'normal',
                  background: wizardStep === idx + 1 ? 'var(--bg-hover)' : 'transparent',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  cursor: (idx + 1 < wizardStep) ? 'pointer' : 'default'
                }}>
                {idx + 1}. {label}
              </span>
              {idx < steps.length - 1 && <span>›</span>}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Step 1: Selection */}
      {wizardStep === 1 && (
        <div className="panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-navbar)' }}>
            <span style={{ fontWeight: 600, fontSize: '13px' }}>Select Compounds for QSPR Training Set</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <input
                type="text"
                placeholder="Custom analysis name (optional)..."
                value={analysisName}
                onChange={(e) => setAnalysisName(e.target.value)}
                style={{
                  padding: '6px 12px',
                  background: 'rgba(0, 0, 0, 0.2)',
                  border: '1px solid var(--border-light)',
                  borderRadius: '4px',
                  color: 'var(--text-primary)',
                  fontSize: '12px',
                  width: '240px'
                }}
              />
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Selected: {selectedDrugIds.length}</span>
              <button className="btn btn-primary" onClick={() => startAnalysis(analysisName)} disabled={selectedDrugIds.length < 3}>
                Initialize Dataset →
              </button>
            </div>
          </div>
          <div style={{ overflowY: 'auto', flex: 1 }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '40px', textAlign: 'center' }}>[ ]</th>
                  <th>Compound</th>
                  <th>SMILES Reference</th>
                </tr>
              </thead>
              <tbody>
                {drugs.map(drug => (
                  <tr key={drug.id}>
                    <td style={{ textAlign: 'center' }}>
                      <input 
                        type="checkbox" 
                        checked={selectedDrugIds.includes(drug.id)}
                        onChange={(e) => {
                          if (e.target.checked) setSelectedDrugIds([...selectedDrugIds, drug.id]);
                          else setSelectedDrugIds(selectedDrugIds.filter(id => id !== drug.id));
                        }}
                      />
                    </td>
                    <td style={{ fontWeight: 500 }}>{drug.name}</td>
                    <td className="mono" style={{ color: 'var(--text-dim)' }}>{drug.smiles}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Step 2: Refinement */}
      {wizardStep === 2 && (
        <div className="panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-navbar)' }}>
            <span style={{ fontWeight: 600, fontSize: '13px' }}>Spreadsheet Editor (Snapshot ID: {currentAnalysis?.id})</span>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn btn-outline" onClick={resetWizard}>
                Cancel Analysis
              </button>
              <button className="btn btn-primary" onClick={runFinalAnalysis}>
                ▶ Run Linear Regressions
              </button>
            </div>
          </div>
          <div style={{ overflowY: 'auto', flex: 1 }}>
            <table className="data-table" style={{ whiteSpace: 'nowrap' }}>
              <thead>
                <tr>
                  <th style={{ minWidth: '150px' }}>Entity</th>
                  <th style={{ width: '100px' }}>BP (°C)</th>
                  <th style={{ width: '100px' }}>VP (mmHg)</th>
                  <th style={{ width: '100px' }}>EV (kJ/mol)</th>
                  <th style={{ width: '100px' }}>FP (°C)</th>
                  <th style={{ width: '100px' }}>MR</th>
                  <th style={{ width: '100px' }}>ST (dyn/cm)</th>
                  <th style={{ width: '100px' }}>MV (cm³/mol)</th>
                  <th style={{ width: '100px' }}>MW (g/mol)</th>
                  <th style={{ width: '100px' }}>Complexity</th>
                </tr>
              </thead>
              <tbody>
                {analysisItems.map(item => (
                  <tr key={item.id}>
                    <td style={{ fontWeight: 500 }}>{item.drug_name}</td>
                    <td style={{ padding: '2px' }}><input className="input-dense mono" type="number" value={item.bp || ''} onChange={(e) => handleOverwrite(item.id, 'bp', e.target.value)} /></td>
                    <td style={{ padding: '2px' }}><input className="input-dense mono" type="number" value={item.vp || ''} onChange={(e) => handleOverwrite(item.id, 'vp', e.target.value)} /></td>
                    <td style={{ padding: '2px' }}><input className="input-dense mono" type="number" value={item.ev || ''} onChange={(e) => handleOverwrite(item.id, 'ev', e.target.value)} /></td>
                    <td style={{ padding: '2px' }}><input className="input-dense mono" type="number" value={item.fp || ''} onChange={(e) => handleOverwrite(item.id, 'fp', e.target.value)} /></td>
                    <td style={{ padding: '2px' }}><input className="input-dense mono" type="number" value={item.mr || ''} onChange={(e) => handleOverwrite(item.id, 'mr', e.target.value)} /></td>
                    <td style={{ padding: '2px' }}><input className="input-dense mono" type="number" value={item.st || ''} onChange={(e) => handleOverwrite(item.id, 'st', e.target.value)} /></td>
                    <td style={{ padding: '2px' }}><input className="input-dense mono" type="number" value={item.mv || ''} onChange={(e) => handleOverwrite(item.id, 'mv', e.target.value)} /></td>
                    <td style={{ padding: '2px' }}><input className="input-dense mono" type="number" value={item.mw || ''} onChange={(e) => handleOverwrite(item.id, 'mw', e.target.value)} /></td>
                    <td style={{ padding: '2px' }}><input className="input-dense mono" type="number" value={item.complexity || ''} onChange={(e) => handleOverwrite(item.id, 'complexity', e.target.value)} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Step 3: Viewer */}
      {wizardStep === 3 && (
        <ResultsGallery analysis={currentAnalysis} setView={setView} resetWizard={resetWizard} />
      )}
    </div>
  );
};

export default WizardView;
