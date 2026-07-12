import os
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Handle DB IntegrityErrors explicitly mapping them to 409 XML standard responses
    if isinstance(exc, IntegrityError):
        error_str = str(exc)
        if 'one_active_allocation_per_asset' in error_str:
            return Response({
                'error': {
                    'code': 'ALREADY_ALLOCATED',
                    'message': 'Asset is already allocated',
                    'details': {}
                }
            }, status=status.HTTP_409_CONFLICT)
        elif 'no_overlap' in error_str:
            return Response({
                'error': {
                    'code': 'SLOT_UNAVAILABLE',
                    'message': 'Requested time overlaps an existing booking',
                    'details': {}
                }
            }, status=status.HTTP_409_CONFLICT)
        else:
            return Response({
                'error': {
                    'code': 'DATABASE_ERROR',
                    'message': 'Database integrity error',
                    'details': {}
                }
            }, status=status.HTTP_400_BAD_REQUEST)

    if response is not None:
        # Wrap DRF exceptions in the standard error envelope
        code = getattr(exc, 'default_code', 'error').upper()
        # If the response is already properly formatted, pass it along
        if isinstance(response.data, dict) and 'error' in response.data:
            pass
        else:
            original_data = response.data
            response.data = {
                'error': {
                    'code': code,
                    'message': str(exc),
                    'details': original_data
                }
            }
    
    return response
