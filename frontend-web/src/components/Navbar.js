import React from 'react';
import './Navbar.css';

function Navbar({ activeTab, setActiveTab }) {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <h1 className="brand-title">
            🧪 <span>ChemFlow</span>
          </h1>
          <p className="brand-subtitle">Analytics Platform</p>
        </div>

        <div className="navbar-menu">
          <button
            className={`nav-button ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <span className="nav-icon">🎯</span>
            <span className="nav-label">Dashboard</span>
          </button>
          <button
            className={`nav-button ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            <span className="nav-icon">📤</span>
            <span className="nav-label">Upload</span>
          </button>
          <button
            className={`nav-button ${activeTab === 'visualizations' ? 'active' : ''}`}
            onClick={() => setActiveTab('visualizations')}
          >
            <span className="nav-icon">📈</span>
            <span className="nav-label">Visualizations</span>
          </button>
          <button
            className={`nav-button ${activeTab === 'datasets' ? 'active' : ''}`}
            onClick={() => setActiveTab('datasets')}
          >
            <span className="nav-icon">📊</span>
            <span className="nav-label">Datasets</span>
          </button>
        </div>

        <div className="navbar-info">
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
