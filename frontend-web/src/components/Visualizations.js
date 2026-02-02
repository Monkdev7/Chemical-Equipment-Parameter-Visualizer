import { useState } from 'react';
import { Bar, Pie, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import './Visualizations.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

function Visualizations({ datasets }) {
  const [selectedDatasetId, setSelectedDatasetId] = useState(
    datasets.length > 0 ? datasets[0].id : null
  );
  const [chartType, setChartType] = useState('equipment-distribution');

  const selectedDataset = datasets.find(d => d.id === selectedDatasetId);
  const summary = selectedDataset?.summary || {};

  const generateEquipmentDistributionChart = () => {
    const typeDistribution = summary.type_distribution || {};
    const labels = Object.keys(typeDistribution);
    const data = Object.values(typeDistribution);

    return {
      labels,
      datasets: [
        {
          label: 'Equipment Count',
          data,
          backgroundColor: [
            '#3b82f6',
            '#ef4444',
            '#10b981',
            '#f59e0b',
            '#8b5cf6',
            '#ec4899',
            '#14b8a6',
            '#f97316',
          ],
          borderColor: '#fff',
          borderWidth: 2,
        },
      ],
    };
  };

  const generateParameterComparisonChart = () => {
    const typeDistribution = summary.type_distribution || {};
    const labels = Object.keys(typeDistribution);

    return {
      labels,
      datasets: [
        {
          label: 'Avg Flowrate',
          data: labels.map(() => summary.avg_flowrate || 0),
          backgroundColor: '#3b82f6',
          borderColor: '#1e40af',
          borderWidth: 2,
        },
        {
          label: 'Avg Pressure',
          data: labels.map(() => summary.avg_pressure || 0),
          backgroundColor: '#ef4444',
          borderColor: '#991b1b',
          borderWidth: 2,
        },
        {
          label: 'Avg Temperature',
          data: labels.map(() => summary.avg_temperature || 0),
          backgroundColor: '#f59e0b',
          borderColor: '#b45309',
          borderWidth: 2,
        },
      ],
    };
  };

  const generateParameterTrendChart = () => {
    return {
      labels: ['Flowrate', 'Pressure', 'Temperature'],
      datasets: [
        {
          label: 'Average Values',
          data: [
            summary.avg_flowrate || 0,
            summary.avg_pressure || 0,
            summary.avg_temperature || 0,
          ],
          fill: true,
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderColor: '#3b82f6',
          borderWidth: 3,
          pointBackgroundColor: '#3b82f6',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 6,
          tension: 0.4,
        },
      ],
    };
  };

  const generateEquipmentTypePercentageChart = () => {
    const typeDistribution = summary.type_distribution || {};
    const labels = Object.keys(typeDistribution);
    const data = Object.values(typeDistribution);

    return {
      labels: labels.map((label, idx) => `${label} (${data[idx]})`),
      datasets: [
        {
          data,
          backgroundColor: [
            '#3b82f6',
            '#ef4444',
            '#10b981',
            '#f59e0b',
            '#8b5cf6',
            '#ec4899',
            '#14b8a6',
            '#f97316',
          ],
          borderColor: '#fff',
          borderWidth: 2,
        },
      ],
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          font: { size: 12 },
          padding: 15,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: { size: 13 },
        bodyFont: { size: 12 },
      },
    },
  };

  const barChartOptions = {
    ...chartOptions,
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(0, 0, 0, 0.1)' },
      },
      x: {
        grid: { display: false },
      },
    },
  };

  const lineChartOptions = {
    ...chartOptions,
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(0, 0, 0, 0.1)' },
      },
      x: {
        grid: { display: false },
      },
    },
  };

  const pieChartOptions = {
    ...chartOptions,
    plugins: {
      ...chartOptions.plugins,
      legend: {
        position: 'right',
        labels: { font: { size: 12 }, padding: 15 },
      },
    },
  };

  if (datasets.length === 0) {
    return (
      <div className="visualizations-container">
        <div className="empty-state">
          <div className="empty-icon">📈</div>
          <h3>No Data to Visualize</h3>
          <p>Upload a dataset first to see visualizations</p>
        </div>
      </div>
    );
  }

  return (
    <div className="visualizations-container">
      <div className="viz-header">
        <h1>📊 Visualizations</h1>
        <p>Equipment Parameter Analysis & Statistics</p>
      </div>

      <div className="viz-controls">
        <div className="dataset-selector">
          <label>Select Dataset:</label>
          <select
            value={selectedDatasetId}
            onChange={(e) => setSelectedDatasetId(Number(e.target.value))}
            className="dataset-select"
          >
            {datasets.map(d => (
              <option key={d.id} value={d.id}>
                {d.filename} ({d.total_records} records)
              </option>
            ))}
          </select>
        </div>

        <div className="chart-selector">
          <label>Chart Type:</label>
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value)}
            className="chart-select"
          >
            <option value="equipment-distribution">Equipment Distribution (Bar)</option>
            <option value="equipment-pie">Equipment Distribution (Pie)</option>
            <option value="parameter-comparison">Parameter Comparison</option>
            <option value="parameter-trend">Parameter Trend</option>
          </select>
        </div>
      </div>

      {selectedDataset && (
        <div className="viz-info-bar">
          <div className="info-item">
            <span className="info-label">Total Records:</span>
            <span className="info-value">{selectedDataset.total_records}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Avg Flowrate:</span>
            <span className="info-value">{summary.avg_flowrate?.toFixed(2) || 'N/A'}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Avg Pressure:</span>
            <span className="info-value">{summary.avg_pressure?.toFixed(2) || 'N/A'}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Avg Temperature:</span>
            <span className="info-value">{summary.avg_temperature?.toFixed(2) || 'N/A'}°</span>
          </div>
        </div>
      )}

      <div className="chart-container">
        {chartType === 'equipment-distribution' && (
          <div className="chart-wrapper">
            <h2>Equipment Distribution (Bar Chart)</h2>
            <Bar data={generateEquipmentDistributionChart()} options={barChartOptions} />
          </div>
        )}

        {chartType === 'equipment-pie' && (
          <div className="chart-wrapper">
            <h2>Equipment Distribution (Pie Chart)</h2>
            <Pie data={generateEquipmentTypePercentageChart()} options={pieChartOptions} />
          </div>
        )}

        {chartType === 'parameter-comparison' && (
          <div className="chart-wrapper">
            <h2>Parameter Comparison by Equipment Type</h2>
            <Bar data={generateParameterComparisonChart()} options={barChartOptions} />
          </div>
        )}

        {chartType === 'parameter-trend' && (
          <div className="chart-wrapper">
            <h2>Parameter Trend Analysis</h2>
            <Line data={generateParameterTrendChart()} options={lineChartOptions} />
          </div>
        )}
      </div>

      {summary.type_distribution && Object.keys(summary.type_distribution).length > 0 && (
        <div className="stats-summary">
          <h3>Equipment Type Breakdown</h3>
          <div className="type-stats">
            {Object.entries(summary.type_distribution).map(([type, count]) => {
              const percentage = ((count / selectedDataset.total_records) * 100).toFixed(1);
              return (
                <div key={type} className="type-stat">
                  <div className="type-stat-header">
                    <span className="type-name">{type}</span>
                    <span className="type-percentage">{percentage}%</span>
                  </div>
                  <div className="type-stat-bar">
                    <div
                      className="type-stat-fill"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <div className="type-stat-count">{count} items</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default Visualizations;
