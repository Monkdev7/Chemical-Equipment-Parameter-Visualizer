"""
DRF Serializers for equipment app
"""

from rest_framework import serializers
from typing import Dict, Any
from .models import Dataset, Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Equipment model.
    
    Provides serialization/deserialization of equipment records with all fields.
    """
    
    class Meta:
        model = Equipment
        fields = [
            'id',
            'equipment_name',
            'equipment_type',
            'flowrate',
            'pressure',
            'temperature'
        ]
        read_only_fields = ['id']


class DatasetDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Dataset model including all equipment records.
    
    Used when retrieving complete dataset information with all related equipment.
    """
    
    equipment_records = EquipmentSerializer(many=True, read_only=True)
    summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'filename',
            'uploaded_at',
            'total_records',
            'summary',
            'equipment_records'
        ]
        read_only_fields = [
            'id',
            'uploaded_at',
            'total_records',
            'summary',
            'equipment_records'
        ]
    
    def get_summary(self, obj: Dataset) -> Dict[str, Any]:
        """
        Get summary data as dictionary.
        
        Args:
            obj: Dataset instance
            
        Returns:
            Dict[str, Any]: Parsed summary statistics
        """
        return obj.get_summary_data()


class DatasetListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Dataset list view.
    
    Excludes equipment records for faster list responses.
    Used when displaying dataset history/list.
    """
    
    summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'filename',
            'uploaded_at',
            'total_records',
            'summary'
        ]
        read_only_fields = [
            'id',
            'filename',
            'uploaded_at',
            'total_records',
            'summary'
        ]
    
    def get_summary(self, obj: Dataset) -> Dict[str, Any]:
        """
        Get summary data as dictionary.
        
        Args:
            obj: Dataset instance
            
        Returns:
            Dict[str, Any]: Parsed summary statistics
        """
        return obj.get_summary_data()