import sys

from django.http import JsonResponse
from rest_framework import status


def handler404(request, exception):
    return JsonResponse({
        'error': 'The resource was not found'
    }, status=status.HTTP_404_NOT_FOUND)


def handler500(request):
    type_, value, traceback = sys.exc_info()
    return JsonResponse({
        'error': 'Server error',
        'details': str(value)
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
