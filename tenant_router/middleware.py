# tenant_router/middleware.py
from django.http import JsonResponse
from django_tenants.utils import schema_context, get_tenant_model
from django.db import ProgrammingError
import json

class SmartTenantRoutingMiddleware:
    """
    Middleware that switches tenant schemas smartly:
    - Reads tenant_id from header, query param, or request body
    - Falls back to public schema if tenant not found or schema missing
    - Can be skipped per request via body key 'disable_smart_routing': true
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.TenantModel = get_tenant_model()

    def __call__(self, request):
        tenant_id = (
            request.headers.get("X-Tenant-ID") or
            request.GET.get("tenant_id")
        )

        body_data = {}
        # Try to get body data for POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_data = json.loads(request.body.decode("utf-8"))
            except Exception:
                pass

        # Check if middleware should be disabled via body
        if body_data.get("disable_smart_routing", False):
            return self.get_response(request)

        # Try to get tenant_id from body if not set
        if not tenant_id:
            tenant_id = body_data.get("tenant_id")

        # Default schema
        schema_name = "public"

        # Try to find tenant
        if tenant_id:
            try:
                tenant = self.TenantModel.objects.get(schema_name=tenant_id)
                schema_name = tenant.schema_name
            except self.TenantModel.DoesNotExist:
                return JsonResponse(
                    {"error": f"Tenant '{tenant_id}' not found"},
                    status=404
                )

        request.tenant_schema = schema_name

        # Smart schema context
        try:
            with schema_context(schema_name):
                response = self.get_response(request)
        except ProgrammingError as e:
            if 'does not exist' in str(e):
                return JsonResponse({
                    "error": f"Schema '{schema_name}' not initialized. "
                             f"Run migrations for this tenant."
                }, status=500)
            raise e

        return response
