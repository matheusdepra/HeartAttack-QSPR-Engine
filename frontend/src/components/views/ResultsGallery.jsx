import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { API_BASE, API_STATIC } from '../../config';

const ResultsGallery = ({ analysis, setView, resetWizard }) => {
  const analysisId = analysis?.id;
  const folderName = analysis?.folder_name || `analysis_${analysisId}`;

  const plots = [
    { id: 'report', title: '📄 Statistical Report', file: 'qspr_report.md' },
    { id: 'structures', title: 'Atomic Connectivity & Structures', file: 'molecule_structures.png' },
    { id: 'global_r', title: 'Global Correlation Map (|r|)', file: 'comparison_all_correlations.png' },
    { id: 'bp', title: 'Boiling Point Trends', file: 'correlation_bp.png' },
    { id: 'vp', title: 'Vapor Pressure Trends', file: 'correlation_vp.png' },
    { id: 'ev', title: 'Enthalpy of Vaporization Trends', file: 'correlation_ev.png' },
    { id: 'fp', title: 'Flash Point Trends', file: 'correlation_fp.png' },
    { id: 'mr', title: 'Molar Refractivity Trends', file: 'correlation_mr.png' },
    { id: 'st', title: 'Surface Tension Trends', file: 'correlation_st.png' },
    { id: 'mv', title: 'Molar Volume Trends', file: 'correlation_mv.png' },
    { id: 'mw', title: 'Molecular Weight Trends', file: 'correlation_mw.png' },
    { id: 'complexity', title: 'Complexity Trends', file: 'correlation_complexity.png' }
  ];

  const [activePlotId, setActivePlotId] = useState(plots[0].id);
  const [reportContent, setReportContent] = useState('Loading report...');

  const activePlot = plots.find(p => p.id === activePlotId);

  useEffect(() => {
    if (activePlotId === 'report' && analysisId) {
      fetch(`${API_BASE}/analyses/${analysisId}/report`)
        .then(r => r.json())
        .then(d => setReportContent(d.content))
        .catch(e => setReportContent('Error loading report.'));
    }
  }, [activePlotId, analysisId]);

  const handleDownloadMD = () => {
    const blob = new Blob([reportContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${folderName}_report.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadPDF = () => {
    window.print();
  };

  return (
    <div className="split-layout">
      <div className="split-sidebar">
        <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-light)', fontSize: '11px', fontWeight: '600', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
          Outputs
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {plots.map(plot => (
            <button
              key={plot.id}
              onClick={() => setActivePlotId(plot.id)}
              style={{
                padding: '8px 16px',
                border: 'none',
                background: activePlotId === plot.id ? 'var(--bg-hover)' : 'transparent',
                color: activePlotId === plot.id ? 'var(--text-primary)' : 'var(--text-secondary)',
                cursor: 'pointer',
                textAlign: 'left',
                fontSize: '13px',
                borderLeft: activePlotId === plot.id ? '2px solid var(--primary)' : '2px solid transparent'
              }}
            >
              {plot.title}
            </button>
          ))}
        </div>
      </div>
      
      <div className="split-main print-container">
        <div className="no-print" style={{ padding: '8px 16px', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-navbar)' }}>
          <span style={{ fontWeight: 600, fontSize: '13px' }}>{activePlot.title}</span>
          <div style={{ display: 'flex', gap: '8px' }}>
            {activePlotId === 'report' ? (
              <>
                <button className="btn btn-outline" onClick={handleDownloadMD} style={{ fontSize: '11px', padding: '4px 8px' }}>
                  ↓ .MD
                </button>
                <button className="btn btn-outline" onClick={handleDownloadPDF} style={{ fontSize: '11px', padding: '4px 8px' }}>
                  ↓ .PDF
                </button>
              </>
            ) : (
              <a href={`${API_STATIC}/${folderName}/${activePlot.file}`} target="_blank" rel="noopener noreferrer" className="btn btn-outline" style={{ fontSize: '11px', padding: '4px 8px' }}>
                Open Full
              </a>
            )}
            
            {resetWizard && (
              <button className="btn btn-primary" onClick={resetWizard} style={{ fontSize: '11px', padding: '4px 8px' }}>
                New Analysis
              </button>
            )}
            <button className="btn btn-outline" onClick={() => setView('library')} style={{ fontSize: '11px', padding: '4px 8px' }}>
              Library
            </button>
          </div>
        </div>
        
        <div style={{ flex: 1, padding: '24px', overflow: 'auto', display: 'flex', justifyContent: 'center', alignItems: 'flex-start' }}>
          {activePlotId === 'report' ? (
            <div className="report-markdown" style={{ width: '100%', maxWidth: '900px', background: '#fff', color: '#000', padding: '40px', borderRadius: '4px' }}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {reportContent}
              </ReactMarkdown>
            </div>
          ) : (
            <img 
              src={`${API_STATIC}/${folderName}/${activePlot.file}`} 
              alt={activePlot.title}
              style={{ maxWidth: '100%', border: '1px solid var(--border-light)', borderRadius: '4px', background: '#fff' }}
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.parentNode.innerHTML = '<div style="padding: 2rem; color: var(--text-dim); text-align: center; border: 1px dashed var(--border-light); border-radius: 4px;">Data insufficient to compute this specific correlation metric for the selected subset.</div>';
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsGallery;
