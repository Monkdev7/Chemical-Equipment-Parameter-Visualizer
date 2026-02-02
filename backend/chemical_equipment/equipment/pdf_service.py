"""
PDF Report Generation Service
"""

from typing import Optional, Dict, Any
import io
import tempfile
import os
import logging
from datetime import datetime

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, PageTemplate, Frame
)
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas

from .models import Dataset
from .exceptions import PDFGenerationError

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generates comprehensive PDF reports for equipment datasets"""
    
    # Chart colors palette
    COLORS = ['#818cf8', '#34d399', '#a78bfa', '#fb923c', '#fbbf24', '#38bdf8']
    
    # PDF Configuration
    PDF_CONFIG = {
        'pagesize': letter,
        'rightMargin': 0.75 * inch,
        'leftMargin': 0.75 * inch,
        'topMargin': 1 * inch,
        'bottomMargin': 0.75 * inch,
    }
    
    # Color scheme
    PRIMARY_COLOR = '#10b981'
    SECONDARY_COLOR = '#334155'
    ACCENT_COLOR_1 = '#ef4444'
    ACCENT_COLOR_2 = '#3b82f6'
    LIGHT_BG = '#f8fafc'
    BORDER_COLOR = '#e2e8f0'
    
    def __init__(self, dataset: Dataset):
        """
        Initialize PDF generator with dataset.
        
        Args:
            dataset: Dataset instance to generate report for
        """
        self.dataset = dataset
        self.summary = dataset.get_summary_data()
        self.temp_dir = tempfile.mkdtemp()
        
    def generate(self) -> io.BytesIO:
        """
        Generate complete PDF report.
        
        Returns:
            io.BytesIO: PDF file buffer
            
        Raises:
            PDFGenerationError: If PDF generation fails
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                **self.PDF_CONFIG,
                title=f'ChemFlow Report - {self.dataset.filename}',
                author='ChemFlow Analytics Platform',
                subject='Chemical Equipment Analysis Report'
            )
            
            elements = []
            styles = getSampleStyleSheet()
            
            # Add sections
            elements.extend(self._create_header(styles))
            elements.extend(self._create_info_section(styles))
            elements.extend(self._create_statistics_section(styles))
            elements.extend(self._create_enhanced_statistics_section(styles))
            elements.extend(self._create_equipment_type_breakdown(styles))
            elements.extend(self._create_charts_section(styles))
            elements.extend(self._create_equipment_table(styles))
            elements.extend(self._create_footer(styles))
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            
            # Cleanup
            self._cleanup_temp_files()
            
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
            self._cleanup_temp_files()
            raise PDFGenerationError(f"Failed to generate PDF: {str(e)}")
    
    def _create_header(self, styles) -> list:
        """Create report header section"""
        header_data = [[
            Paragraph(
                '<font size=24 color="#ffffff"><b>ChemFlow Analytics Report</b></font>',
                styles['Normal']
            )
        ]]
        header_table = Table(header_data, colWidths=[6.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(self.PRIMARY_COLOR)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        return [header_table, Spacer(1, 0.4*inch)]
    
    def _create_info_section(self, styles) -> list:
        """Create dataset information section"""
        info_data = [
            ['Dataset Information', ''],
            ['Filename:', self.dataset.filename],
            ['Upload Date:', self.dataset.uploaded_at.strftime('%B %d, %Y at %H:%M:%S')],
            ['Total Records:', str(self.dataset.total_records)],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4.5*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.SECONDARY_COLOR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor(self.LIGHT_BG)),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.HexColor(self.SECONDARY_COLOR)),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(self.BORDER_COLOR)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        return [info_table, Spacer(1, 0.3*inch)]
    
    def _create_statistics_section(self, styles) -> list:
        """Create statistics table section"""
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor(self.SECONDARY_COLOR),
            spaceAfter=12,
            spaceBefore=0,
            fontName='Helvetica-Bold'
        )
        
        stats_data = [
            ['Parameter', 'Minimum', 'Average', 'Maximum'],
            [
                'Flowrate',
                f"{self.summary.get('min_flowrate', 0):.2f}",
                f"{self.summary.get('avg_flowrate', 0):.2f}",
                f"{self.summary.get('max_flowrate', 0):.2f}"
            ],
            [
                'Pressure',
                f"{self.summary.get('min_pressure', 0):.2f}",
                f"{self.summary.get('avg_pressure', 0):.2f}",
                f"{self.summary.get('max_pressure', 0):.2f}"
            ],
            [
                'Temperature',
                f"{self.summary.get('min_temperature', 0):.2f}",
                f"{self.summary.get('avg_temperature', 0):.2f}",
                f"{self.summary.get('max_temperature', 0):.2f}"
            ],
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.PRIMARY_COLOR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(self.LIGHT_BG)]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(self.BORDER_COLOR)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        return [
            Paragraph('Summary Statistics', heading_style),
            stats_table,
            Spacer(1, 0.4*inch)
        ]
    
    def _calculate_extended_statistics(self) -> Dict[str, Dict[str, float]]:
        """Calculate extended statistics including median and std deviation"""
        equipment_records = self.dataset.equipment_records.all()
        
        flowrates = []
        pressures = []
        temperatures = []
        
        for eq in equipment_records:
            flowrates.append(eq.flowrate)
            pressures.append(eq.pressure)
            temperatures.append(eq.temperature)
        
        def calc_stats(values):
            if not values:
                return {'median': 0, 'std_dev': 0, 'variance': 0}
            arr = np.array(values)
            return {
                'median': float(np.median(arr)),
                'std_dev': float(np.std(arr)),
                'variance': float(np.var(arr))
            }
        
        return {
            'flowrate': calc_stats(flowrates),
            'pressure': calc_stats(pressures),
            'temperature': calc_stats(temperatures)
        }
    
    def _create_enhanced_statistics_section(self, styles) -> list:
        """Create enhanced statistics section with median and std deviation"""
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor(self.SECONDARY_COLOR),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        ext_stats = self._calculate_extended_statistics()
        
        stats_data = [
            ['Parameter', 'Median', 'Std Deviation', 'Variance'],
            [
                'Flowrate',
                f"{ext_stats['flowrate']['median']:.2f}",
                f"{ext_stats['flowrate']['std_dev']:.2f}",
                f"{ext_stats['flowrate']['variance']:.2f}"
            ],
            [
                'Pressure',
                f"{ext_stats['pressure']['median']:.2f}",
                f"{ext_stats['pressure']['std_dev']:.2f}",
                f"{ext_stats['pressure']['variance']:.2f}"
            ],
            [
                'Temperature',
                f"{ext_stats['temperature']['median']:.2f}",
                f"{ext_stats['temperature']['std_dev']:.2f}",
                f"{ext_stats['temperature']['variance']:.2f}"
            ],
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.ACCENT_COLOR_2)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(self.LIGHT_BG)]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(self.BORDER_COLOR)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        return [
            Paragraph('Advanced Statistics', heading_style),
            stats_table,
            Spacer(1, 0.4*inch)
        ]
    
    def _create_equipment_type_breakdown(self, styles) -> list:
        """Create equipment type breakdown section"""
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor(self.SECONDARY_COLOR),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        equipment_records = self.dataset.equipment_records.all()
        type_distribution = {}
        type_stats = {}
        
        # Group equipment by type and calculate statistics
        for eq in equipment_records:
            if eq.equipment_type not in type_distribution:
                type_distribution[eq.equipment_type] = []
            type_distribution[eq.equipment_type].append({
                'flowrate': eq.flowrate,
                'pressure': eq.pressure,
                'temperature': eq.temperature
            })
        
        # Calculate averages per type
        for eq_type, records in type_distribution.items():
            avg_flowrate = sum(r['flowrate'] for r in records) / len(records)
            avg_pressure = sum(r['pressure'] for r in records) / len(records)
            avg_temperature = sum(r['temperature'] for r in records) / len(records)
            
            type_stats[eq_type] = {
                'count': len(records),
                'avg_flowrate': avg_flowrate,
                'avg_pressure': avg_pressure,
                'avg_temperature': avg_temperature
            }
        
        # Create table
        type_data = [['Equipment Type', 'Count', 'Avg Flowrate', 'Avg Pressure', 'Avg Temperature']]
        for eq_type in sorted(type_stats.keys()):
            stats = type_stats[eq_type]
            type_data.append([
                eq_type,
                str(stats['count']),
                f"{stats['avg_flowrate']:.2f}",
                f"{stats['avg_pressure']:.2f}",
                f"{stats['avg_temperature']:.2f}"
            ])
        
        type_table = Table(type_data, colWidths=[1.8*inch, 0.8*inch, 1.3*inch, 1.3*inch, 1.3*inch])
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.SECONDARY_COLOR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(self.LIGHT_BG)]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(self.BORDER_COLOR)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        return [
            Paragraph('Equipment Type Breakdown', heading_style),
            type_table,
            Spacer(1, 0.4*inch)
        ]
    
    def _create_charts_section(self, styles) -> list:
        """Create charts visualization section"""
        elements = []
        type_dist = self.summary.get('type_distribution', {})
        
        if not type_dist:
            return elements
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor(self.SECONDARY_COLOR),
            spaceAfter=12,
            spaceBefore=0,
            fontName='Helvetica-Bold'
        )
        
        try:
            # Bar chart - returns a list, so extend it
            bar_elements = self._create_bar_chart(heading_style, type_dist)
            elements.extend(bar_elements)
            
            # Pie chart - add page break and pie chart
            elements.append(PageBreak())
            pie_elements = self._create_pie_chart(heading_style, type_dist)
            elements.extend(pie_elements)
            
            # Parameter comparison - add page break and comparison chart
            elements.append(PageBreak())
            comp_elements = self._create_comparison_chart(heading_style)
            elements.extend(comp_elements)
        except Exception as e:
            logger.warning(f"Error creating charts: {str(e)}, continuing without charts")
            # Continue with other sections even if charts fail
        
        return elements
    
    def _create_bar_chart(self, heading_style, type_dist) -> list:
        """Create equipment type distribution bar chart"""
        fig, ax = plt.subplots(figsize=(8, 4))
        types = list(type_dist.keys())
        counts = list(type_dist.values())
        
        colors_list = self.COLORS
        bars = ax.bar(types, counts, color=colors_list[:len(types)], edgecolor='white', linewidth=2)
        
        ax.set_xlabel('Equipment Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title('Equipment Type Distribution', fontsize=14, fontweight='bold', pad=20)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        chart_path = os.path.join(self.temp_dir, 'bar_chart.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return [
            Paragraph('Equipment Type Distribution', heading_style),
            Spacer(1, 0.1*inch),
            Image(chart_path, width=6*inch, height=3*inch),
            Spacer(1, 0.3*inch)
        ]
    
    def _create_pie_chart(self, heading_style, type_dist) -> list:
        """Create type distribution pie chart"""
        fig, ax = plt.subplots(figsize=(7, 5))
        types = list(type_dist.keys())
        counts = list(type_dist.values())
        colors_list = self.COLORS
        
        pie_result = ax.pie(
            counts,
            labels=types,
            autopct='%1.1f%%',
            colors=colors_list[:len(types)],
            startangle=90,
            explode=[0.05] * len(types),
            shadow=True
        )
        
        wedges, texts, autotexts = pie_result if len(pie_result) == 3 else (pie_result[0], pie_result[1], [])
        
        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax.set_title('Type Distribution Breakdown', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        chart_path = os.path.join(self.temp_dir, 'pie_chart.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return [
            Paragraph('Type Distribution Breakdown', heading_style),
            Spacer(1, 0.1*inch),
            Image(chart_path, width=5*inch, height=3.5*inch),
            Spacer(1, 0.3*inch)
        ]
    
    def _create_comparison_chart(self, heading_style) -> list:
        """Create parameter comparison chart"""
        fig, ax = plt.subplots(figsize=(8, 4))
        parameters = ['Flowrate', 'Pressure', 'Temperature']
        min_vals = [
            self.summary.get('min_flowrate', 0),
            self.summary.get('min_pressure', 0),
            self.summary.get('min_temperature', 0)
        ]
        avg_vals = [
            self.summary.get('avg_flowrate', 0),
            self.summary.get('avg_pressure', 0),
            self.summary.get('avg_temperature', 0)
        ]
        max_vals = [
            self.summary.get('max_flowrate', 0),
            self.summary.get('max_pressure', 0),
            self.summary.get('max_temperature', 0)
        ]
        
        x = range(len(parameters))
        width = 0.25
        
        ax.bar([i - width for i in x], min_vals, width, label='Minimum', color=self.ACCENT_COLOR_1)
        ax.bar(x, avg_vals, width, label='Average', color=self.PRIMARY_COLOR)
        ax.bar([i + width for i in x], max_vals, width, label='Maximum', color=self.ACCENT_COLOR_2)
        
        ax.set_xlabel('Parameters', fontsize=12, fontweight='bold')
        ax.set_ylabel('Values', fontsize=12, fontweight='bold')
        ax.set_title('Parameter Comparison (Min/Avg/Max)', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(parameters)
        ax.legend(loc='upper left', framealpha=0.9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        chart_path = os.path.join(self.temp_dir, 'comparison_chart.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return [
            Paragraph('Parameter Comparison Analysis', heading_style),
            Spacer(1, 0.1*inch),
            Image(chart_path, width=6*inch, height=3*inch),
            Spacer(1, 0.3*inch)
        ]
    
    def _create_equipment_table(self, styles) -> list:
        """Create equipment records table"""
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor(self.SECONDARY_COLOR),
            spaceAfter=12,
            spaceBefore=0,
            fontName='Helvetica-Bold'
        )
        
        equipment = self.dataset.equipment_records.all()[:20]
        
        eq_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
        for eq in equipment:
            eq_data.append([
                eq.equipment_name[:25],
                eq.equipment_type,
                f"{eq.flowrate:.2f}",
                f"{eq.pressure:.2f}",
                f"{eq.temperature:.2f}"
            ])
        
        eq_table = Table(eq_data, colWidths=[2*inch, 1.3*inch, 1.1*inch, 1.1*inch, 1*inch])
        eq_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.SECONDARY_COLOR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(self.LIGHT_BG)]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(self.BORDER_COLOR)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        return [
            PageBreak(),
            Paragraph('Equipment Records Details', heading_style),
            Spacer(1, 0.2*inch),
            eq_table
        ]
    
    def _create_footer(self, styles) -> list:
        """Create footer section"""
        footer_text = (
            f'<para align=center><font size=8 color="#64748b">'
            f'Generated by ChemFlow Analytics Platform | {self.dataset.uploaded_at.strftime("%B %d, %Y")}'
            f'</font></para>'
        )
        return [Spacer(1, 0.5*inch), Paragraph(footer_text, styles['Normal'])]
    
    def _cleanup_temp_files(self) -> None:
        """Clean up temporary chart files"""
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(self.temp_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {str(e)}")
