"""
Chemical Equipment Parameter Visualizer - Desktop Application
Enhanced version with improved error handling, validation, and features
Author: Enhanced by Claude
Version: 2.0
"""

import sys
import os
import logging
from typing import Optional, Dict, List, Any
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem, 
    QTabWidget, QMessageBox, QProgressBar, QComboBox, QGroupBox,
    QGridLayout, QHeaderView, QTextEdit, QSplitter, QLineEdit,
    QCheckBox, QDialog, QDialogButtonBox, QSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import requests
import json
from datetime import datetime
import csv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chemical_equipment_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_API_BASE_URL = 'http://localhost:8000/api'
API_TIMEOUT = 30
MAX_FILE_SIZE_MB = 50
REQUIRED_COLUMNS = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
APP_VERSION = '2.0'


class Config:
    """Application configuration management"""
    
    def __init__(self):
        self.settings = QSettings('ChemicalEquipment', 'Visualizer')
        
    def get_api_url(self) -> str:
        return self.settings.value('api_url', DEFAULT_API_BASE_URL)
    
    def set_api_url(self, url: str):
        self.settings.setValue('api_url', url)
    
    def get_api_timeout(self) -> int:
        return self.settings.value('api_timeout', API_TIMEOUT, type=int)
    
    def set_api_timeout(self, timeout: int):
        self.settings.setValue('api_timeout', timeout)


class SettingsDialog(QDialog):
    """Settings dialog for application configuration"""
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Settings')
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # API URL
        api_group = QGroupBox('API Configuration')
        api_layout = QVBoxLayout()
        
        api_layout.addWidget(QLabel('API Base URL:'))
        self.api_url_input = QLineEdit(self.config.get_api_url())
        api_layout.addWidget(self.api_url_input)
        
        api_layout.addWidget(QLabel('API Timeout (seconds):'))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 120)
        self.timeout_spin.setValue(self.config.get_api_timeout())
        api_layout.addWidget(self.timeout_spin)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def save_settings(self):
        self.config.set_api_url(self.api_url_input.text())
        self.config.set_api_timeout(self.timeout_spin.value())
        self.accept()


class UploadThread(QThread):
    """Background thread for file upload with improved error handling"""
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, file_path: str, api_url: str, timeout: int):
        super().__init__()
        self.file_path = file_path
        self.api_url = api_url
        self.timeout = timeout
    
    def run(self):
        try:
            logger.info(f'Starting upload of file: {self.file_path}')
            self.progress.emit(10)
            
            # Validate file before upload
            if not self._validate_csv():
                self.error.emit('Invalid CSV format. Please check required columns.')
                return
            
            self.progress.emit(30)
            
            with open(self.file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f'{self.api_url}/datasets/upload/',
                    files=files,
                    timeout=self.timeout
                )
            
            self.progress.emit(70)
            
            if response.status_code == 201:
                data = response.json()
                self.progress.emit(100)
                logger.info(f'Upload successful: {data.get("id")}')
                self.finished.emit(data)
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                error_msg = error_data.get('error', f'Upload failed with status {response.status_code}')
                logger.error(f'Upload failed: {error_msg}')
                self.error.emit(error_msg)
                
        except requests.exceptions.ConnectionError:
            error_msg = f'Cannot connect to server at {self.api_url}'
            logger.error(error_msg)
            self.error.emit(error_msg)
        except requests.exceptions.Timeout:
            error_msg = 'Request timed out. Please try again.'
            logger.error(error_msg)
            self.error.emit(error_msg)
        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
    
    def _validate_csv(self) -> bool:
        """Validate CSV file structure"""
        try:
            with open(self.file_path, 'r') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                if not headers:
                    return False
                
                # Check for required columns
                for required in REQUIRED_COLUMNS:
                    if required not in headers:
                        logger.error(f'Missing required column: {required}')
                        return False
                
                # Validate at least one row exists
                first_row = next(reader, None)
                if not first_row:
                    logger.error('CSV file is empty')
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f'CSV validation error: {e}')
            return False


class MatplotlibWidget(QWidget):
    """Enhanced widget to embed matplotlib figures with better styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Set matplotlib style
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def plot_bar_chart(self, data_dict: Dict, title: str, xlabel: str, ylabel: str):
        """Create an enhanced bar chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not data_dict:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=14, transform=ax.transAxes)
            ax.axis('off')
            self.canvas.draw()
            return
        
        keys = list(data_dict.keys())
        values = list(data_dict.values())
        
        colors = plt.cm.viridis(range(len(keys)))
        bars = ax.bar(keys, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_multi_bar_chart(self, summary: Dict, title: str):
        """Create enhanced grouped bar chart for parameter comparison"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not summary:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=14, transform=ax.transAxes)
            ax.axis('off')
            self.canvas.draw()
            return
        
        parameters = ['Flowrate', 'Pressure', 'Temperature']
        min_values = [
            summary.get('min_flowrate', 0),
            summary.get('min_pressure', 0),
            summary.get('min_temperature', 0)
        ]
        avg_values = [
            summary.get('avg_flowrate', 0),
            summary.get('avg_pressure', 0),
            summary.get('avg_temperature', 0)
        ]
        max_values = [
            summary.get('max_flowrate', 0),
            summary.get('max_pressure', 0),
            summary.get('max_temperature', 0)
        ]
        
        x = range(len(parameters))
        width = 0.25
        
        ax.bar([i - width for i in x], min_values, width, label='Min', 
               color='#EF4444', alpha=0.8, edgecolor='black')
        ax.bar(x, avg_values, width, label='Average', 
               color='#3B82F6', alpha=0.8, edgecolor='black')
        ax.bar([i + width for i in x], max_values, width, label='Max', 
               color='#10B981', alpha=0.8, edgecolor='black')
        
        ax.set_xlabel('Parameters', fontsize=12, fontweight='bold')
        ax.set_ylabel('Values', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(parameters)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_pie_chart(self, data_dict: Dict, title: str):
        """Create an enhanced pie chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not data_dict:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=14, transform=ax.transAxes)
            ax.axis('off')
            self.canvas.draw()
            return
        
        keys = list(data_dict.keys())
        values = list(data_dict.values())
        
        colors = plt.cm.Set3(range(len(keys)))
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=keys, 
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 10},
            explode=[0.05] * len(keys)  # Slight separation
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Style percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)
        
        self.figure.tight_layout()
        self.canvas.draw()


class ChemicalEquipmentApp(QMainWindow):
    """Enhanced main application window with improved features and error handling"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.current_dataset: Optional[Dict] = None
        self.datasets_list: List[Dict] = []
        self.selected_file_path: Optional[str] = None
        
        self.init_ui()
        self.load_datasets()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh_datasets)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        """Initialize the enhanced user interface"""
        self.setWindowTitle(f'Chemical Equipment Parameter Visualizer v{APP_VERSION}')
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont('Arial', 10))
        self.tabs.setDocumentMode(True)
        
        # Tab 1: Upload
        self.upload_tab = self.create_upload_tab()
        self.tabs.addTab(self.upload_tab, '📤 Upload CSV')
        
        # Tab 2: Dashboard
        self.dashboard_tab = self.create_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, '📊 Dashboard')
        
        # Tab 3: Visualizations
        self.viz_tab = self.create_visualization_tab()
        self.tabs.addTab(self.viz_tab, '📈 Visualizations')
        
        # Tab 4: Data Table
        self.table_tab = self.create_table_tab()
        self.tabs.addTab(self.table_tab, '📋 Data Table')
        
        # Tab 5: History
        self.history_tab = self.create_history_tab()
        self.tabs.addTab(self.history_tab, '🕐 History')
        
        # Connect tab change event to update data table when switched to
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        main_layout.addWidget(self.tabs)
        
        # Enhanced status bar
        self.statusBar().showMessage('Ready | Connected to API')
        
        # Add keyboard shortcuts
        self.setup_shortcuts()
    
    def on_tab_changed(self, index):
        """Handle tab change event"""
        # Update data table when switching to Data Table tab (index 3)
        if index == 3:
            logger.info('Switched to Data Table tab, refreshing table')
            self.update_table()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        # Ctrl+O: Open file
        open_shortcut = QShortcut(QKeySequence('Ctrl+O'), self)
        open_shortcut.activated.connect(self.select_file)
        
        # Ctrl+R: Refresh
        refresh_shortcut = QShortcut(QKeySequence('Ctrl+R'), self)
        refresh_shortcut.activated.connect(self.load_datasets)
        
        # Ctrl+S: Settings
        settings_shortcut = QShortcut(QKeySequence('Ctrl+,'), self)
        settings_shortcut.activated.connect(self.open_settings)
        
        # F5: Refresh
        f5_shortcut = QShortcut(QKeySequence('F5'), self)
        f5_shortcut.activated.connect(self.load_datasets)
    
    def create_header(self):
        """Create enhanced application header"""
        header = QWidget()
        header.setStyleSheet('''
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1E40AF, stop:1 #3B82F6);
            padding: 15px;
            border-radius: 8px;
        ''')
        layout = QHBoxLayout(header)
        
        # Left side: Title
        title_layout = QVBoxLayout()
        title = QLabel('Chemical Equipment Parameter Visualizer')
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setStyleSheet('color: white;')
        
        subtitle = QLabel(f'Desktop Application v{APP_VERSION} - PyQt5 + Matplotlib')
        subtitle.setFont(QFont('Arial', 11))
        subtitle.setStyleSheet('color: #BFDBFE;')
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        layout.addLayout(title_layout)
        
        layout.addStretch()
        
        # Right side: Settings button
        settings_btn = QPushButton('⚙️ Settings')
        settings_btn.setFont(QFont('Arial', 10, QFont.Bold))
        settings_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                border: 2px solid white;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        ''')
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)
        
        return header
    
    def create_upload_tab(self):
        """Create enhanced upload tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignCenter)
        
        # Upload group box
        upload_group = QGroupBox('Upload CSV File')
        upload_group.setFont(QFont('Arial', 12, QFont.Bold))
        upload_layout = QVBoxLayout(upload_group)
        
        # Info label with better formatting
        info_label = QLabel(
            '<b>Required CSV Format:</b><br><br>'
            '• <b>Equipment Name</b> - Name of the equipment<br>'
            '• <b>Type</b> - Equipment type/category<br>'
            '• <b>Flowrate</b> - Flow rate value (numeric)<br>'
            '• <b>Pressure</b> - Pressure value (numeric)<br>'
            '• <b>Temperature</b> - Temperature value (numeric)<br><br>'
            f'<i>Maximum file size: {MAX_FILE_SIZE_MB}MB</i>'
        )
        info_label.setFont(QFont('Arial', 10))
        info_label.setStyleSheet('''
            padding: 15px;
            background-color: #DBEAFE;
            border-radius: 8px;
            border-left: 4px solid #3B82F6;
        ''')
        info_label.setWordWrap(True)
        upload_layout.addWidget(info_label)
        
        # Select file button
        self.select_file_btn = QPushButton('📁 Select CSV File')
        self.select_file_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.select_file_btn.setStyleSheet('''
            QPushButton {
                background-color: #3B82F6;
                color: white;
                padding: 15px;
                border-radius: 8px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        ''')
        self.select_file_btn.clicked.connect(self.select_file)
        upload_layout.addWidget(self.select_file_btn, alignment=Qt.AlignCenter)
        
        # Selected file label
        self.selected_file_label = QLabel('No file selected')
        self.selected_file_label.setFont(QFont('Arial', 10))
        self.selected_file_label.setAlignment(Qt.AlignCenter)
        self.selected_file_label.setStyleSheet('color: #6B7280; padding: 5px;')
        upload_layout.addWidget(self.selected_file_label)
        
        # Upload button
        self.upload_btn = QPushButton('⬆️ Upload and Process')
        self.upload_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.upload_btn.setStyleSheet('''
            QPushButton {
                background-color: #10B981;
                color: white;
                padding: 15px;
                border-radius: 8px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:disabled {
                background-color: #9CA3AF;
            }
        ''')
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self.upload_file)
        upload_layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                border: 2px solid #3B82F6;
                border-radius: 8px;
                text-align: center;
                height: 25px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 6px;
            }
        ''')
        upload_layout.addWidget(self.progress_bar)
        
        # Status message label
        self.upload_status_label = QLabel()
        self.upload_status_label.setVisible(False)
        self.upload_status_label.setFont(QFont('Arial', 10))
        self.upload_status_label.setAlignment(Qt.AlignCenter)
        self.upload_status_label.setWordWrap(True)
        upload_layout.addWidget(self.upload_status_label)
        
        layout.addWidget(upload_group)
        layout.addStretch()
        
        return tab
    
    def create_dashboard_tab(self):
        """Create enhanced dashboard tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Dataset info
        self.dataset_info_label = QLabel('No dataset loaded')
        self.dataset_info_label.setFont(QFont('Arial', 11, QFont.Bold))
        self.dataset_info_label.setStyleSheet('''
            padding: 12px;
            background-color: #DBEAFE;
            border-radius: 8px;
            color: #1E40AF;
            border-left: 4px solid #3B82F6;
        ''')
        layout.addWidget(self.dataset_info_label)
        
        # Summary statistics grid
        summary_group = QGroupBox('Summary Statistics')
        summary_group.setFont(QFont('Arial', 11, QFont.Bold))
        summary_layout = QGridLayout(summary_group)
        
        # Create stat cards
        self.stat_cards = {}
        stat_items = [
            ('total_count', 'Total Records', '#3B82F6', '📊'),
            ('avg_flowrate', 'Avg Flowrate', '#10B981', '💧'),
            ('avg_pressure', 'Avg Pressure', '#8B5CF6', '⚡'),
            ('avg_temperature', 'Avg Temperature', '#EF4444', '🌡️'),
        ]
        
        for i, (key, label, color, icon) in enumerate(stat_items):
            card = self.create_stat_card(label, '0', color, icon)
            self.stat_cards[key] = card
            row = i // 2
            col = i % 2
            summary_layout.addWidget(card, row, col)
        
        layout.addWidget(summary_group)
        
        # Parameter ranges
        ranges_group = QGroupBox('Parameter Ranges')
        ranges_group.setFont(QFont('Arial', 11, QFont.Bold))
        ranges_layout = QVBoxLayout(ranges_group)
        
        self.ranges_text = QTextEdit()
        self.ranges_text.setReadOnly(True)
        self.ranges_text.setFont(QFont('Courier', 10))
        self.ranges_text.setMinimumHeight(250)
        self.ranges_text.setStyleSheet('''
            QTextEdit {
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: 5px;
                padding: 10px;
            }
        ''')
        ranges_layout.addWidget(self.ranges_text)
        
        layout.addWidget(ranges_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        # Download PDF button
        self.download_pdf_btn = QPushButton('📥 Download PDF Report')
        self.download_pdf_btn.setFont(QFont('Arial', 11, QFont.Bold))
        self.download_pdf_btn.setStyleSheet('''
            QPushButton {
                background-color: #DC2626;
                color: white;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #B91C1C;
            }
            QPushButton:disabled {
                background-color: #9CA3AF;
            }
        ''')
        self.download_pdf_btn.setEnabled(False)
        self.download_pdf_btn.clicked.connect(self.download_pdf)
        button_layout.addWidget(self.download_pdf_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return tab
    
    def create_visualization_tab(self):
        """Create enhanced visualization tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Chart type selector with better styling
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel('Select Chart Type:'))
        
        self.chart_selector = QComboBox()
        self.chart_selector.setFont(QFont('Arial', 10))
        self.chart_selector.addItems([
            'Equipment Type Distribution (Bar)',
            'Equipment Type Distribution (Pie)',
            'Parameter Comparison (Multi-Bar)'
        ])
        self.chart_selector.setStyleSheet('''
            QComboBox {
                padding: 5px;
                border: 2px solid #3B82F6;
                border-radius: 5px;
                min-width: 300px;
            }
        ''')
        self.chart_selector.currentIndexChanged.connect(self.update_chart)
        selector_layout.addWidget(self.chart_selector)
        selector_layout.addStretch()
        
        # Save chart button
        save_chart_btn = QPushButton('💾 Save Chart')
        save_chart_btn.setFont(QFont('Arial', 10, QFont.Bold))
        save_chart_btn.setStyleSheet('''
            QPushButton {
                background-color: #8B5CF6;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7C3AED;
            }
        ''')
        save_chart_btn.clicked.connect(self.save_chart)
        selector_layout.addWidget(save_chart_btn)
        
        layout.addLayout(selector_layout)
        
        # Matplotlib widget
        self.chart_widget = MatplotlibWidget()
        layout.addWidget(self.chart_widget)
        
        return tab
    
    def create_table_tab(self):
        """Create enhanced data table tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Table controls
        controls_layout = QHBoxLayout()
        
        # Table info
        self.table_info_label = QLabel('Equipment Records (0 total)')
        self.table_info_label.setFont(QFont('Arial', 11, QFont.Bold))
        controls_layout.addWidget(self.table_info_label)
        
        controls_layout.addStretch()
        
        # Search box
        search_label = QLabel('Search:')
        controls_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Filter records...')
        self.search_box.setMaximumWidth(200)
        self.search_box.textChanged.connect(self.filter_table)
        controls_layout.addWidget(self.search_box)
        
        layout.addLayout(controls_layout)
        
        # Table widget
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels([
            'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'
        ])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSortingEnabled(True)
        self.data_table.setStyleSheet('''
            QTableWidget {
                gridline-color: #D1D5DB;
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #3B82F6;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
            }
        ''')
        
        layout.addWidget(self.data_table)
        
        return tab
    
    def create_history_tab(self):
        """Create enhanced history tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton('🔄 Refresh History')
        refresh_btn.setFont(QFont('Arial', 10, QFont.Bold))
        refresh_btn.clicked.connect(self.load_datasets)
        refresh_btn.setStyleSheet('''
            QPushButton {
                background-color: #3B82F6;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        ''')
        controls_layout.addWidget(refresh_btn)
        
        # Delete all button
        delete_all_btn = QPushButton('🗑️ Delete All')
        delete_all_btn.setFont(QFont('Arial', 10, QFont.Bold))
        delete_all_btn.clicked.connect(self.delete_all_datasets)
        delete_all_btn.setStyleSheet('''
            QPushButton {
                background-color: #EF4444;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        ''')
        controls_layout.addWidget(delete_all_btn)
        
        controls_layout.addStretch()
        
        # Auto-refresh checkbox
        self.auto_refresh_checkbox = QCheckBox('Auto-refresh every 30s')
        self.auto_refresh_checkbox.setChecked(True)
        self.auto_refresh_checkbox.stateChanged.connect(self.toggle_auto_refresh)
        controls_layout.addWidget(self.auto_refresh_checkbox)
        
        layout.addLayout(controls_layout)
        
        # History list
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            'Filename', 'Upload Date', 'Records', 'Actions'
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setRowHeight(0, 45)
        self.history_table.setStyleSheet('''
            QTableWidget {
                gridline-color: #D1D5DB;
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #8B5CF6;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        ''')
        
        layout.addWidget(self.history_table)
        
        return tab
    
    def create_stat_card(self, title: str, value: str, color: str, icon: str = ''):
        """Create an enhanced statistics card widget"""
        card = QGroupBox()
        card.setStyleSheet(f'''
            QGroupBox {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 {self.adjust_color(color, -20)});
                border-radius: 10px;
                padding: 20px;
                color: white;
                border: none;
            }}
        ''')
        
        layout = QVBoxLayout(card)
        
        # Icon and title
        header_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont('Arial', 20))
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', 11, QFont.Bold))
        title_label.setStyleSheet('color: rgba(255, 255, 255, 0.95);')
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setFont(QFont('Arial', 28, QFont.Bold))
        value_label.setStyleSheet('color: white; margin-top: 10px;')
        value_label.setObjectName('value_label')
        
        layout.addWidget(value_label)
        
        return card
    
    def adjust_color(self, hex_color: str, adjustment: int) -> str:
        """Adjust color brightness"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
        r = max(0, min(255, r + adjustment))
        g = max(0, min(255, g + adjustment))
        b = max(0, min(255, b + adjustment))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec_():
            QMessageBox.information(
                self,
                'Settings Saved',
                'Settings have been saved successfully.'
            )
    
    def select_file(self):
        """Open file dialog to select CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select CSV File',
            str(Path.home()),
            'CSV Files (*.csv);;All Files (*)'
        )
        
        if file_path:
            # Check file size
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            if file_size > MAX_FILE_SIZE_MB:
                QMessageBox.warning(
                    self,
                    'File Too Large',
                    f'The selected file is {file_size:.1f}MB.\n'
                    f'Maximum allowed size is {MAX_FILE_SIZE_MB}MB.'
                )
                return
            
            self.selected_file_path = file_path
            self.selected_file_label.setText(f'✓ Selected: {os.path.basename(file_path)}')
            self.selected_file_label.setStyleSheet('color: #10B981; padding: 5px; font-weight: bold;')
            self.upload_btn.setEnabled(True)
            self.statusBar().showMessage(f'File selected: {os.path.basename(file_path)}')
            logger.info(f'File selected: {file_path}')
    
    def upload_file(self):
        """Upload CSV file to backend"""
        if not self.selected_file_path:
            return
        
        self.upload_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.upload_status_label.setVisible(False)
        self.statusBar().showMessage('Uploading file...')
        
        # Create and start upload thread
        api_url = self.config.get_api_url()
        timeout = self.config.get_api_timeout()
        
        self.upload_thread = UploadThread(self.selected_file_path, api_url, timeout)
        self.upload_thread.finished.connect(self.on_upload_success)
        self.upload_thread.error.connect(self.on_upload_error)
        self.upload_thread.progress.connect(self.progress_bar.setValue)
        self.upload_thread.start()
    
    def on_upload_success(self, data: Dict):
        """Handle successful upload"""
        self.progress_bar.setVisible(False)
        self.upload_btn.setEnabled(True)
        
        # Show success message
        self.upload_status_label.setText('✓ File uploaded and processed successfully!')
        self.upload_status_label.setStyleSheet('''
            padding: 12px;
            border-radius: 8px;
            margin-top: 10px;
            background-color: #DCFCE7;
            border: 2px solid #22C55E;
            color: #166534;
            font-weight: bold;
        ''')
        self.upload_status_label.setVisible(True)
        
        self.current_dataset = data
        self.load_datasets()
        self.update_dashboard()
        self.update_table()
        self.update_chart()
        self.tabs.setCurrentIndex(1)  # Switch to dashboard
        
        self.statusBar().showMessage('✓ Upload completed successfully')
        logger.info('Upload completed successfully')
        
        # Auto-hide success message after 5 seconds
        QTimer.singleShot(5000, lambda: self.upload_status_label.setVisible(False))
    
    def on_upload_error(self, error_msg: str):
        """Handle upload error"""
        self.progress_bar.setVisible(False)
        self.upload_btn.setEnabled(True)
        
        # Show error message
        self.upload_status_label.setText(f'✗ Error: {error_msg}')
        self.upload_status_label.setStyleSheet('''
            padding: 12px;
            border-radius: 8px;
            margin-top: 10px;
            background-color: #FEE2E2;
            border: 2px solid #EF4444;
            color: #991B1B;
            font-weight: bold;
        ''')
        self.upload_status_label.setVisible(True)
        
        self.statusBar().showMessage('✗ Upload failed')
        logger.error(f'Upload failed: {error_msg}')
    
    def load_datasets(self):
        """Load list of datasets from API"""
        try:
            api_url = self.config.get_api_url()
            timeout = self.config.get_api_timeout()
            
            logger.info(f"Loading datasets from {api_url}/datasets/")
            response = requests.get(f'{api_url}/datasets/', timeout=timeout)
            logger.debug(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"API Response Data: {data}")
                
                # Handle both single object and list responses
                if isinstance(data, dict) and 'id' in data:
                    self.datasets_list = [data]
                    logger.debug("Wrapped single object into list")
                elif isinstance(data, list):
                    self.datasets_list = data
                    logger.debug(f"Data is a list with {len(data)} items")
                else:
                    self.datasets_list = []
                    logger.warning("Unexpected data format")
                
                self.update_history_table()
                
                # Auto-load latest dataset
                if self.datasets_list:
                    self.current_dataset = self.datasets_list[0]
                    logger.debug(f"Setting current dataset: {self.current_dataset.get('id', 'Unknown')}")
                    self.update_dashboard()
                    self.update_table()
                    self.update_chart()
                else:
                    logger.warning("No datasets available")
                    self.current_dataset = None
                    self.update_dashboard()
                    self.update_table()
                    self.update_chart()
                
                self.statusBar().showMessage(f'✓ Loaded {len(self.datasets_list)} dataset(s)')
                
            else:
                logger.error(f"API returned status {response.status_code}")
                self.datasets_list = []
                self.statusBar().showMessage(f'✗ API error: {response.status_code}')
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            self.statusBar().showMessage('✗ Cannot connect to server')
            self.datasets_list = []
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error: {e}")
            self.statusBar().showMessage('✗ Request timed out')
            self.datasets_list = []
        except Exception as e:
            logger.error(f'Error loading datasets: {e}', exc_info=True)
            self.statusBar().showMessage('✗ Error loading datasets')
            self.datasets_list = []
    
    def auto_refresh_datasets(self):
        """Auto-refresh datasets if enabled"""
        if self.auto_refresh_checkbox.isChecked():
            self.load_datasets()
    
    def toggle_auto_refresh(self, state):
        """Toggle auto-refresh timer"""
        if state == Qt.Checked:
            self.refresh_timer.start(30000)
            logger.info('Auto-refresh enabled')
        else:
            self.refresh_timer.stop()
            logger.info('Auto-refresh disabled')
    
    def load_dataset_details(self, dataset_id: int):
        """Load detailed dataset information"""
        try:
            api_url = self.config.get_api_url()
            timeout = self.config.get_api_timeout()
            
            response = requests.get(f'{api_url}/datasets/{dataset_id}/', timeout=timeout)
            
            if response.status_code == 200:
                self.current_dataset = response.json()
                self.update_dashboard()
                self.update_table()
                self.update_chart()
                self.tabs.setCurrentIndex(1)  # Switch to dashboard
                self.statusBar().showMessage(f'✓ Loaded dataset {dataset_id}')
                logger.info(f'Loaded dataset details: {dataset_id}')
            else:
                QMessageBox.warning(self, 'Error', f'Failed to load dataset: {response.status_code}')
                
        except Exception as e:
            logger.error(f'Error loading dataset details: {e}', exc_info=True)
            QMessageBox.critical(self, 'Error', f'Failed to load dataset:\n{str(e)}')
    
    def update_dashboard(self):
        """Update dashboard with current dataset"""
        if not self.current_dataset:
            # Empty state
            self.dataset_info_label.setText('📊 No dataset loaded. Upload a CSV file to get started.')
            self.ranges_text.setText('No data available.\n\nUpload a CSV file to see parameter ranges and statistics.')
            
            # Reset stat cards
            for key in self.stat_cards:
                card = self.stat_cards[key]
                value_label = card.findChild(QLabel, 'value_label')
                if value_label:
                    value_label.setText('0')
            
            self.download_pdf_btn.setEnabled(False)
            return
        
        # Update dataset info
        filename = self.current_dataset.get('filename', 'Unknown')
        upload_date = self.current_dataset.get('uploaded_at', '')
        
        if upload_date:
            try:
                upload_date = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                upload_date = upload_date.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                logger.warning(f"Failed to parse date: {e}")
                upload_date = 'Unknown'
        
        self.dataset_info_label.setText(
            f'📊 <b>Dataset:</b> {filename} | <b>Uploaded:</b> {upload_date}'
        )
        
        # Update stat cards
        summary = self.current_dataset.get('summary', {})
        logger.debug(f"Summary data: {summary}")
        
        stats = {
            'total_count': str(summary.get('total_count', 0)),
            'avg_flowrate': f"{summary.get('avg_flowrate', 0):.2f}",
            'avg_pressure': f"{summary.get('avg_pressure', 0):.2f}",
            'avg_temperature': f"{summary.get('avg_temperature', 0):.2f}",
        }
        
        for key, value in stats.items():
            card = self.stat_cards[key]
            value_label = card.findChild(QLabel, 'value_label')
            if value_label:
                value_label.setText(value)
        
        # Update parameter ranges
        ranges_text = "=" * 50 + "\n"
        ranges_text += "PARAMETER RANGES SUMMARY\n"
        ranges_text += "=" * 50 + "\n\n"
        
        ranges_text += f"Flowrate:\n"
        ranges_text += f"  Minimum    : {summary.get('min_flowrate', 0):>10.2f}\n"
        ranges_text += f"  Average    : {summary.get('avg_flowrate', 0):>10.2f}\n"
        ranges_text += f"  Maximum    : {summary.get('max_flowrate', 0):>10.2f}\n\n"
        
        ranges_text += f"Pressure:\n"
        ranges_text += f"  Minimum    : {summary.get('min_pressure', 0):>10.2f}\n"
        ranges_text += f"  Average    : {summary.get('avg_pressure', 0):>10.2f}\n"
        ranges_text += f"  Maximum    : {summary.get('max_pressure', 0):>10.2f}\n\n"
        
        ranges_text += f"Temperature:\n"
        ranges_text += f"  Minimum    : {summary.get('min_temperature', 0):>10.2f}\n"
        ranges_text += f"  Average    : {summary.get('avg_temperature', 0):>10.2f}\n"
        ranges_text += f"  Maximum    : {summary.get('max_temperature', 0):>10.2f}\n"
        
        ranges_text += "\n" + "=" * 50
        
        self.ranges_text.setText(ranges_text)
        
        self.download_pdf_btn.setEnabled(True)
    
    def update_table(self):
        """Update data table with equipment records"""
        logger.info('Updating data table')
        
        if not self.current_dataset:
            self.data_table.setRowCount(0)
            self.table_info_label.setText('Equipment Records (0 total)')
            logger.debug('No current dataset, table cleared')
            return
        
        equipment_records = self.current_dataset.get('equipment_records', [])
        logger.debug(f'Found {len(equipment_records)} equipment records')
        logger.debug(f'Equipment records data: {equipment_records}')
        
        self.data_table.setRowCount(len(equipment_records))
        
        for row, equipment in enumerate(equipment_records):
            logger.debug(f'Processing row {row}: {equipment}')
            self.data_table.setItem(row, 0, QTableWidgetItem(str(equipment.get('equipment_name', ''))))
            self.data_table.setItem(row, 1, QTableWidgetItem(str(equipment.get('equipment_type', ''))))
            self.data_table.setItem(row, 2, QTableWidgetItem(f"{float(equipment.get('flowrate', 0)):.2f}"))
            self.data_table.setItem(row, 3, QTableWidgetItem(f"{float(equipment.get('pressure', 0)):.2f}"))
            self.data_table.setItem(row, 4, QTableWidgetItem(f"{float(equipment.get('temperature', 0)):.2f}"))
        
        self.table_info_label.setText(f'Equipment Records ({len(equipment_records)} total)')
        logger.info(f'Data table updated with {len(equipment_records)} records')
        
        # Force table to refresh and display
        self.data_table.resizeRowsToContents()
        self.data_table.viewport().update()
    
    def filter_table(self):
        """Filter table based on search text"""
        search_text = self.search_box.text().lower()
        
        for row in range(self.data_table.rowCount()):
            should_show = False
            
            for col in range(self.data_table.columnCount()):
                item = self.data_table.item(row, col)
                if item and search_text in item.text().lower():
                    should_show = True
                    break
            
            self.data_table.setRowHidden(row, not should_show)
    
    def update_chart(self):
        """Update visualization chart"""
        if not self.current_dataset:
            # Empty state
            self.chart_widget.figure.clear()
            ax = self.chart_widget.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available\n\nUpload a CSV file to see visualizations',
                   ha='center', va='center', fontsize=14, transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            ax.axis('off')
            self.chart_widget.canvas.draw()
            return
        
        summary = self.current_dataset.get('summary', {})
        chart_type = self.chart_selector.currentText()
        type_dist = summary.get('type_distribution', {})
        
        if not type_dist and 'Distribution' in chart_type:
            self.chart_widget.figure.clear()
            ax = self.chart_widget.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No equipment type data available',
                   ha='center', va='center', fontsize=12, transform=ax.transAxes)
            ax.axis('off')
            self.chart_widget.canvas.draw()
            return
        
        if 'Bar' in chart_type and 'Multi' not in chart_type:
            self.chart_widget.plot_bar_chart(
                type_dist,
                'Equipment Type Distribution',
                'Equipment Type',
                'Count'
            )
        elif 'Pie' in chart_type:
            self.chart_widget.plot_pie_chart(
                type_dist,
                'Equipment Type Distribution'
            )
        elif 'Multi-Bar' in chart_type or 'Parameter' in chart_type:
            self.chart_widget.plot_multi_bar_chart(
                summary,
                'Parameter Comparison (Min, Avg, Max)'
            )
    
    def save_chart(self):
        """Save current chart to file"""
        if not self.current_dataset:
            QMessageBox.warning(self, 'Error', 'No data to save. Please upload a file first.')
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            'Save Chart',
            f'chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png',
            'PNG Files (*.png);;PDF Files (*.pdf);;SVG Files (*.svg)'
        )
        
        if filename:
            try:
                self.chart_widget.figure.savefig(filename, dpi=300, bbox_inches='tight')
                QMessageBox.information(
                    self,
                    'Success',
                    f'Chart saved successfully!\n\n{filename}'
                )
                logger.info(f'Chart saved: {filename}')
            except Exception as e:
                logger.error(f'Error saving chart: {e}', exc_info=True)
                QMessageBox.critical(self, 'Error', f'Failed to save chart:\n{str(e)}')
    
    def update_history_table(self):
        """Update history table with datasets"""
        self.history_table.setRowCount(len(self.datasets_list))
        
        for row, dataset in enumerate(self.datasets_list):
            filename = dataset.get('filename', 'Unknown')
            upload_date = dataset.get('uploaded_at', '')
            
            if upload_date:
                try:
                    upload_date = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                    upload_date = upload_date.strftime('%Y-%m-%d %H:%M')
                except:
                    upload_date = 'Unknown'
            
            records = str(dataset.get('total_records', 0))
            
            self.history_table.setItem(row, 0, QTableWidgetItem(filename))
            self.history_table.setItem(row, 1, QTableWidgetItem(upload_date))
            self.history_table.setItem(row, 2, QTableWidgetItem(records))
            
            # Action buttons
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(2, 2, 2, 2)
            button_layout.setSpacing(3)
            
            # Load button
            load_btn = QPushButton('📂 Load')
            load_btn.setFont(QFont('Arial', 8))
            load_btn.setMinimumWidth(70)
            load_btn.setMinimumHeight(32)
            load_btn.setStyleSheet('''
                QPushButton {
                    background-color: #10B981;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            ''')
            dataset_id = dataset.get('id')
            load_btn.clicked.connect(lambda checked, did=dataset_id: self.load_dataset_details(did))
            button_layout.addWidget(load_btn)
            
            # Delete button
            delete_btn = QPushButton('🗑️ Delete')
            delete_btn.setFont(QFont('Arial', 8))
            delete_btn.setMinimumWidth(70)
            delete_btn.setMinimumHeight(32)
            delete_btn.setStyleSheet('''
                QPushButton {
                    background-color: #EF4444;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                }
            ''')
            delete_btn.clicked.connect(lambda checked, did=dataset_id: self.delete_dataset(did))
            button_layout.addWidget(delete_btn)
            
            button_container = QWidget()
            button_container.setLayout(button_layout)
            button_container.setMinimumHeight(40)
            self.history_table.setCellWidget(row, 3, button_container)
    
    def delete_dataset(self, dataset_id: int):
        """Delete a dataset"""
        reply = QMessageBox.question(
            self,
            'Confirm Delete',
            'Are you sure you want to delete this dataset?\n\nThis action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            api_url = self.config.get_api_url()
            timeout = self.config.get_api_timeout()
            
            response = requests.delete(f'{api_url}/datasets/{dataset_id}/', timeout=timeout)
            
            if response.status_code in [200, 204]:
                # Clear upload status
                self.upload_status_label.setVisible(False)
                
                # If deleted dataset was current, clear it
                if self.current_dataset and self.current_dataset.get('id') == dataset_id:
                    self.current_dataset = None
                
                self.load_datasets()
                self.statusBar().showMessage(f'✓ Dataset {dataset_id} deleted successfully')
                logger.info(f'Dataset deleted: {dataset_id}')
            else:
                QMessageBox.warning(self, 'Error', f'Failed to delete dataset: {response.status_code}')
                
        except Exception as e:
            logger.error(f'Error deleting dataset: {e}', exc_info=True)
            QMessageBox.critical(self, 'Error', f'Failed to delete dataset:\n{str(e)}')
    
    def delete_all_datasets(self):
        """Delete all datasets"""
        if not self.datasets_list:
            QMessageBox.information(self, 'Info', 'No datasets to delete.')
            return
        
        reply = QMessageBox.question(
            self,
            'Confirm Delete All',
            f'Are you sure you want to delete ALL {len(self.datasets_list)} dataset(s)?\n\n'
            'This action cannot be undone!',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            api_url = self.config.get_api_url()
            timeout = self.config.get_api_timeout()
            
            deleted_count = 0
            for dataset in self.datasets_list:
                dataset_id = dataset.get('id')
                response = requests.delete(f'{api_url}/datasets/{dataset_id}/', timeout=timeout)
                if response.status_code in [200, 204]:
                    deleted_count += 1
            
            self.current_dataset = None
            self.load_datasets()
            
            QMessageBox.information(
                self,
                'Success',
                f'Successfully deleted {deleted_count} dataset(s).'
            )
            logger.info(f'Deleted {deleted_count} datasets')
            
        except Exception as e:
            logger.error(f'Error deleting datasets: {e}', exc_info=True)
            QMessageBox.critical(self, 'Error', f'Failed to delete datasets:\n{str(e)}')
    
    def download_pdf(self):
        """Download PDF report"""
        if not self.current_dataset:
            QMessageBox.warning(self, 'Error', 'No dataset selected. Please upload a file first.')
            return
        
        dataset_id = self.current_dataset.get('id')
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            'Save PDF Report',
            f'equipment_report_{dataset_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            'PDF Files (*.pdf)'
        )
        
        if filename:
            try:
                api_url = self.config.get_api_url()
                timeout = self.config.get_api_timeout()
                url = f'{api_url}/datasets/{dataset_id}/generate_pdf/'
                
                logger.info(f"Requesting PDF from: {url}")
                response = requests.get(url, timeout=timeout)
                
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    QMessageBox.information(
                        self,
                        'Success',
                        f'PDF report saved successfully!\n\n{filename}'
                    )
                    self.statusBar().showMessage('✓ PDF downloaded successfully')
                    logger.info(f'PDF saved: {filename}')
                else:
                    error_msg = f"Server returned status {response.status_code}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error: {e}")
                QMessageBox.critical(
                    self,
                    'Connection Error',
                    f'Cannot connect to server.\n\nPlease ensure the backend is running.'
                )
            except Exception as e:
                logger.error(f'Error downloading PDF: {e}', exc_info=True)
                QMessageBox.critical(self, 'Error', f'Failed to download PDF:\n\n{str(e)}')
    
    def closeEvent(self, event):
        """Handle application close event"""
        reply = QMessageBox.question(
            self,
            'Confirm Exit',
            'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info('Application closing')
            event.accept()
        else:
            event.ignore()


def main():
    """Main application entry point"""
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Set application metadata
        app.setApplicationName('Chemical Equipment Visualizer')
        app.setApplicationVersion(APP_VERSION)
        app.setOrganizationName('ChemicalEquipment')
        
        # Set application font
        font = QFont('Arial', 10)
        app.setFont(font)
        
        # Create and show main window
        window = ChemicalEquipmentApp()
        window.show()
        
        logger.info(f'Application started - Version {APP_VERSION}')
        
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.critical(f'Fatal error: {e}', exc_info=True)
        QMessageBox.critical(None, 'Fatal Error', f'Application failed to start:\n{str(e)}')
        sys.exit(1)


if __name__ == '__main__':
    main()