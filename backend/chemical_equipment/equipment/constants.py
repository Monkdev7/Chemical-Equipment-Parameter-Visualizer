"""
Constants and configuration for the equipment app
"""

# CSV VALIDATION CONSTANTS
REQUIRED_CSV_COLUMNS = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
ALLOWED_FILE_EXTENSIONS = ['.csv']
MAX_FILE_SIZE_MB = 10
MAX_DATASETS_HISTORY = 5

# ERROR MESSAGES
ERROR_MESSAGES = {
    'no_file': 'No file provided',
    'invalid_format': 'File must be CSV format',
    'missing_columns': 'Missing required columns: {}',
    'no_valid_data': 'No valid data found in CSV',
    'file_too_large': f'File size exceeds {MAX_FILE_SIZE_MB}MB limit',
    'invalid_numeric': 'Invalid numeric value in {}',
    'dataset_not_found': 'Dataset not found',
}

# ANALYSIS METRICS
ANALYSIS_METRICS = {
    'total_count',
    'avg_flowrate',
    'avg_pressure',
    'avg_temperature',
    'min_flowrate',
    'max_flowrate',
    'min_pressure',
    'max_pressure',
    'min_temperature',
    'max_temperature',
    'type_distribution',
}

# API RESPONSE CODES
RESPONSE_CODES = {
    'success': 200,
    'created': 201,
    'bad_request': 400,
    'unauthorized': 401,
    'not_found': 404,
    'internal_error': 500,
}

# PDF REPORT CONFIGURATION
PDF_CONFIG = {
    'title': 'ChemFlow Analytics Report',
    'author': 'ChemFlow Analytics Platform',
    'subject': 'Chemical Equipment Analysis Report',
    'page_width': 8.5,
    'page_height': 11,
    'margin_left': 0.75,
    'margin_right': 0.75,
    'margin_top': 1.0,
    'margin_bottom': 0.75,
    'color_primary': '#10b981',
    'color_secondary': '#334155',
}

# NUMERIC FIELD VALIDATION
NUMERIC_FIELDS = ['Flowrate', 'Pressure', 'Temperature']
