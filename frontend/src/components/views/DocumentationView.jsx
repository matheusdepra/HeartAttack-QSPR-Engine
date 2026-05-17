import React from 'react';

export default function DocumentationView() {
  const indices = [
    {
      symbol: 'ABC',
      name: 'Atom-Bond Connectivity Index',
      formula: 'ABC(G) = ∑_{uv ∈ E} √((d_u + d_v - 2) / (d_u · d_v))',
      desc: 'Measures the thermodynamic stability of organic compounds. Highly correlated with the strain energy of alkanes.'
    },
    {
      symbol: 'GA',
      name: 'Geometric-Arithmetic Index',
      formula: 'GA(G) = ∑_{uv ∈ E} (2√(d_u · d_v)) / (d_u + d_v)',
      desc: 'Based on the ratio of the geometric and arithmetic means of the degrees of the connected atoms. Reflects molecular symmetry and branching.'
    },
    {
      symbol: 'RI (RA)',
      name: 'Randić Index (Product Connectivity)',
      formula: 'χ(G) = ∑_{uv ∈ E} 1 / √(d_u · d_v)',
      desc: 'The most widely used classical topological index. Measures the degree of molecular branching and strongly correlates with surface area and boiling point.'
    },
    {
      symbol: 'RR',
      name: 'Reciprocal Randić Index',
      formula: 'RR(G) = ∑_{uv ∈ E} √(d_u · d_v)',
      desc: 'Reciprocal version of the Randić index, giving weight directly proportional to the vertex degrees of each chemical bond.'
    },
    {
      symbol: 'SCI (S)',
      name: 'Sum Connectivity Index',
      formula: 'SCI(G) = ∑_{uv ∈ E} 1 / √(d_u + d_v)',
      desc: 'Proposed as a robust variation of the Randić index, replacing the product of atomic degrees with their sum.'
    },
    {
      symbol: 'H',
      name: 'Harmonic Index',
      formula: 'H(G) = ∑_{uv ∈ E} 2 / (d_u + d_v)',
      desc: 'Based on the sum of reciprocals of the arithmetic mean of the degrees of bonds. Has strong predictive power for physical properties of hydrocarbons.'
    },
    {
      symbol: 'M1',
      name: 'First Zagreb Index',
      formula: 'M1(G) = ∑_{uv ∈ E} (d_u + d_v) = ∑_{u ∈ V} (d_u)^2',
      desc: 'Measures the branching extent of the molecular structure by summing the squares of the degrees of all atoms.'
    },
    {
      symbol: 'M2',
      name: 'Second Zagreb Index',
      formula: 'M2(G) = ∑_{uv ∈ E} (d_u · d_v)',
      desc: 'Sum of products of the degrees of chemical bonds. Widely used to estimate chemometric properties and biological activity.'
    },
    {
      symbol: 'HM',
      name: 'Hyper-Zagreb Index',
      formula: 'HM(G) = ∑_{uv ∈ E} (d_u + d_v)^2',
      desc: 'High-sensitivity extension of the First Zagreb Index, squaring the sum of degrees of the incident vertices.'
    },
    {
      symbol: 'RM2',
      name: 'Redefined Second Zagreb Index',
      formula: 'RM2(G) = ∑_{uv ∈ E} (d_u - 1) · (d_v - 1)',
      desc: 'Sums the product of atomic degrees minus 1, measuring internal connectivity by disregarding bonds with implicit hydrogens.'
    },
    {
      symbol: 'F',
      name: 'Forgotten Topological Index',
      formula: 'F(G) = ∑_{u ∈ V} (d_u)^3 = ∑_{uv ∈ E} ((d_u)^2 + (d_v)^2)',
      desc: 'Introduced in the spectral analysis of molecular graphs. Significantly measures molecular complexity and branching.'
    },
    {
      symbol: 'HF',
      name: 'Hyper-Forgotten Index',
      formula: 'HF(G) = ∑_{uv ∈ E} ((d_u)^2 + (d_v)^2)^2',
      desc: 'Hyperbolic version of the Forgotten Index. Provides extreme sensitivity to small conformational changes in the molecule.'
    }
  ];

  const properties = [
    { prop: 'BP', name: 'Boiling Point (°C)', desc: 'Boiling Point. Indicates the volatility of the compound.', fallback: 'PubChem experimental ➔ EPI Suite Estimation ➔ RDKit Theoretical Estimator' },
    { prop: 'VP', name: 'Vapor Pressure (mmHg)', desc: 'Vapor Pressure. Measures ease of evaporation at 25°C.', fallback: 'PubChem experimental ➔ EPI Suite Estimation (EPIWeb)' },
    { prop: 'EV', name: 'Heat of Vaporization (kJ/mol)', desc: 'Enthalpy of Vaporization. Energy required to transform 1 mol of liquid to gas.', fallback: 'PubChem ➔ Trouton\'s Rule based on BP: ΔHvap ≈ 88 · Tb(K) / 1000' },
    { prop: 'FP', name: 'Flash Point (°C)', desc: 'Flash Point. Lowest temperature where flammable vapor forms.', fallback: 'PubChem ➔ Sinnott\'s Rule based on BP: FP ≈ 0.683 · BP - 73' },
    { prop: 'MR', name: 'Molar Refractivity (cm³/mol)', desc: 'Molar Refractivity. Measures structural electronic polarizability.', fallback: 'PubChem ➔ RDKit Crippen MR Estimator (Based on SMILES)' },
    { prop: 'ST', name: 'Surface Tension (mN/m)', desc: 'Surface Tension. Molecular cohesion at the compound surface.', fallback: 'PubChem ➔ Macleod-Sugden proxy based on Molar Refractivity: ST ≈ 0.5 · MR' },
    { prop: 'MV', name: 'Molar Volume (cm³/mol)', desc: 'Molar Volume. Space occupied by 1 mol of compound.', fallback: 'PubChem ➔ RDKit molecular volume proxy: MV ≈ Molecular Weight / Density (=1 g/cm³)' },
    { prop: 'MW', name: 'Molecular Weight (g/mol)', desc: 'Molecular Weight. Sum of the atomic masses of constituent atoms.', fallback: 'PubChem PUG-REST ➔ RDKit Exact Molecular Weight' },
    { prop: 'Complexity', name: 'Molecular Complexity', desc: 'Bertz-Crippen Complexity. Measures branching, heteroatoms, and molecular symmetry.', fallback: 'PubChem API ➔ RDKit BertzCT Graph Complexity' }
  ];

  return (
    <div className="view-container" style={{ padding: '0 8px 40px 8px', maxWidth: '1200px' }}>
      
      {/* Introduction Card */}
      <div className="card" style={{ padding: '32px', marginBottom: '24px', background: 'radial-gradient(circle at top right, rgba(56, 189, 248, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%)' }}>
        <h1 style={{
          fontSize: '28px',
          fontWeight: 800,
          letterSpacing: '-0.5px',
          margin: '0 0 12px 0',
          background: 'linear-gradient(135deg, #38bdf8 0%, #ec4899 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          display: 'inline-block'
        }}>
          CardioQSPR Documentation
        </h1>
        <p style={{ fontSize: '15px', color: '#94a3b8', lineHeight: '1.6', margin: 0, maxWidth: '900px' }}>
          CardioQSPR is a comprehensive chemometric ecosystem designed to investigate the Quantitative Structure-Property Relationship (**QSPR**) of cardiac and cardiovascular drugs. The platform analyzes the molecular topology of compounds and correlates their indices with essential physical-chemical properties, providing mathematical tools for *in-silico* biological prediction.
        </p>
      </div>

      {/* Methodology Section */}
      <div className="card" style={{ padding: '24px', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 700, margin: '0 0 16px 0', color: '#38bdf8', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '10px' }}>
          QSPR Methodology & Regression Models
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', fontSize: '13px', lineHeight: '1.6' }}>
          <div>
            <h4 style={{ color: '#fff', fontSize: '14px', fontWeight: 600, margin: '0 0 8px 0' }}>Linear Regression Equation</h4>
            <p style={{ color: 'var(--text-dim)' }}>
              The platform constructs regression models based on the Ordinary Least Squares (OLS) method, mapping the physical-chemical property (P) as a function of the topological index (TI):
            </p>
            <div style={{
              background: 'rgba(0, 0, 0, 0.3)',
              padding: '12px',
              borderRadius: '8px',
              textAlign: 'center',
              margin: '12px 0',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              fontSize: '15px',
              fontWeight: 700,
              fontFamily: 'monospace',
              color: '#38bdf8'
            }}>
              P = A + b · (TI)
            </div>
            <p style={{ color: 'var(--text-dim)', fontSize: '12px' }}>
              Where A is the y-intercept and b is the slope of the calibrated regression line.
            </p>
          </div>

          <div>
            <h4 style={{ color: '#fff', fontSize: '14px', fontWeight: 600, margin: '0 0 8px 0' }}>Statistical Validation Metrics</h4>
            <ul style={{ paddingLeft: '18px', color: 'var(--text-dim)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <li><strong>Correlation Coefficient (r):</strong> Measures the direction and strength of linear association (ranges from -1 to 1).</li>
              <li><strong>Coefficient of Determination (r² / R²):</strong> Indicates the proportion of the property's variance explained by the topological index.</li>
              <li><strong>F-Statistic:</strong> Used in the F-test to measure the global significance of the linear model against a null model.</li>
              <li><strong>p-value:</strong> Probability measure of significance (frequently with a threshold &alpha; &lt; 0.05 indicating scientific relevance).</li>
              <li><strong>RMSE (Root Mean Square Error):</strong> Root mean square error, indicating the average dispersion of actual values against predicted values.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* 12 Topological Indices Section */}
      <h2 style={{ fontSize: '18px', fontWeight: 700, margin: '32px 0 16px 0', paddingLeft: '8px' }}>
        The 12 Degree-Based Topological Indices
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '32px' }}>
        {indices.map((ind) => (
          <div key={ind.symbol} className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '8px' }}>
                <span style={{ fontSize: '16px', fontWeight: 800, color: '#38bdf8' }}>{ind.symbol}</span>
                <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 500 }}>Vertex Degree</span>
              </div>
              <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#fff', margin: '0 0 12px 0' }}>{ind.name}</h4>
              <p style={{ fontSize: '12px', color: 'var(--text-dim)', lineHeight: '1.5', margin: 0 }}>{ind.desc}</p>
            </div>
            <div style={{
              background: 'rgba(0, 0, 0, 0.25)',
              padding: '8px 12px',
              borderRadius: '6px',
              fontSize: '11px',
              fontFamily: 'monospace',
              color: '#f472b6',
              marginTop: '16px',
              border: '1px solid rgba(255, 255, 255, 0.04)',
              wordBreak: 'break-all'
            }}>
              {ind.formula}
            </div>
          </div>
        ))}
      </div>

      {/* 9 Properties Fallback Section */}
      <div className="card" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 700, margin: '0 0 8px 0', color: '#ec4899', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '10px' }}>
          The 9 Physical-Chemical Properties & Ingestion Pipeline
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-dim)', marginBottom: '20px', lineHeight: '1.6' }}>
          To guarantee absolute chemometric robustness and prevent data leakage or missing values (Nulls) during regression analyses, CardioQSPR implements a structured pipeline of theoretical calculations and fallbacks if a physical property is not explicitly cataloged in the PubChem database:
        </p>

        <div className="table-wrapper">
          <table className="table" style={{ fontSize: '12px' }}>
            <thead>
              <tr>
                <th style={{ width: '80px' }}>Symbol</th>
                <th style={{ width: '220px' }}>Property</th>
                <th>Scientific Definition</th>
                <th style={{ width: '380px' }}>Fallback Strategy / RDKit Estimator</th>
              </tr>
            </thead>
            <tbody>
              {properties.map((p) => (
                <tr key={p.prop}>
                  <td className="mono" style={{ color: '#ec4899', fontWeight: 700 }}>{p.prop}</td>
                  <td style={{ fontWeight: 600, color: '#fff' }}>{p.name}</td>
                  <td style={{ color: 'var(--text-dim)', lineHeight: '1.4' }}>{p.desc}</td>
                  <td>
                    <span style={{
                      fontSize: '11px',
                      fontFamily: 'monospace',
                      color: '#a7f3d0',
                      background: 'rgba(16, 185, 129, 0.08)',
                      border: '1px solid rgba(16, 185, 129, 0.15)',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      display: 'inline-block',
                      lineHeight: '1.3'
                    }}>
                      {p.fallback}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Academic Citation Card */}
      <div style={{
        marginTop: '24px',
        padding: '20px',
        borderRadius: '12px',
        border: '1px dashed rgba(255, 255, 255, 0.12)',
        background: 'rgba(255, 255, 255, 0.01)',
        fontSize: '12px',
        color: 'var(--text-dim)',
        lineHeight: '1.6',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
      }}>
        <strong>Scientific Reference Article:</strong>
        <span>
          Zaman, S., Yaqoob, H. S. A., Ullah, A., & Sheikh, M. (2023). <em>QSPR Analysis of Some Novel Drugs Used in Blood Cancer Treatment Via Degree Based Topological Indices and Regression Models</em>. Polycyclic Aromatic Compounds. DOI: 10.1080/10406638.2023.XXXXXXX.
        </span>
      </div>

    </div>
  );
}
