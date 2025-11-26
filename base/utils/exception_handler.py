from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    print("Custom Exception Handler Invoked")
    print(f"Exception: {exc}")
    print(f"Context: {context}")
    print(f"Response: {response}")

    if response is None:
        return Response(
            {
                "status": "error",
                "message": "Internal server error."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    error_message = extract_error_message(response.data)

    response.data = {
        "status": "error",
        "message": error_message
    }

    return response


def extract_error_message(data):
    if isinstance(data, str):
        return data

    if "detail" in data:
        detail = data["detail"]
        if isinstance(detail, list):
            return detail[0]
        return detail
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) and value:
                return f"{key}: {value[0]}"
            if isinstance(value, dict):
                inner_key, inner_val = list(value.items())[0]
                if isinstance(inner_val, list):
                    return f"{inner_key}: {inner_val[0]}"
                return f"{inner_key}: {inner_val}"
            if isinstance(value, str):
                return f"{key}: {value}"

    if isinstance(data, list) and data:
        return data[0]
    return "An error occurred."
