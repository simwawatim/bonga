from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return Response({
            "message": getattr(response.data, "get", lambda k, d: d)("detail", "An error occurred."),
            "status": "fail",
            "data": None
        }, status=response.status_code)

    return response
