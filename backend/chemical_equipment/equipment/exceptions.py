"""
Custom exceptions for the equipment app
"""


class CSVValidationError(Exception):
    """Raised when CSV file validation fails"""
    pass


class MissingColumnsError(CSVValidationError):
    """Raised when required columns are missing from CSV"""
    pass


class InvalidDataError(CSVValidationError):
    """Raised when CSV contains invalid data"""
    pass


class NoValidDataError(CSVValidationError):
    """Raised when no valid data is found in CSV after cleaning"""
    pass


class FileFormatError(Exception):
    """Raised when file format is not supported"""
    pass


class DatasetNotFoundError(Exception):
    """Raised when dataset is not found"""
    pass


class PDFGenerationError(Exception):
    """Raised when PDF generation fails"""
    pass
