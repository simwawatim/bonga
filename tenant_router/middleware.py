from django_tenants.utils import schema_context, get_tenant_model
from django.db import ProgrammingError
from django.http import JsonResponse
import json

class SmartTenantRoutingMiddleware:
    """
    Middleware to switch tenant based on tenant ID passed in headers, query params, or request body.
    Defaults to 'public' schema if no tenant ID is provided.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.TenantModel = get_tenant_model()

    def __call__(self, request):
        tenant_id = (
            request.headers.get("X-Tenant-ID")
            or request.GET.get("tenant_id")
        )

        # Try to get tenant_id from JSON body for POST/PUT/PATCH
        if not tenant_id and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = json.loads(request.body.decode("utf-8"))
                tenant_id = body.get("tenant_id")
            except Exception:
                pass

        # Default to public schema if no tenant_id
        if not tenant_id:
            request.tenant_schema = "public"
            with schema_context("public"):
                return self.get_response(request)

        # Validate tenant_id is numeric
        try:
            tenant_id_int = int(tenant_id)
        except ValueError:
            return JsonResponse({"error": f"Invalid tenant_id '{tenant_id}', must be numeric"}, status=400)

        # Try to find tenant by ID
        try:
            tenant = self.TenantModel.objects.get(id=tenant_id_int)
            schema_name = tenant.schema_name
        except self.TenantModel.DoesNotExist:
            return JsonResponse({"error": f"Tenant with ID '{tenant_id}' not found"}, status=404)

        request.tenant_schema = schema_name

        # Switch schema and handle database errors
        try:
            with schema_context(schema_name):
                response = self.get_response(request)
        except ProgrammingError as e:
            # Handle missing schema or tables
            if 'does not exist' in str(e):
                return JsonResponse({
                    "error": f"Schema '{schema_name}' not initialized or missing tables. "
                             f"Run migrations for this tenant."
                }, status=500)
            raise e

        return response
