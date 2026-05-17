import React, { useState, useEffect } from 'react';
import './index.css';

// Layout & Common
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import LibraryView from './components/views/LibraryView';
import WizardView from './components/views/WizardView';
import PredictorView from './components/views/PredictorView';
import HistoryView from './components/views/HistoryView';
import LoginView from './components/views/LoginView';
import UserManagementView from './components/views/UserManagementView';
import DocumentationView from './components/views/DocumentationView';
import LoadingOverlay from './components/common/LoadingOverlay';

import { API_BASE } from './config';

function App() {
  const [user, setUser] = useState(null);
  const [view, setView] = useState('library');
  const [drugs, setDrugs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isStarting, setIsStarting] = useState(true);
  
  // Progress State
  const [syncStatus, setSyncStatus] = useState({ active: false, current: 0, total: 0, label: "" });

  // Wizard State
  const [wizardStep, setWizardStep] = useState(1);
  const [selectedDrugIds, setSelectedDrugIds] = useState([]);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [analysisItems, setAnalysisItems] = useState([]);

  useEffect(() => {
    const savedUser = localStorage.getItem('cardio_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    fetchDrugs(true);
  }, []);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    localStorage.setItem('cardio_user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('cardio_user');
    setView('library');
  };

  const fetchDrugs = async (isInitial = false) => {
    if (!isInitial) setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/drugs`);
      const data = await res.json();
      setDrugs(data);
    } catch (err) {
      console.error("Failed to fetch drugs:", err);
    } finally {
      setLoading(false);
      setIsStarting(false);
    }
  };

  const resetWizard = () => {
    setWizardStep(1);
    setSelectedDrugIds([]);
    setCurrentAnalysis(null);
    setAnalysisItems([]);
    setView('wizard');
  };

  const viewAnalysis = async (id) => {
    setLoading(true);
    try {
      const detailRes = await fetch(`${API_BASE}/analyses/${id}`);
      const detail = await detailRes.json();
      setCurrentAnalysis(detail);
      setAnalysisItems(detail.items);
      setWizardStep(3);
      setView('wizard');
    } catch (err) {
      alert("Error loading analysis history");
    } finally {
      setLoading(false);
    }
  };

  const startAnalysis = async (customName) => {
    if (selectedDrugIds.length < 3) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/analyses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: customName || `Analysis ${new Date().toLocaleString()}`,
          drug_ids: selectedDrugIds,
          user_id: user?.id
        })
      });
      const data = await res.json();
      const detailRes = await fetch(`${API_BASE}/analyses/${data.id}`);
      const detail = await detailRes.json();
      setCurrentAnalysis(detail);
      setAnalysisItems(detail.items);
      setWizardStep(2);
    } catch (err) {
      alert("Error starting analysis");
    } finally {
      setLoading(false);
    }
  };

  const handleOverwrite = async (itemId, field, value) => {
    const newVal = parseFloat(value);
    setAnalysisItems(items => items.map(it => it.id === itemId ? { ...it, [field]: newVal } : it));
    
    await fetch(`${API_BASE}/analyses/${currentAnalysis.id}/items/${itemId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ [field]: newVal })
    });
  };

  const runFinalAnalysis = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/analyses/${currentAnalysis.id}/run`, { method: 'POST' });
      const data = await res.json();
      if (data.status === 'completed') {
        setWizardStep(3);
      }
    } catch (err) {
      alert("Error running QSPR engine");
    } finally {
      setLoading(false);
    }
  };

  const handleAddDrug = async () => {
    const name = prompt("Enter compound name (e.g. Aspirin, Warfarin):");
    if (!name) return;
    
    const smiles = prompt("Optional: Enter SMILES string if you have it (otherwise it will be fetched from PubChem):");
    
    setSyncStatus({ active: true, current: 0, total: 1, label: `Querying/Calculating: ${name}` });
    try {
      let url = `${API_BASE}/drugs/sync?name=${encodeURIComponent(name)}`;
      if (smiles) {
        url += `&smiles=${encodeURIComponent(smiles.trim())}`;
      }
      const res = await fetch(url, {
        method: 'POST'
      });
      if (res.ok) {
        setSyncStatus(s => ({ ...s, current: 1, label: `Ingested ${name}` }));
        fetchDrugs();
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail}`);
      }
    } catch (err) {
      alert("Failed to sync drug from PubChem");
    } finally {
      setTimeout(() => setSyncStatus({ active: false, current: 0, total: 0, label: "" }), 2000);
    }
  };

  const loadDefaults = async () => {
    if (!confirm("Initialize the Baseline Research Dataset? This will trigger batch PubChem requests.")) return;
    const defaults = [
      "Aspirin", "Clopidogrel", "Atorvastatin", "Metoprolol", "Lisinopril",
      "Warfarin", "Propranolol", "Atenolol", "Nitroglycerin", "Enoxaparin",
      "Apixaban", "Rivaroxaban", "Ticagrelor", "Prasugrel", "Ramipril",
      "Captopril", "Enalapril", "Losartan", "Valsartan", "Carvedilol",
      "Bisoprolol", "Spironolactone", "Furosemide", "Dipyridamole", "Amlodipine"
    ];
    
    setSyncStatus({ active: true, current: 0, total: defaults.length, label: "Starting batch job..." });
    
    for (let i = 0; i < defaults.length; i++) {
      const name = defaults[i];
      setSyncStatus(s => ({ ...s, current: i + 1, label: `Fetching ${name}` }));
      try {
        await fetch(`${API_BASE}/drugs/sync?name=${encodeURIComponent(name)}`, { method: 'POST' });
      } catch (e) { 
        console.error("Error loading", name); 
      }
    }
    
    setSyncStatus(s => ({ ...s, label: "Batch complete" }));
    fetchDrugs();
    setTimeout(() => setSyncStatus({ active: false, current: 0, total: 0, label: "" }), 3000);
  };

  const handleUpdateDrugMaster = async (id, data) => {
    try {
      await fetch(`${API_BASE}/drugs/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      fetchDrugs();
    } catch (err) {
      alert("Error updating master drug record");
    }
  };


  const handleResyncDrug = async (id) => {
    setLoading(true);
    setSyncStatus({ active: true, current: 0, total: 1, label: "Re-scanning PubChem records..." });
    try {
      const res = await fetch(`${API_BASE}/drugs/${id}/resync`, { method: 'POST' });
      if (res.ok) {
        setSyncStatus(s => ({ ...s, current: 1, label: "Sync Complete" }));
        fetchDrugs();
      } else {
        alert("Failed to find additional data for this compound.");
      }
    } catch (err) {
      alert("Error during web scraping process");
    } finally {
      setLoading(false);
      setTimeout(() => setSyncStatus({ active: false, current: 0, total: 0, label: "" }), 2000);
    }
  };

  const handleSetView = (newView) => {
    // When changing view, clear selection and reset wizard to Step 1
    if (newView !== view) {
      setSelectedDrugIds([]);
      setWizardStep(1);
      setCurrentAnalysis(null);
      setAnalysisItems([]);
    }
    setView(newView);
  };

  if (!user) {
    return <LoginView apiBase={API_BASE} onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <>
      <Navbar syncStatus={syncStatus} user={user} onLogout={handleLogout} />
      <div className="app-container">
        <Sidebar activeView={view} setView={handleSetView} user={user} />
        
        {loading && <LoadingOverlay message={view === 'wizard' && wizardStep === 2 ? "Executing Regression Models..." : "Synchronizing Database..."} />}
        
        <main className="app-content">
          {view === 'library' && (
            <LibraryView 
              drugs={drugs} 
              syncStatus={syncStatus} 
              loadDefaults={loadDefaults} 
              handleAddDrug={handleAddDrug} 
              isStarting={isStarting}
              onUpdateDrug={handleUpdateDrugMaster}
              onResync={handleResyncDrug}
            />
          )}

          {view === 'wizard' && (
            <WizardView 
              wizardStep={wizardStep}
              setWizardStep={setWizardStep}
              drugs={drugs}
              selectedDrugIds={selectedDrugIds}
              setSelectedDrugIds={setSelectedDrugIds}
              startAnalysis={startAnalysis}
              analysisItems={analysisItems}
              handleOverwrite={handleOverwrite}
              runFinalAnalysis={runFinalAnalysis}
              currentAnalysis={currentAnalysis}
              setView={handleSetView}
              resetWizard={resetWizard}
            />
          )}

          {view === 'predictor' && (
            <PredictorView />
          )}
          
          {view === 'history' && (
            <HistoryView onViewAnalysis={viewAnalysis} user={user} />
          )}

          {view === 'docs' && (
            <DocumentationView />
          )}

          {view === 'users' && user.role === 'admin' && (
            <UserManagementView apiBase={API_BASE} />
          )}
        </main>
      </div>
    </>
  );
}

export default App;
