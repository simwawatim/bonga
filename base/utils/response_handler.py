from rest_framework.response import Response

def api_response(status: str, data=None, status_code=200, is_error=False):

    if is_error:
        return Response({
            "status": status,
            "message": data or "An error occurred."
        }, status=status_code)
    
    return Response({
        "status": status,
        "data": data or {}
    }, status=status_code)
