import React, { useEffect, useMemo, useRef, useState } from 'react';
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
  const editableFields = ['bp', 'vp', 'ev', 'fp', 'mr', 'st', 'mv', 'mw', 'complexity'];
  const [analysisName, setAnalysisName] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [editedCells, setEditedCells] = useState({});
  const [focusedRowId, setFocusedRowId] = useState(null);
  const selectVisibleRef = useRef(null);

  const filteredDrugs = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return drugs;
    return drugs.filter((drug) => {
      const name = drug.name?.toLowerCase() || '';
      const smiles = drug.smiles?.toLowerCase() || '';
      return name.includes(query) || smiles.includes(query);
    });
  }, [drugs, searchQuery]);

  const filteredDrugIds = filteredDrugs.map((drug) => drug.id);
  const selectedVisibleCount = filteredDrugIds.filter((id) => selectedDrugIds.includes(id)).length;
  const allVisibleSelected = filteredDrugIds.length > 0 && selectedVisibleCount === filteredDrugIds.length;
  const partiallyVisibleSelected = selectedVisibleCount > 0 && selectedVisibleCount < filteredDrugIds.length;

  useEffect(() => {
    if (selectVisibleRef.current) {
      selectVisibleRef.current.indeterminate = partiallyVisibleSelected;
    }
  }, [partiallyVisibleSelected]);

  const handleToggleVisible = (checked) => {
    if (checked) {
      setSelectedDrugIds([...new Set([...selectedDrugIds, ...filteredDrugIds])]);
      return;
    }
    setSelectedDrugIds(selectedDrugIds.filter((id) => !filteredDrugIds.includes(id)));
  };

  const handleSelectDrug = (drugId, checked) => {
    if (checked) {
      setSelectedDrugIds(selectedDrugIds.includes(drugId) ? selectedDrugIds : [...selectedDrugIds, drugId]);
      return;
    }
    setSelectedDrugIds(selectedDrugIds.filter((id) => id !== drugId));
  };

  const handleToggleDrug = (drugId) => {
    handleSelectDrug(drugId, !selectedDrugIds.includes(drugId));
  };

  const missingCellCount = useMemo(
    () => analysisItems.reduce(
      (count, item) => count + editableFields.filter((field) => item[field] === null || item[field] === undefined).length,
      0
    ),
    [analysisItems]
  );

  const editedCellCount = Object.keys(editedCells).length;

  const markEditedCell = (itemId, field, value) => {
    setEditedCells((prev) => ({
      ...prev,
      [`${itemId}:${field}`]: value,
    }));
    handleOverwrite(itemId, field, value);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header & Breadcrumb */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <div>
          <h1 style={{ margin: 0 }}>Analysis Workspace</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-dim)', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
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
        <div className="panel table-panel" style={{ flex: 1 }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', background: 'var(--bg-navbar)' }}>
            <span style={{ fontWeight: 600, fontSize: '13px', flex: '1 1 260px' }}>Select Compounds for QSPR Training Set</span>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.75rem', flex: '1 1 520px', flexWrap: 'wrap' }}>
              <input
                type="text"
                placeholder="Search by compound or SMILES..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  padding: '6px 12px',
                  background: 'rgba(0, 0, 0, 0.2)',
                  border: '1px solid var(--border-light)',
                  borderRadius: '4px',
                  color: 'var(--text-primary)',
                  fontSize: '12px',
                  width: '260px',
                  flex: '1 1 260px',
                  minWidth: '220px'
                }}
              />
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
                  width: '220px',
                  flex: '1 1 220px',
                  minWidth: '180px'
                }}
              />
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>Selected: {selectedDrugIds.length}</span>
              <button className="btn btn-primary" onClick={() => startAnalysis(analysisName)} disabled={selectedDrugIds.length < 3}>
                Initialize Dataset →
              </button>
            </div>
          </div>
          <div style={{ padding: '10px 16px', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap', background: 'rgba(255, 255, 255, 0.01)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                {filteredDrugs.length} visible
              </span>
              <span style={{
                fontSize: '12px',
                color: selectedVisibleCount > 0 ? 'var(--primary)' : 'var(--text-secondary)',
                background: selectedVisibleCount > 0 ? 'rgba(56, 189, 248, 0.10)' : 'transparent',
                border: selectedVisibleCount > 0 ? '1px solid rgba(56, 189, 248, 0.22)' : '1px solid transparent',
                borderRadius: '999px',
                padding: '4px 10px',
                fontWeight: selectedVisibleCount > 0 ? 600 : 400
              }}>
                {selectedVisibleCount} selected in view
              </span>
              <span style={{
                fontSize: '12px',
                color: selectedDrugIds.length > 0 ? '#a7f3d0' : 'var(--text-secondary)',
                background: selectedDrugIds.length > 0 ? 'rgba(16, 185, 129, 0.10)' : 'transparent',
                border: selectedDrugIds.length > 0 ? '1px solid rgba(16, 185, 129, 0.22)' : '1px solid transparent',
                borderRadius: '999px',
                padding: '4px 10px',
                fontWeight: selectedDrugIds.length > 0 ? 600 : 400
              }}>
                {selectedDrugIds.length} total selected
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <button
                className="btn btn-outline"
                style={{ fontSize: '11px', padding: '4px 10px' }}
                onClick={() => handleToggleVisible(true)}
                disabled={filteredDrugs.length === 0 || allVisibleSelected}
              >
                Select Visible
              </button>
              <button
                className="btn btn-outline"
                style={{ fontSize: '11px', padding: '4px 10px' }}
                onClick={() => setSelectedDrugIds([])}
                disabled={selectedDrugIds.length === 0}
              >
                Clear All
              </button>
            </div>
          </div>
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th className="text-center" style={{ width: '56px' }}>
                    <input
                      ref={selectVisibleRef}
                      type="checkbox"
                      checked={allVisibleSelected}
                      onChange={(e) => handleToggleVisible(e.target.checked)}
                      aria-label="Select all visible compounds"
                    />
                  </th>
                  <th className="text-left">Compound</th>
                  <th>SMILES Reference</th>
                </tr>
              </thead>
              <tbody>
                {filteredDrugs.length === 0 ? (
                  <tr>
                    <td colSpan="3" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-dim)' }}>
                      No compounds match the current search.
                    </td>
                  </tr>
                ) : filteredDrugs.map(drug => {
                  const isSelected = selectedDrugIds.includes(drug.id);
                  return (
                  <tr
                    key={drug.id}
                    style={{
                      background: isSelected ? 'rgba(56, 189, 248, 0.07)' : 'transparent',
                      boxShadow: isSelected ? 'inset 3px 0 0 0 rgba(56, 189, 248, 0.9)' : 'none',
                      cursor: 'pointer'
                    }}
                    onClick={() => handleToggleDrug(drug.id)}
                  >
                    <td className="text-center">
                      <input 
                        type="checkbox" 
                        checked={isSelected}
                        onClick={(e) => e.stopPropagation()}
                        onChange={(e) => handleSelectDrug(drug.id, e.target.checked)}
                      />
                    </td>
                    <td style={{ fontWeight: isSelected ? 600 : 500, color: isSelected ? '#f8fafc' : 'inherit' }}>
                      {drug.name}
                    </td>
                    <td>
                      <span
                        className="smiles-pill"
                        style={{
                          maxWidth: '420px',
                          borderColor: isSelected ? 'rgba(56, 189, 248, 0.2)' : 'var(--border-light)',
                          background: isSelected ? 'rgba(56, 189, 248, 0.06)' : undefined,
                          color: isSelected ? '#b9e6fb' : undefined
                        }}
                        title={drug.smiles}
                      >
                        {drug.smiles || '—'}
                      </span>
                    </td>
                  </tr>
                )})}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Step 2: Refinement */}
      {wizardStep === 2 && (
        <div className="panel table-panel" style={{ flex: 1 }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', background: 'var(--bg-navbar)' }}>
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
          <div style={{ padding: '10px 16px', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap', background: 'rgba(255, 255, 255, 0.01)' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              {analysisItems.length} compounds
            </span>
            <span style={{
              fontSize: '12px',
              color: missingCellCount > 0 ? '#fbbf24' : 'var(--text-secondary)',
              background: missingCellCount > 0 ? 'rgba(245, 158, 11, 0.10)' : 'transparent',
              border: missingCellCount > 0 ? '1px solid rgba(245, 158, 11, 0.22)' : '1px solid transparent',
              borderRadius: '999px',
              padding: '4px 10px',
              fontWeight: missingCellCount > 0 ? 600 : 400
            }}>
              {missingCellCount} missing values
            </span>
            <span style={{
              fontSize: '12px',
              color: editedCellCount > 0 ? 'var(--primary)' : 'var(--text-secondary)',
              background: editedCellCount > 0 ? 'rgba(56, 189, 248, 0.10)' : 'transparent',
              border: editedCellCount > 0 ? '1px solid rgba(56, 189, 248, 0.22)' : '1px solid transparent',
              borderRadius: '999px',
              padding: '4px 10px',
              fontWeight: editedCellCount > 0 ? 600 : 400
            }}>
              {editedCellCount} manual overrides
            </span>
            <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
              Empty cells are highlighted for review.
            </span>
          </div>
          <div className="table-scroll">
            <table className="data-table" style={{ whiteSpace: 'nowrap' }}>
              <thead>
                <tr>
                  <th className="sticky-col" style={{ minWidth: '170px' }}>Entity</th>
                  <th className="text-right" style={{ width: '100px' }}>BP (°C)</th>
                  <th className="text-right" style={{ width: '100px' }}>VP (mmHg)</th>
                  <th className="text-right" style={{ width: '100px' }}>EV (kJ/mol)</th>
                  <th className="text-right" style={{ width: '100px' }}>FP (°C)</th>
                  <th className="text-right" style={{ width: '100px' }}>MR</th>
                  <th className="text-right" style={{ width: '100px' }}>ST (dyn/cm)</th>
                  <th className="text-right" style={{ width: '100px' }}>MV (cm³/mol)</th>
                  <th className="text-right" style={{ width: '100px' }}>MW (g/mol)</th>
                  <th className="text-right" style={{ width: '100px' }}>Complexity</th>
                </tr>
              </thead>
              <tbody>
                {analysisItems.map(item => {
                  const isFocusedRow = focusedRowId === item.id;
                  const rowStyle = {
                    background: isFocusedRow ? 'rgba(56, 189, 248, 0.05)' : 'transparent',
                  };
                  const stickyStyle = {
                    fontWeight: 600,
                    background: isFocusedRow ? 'rgba(10, 28, 43, 0.95)' : 'var(--bg-panel)',
                    boxShadow: isFocusedRow ? 'inset 3px 0 0 0 rgba(56, 189, 248, 0.8)' : 'none',
                  };

                  return (
                    <tr key={item.id} style={rowStyle}>
                      <td className="sticky-col" style={stickyStyle}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                          <span>{item.drug_name}</span>
                          {isFocusedRow && (
                            <span style={{ fontSize: '10px', color: 'var(--primary)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                              Reviewing row
                            </span>
                          )}
                        </div>
                      </td>
                      {editableFields.map((field) => {
                        const isMissing = item[field] === null || item[field] === undefined;
                        const isEdited = editedCells[`${item.id}:${field}`] !== undefined;

                        return (
                          <td key={`${item.id}-${field}`} className="text-right" style={{ padding: '4px 6px' }}>
                            <input
                              className={`input-dense table-input mono${isMissing ? ' table-input-missing' : ''}${isEdited ? ' table-input-edited' : ''}`}
                              type="number"
                              value={item[field] ?? ''}
                              onFocus={() => setFocusedRowId(item.id)}
                              onBlur={() => setFocusedRowId((current) => (current === item.id ? null : current))}
                              onChange={(e) => markEditedCell(item.id, field, e.target.value)}
                            />
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
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
