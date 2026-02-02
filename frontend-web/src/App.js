import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import Dashboard from './components/Dashboard';
import DatasetList from './components/DatasetList';
import FileUpload from './components/FileUpload';
import Navbar from './components/Navbar';
import Toast from './components/Toast';
import Visualizations from './components/Visualizations';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const [stats, setStats] = useState({
    totalDatasets: 0,
    totalRecords: 0,
    avgFlowrate: 0,
  });

  useEffect(() => {
    fetchDatasets();
    // Refresh every 30 seconds
    const interval = setInterval(fetchDatasets, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/datasets/`);

      // Handle both single object and array responses
      let datasetsArray = Array.isArray(response.data) ? response.data : [response.data];

      setDatasets(datasetsArray);

      // Calculate stats with better error handling
      if (datasetsArray && datasetsArray.length > 0) {
        let totalRecords = 0;
        let totalFlowrate = 0;
        let flowrateCount = 0;

        datasetsArray.forEach((dataset) => {
          // Sum total records
          totalRecords += (dataset.total_records || 0);

          // Calculate average flowrate
          try {
            // The API returns 'summary' field which is already parsed
            const summary = dataset.summary || {};
            if (summary.avg_flowrate !== undefined && summary.avg_flowrate !== null) {
              totalFlowrate += parseFloat(summary.avg_flowrate);
              flowrateCount++;
            }
          } catch (e) {
            console.warn('Could not get avg_flowrate for dataset:', dataset.id, e);
          }
        });

        const avgFlowrate = flowrateCount > 0 ? (totalFlowrate / flowrateCount).toFixed(2) : 0;

        setStats({
          totalDatasets: datasetsArray.length,
          totalRecords,
          avgFlowrate: parseFloat(avgFlowrate),
        });
      } else {
        // No datasets - reset stats to 0
        setStats({
          totalDatasets: 0,
          totalRecords: 0,
          avgFlowrate: 0,
        });
      }
    } catch (error) {
      console.error('Error fetching datasets:', error);
      showToast('Failed to fetch datasets', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (dataset) => {
    if (!dataset) return;

    setDatasets([dataset, ...datasets.slice(0, 4)]);
    showToast(`Dataset uploaded successfully with ${dataset.total_records} records!`, 'success');
    setActiveTab('datasets');

    // Refresh datasets list
    setTimeout(() => {
      fetchDatasets();
    }, 500);
  };

  const handleDeleteDataset = async (datasetId) => {
    if (window.confirm('Are you sure you want to delete this dataset?')) {
      try {
        await axios.delete(`${API_URL}/datasets/${datasetId}/`);
        setDatasets(datasets.filter(d => d.id !== datasetId));
        showToast('Dataset deleted successfully', 'success');
        fetchDatasets();
      } catch (error) {
        showToast('Failed to delete dataset', 'error');
      }
    }
  };

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content">
        {toast && <Toast message={toast.message} type={toast.type} />}

        {activeTab === 'dashboard' && (
          <Dashboard datasets={datasets} stats={stats} loading={loading} />
        )}

        {activeTab === 'upload' && (
          <FileUpload onUploadSuccess={handleUploadSuccess} />
        )}

        {activeTab === 'datasets' && (
          <DatasetList
            datasets={datasets}
            loading={loading}
            onDelete={handleDeleteDataset}
            onRefresh={fetchDatasets}
          />
        )}

        {activeTab === 'visualizations' && (
          <Visualizations datasets={datasets} />
        )}
      </main>
    </div>
  );
}

export default App;
