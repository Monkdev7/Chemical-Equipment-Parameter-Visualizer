import React from 'react';
import './Dashboard.css';

function Dashboard({ datasets, stats, loading }) {
  const getRecentActivity = () => {
    return datasets.slice(0, 5).map((d) => ({
      id: d.id,
      filename: d.filename,
      records: d.total_records,
      date: new Date(d.uploaded_at),
    }));
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>🎯 Dashboard</h1>
        <p>Chemical Equipment Parameter Analytics</p>
      </div>

      {loading ? (
        <p className="loading-text">⏳ Loading dashboard...</p>
      ) : (
        <>
          <div className="stats-cards">
            <div className="stat-card datasets">
              <div className="stat-icon">📊</div>
              <div className="stat-content">
                <h3>Total Datasets</h3>
                <p className="stat-number">{stats.totalDatasets}</p>
              </div>
            </div>

            <div className="stat-card records">
              <div className="stat-icon">📝</div>
              <div className="stat-content">
                <h3>Total Records</h3>
                <p className="stat-number">{stats.totalRecords}</p>
              </div>
            </div>

            <div className="stat-card flowrate">
              <div className="stat-icon">⚙️</div>
              <div className="stat-content">
                <h3>Avg Flowrate</h3>
                <p className="stat-number">{stats.avgFlowrate}</p>
              </div>
            </div>

            <div className="stat-card status">
              <div className="stat-icon">✅</div>
              <div className="stat-content">
                <h3>System Status</h3>
                <p className="stat-number">Active</p>
              </div>
            </div>
          </div>

          <div className="dashboard-content">
            <div className="section recent-activity">
              <h2>📈 Recent Uploads</h2>
              {getRecentActivity().length === 0 ? (
                <p className="empty-message">No datasets yet. Start by uploading a CSV file!</p>
              ) : (
                <div className="activity-list">
                  {getRecentActivity().map((activity) => (
                    <div key={activity.id} className="activity-item">
                      <div className="activity-info">
                        <h4>{activity.filename}</h4>
                        <p>{activity.date.toLocaleDateString()}</p>
                      </div>
                      <span className="activity-records">{activity.records} records</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="section quick-stats">
              <h2>📊 Quick Stats</h2>
              <div className="quick-stats-grid">
                <div className="quick-stat">
                  <span className="quick-label">Avg Records per Dataset</span>
                  <span className="quick-value">
                    {stats.totalDatasets > 0
                      ? (stats.totalRecords / stats.totalDatasets).toFixed(0)
                      : 0}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="dashboard-guide">
            <h2>🚀 Getting Started</h2>
            <div className="guide-steps">
              <div className="step">
                <span className="step-number">1</span>
                <h4>Prepare CSV File</h4>
                <p>Create a CSV with columns: Equipment Name, Type, Flowrate, Pressure, Temperature</p>
              </div>
              <div className="step">
                <span className="step-number">2</span>
                <h4>Upload Data</h4>
                <p>Click the "Upload" tab and drag-drop your CSV or select from your computer</p>
              </div>
              <div className="step">
                <span className="step-number">3</span>
                <h4>View & Analyze</h4>
                <p>Go to "Datasets" tab to view, search, and analyze your data</p>
              </div>
              <div className="step">
                <span className="step-number">4</span>
                <h4>Generate Reports</h4>
                <p>Click "PDF Report" to download professional analysis reports</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Dashboard;
