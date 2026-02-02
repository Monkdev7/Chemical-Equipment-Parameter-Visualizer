"""
Business logic services for equipment data processing
"""

from typing import Dict, Any, List
import pandas as pd
from django.db import transaction

from .models import Dataset, Equipment
from .utils import (
    validate_file_extension,
    validate_csv_columns,
    clean_data,
    calculate_statistics,
)
from .constants import MAX_DATASETS_HISTORY, REQUIRED_CSV_COLUMNS
from .exceptions import FileFormatError


class DatasetService:
    """Service for handling dataset operations"""
    
    @staticmethod
    def validate_and_parse_csv(csv_file) -> pd.DataFrame:
        """
        Validate and parse CSV file with proper error handling
        
        Args:
            csv_file: Django UploadedFile object
            
        Returns:
            pd.DataFrame: Parsed CSV data
            
        Raises:
            FileFormatError: If file format is invalid
            CSVValidationError: If CSV structure is invalid
        """
        # Validate file extension
        if not validate_file_extension(csv_file.name):
            raise FileFormatError("File must be CSV format (.csv)")
        
        # Read CSV with error handling
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            raise FileFormatError(f"Error reading CSV file: {str(e)}")
        
        # Check if DataFrame is empty
        if df.empty:
            raise FileFormatError("CSV file is empty")
        
        # Validate required columns
        try:
            validate_csv_columns(df)
        except Exception as e:
            raise CSVValidationError(str(e))
        
        # Clean and validate data
        try:
            df_clean = clean_data(df)
        except Exception as e:
            raise CSVValidationError(str(e))
        
        return df_clean
    
    @staticmethod
    @transaction.atomic
    def create_dataset_with_equipment(
        user,
        filename: str,
        df: pd.DataFrame
    ) -> Dataset:
        """
        Create dataset and equipment records from DataFrame
        
        Args:
            user: User object (can be None)
            filename: Name of the uploaded file
            df: Cleaned DataFrame with equipment data
            
        Returns:
            Dataset: Created dataset object
        """
        # Calculate statistics
        summary = calculate_statistics(df)
        
        # Create dataset
        dataset = Dataset.objects.create(
            user=user,
            filename=filename,
            total_records=len(df)
        )
        dataset.set_summary_data(summary)
        dataset.save()
        
        # Create equipment records
        equipment_list = [
            Equipment(
                dataset=dataset,
                equipment_name=row['Equipment Name'],
                equipment_type=row['Type'],
                flowrate=float(row['Flowrate']),
                pressure=float(row['Pressure']),
                temperature=float(row['Temperature'])
            )
            for _, row in df.iterrows()
        ]
        
        Equipment.objects.bulk_create(equipment_list)
        
        return dataset
    
    @staticmethod
    def cleanup_old_datasets() -> int:
        """
        Remove datasets beyond the history limit (keep last 5)
        
        Returns:
            int: Number of datasets deleted
        """
        # Get IDs of datasets to keep (last MAX_DATASETS_HISTORY)
        datasets_to_keep = Dataset.objects.all().order_by('-uploaded_at')[:MAX_DATASETS_HISTORY].values_list('id', flat=True)
        
        # Delete all others
        deleted_count, _ = Dataset.objects.exclude(id__in=list(datasets_to_keep)).delete()
        return deleted_count
    
    @staticmethod
    def get_dataset_with_summary(dataset_id: int) -> Dict[str, Any]:
        """
        Get dataset details with summary information
        
        Args:
            dataset_id: ID of the dataset
            
        Returns:
            Dict[str, Any]: Dataset information
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            return {
                'id': dataset.id,
                'filename': dataset.filename,
                'uploaded_at': dataset.uploaded_at,
                'total_records': dataset.total_records,
                'summary': dataset.get_summary_data(),
            }
        except Dataset.DoesNotExist:
            return None
    
    @staticmethod
    def get_recent_datasets(limit: int = 5) -> List[Dataset]:
        """
        Get most recent datasets ordered by upload time
        
        Args:
            limit: Number of datasets to retrieve
            
        Returns:
            List[Dataset]: List of recent datasets
        """
        return list(Dataset.objects.all().order_by('-uploaded_at')[:limit])
