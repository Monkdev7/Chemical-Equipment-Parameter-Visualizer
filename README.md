# Chemical Equipment Parameter Visualizer

A comprehensive web and desktop application for uploading, analyzing, and visualizing chemical equipment data. The platform allows users to upload CSV files containing equipment specifications, view detailed analytics, generate PDF reports, and track data history.

**Version:** 2.0 (Enhanced with UI/UX Improvements)

## 🚀 Features

### Core Features
- **CSV Upload & Validation** - Upload chemical equipment data with automatic validation
- **Data Analysis** - Automatic calculation of statistics (averages, min/max, distributions)
- **Data Visualization** - Interactive charts and graphs using Chart.js (Web) and Matplotlib (Desktop)
- **PDF Report Generation** - Generate professional PDF reports with charts and summaries
- **History Management** - Keep track of last 5 uploaded datasets with Load/Delete actions
- **Responsive Design** - Works seamlessly on web and desktop platforms

### Advanced Features
- Real-time data summary statistics with animated stat cards
- Equipment type distribution analysis (Bar, Pie, Multi-bar charts)
- Parameter range analysis (min/max values) with expanded display
- Equipment records table with search/filter functionality
- Fully visible history table with action buttons (Load/Delete)
- User authentication and history tracking
- CORS-enabled API for multiple frontend implementations
- Production-ready with Gunicorn/Heroku deployment support
- Enhanced desktop application with PyQt5 styling

## 📋 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend API** | Django 5.2 + Django REST Framework | RESTful API for data management |
| **Frontend (Web)** | React.js + Chart.js | Interactive web dashboard |
| **Frontend (Desktop)** | PyQt5 + Matplotlib | Desktop application |
| **Data Processing** | Pandas | CSV parsing and analytics |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Persistent data storage |
| **PDF Generation** | ReportLab | Professional report generation |
| **Deployment** | Gunicorn + Heroku | Cloud hosting and scaling |
| **Version Control** | Git & GitHub | Collaboration and tracking |

## 📁 Project Structure

```
Chemical-Equipment-Parameter-Visualizer/
├── backend/                              # Django REST API
│   ├── chemical_equipment/               # Main project configuration
│   │   ├── settings.py                  # Django settings
│   │   ├── urls.py                      # URL routing
│   │   ├── wsgi.py                      # WSGI configuration
│   │   └── asgi.py                      # ASGI configuration
│   ├── equipment/                        # Equipment app
│   │   ├── models.py                    # Database models
│   │   ├── views.py                     # API viewsets
│   │   ├── serializers.py               # API serializers
│   │   ├── services.py                  # Business logic
│   │   ├── utils.py                     # Utility functions
│   │   ├── constants.py                 # Constants
│   │   ├── exceptions.py                # Custom exceptions
│   │   ├── migrations/                  # Database migrations
│   │   ├── admin.py                     # Django admin config
│   │   ├── apps.py                      # App configuration
│   │   └── tests.py                     # Unit tests
│   ├── manage.py                         # Django management
│   ├── requirements.txt                  # Python dependencies
│   ├── Procfile                          # Heroku deployment
│   └── venv/                             # Virtual environment
├── frontend-web/                         # React web application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
├── frontend-desktop/                     # PyQt5 desktop application
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── docs/                                 # Documentation
│   ├── API.md                            # API documentation
│   ├── SETUP.md                          # Setup guide
│   └── DEPLOYMENT.md                     # Deployment guide
├── README.md                             # Project overview
├── LICENSE                               # Project license
└── .gitignore                            # Git ignore rules
```

## 🔧 Installation & Setup

### Quick Start (Windows PowerShell)

#### 1. Backend Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd chemical_equipment
python manage.py migrate
python manage.py runserver
# Backend runs on http://localhost:8000/
```

#### 2. Web Frontend Setup (New Terminal)
```powershell
cd frontend-web
npm install
npm start
# Web app runs on http://localhost:3000/
```

#### 3. Desktop Frontend Setup (New Terminal)
```powershell
cd frontend-desktop
python main.py
# PyQt5 desktop application launches
```

### Prerequisites
- Python 3.9+
- Node.js 14+ (for web frontend)
- pip & npm

### Detailed Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Chemical-Equipment-Parameter-Visualizer.git
   cd Chemical-Equipment-Parameter-Visualizer/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows: .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**
   ```bash
   cd chemical_equipment
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

### Detailed Web Frontend Setup

1. Navigate to frontend-web directory
2. Install dependencies: `npm install`
3. Ensure backend is running on `http://localhost:8000`
4. Start development server: `npm start`
5. Access at `http://localhost:3000`

### Detailed Desktop Frontend Setup

1. Navigate to frontend-desktop directory
2. Create virtual environment: `python -m venv venv`
3. Activate: `.\venv\Scripts\Activate.ps1` (Windows) or `source venv/bin/activate` (Unix)
4. Install requirements: `pip install -r requirements.txt`
5. Ensure backend is running on `http://localhost:8000`
6. Run: `python main.py`

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Endpoints

#### 1. Upload CSV Dataset
```
POST /datasets/upload/
```

**Request:**
- Content-Type: multipart/form-data
- File field: `file` (CSV format required)

**Expected CSV Columns:**
- Equipment Name (string)
- Type (string)
- Flowrate (float)
- Pressure (float)
- Temperature (float)

**Response (201 Created):**
```json
{
  "id": 1,
  "filename": "equipment_data.csv",
  "uploaded_at": "2026-01-29T10:30:00Z",
  "total_records": 25,
  "summary": {
    "total_count": 25,
    "avg_flowrate": 15.5,
    "avg_pressure": 102.3,
    "avg_temperature": 75.4,
    "min_flowrate": 5.0,
    "max_flowrate": 25.0,
    "min_pressure": 95.0,
    "max_pressure": 110.0,
    "min_temperature": 60.0,
    "max_temperature": 90.0,
    "type_distribution": {
      "Pump": 8,
      "Heat Exchanger": 10,
      "Compressor": 7
    }
  },
  "equipment_records": [...]
}
```

#### 2. List Last 5 Datasets
```
GET /datasets/
```

**Response (200 OK):** Returns last 5 datasets ordered by upload time, with complete equipment records included
```json
[
  {
    "id": 1,
    "filename": "equipment_data.csv",
    "uploaded_at": "2026-02-02T21:30:00Z",
    "total_records": 25,
    "summary": {
      "total_count": 25,
      "avg_flowrate": 15.5,
      "avg_pressure": 102.3,
      "avg_temperature": 75.4,
      "min_flowrate": 5.0,
      "max_flowrate": 25.0,
      "min_pressure": 95.0,
      "max_pressure": 110.0,
      "min_temperature": 60.0,
      "max_temperature": 90.0,
      "type_distribution": {
        "Pump": 8,
        "Heat Exchanger": 10,
        "Compressor": 7
      }
    },
    "equipment_records": [
      {
        "id": 1,
        "equipment_name": "Pump A",
        "equipment_type": "Pump",
        "flowrate": 12.5,
        "pressure": 100.5,
        "temperature": 75.2
      },
      {...}
    ]
  }
]
```

#### 3. Get Dataset Details
```
GET /datasets/{id}/
```

**Response (200 OK):** Full dataset with all equipment records

#### 4. Generate PDF Report
```
GET /datasets/{id}/generate_pdf/
```

**Response:** PDF file download with charts and statistics

### Error Responses

**Invalid File Format (400):**
```json
{
  "error": "File must be CSV format"
}
```

**Missing Columns (400):**
```json
{
  "error": "Missing required columns: Flowrate, Temperature"
}
```

**No Valid Data (400):**
```json
{
  "error": "No valid data found in CSV"
}
```

## 🗂️ Sample Data Format

Create a CSV file with the following structure:

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump A,Pump,12.5,100.5,75.2
Heat Exchanger 1,Heat Exchanger,20.0,105.0,80.5
Compressor B,Compressor,15.3,110.0,85.0
Pump C,Pump,10.0,98.5,70.0
```

## 🔐 Security Considerations

- CORS enabled for frontend communication
- Input validation on file uploads
- SQL injection protection via ORM
- CSRF protection on POST requests
- Environment variables for sensitive data
- Debug mode disabled in production

## 🚀 Deployment

### Heroku Deployment

1. Create Heroku app: `heroku create your-app-name`
2. Add PostgreSQL: `heroku addons:create heroku-postgresql:hobby-dev`
3. Set environment variables:
   ```bash
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   heroku config:set DJANGO_SECRET_KEY=your-secret-key
   ```
4. Deploy: `git push heroku main`

### Docker Deployment

Build and run:
```bash
docker build -t chemflow .
docker run -p 8000:8000 chemflow
```

## 📊 Database Schema

### Dataset Model
- `id` (Primary Key)
- `user` (Foreign Key to User, nullable)
- `filename` (CharField)
- `uploaded_at` (DateTimeField, auto-set)
- `total_records` (IntegerField)
- `summary_data` (TextField, JSON format)

### Equipment Model
- `id` (Primary Key)
- `dataset` (Foreign Key to Dataset)
- `equipment_name` (CharField)
- `equipment_type` (CharField)
- `flowrate` (FloatField)
- `pressure` (FloatField)
- `temperature` (FloatField)

## 🧪 Testing

Run unit tests:
```bash
python manage.py test
```

## 📝 API Testing with cURL

Upload a CSV:
```bash
curl -X POST http://localhost:8000/api/datasets/upload/ \
  -F "file=@sample_equipment_data.csv"
```

List datasets:
```bash
curl http://localhost:8000/api/datasets/
```

Get PDF report:
```bash
curl http://localhost:8000/api/datasets/1/generate_pdf/ \
  -o report.pdf
```

