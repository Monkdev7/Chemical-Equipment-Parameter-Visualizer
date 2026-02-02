"""
Utility functions for the equipment app
"""

import csv
from typing import Dict, List, Any
import pandas as pd
from .constants import REQUIRED_CSV_COLUMNS, NUMERIC_FIELDS
from .exceptions import (
    FileFormatError,
    MissingColumnsError,
    InvalidDataError,
    NoValidDataError,
)


def validate_file_extension(filename: str) -> bool:
    """
    Validate if the file has a .csv extension
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        bool: True if file is CSV format, False otherwise
    """
    return filename.lower().endswith('.csv')


def validate_csv_columns(df: pd.DataFrame) -> List[str]:
    """
    Validate that CSV contains all required columns
    
    Args:
        df: Pandas DataFrame from CSV file
        
    Returns:
        List[str]: List of missing columns, empty if all present
        
    Raises:
        MissingColumnsError: If required columns are missing
    """
    missing_columns = [col for col in REQUIRED_CSV_COLUMNS if col not in df.columns]
    
    if missing_columns:
        raise MissingColumnsError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )
    
    return missing_columns


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean DataFrame by removing rows with missing values in required columns
    and validating numeric values
    
    Args:
        df: Pandas DataFrame to clean
        
    Returns:
        pd.DataFrame: Cleaned DataFrame
        
    Raises:
        NoValidDataError: If no valid data remains after cleaning
        InvalidDataError: If numeric columns contain invalid values
    """
    # Check for missing values
    df_clean = df.dropna(subset=REQUIRED_CSV_COLUMNS)
    
    if len(df_clean) == 0:
        raise NoValidDataError("No valid data found in CSV after removing missing values")
    
    # Validate numeric columns
    for col in NUMERIC_FIELDS:
        if col in df_clean.columns:
            try:
                # Try to convert to numeric
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                # Remove rows where conversion failed (NaN)
                df_clean = df_clean[df_clean[col].notna()]
            except Exception as e:
                raise InvalidDataError(f"Invalid numeric values in column '{col}': {str(e)}")
    
    # Final check
    if len(df_clean) == 0:
        raise NoValidDataError("No valid data found in CSV after validating numeric columns")
    
    return df_clean


def validate_numeric_values(df: pd.DataFrame) -> None:
    """
    Validate that numeric columns contain valid numeric values
    
    Args:
        df: Pandas DataFrame to validate
        
    Raises:
        InvalidDataError: If numeric columns contain non-numeric values
    """
    for col in NUMERIC_FIELDS:
        if col in df.columns:
            try:
                pd.to_numeric(df[col], errors='coerce')
            except Exception as e:
                raise InvalidDataError(f"Invalid numeric values in column '{col}': {str(e)}")


def calculate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate summary statistics from equipment data
    
    Args:
        df: Pandas DataFrame with equipment data
        
    Returns:
        Dict[str, Any]: Dictionary containing statistical summaries
    """
    statistics = {
        'total_count': len(df),
        'avg_flowrate': float(df['Flowrate'].mean()),
        'avg_pressure': float(df['Pressure'].mean()),
        'avg_temperature': float(df['Temperature'].mean()),
        'min_flowrate': float(df['Flowrate'].min()),
        'max_flowrate': float(df['Flowrate'].max()),
        'min_pressure': float(df['Pressure'].min()),
        'max_pressure': float(df['Pressure'].max()),
        'min_temperature': float(df['Temperature'].min()),
        'max_temperature': float(df['Temperature'].max()),
        'type_distribution': df['Type'].value_counts().to_dict(),
    }
    
    return statistics


def format_number(value: float, decimals: int = 2) -> float:
    """
    Format number to specified decimal places
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        
    Returns:
        float: Formatted number
    """
    return round(value, decimals)
