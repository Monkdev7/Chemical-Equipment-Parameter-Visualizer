"""
Database models for equipment data management
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from typing import Dict, Any
import json


class Dataset(models.Model):
    """Model to store uploaded CSV datasets with metadata and summary statistics."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='datasets')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_records = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    summary_data = models.TextField(blank=True, default='')
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [models.Index(fields=['-uploaded_at'])]
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'
        
    def __str__(self) -> str:
        """Return string representation of dataset"""
        return f"{self.filename} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_summary_data(self) -> Dict[str, Any]:
        """
        Retrieve summary statistics as dictionary.
        
        Returns:
            Dict[str, Any]: Parsed summary data or empty dict if invalid
        """
        try:
            if self.summary_data and self.summary_data.strip():
                return json.loads(self.summary_data)
        except (json.JSONDecodeError, ValueError):
            pass
        return {}
    
    def set_summary_data(self, data: Dict[str, Any]) -> None:
        """
        Store summary statistics as JSON string.
        
        Args:
            data: Dictionary containing statistical analysis
        """
        self.summary_data = json.dumps(data)


class Equipment(models.Model):
    """Model to store individual equipment records from uploaded datasets."""
    
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipment_records')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField(validators=[MinValueValidator(0)])
    pressure = models.FloatField(validators=[MinValueValidator(0)])
    temperature = models.FloatField()
    
    class Meta:
        ordering = ['equipment_name']
        indexes = [
            models.Index(fields=['dataset', 'equipment_name']),
            models.Index(fields=['equipment_type']),
        ]
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'
        
    def __str__(self) -> str:
        """Return string representation of equipment"""
        return f"{self.equipment_name} ({self.equipment_type})"