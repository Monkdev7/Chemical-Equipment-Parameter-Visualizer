import { useState, useRef } from 'react';
import axios from 'axios';
import './FileUpload.css';

const API_URL = process.env.REACT_APP_API_URL || 'https://chemical-equipment-parameter-visualizer-u33b.onrender.com/api';

function FileUpload({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = (file) => {
    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
      alert('Please select a CSV file');
      return;
    }
    setSelectedFile(file);
  };

  const handleFileInput = (e) => {
    if (e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      setUploading(true);
      setUploadProgress(0);

      const response = await axios.post(
        `${API_URL}/datasets/upload/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percent);
          },
        }
      );

      // Handle successful upload
      if (response.data && response.data.success) {
        onUploadSuccess(response.data.data);
        setSelectedFile(null);
        setUploadProgress(0);
        fileInputRef.current.value = '';
      } else {
        // Unexpected response format
        console.error('Unexpected response format:', response.data);
        alert('Upload completed but received unexpected response format');
      }
    } catch (error) {
      console.error('Upload error:', error);

      // Extract error message from different error sources
      let errorMessage = 'Failed to upload file';

      if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }

      alert(errorMessage);

      // Reset form on error
      setSelectedFile(null);
      setUploadProgress(0);
      fileInputRef.current.value = '';
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-card">
        <div className="upload-header">
          <h2>📤 Upload CSV File</h2>
          <p>Import your chemical equipment data</p>
        </div>

        <div
          className={`drag-drop-zone ${isDragging ? 'dragging' : ''} ${selectedFile ? 'file-selected' : ''
            }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {selectedFile ? (
            <div className="file-selected-content">
              <div className="file-icon">✓</div>
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">
                {(selectedFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
          ) : (
            <div className="drag-drop-content">
              <div className="drag-icon">📁</div>
              <p className="drag-title">Drag and drop your CSV file here</p>
              <p className="drag-subtitle">or click to browse</p>
            </div>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileInput}
            style={{ display: 'none' }}
          />
        </div>

        <button
          className="browse-btn"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          📂 Browse Files
        </button>

        {uploading && (
          <div className="upload-progress">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
            </div>
            <p className="progress-text">{uploadProgress}% Uploading...</p>
          </div>
        )}

        <button
          className={`upload-btn ${uploading ? 'uploading' : ''}`}
          onClick={handleUpload}
          disabled={!selectedFile || uploading}
        >
          {uploading ? '⏳ Uploading...' : '🚀 Upload'}
        </button>

        <div className="upload-info">
          <h3>📋 Required CSV Format</h3>
          <table className="format-table">
            <thead>
              <tr>
                <th>Column Name</th>
                <th>Type</th>
                <th>Example</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Equipment Name</td>
                <td>Text</td>
                <td>Pump A</td>
              </tr>
              <tr>
                <td>Type</td>
                <td>Text</td>
                <td>Pump</td>
              </tr>
              <tr>
                <td>Flowrate</td>
                <td>Number</td>
                <td>12.5</td>
              </tr>
              <tr>
                <td>Pressure</td>
                <td>Number</td>
                <td>100.5</td>
              </tr>
              <tr>
                <td>Temperature</td>
                <td>Number</td>
                <td>75.2</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="upload-tips">
          <h3>💡 Tips</h3>
          <ul>
            <li>File size limit: 50 MB</li>
            <li>Only CSV format is supported</li>
            <li>First row should contain column headers</li>
            <li>All numeric columns must contain valid numbers</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default FileUpload;
