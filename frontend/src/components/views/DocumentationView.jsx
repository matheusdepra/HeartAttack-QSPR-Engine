import React from 'react';

export default function DocumentationView() {
  const workflow = [
    ['1', 'Compound library', 'Seeded cardiovascular compounds can be reviewed, edited, or refreshed from PubChem.'],
    ['2', 'Descriptor calculation', 'RDKit parses each SMILES string and builds the molecular graph used for degree-based indices.'],
    ['3', 'Analysis snapshot', 'Selected compounds are copied into an analysis-specific dataset so later library edits do not alter past runs.'],
    ['4', 'Regression report', 'Each property is regressed against each topological index and summarized in tables, plots, and Markdown output.'],
  ];

  const indices = [
    ['ABC', 'Atom-Bond Connectivity'],
    ['GA', 'Geometric-Arithmetic'],
    ['RI', 'Randic'],
    ['RR', 'Reciprocal Randic'],
    ['SCI', 'Sum Connectivity'],
    ['H', 'Harmonic'],
    ['M1', 'First Zagreb'],
    ['M2', 'Second Zagreb'],
    ['HM', 'Hyper-Zagreb'],
    ['RM2', 'Redefined Second Zagreb'],
    ['F', 'Forgotten'],
    ['HF', 'Hyper-Forgotten'],
  ];

  const properties = [
    ['BP', 'Boiling Point'],
    ['VP', 'Vapor Pressure'],
    ['EV', 'Heat of Vaporization'],
    ['FP', 'Flash Point'],
    ['MR', 'Molar Refractivity'],
    ['ST', 'Surface Tension'],
    ['MV', 'Molar Volume'],
    ['MW', 'Molecular Weight'],
    ['Complexity', 'Molecular Complexity'],
  ];

  return (
    <div className="view-container" style={{ padding: '0 8px 40px 8px', maxWidth: '1120px' }}>
      <div className="card" style={{ padding: '28px', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 800, margin: '0 0 10px 0' }}>
          Methodological Overview
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.65, margin: 0, maxWidth: '900px' }}>
          CardioQSPR is a local academic platform for exploratory QSPR analysis of cardiovascular and heart attack
          treatment compounds. It combines a curated baseline library, public chemical data retrieval, RDKit molecular
          descriptors, degree-based topological indices, and simple linear regression models.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px', marginBottom: '20px' }}>
        <div className="card" style={{ padding: '20px' }}>
          <h2 style={{ fontSize: '16px', margin: '0 0 10px 0', color: '#38bdf8' }}>Data Sources</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-dim)', lineHeight: 1.6, margin: 0 }}>
            The application starts from a seeded cardiovascular drug dataset. Missing or refreshed values may be retrieved
            from PubChem, estimated through EPI Suite-style fallbacks, or derived from RDKit descriptors when experimental
            values are unavailable.
          </p>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <h2 style={{ fontSize: '16px', margin: '0 0 10px 0', color: '#38bdf8' }}>Regression Model</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-dim)', lineHeight: 1.6, margin: 0 }}>
            For each property and topological index pair, CardioQSPR fits an ordinary least squares model of the form
            <span className="mono" style={{ color: '#f472b6' }}> P = a + b * TI</span>. Results include r, R2,
            adjusted R2, p-value, F-statistic, RMSE, MAE, and prediction tables.
          </p>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <h2 style={{ fontSize: '16px', margin: '0 0 10px 0', color: '#38bdf8' }}>Scope</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-dim)', lineHeight: 1.6, margin: 0 }}>
            The platform is intended for academic exploration and reproducible computational experiments. It should not be
            used as a regulatory, clinical, or standalone experimental source of truth.
          </p>
        </div>
      </div>

      <div className="card" style={{ padding: '22px', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '17px', margin: '0 0 16px 0' }}>Analysis Workflow</h2>
        <div style={{ display: 'grid', gap: '10px' }}>
          {workflow.map(([step, title, text]) => (
            <div key={step} style={{ display: 'grid', gridTemplateColumns: '36px 1fr', gap: '12px', alignItems: 'start' }}>
              <div className="mono" style={{
                height: '28px',
                width: '28px',
                borderRadius: '6px',
                background: 'rgba(56, 189, 248, 0.12)',
                color: '#38bdf8',
                display: 'grid',
                placeItems: 'center',
                fontWeight: 700,
              }}>{step}</div>
              <div>
                <div style={{ color: '#fff', fontSize: '13px', fontWeight: 700 }}>{title}</div>
                <div style={{ color: 'var(--text-dim)', fontSize: '12px', lineHeight: 1.5 }}>{text}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px', marginBottom: '20px' }}>
        <div className="card" style={{ padding: '22px' }}>
          <h2 style={{ fontSize: '17px', margin: '0 0 14px 0' }}>Topological Indices</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '8px' }}>
            {indices.map(([symbol, name]) => (
              <div key={symbol} style={{
                border: '1px solid var(--border-light)',
                borderRadius: '6px',
                padding: '8px',
                minHeight: '48px',
              }}>
                <div className="mono" style={{ color: '#38bdf8', fontSize: '12px', fontWeight: 700 }}>{symbol}</div>
                <div style={{ color: 'var(--text-dim)', fontSize: '11px', marginTop: '3px' }}>{name}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card" style={{ padding: '22px' }}>
          <h2 style={{ fontSize: '17px', margin: '0 0 14px 0' }}>Modeled Properties</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '8px' }}>
            {properties.map(([symbol, name]) => (
              <div key={symbol} style={{
                border: '1px solid var(--border-light)',
                borderRadius: '6px',
                padding: '8px',
                minHeight: '48px',
              }}>
                <div className="mono" style={{ color: '#f472b6', fontSize: '12px', fontWeight: 700 }}>{symbol}</div>
                <div style={{ color: 'var(--text-dim)', fontSize: '11px', marginTop: '3px' }}>{name}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: '22px', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '17px', margin: '0 0 12px 0' }}>Known Limitations</h2>
        <ul style={{ color: 'var(--text-dim)', fontSize: '13px', lineHeight: 1.65, margin: 0, paddingLeft: '18px' }}>
          <li>Public chemical databases may mix experimental, computed, and context-dependent values.</li>
          <li>Fallback estimates are heuristic and should be reviewed before publication-grade interpretation.</li>
          <li>Vapor pressure values can span many orders of magnitude, which may require transformation or manual review.</li>
          <li>Single-variable linear regressions are useful for comparison, but they do not capture all molecular effects.</li>
        </ul>
      </div>

      <div style={{
        padding: '18px',
        borderRadius: '8px',
        border: '1px dashed rgba(255, 255, 255, 0.16)',
        color: 'var(--text-dim)',
        fontSize: '12px',
        lineHeight: 1.6,
      }}>
        <strong style={{ color: '#fff' }}>Primary reference:</strong>{' '}
        Rasheed, M. W., Mahboob, A., & Hanif, I. (2023). <em>An estimation of physicochemical
        properties of heart attack treatment medicines by using molecular descriptor&apos;s</em>. South African Journal
        of Chemical Engineering, 45, 20-29. DOI: 10.1016/j.sajce.2023.04.003.
      </div>
    </div>
  );
}
