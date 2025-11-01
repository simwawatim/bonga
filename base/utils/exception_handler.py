from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom exception handler to return consistent single-error responses.
    """
    # Let DRF handle the default exception first
    response = exception_handler(exc, context)

    if response is not None:
        # If serializer validation error
        if isinstance(response.data, dict):
            error_message = None

            # Handle ValidationError responses like {'field': ['error message']}
            for key, value in response.data.items():
                if isinstance(value, list) and value:
                    error_message = f"{key}: {value[0]}"
                    break
                elif isinstance(value, dict):
                    # nested error dicts
                    inner_key, inner_val = list(value.items())[0]
                    error_message = f"{inner_key}: {inner_val[0]}"
                    break
                elif isinstance(value, str):
                    error_message = f"{key}: {value}"
                    break

            # Replace response with cleaner JSON
            response.data = {
                "error": error_message or "An unknown error occurred."
            }

        else:
            # If it's not a dict (e.g. custom raise serializers.ValidationError("message"))
            response.data = {"error": str(response.data)}

    else:
        # Non-DRF exceptions (e.g., runtime errors)
        response = Response(
            {"error": "An internal server error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
