# tenant_router/public_middleware.py
from django.http import JsonResponse
from django_tenants.utils import schema_context
from django.db import ProgrammingError

class PublicTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant_schema = "public"

        try:
            with schema_context("public"):
                response = self.get_response(request)
        except ProgrammingError as e:
            if 'does not exist' in str(e):
                return JsonResponse({
                    "error": "Public schema not initialized. "
                             "Run migrations for the public schema."
                }, status=500)
            raise e

        return response
