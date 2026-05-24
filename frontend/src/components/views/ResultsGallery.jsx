import React, { useEffect, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { API_BASE, API_STATIC } from '../../config';

const ResultsGallery = ({ analysis, setView, resetWizard }) => {
  const analysisId = analysis?.id;
  const folderName = analysis?.folder_name || `analysis_${analysisId}`;

  const plots = [
    { id: 'report', title: 'Statistical Report', shortLabel: 'Report', file: 'qspr_report.md', icon: 'doc' },
    { id: 'stats', title: 'Regression Statistics', shortLabel: 'Stats', file: '', icon: 'chart' },
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

  const plotGroups = [
    {
      label: 'Report',
      items: ['report'],
    },
    {
      label: 'Statistics',
      items: ['stats'],
    },
    {
      label: 'Correlation Plots',
      items: ['structures', 'global_r', 'bp', 'vp', 'ev', 'fp', 'mr', 'st', 'mv', 'mw', 'complexity'],
    },
  ];

  const [activePlotId, setActivePlotId] = useState(plots[0].id);
  const [reportContent, setReportContent] = useState('Loading report...');

  const [stats, setStats] = useState([]);
  const [statsLoading, setStatsLoading] = useState(false);
  const [filterProp, setFilterProp] = useState('');
  const [filterIdx, setFilterIdx] = useState('');
  const [sortField, setSortField] = useState('r2');
  const [sortAsc, setSortAsc] = useState(false);
  const [copiedKey, setCopiedKey] = useState('');
  const [isOutputsCollapsed, setIsOutputsCollapsed] = useState(false);

  const activePlot = plots.find(p => p.id === activePlotId);

  const renderPlotIcon = (kind = 'plot') => {
    if (kind === 'doc') {
      return (
        <svg style={{ width: '16px', height: '16px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <line x1="10" y1="9" x2="8" y2="9"></line>
        </svg>
      );
    }
    if (kind === 'chart') {
      return (
        <svg style={{ width: '16px', height: '16px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="20" x2="12" y2="10"></line>
          <line x1="18" y1="20" x2="18" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
      );
    }
    return (
      <svg style={{ width: '16px', height: '16px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="3 17 9 11 13 15 21 7"></polyline>
        <polyline points="14 7 21 7 21 14"></polyline>
      </svg>
    );
  };

  const reportSections = useMemo(() => {
    const content = reportContent || '';
    const summaryMatch = content.match(/Best model per property[\s\S]*?(?=\nStatistical Tables|\n## |$)/i);
    const tablesMatch = content.match(/Statistical Tables[\s\S]*?(?=\nRegression Equations by Index|\n## |$)/i);
    const equationsMatch = content.match(/Regression Equations by Index[\s\S]*$/i);

    return {
      full: content,
      summary: summaryMatch?.[0] || '',
      tables: tablesMatch?.[0] || '',
      equations: equationsMatch?.[0] || '',
    };
  }, [reportContent]);

  const reportAnchors = [
    { id: 'best-model-per-property', label: 'Best Model' },
    { id: 'statistical-tables-article-format', label: 'Tables' },
    { id: 'regression-equations-by-index', label: 'Equations' },
  ];

  const handleDownloadCSV = () => {
    if (stats.length === 0) return;
    const headers = ["Property", "Index", "r", "R2", "Adj_R2", "Slope", "Intercept", "p-value", "RMSE", "n", "F-statistic"];
    const rows = stats.map(s => [
      s.property_name,
      s.index_name,
      s.r,
      s.r2,
      s.adj_r2,
      s.slope,
      s.intercept,
      s.p_value,
      s.rmse,
      s.n,
      s.f_statistic
    ]);
    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(","), ...rows.map(e => e.map(val => val !== null && val !== undefined ? val : '').join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `${folderName}_stats.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const renderHeader = (label, field, className = '') => {
    const isSorted = sortField === field;
    return (
      <th
        className={className}
        onClick={() => handleSort(field)} 
        style={{ cursor: 'pointer', userSelect: 'none' }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: className.includes('right') ? 'flex-end' : 'flex-start', gap: '4px' }}>
          {label}
          {isSorted ? (sortAsc ? ' ▲' : ' ▼') : ''}
        </div>
      </th>
    );
  };

  const uniqueProperties = Array.from(new Set(stats.map(s => s.property_name)));
  const uniqueIndices = Array.from(new Set(stats.map(s => s.index_name)));

  const sortedStats = [...stats]
    .filter(s => (!filterProp || s.property_name === filterProp) && (!filterIdx || s.index_name === filterIdx))
    .sort((a, b) => {
      let valA = a[sortField];
      let valB = b[sortField];
      
      if (valA === null || valA === undefined) return sortAsc ? -1 : 1;
      if (valB === null || valB === undefined) return sortAsc ? 1 : -1;
      
      if (typeof valA === 'string') {
        return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      } else {
        return sortAsc ? valA - valB : valB - valA;
      }
    });

  useEffect(() => {
    if (activePlotId === 'report' && analysisId) {
      fetch(`${API_BASE}/analyses/${analysisId}/report`)
        .then(r => r.json())
        .then(d => setReportContent(d.content))
        .catch(e => setReportContent('Error loading report.'));
    }
  }, [activePlotId, analysisId]);

  useEffect(() => {
    if (activePlotId === 'stats' && analysisId) {
      setStatsLoading(true);
      fetch(`${API_BASE}/analyses/${analysisId}/stats`)
        .then(r => r.json())
        .then(d => {
          setStats(d);
          setStatsLoading(false);
        })
        .catch(e => {
          console.error("Error loading stats:", e);
          setStatsLoading(false);
        });
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

  const handleCopy = async (text, key) => {
    if (!text?.trim()) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopiedKey(key);
      window.setTimeout(() => setCopiedKey((current) => (current === key ? '' : current)), 1600);
    } catch (error) {
      console.error('Failed to copy report content:', error);
    }
  };

  const jumpToReportSection = (anchorId) => {
    const element = document.getElementById(`report-${anchorId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const renderReportHeading = (Tag, children) => {
    const text = Array.isArray(children) ? children.join('') : String(children ?? '');
    const slug = text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');

    return <Tag id={`report-${slug}`}>{children}</Tag>;
  };

  return (
    <div className="split-layout">
      <div className="split-sidebar" style={{ width: isOutputsCollapsed ? '74px' : '350px', transition: 'width 0.18s ease' }}>
        <div style={{ padding: '12px 12px 12px 16px', borderBottom: '1px solid var(--border-light)', display: 'flex', alignItems: 'center', justifyContent: isOutputsCollapsed ? 'center' : 'space-between', gap: '8px', fontSize: '11px', fontWeight: '600', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
          {!isOutputsCollapsed && <span>Outputs</span>}
          <button
            onClick={() => setIsOutputsCollapsed((current) => !current)}
            style={{
              background: 'transparent',
              border: '1px solid var(--border-light)',
              color: 'var(--text-dim)',
              cursor: 'pointer',
              width: '28px',
              height: '28px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title={isOutputsCollapsed ? 'Expand outputs' : 'Collapse outputs'}
          >
            <svg style={{ width: '14px', height: '14px' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {isOutputsCollapsed ? <polyline points="9 18 15 12 9 6"></polyline> : <polyline points="15 18 9 12 15 6"></polyline>}
            </svg>
          </button>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', padding: '8px 0 12px' }}>
          {plotGroups.map((group) => (
            <div key={group.label} style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              {!isOutputsCollapsed && (
                <div style={{ padding: '12px 16px 6px', fontSize: '10px', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>
                  {group.label}
                </div>
              )}
              {group.items.map((plotId) => {
                const plot = plots.find((item) => item.id === plotId);
                if (!plot) return null;

                return (
                  <button
                    key={plot.id}
                    onClick={() => setActivePlotId(plot.id)}
                    title={plot.title}
                    style={{
                      padding: isOutputsCollapsed ? '10px' : '8px 16px',
                      margin: isOutputsCollapsed ? '0 10px' : '0 8px',
                      border: 'none',
                      borderRadius: '8px',
                      background: activePlotId === plot.id ? 'var(--bg-hover)' : 'transparent',
                      color: activePlotId === plot.id ? 'var(--text-primary)' : 'var(--text-secondary)',
                      cursor: 'pointer',
                      textAlign: isOutputsCollapsed ? 'center' : 'left',
                      fontSize: '13px',
                      fontWeight: activePlotId === plot.id ? 500 : 400,
                      borderLeft: activePlotId === plot.id ? '2px solid var(--primary)' : '2px solid transparent',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: isOutputsCollapsed ? 'center' : 'flex-start',
                      gap: isOutputsCollapsed ? 0 : '10px',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    }}
                  >
                    <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: activePlotId === plot.id ? '#93c5fd' : 'var(--text-dim)' }}>
                      {renderPlotIcon(plot.icon)}
                    </span>
                    {!isOutputsCollapsed && (plot.shortLabel || plot.title)}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>
      
      <div className="split-main print-container">
        <div className="no-print" style={{ padding: '8px 16px', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-navbar)' }}>
          <span style={{ fontWeight: 600, fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ display: 'flex', alignItems: 'center', color: '#cbd5e1' }}>{renderPlotIcon(activePlot.icon)}</span>
            {activePlot.title}
          </span>
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
            ) : activePlotId === 'stats' ? (
              <button className="btn btn-outline" onClick={handleDownloadCSV} style={{ fontSize: '11px', padding: '4px 8px' }}>
                ↓ .CSV
              </button>
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
            <div className="report-shell" style={{ width: '100%', maxWidth: '920px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="report-toolbar no-print">
                <div className="report-toolbar-copy">
                  <button className="btn btn-outline" style={{ fontSize: '11px', padding: '4px 10px' }} onClick={() => handleCopy(reportSections.full, 'full')}>
                    {copiedKey === 'full' ? 'Copied report' : 'Copy Report'}
                  </button>
                  <button className="btn btn-outline" style={{ fontSize: '11px', padding: '4px 10px' }} onClick={() => handleCopy(reportSections.summary, 'summary')} disabled={!reportSections.summary}>
                    {copiedKey === 'summary' ? 'Copied summary' : 'Copy Summary'}
                  </button>
                  <button className="btn btn-outline" style={{ fontSize: '11px', padding: '4px 10px' }} onClick={() => handleCopy(reportSections.tables, 'tables')} disabled={!reportSections.tables}>
                    {copiedKey === 'tables' ? 'Copied tables' : 'Copy Tables'}
                  </button>
                  <button className="btn btn-outline" style={{ fontSize: '11px', padding: '4px 10px' }} onClick={() => handleCopy(reportSections.equations, 'equations')} disabled={!reportSections.equations}>
                    {copiedKey === 'equations' ? 'Copied equations' : 'Copy Equations'}
                  </button>
                </div>
                <div className="report-toolbar-nav">
                  {reportAnchors.map((anchor) => (
                    <button
                      key={anchor.id}
                      className="btn btn-outline"
                      style={{ fontSize: '11px', padding: '4px 10px' }}
                      onClick={() => jumpToReportSection(anchor.id)}
                    >
                      {anchor.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="report-paper">
                <div className="report-paper-meta">
                  <span className="report-kicker">QSPR Analysis Viewer</span>
                  <span className="report-chip">{folderName}</span>
                </div>
                <div className="report-markdown" style={{ width: '100%', background: '#fff', color: '#000', padding: '40px', borderRadius: '4px' }}>
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h1: ({ children }) => renderReportHeading('h1', children),
                      h2: ({ children }) => renderReportHeading('h2', children),
                      h3: ({ children }) => renderReportHeading('h3', children),
                    }}
                  >
                    {reportContent}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          ) : activePlotId === 'stats' ? (
            <div style={{ width: '100%', display: 'flex', flexDirection: 'column', height: '100%' }}>
              {/* Filter controls */}
              <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', alignItems: 'center' }} className="no-print">
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>Filter by Property</label>
                  <select 
                    className="input-dense" 
                    style={{ width: '150px', background: 'var(--bg-panel)' }} 
                    value={filterProp} 
                    onChange={e => setFilterProp(e.target.value)}
                  >
                    <option value="">All Properties</option>
                    {uniqueProperties.map(p => <option key={p} value={p}>{p}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>Filter by Index</label>
                  <select 
                    className="input-dense" 
                    style={{ width: '150px', background: 'var(--bg-panel)' }} 
                    value={filterIdx} 
                    onChange={e => setFilterIdx(e.target.value)}
                  >
                    <option value="">All Indices</option>
                    {uniqueIndices.map(i => <option key={i} value={i}>{i}</option>)}
                  </select>
                </div>
                {(filterProp || filterIdx) && (
                  <button 
                    className="btn btn-outline" 
                    style={{ alignSelf: 'flex-end', fontSize: '11px', padding: '4px 8px' }}
                    onClick={() => { setFilterProp(''); setFilterIdx(''); }}
                  >
                    Clear Filters
                  </button>
                )}
              </div>

              {/* Data Table */}
              <div className="panel table-panel" style={{ flex: 1 }}>
                <div className="table-scroll">
                  <table className="data-table">
                    <thead>
                      <tr>
                        {renderHeader('Property', 'property_name')}
                        {renderHeader('Index', 'index_name')}
                        {renderHeader('r', 'r', 'text-right')}
                        {renderHeader('R²', 'r2', 'text-right')}
                        {renderHeader('Adj. R²', 'adj_r2', 'text-right')}
                        {renderHeader('Slope (b)', 'slope', 'text-right')}
                        {renderHeader('Intercept (a)', 'intercept', 'text-right')}
                        {renderHeader('p-value', 'p_value', 'text-right')}
                        {renderHeader('RMSE', 'rmse', 'text-right')}
                        {renderHeader('F-stat', 'f_statistic', 'text-right')}
                        {renderHeader('n', 'n', 'text-right')}
                      </tr>
                    </thead>
                    <tbody>
                      {statsLoading ? (
                        <tr>
                          <td colSpan="11" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                            Loading statistics...
                          </td>
                        </tr>
                      ) : sortedStats.length === 0 ? (
                        <tr>
                          <td colSpan="11" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                            No statistics found matching filters.
                          </td>
                        </tr>
                      ) : (
                        sortedStats.map((s) => (
                          <tr key={s.id}>
                            <td style={{ fontWeight: '600' }}>{s.property_name}</td>
                            <td className="mono" style={{ color: 'var(--primary)' }}>{s.index_name}</td>
                            <td className="mono text-right">{s.r !== null ? s.r.toFixed(4) : '-'}</td>
                            <td className="mono text-right" style={{ fontWeight: s.r2 >= 0.8 ? '600' : '400', color: s.r2 >= 0.8 ? '#3fb950' : 'inherit' }}>
                              {s.r2 !== null ? s.r2.toFixed(4) : '-'}
                            </td>
                            <td className="mono text-right">{s.adj_r2 !== null ? s.adj_r2.toFixed(4) : '-'}</td>
                            <td className="mono text-right">{s.slope !== null ? s.slope.toFixed(4) : '-'}</td>
                            <td className="mono text-right">{s.intercept !== null ? s.intercept.toFixed(4) : '-'}</td>
                            <td className="mono text-right" style={{ color: s.p_value < 0.05 ? '#3fb950' : 'inherit' }}>
                              {s.p_value !== null ? (s.p_value < 0.0001 ? s.p_value.toExponential(2) : s.p_value.toFixed(4)) : '-'}
                            </td>
                            <td className="mono text-right">{s.rmse !== null ? s.rmse.toFixed(4) : '-'}</td>
                            <td className="mono text-right">{s.f_statistic !== null ? s.f_statistic.toFixed(2) : '-'}</td>
                            <td className="mono text-right">{s.n}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
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
