"""
Django Admin configuration for equipment app
"""

from django.contrib import admin
from .models import Dataset, Equipment


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    """Admin configuration for Dataset model"""
    
    list_display = ('filename', 'uploaded_at', 'total_records', 'user')
    list_filter = ('uploaded_at', 'total_records')
    search_fields = ('filename', 'user__username')
    readonly_fields = ('uploaded_at', 'summary_data')
    fieldsets = (
        ('Basic Information', {
            'fields': ('filename', 'user', 'uploaded_at')
        }),
        ('Statistics', {
            'fields': ('total_records', 'summary_data')
        }),
    )


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """Admin configuration for Equipment model"""
    
    list_display = ('equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature')
    list_filter = ('equipment_type', 'dataset__uploaded_at')
    search_fields = ('equipment_name', 'equipment_type', 'dataset__filename')
    raw_id_fields = ('dataset',)
    
    fieldsets = (
        ('Equipment Information', {
            'fields': ('equipment_name', 'equipment_type', 'dataset')
        }),
        ('Parameters', {
            'fields': ('flowrate', 'pressure', 'temperature')
        }),
    )