import React, { useState } from 'react';
import axios from 'axios';
import './DatasetList.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function DatasetList({ datasets, loading, onDelete, onRefresh }) {
  const [expandedId, setExpandedId] = useState(null);
  const [downloadingId, setDownloadingId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('date');

  const toggleExpand = (datasetId) => {
    setExpandedId(currentId => currentId === datasetId ? null : datasetId);
  };

  const handleDownloadPDF = async (datasetId, filename) => {
    try {
      setDownloadingId(datasetId);
      const response = await axios.get(
        `${API_URL}/datasets/${datasetId}/generate_pdf/`,
        { responseType: 'blob' }
      );

      // Verify we got a valid PDF
      if (response.data.size === 0) {
        throw new Error('PDF file is empty');
      }

      // Check for error responses
      if (response.status !== 200) {
        throw new Error(`Server error: ${response.status}`);
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${filename.split('.')[0]}_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentElement.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Failed to download PDF: ' + (error.message || 'Unknown error'));
    } finally {
      setDownloadingId(null);
    }
  };

  const filteredDatasets = datasets.filter(d =>
    d.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedDatasets = [...filteredDatasets].sort((a, b) => {
    if (sortBy === 'date') {
      return new Date(b.uploaded_at) - new Date(a.uploaded_at);
    } else if (sortBy === 'records') {
      return b.total_records - a.total_records;
    } else if (sortBy === 'name') {
      return a.filename.localeCompare(b.filename);
    }
    return 0;
  });

  return (
    <div className="dataset-list-container">
      <div className="list-header">
        <div className="list-title">
          <h2>📊 Datasets</h2>
          <p>Total: {datasets.length} datasets</p>
        </div>
        <div className="list-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search datasets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <span className="search-icon">🔍</span>
          </div>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="date">📅 Sort by Date</option>
            <option value="records">📈 Sort by Records</option>
            <option value="name">📝 Sort by Name</option>
          </select>
          <button className="refresh-btn" onClick={onRefresh} disabled={loading}>
            🔄 Refresh
          </button>
        </div>
      </div>

      {loading && <p className="loading-text">⏳ Loading datasets...</p>}

      {!loading && sortedDatasets.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h3>No datasets found</h3>
          <p>Upload a CSV file to get started</p>
        </div>
      ) : (
        <div className="datasets-grid">
          {sortedDatasets.map((dataset) => {
            const summary = dataset.summary || {};
            const isExpanded = expandedId === dataset.id;

            return (
              <div key={dataset.id} className={`dataset-card ${isExpanded ? 'expanded' : ''}`}>
                <div className="card-header" onClick={() => toggleExpand(dataset.id)}>
                  <div className="card-title">
                    <h3>{dataset.filename}</h3>
                    <span className="record-badge">{dataset.total_records} records</span>
                  </div>
                  <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                </div>

                <div className="card-date">
                  📅 {new Date(dataset.uploaded_at).toLocaleDateString()}
                  {' at '}
                  {new Date(dataset.uploaded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>

                {isExpanded && (
                  <div className="card-details">
                    <div className="stats-grid">
                      <div className="stat-box">
                        <div className="stat-label">Avg Flowrate</div>
                        <div className="stat-value">{summary.avg_flowrate?.toFixed(2) || 'N/A'}</div>
                      </div>
                      <div className="stat-box">
                        <div className="stat-label">Avg Pressure</div>
                        <div className="stat-value">{summary.avg_pressure?.toFixed(2) || 'N/A'}</div>
                      </div>
                      <div className="stat-box">
                        <div className="stat-label">Avg Temp</div>
                        <div className="stat-value">{summary.avg_temperature?.toFixed(2) || 'N/A'}°</div>
                      </div>
                      <div className="stat-box">
                        <div className="stat-label">Equipment Types</div>
                        <div className="stat-value">{Object.keys(summary.type_distribution || {}).length}</div>
                      </div>
                    </div>

                    {summary.type_distribution && Object.keys(summary.type_distribution).length > 0 && (
                      <div className="type-distribution">
                        <h4>Equipment Types</h4>
                        <div className="types-list">
                          {Object.entries(summary.type_distribution).map(([type, count]) => (
                            <div key={type} className="type-item">
                              <span className="type-name">{type}</span>
                              <div className="type-bar">
                                <div
                                  className="type-fill"
                                  style={{
                                    width: `${(count / dataset.total_records) * 100}%`
                                  }}
                                ></div>
                              </div>
                              <span className="type-count">{count}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <div className="card-actions">
                  <button
                    className={`pdf-btn ${downloadingId === dataset.id ? 'downloading' : ''}`}
                    onClick={() => handleDownloadPDF(dataset.id, dataset.filename)}
                    disabled={downloadingId === dataset.id}
                  >
                    {downloadingId === dataset.id ? '⏳ Generating...' : '📄 PDF Report'}
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => onDelete(dataset.id)}
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default DatasetList;
