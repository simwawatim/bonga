from rest_framework.response import Response

def api_response(status: str, data=None, status_code=200, is_error=False, message=None):
    response_payload = {
        "status": status,
        "message": message or ("An error occurred." if is_error else "Request was successful."),
        "data": {} if is_error else (data or {})
    }
    return Response(response_payload, status=status_code)
