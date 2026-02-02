"""
API ViewSets for equipment data management
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
import logging

from .models import Dataset
from .serializers import DatasetDetailSerializer, DatasetListSerializer
from .services import DatasetService
from .exceptions import (
    FileFormatError,
    CSVValidationError,
    PDFGenerationError,
)
from .pdf_service import PDFReportGenerator

logger = logging.getLogger(__name__)


class DatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chemical equipment datasets.
    
    Provides CRUD operations and custom actions for:
    - CSV file upload and processing
    - Data analysis and statistics
    - PDF report generation
    """
    
    queryset = Dataset.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return DatasetDetailSerializer
        return DatasetDetailSerializer
    
    def list(self, request):
        """Get last 5 datasets ordered by upload time"""
        datasets = Dataset.objects.all().order_by('-uploaded_at')[:5]
        serializer = self.get_serializer(datasets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Upload and process CSV file.
        Expected columns: Equipment Name, Type, Flowrate, Pressure, Temperature
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        csv_file = request.FILES['file']
        
        try:
            # Validate and parse CSV using service
            df = DatasetService.validate_and_parse_csv(csv_file)
            
            # Create dataset with equipment records
            dataset = DatasetService.create_dataset_with_equipment(
                user=request.user if request.user.is_authenticated else None,
                filename=csv_file.name,
                df=df
            )
            
            # Cleanup old datasets (non-blocking)
            try:
                DatasetService.cleanup_old_datasets()
            except Exception as cleanup_error:
                logger.warning(f"Non-critical cleanup error: {str(cleanup_error)}")
            
            # Return created dataset with success response
            serializer = self.get_serializer(dataset)
            return Response(
                {
                    'success': True,
                    'message': f'Dataset "{csv_file.name}" uploaded successfully with {dataset.total_records} records',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except FileFormatError as e:
            logger.warning(f"File format error: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': str(e),
                    'type': 'format_error'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except CSVValidationError as e:
            logger.warning(f"CSV validation error: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': str(e),
                    'type': 'validation_error'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error during CSV upload: {str(e)}", exc_info=True)
            return Response(
                {
                    'success': False,
                    'error': 'Failed to process CSV file. Please check the format and try again.',
                    'details': str(e) if not isinstance(e, (FileFormatError, CSVValidationError)) else None,
                    'type': 'processing_error'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        """
        Generate comprehensive PDF report with charts and statistics.
        
        Report includes:
        - Dataset information and upload metadata
        - Summary statistics table
        - Equipment type distribution chart
        - Parameter comparison analysis
        - Complete equipment records table
        """
        try:
            dataset = self.get_object()
            
            # Generate PDF using service
            pdf_generator = PDFReportGenerator(dataset)
            pdf_buffer = pdf_generator.generate()
            
            # Return PDF response
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = (
                f'attachment; filename="chemflow_report_{dataset.id}.pdf"'
            )
            return response
            
        except Dataset.DoesNotExist:
            logger.warning(f"Dataset not found: {pk}")
            return Response(
                {'error': 'Dataset not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except PDFGenerationError as e:
            logger.error(f"PDF generation error: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error generating PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error during PDF generation: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Error generating PDF report'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )