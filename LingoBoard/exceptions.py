from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status as drf_status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return Response({
            'status': response.status_code,
            'errormessage': response.data.get('detail', str(response.data))
        }, status=response.status_code)

    # If DRF couldn't handle it (e.g., server error), return 500
    return Response({
        'status': 500,
        'errormessage': str(exc)
    }, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)