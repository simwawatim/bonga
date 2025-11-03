from django_tenants.utils import schema_context, get_tenant_model
from django.db import connection, ProgrammingError
from django.http import JsonResponse
import json

class SmartTenantRoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.TenantModel = get_tenant_model()

    def __call__(self, request):
        tenant_id = (
            request.headers.get("X-Tenant-ID")
            or request.GET.get("tenant_id")
        )

        if not tenant_id and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = json.loads(request.body.decode("utf-8"))
                tenant_id = body.get("tenant_id")
            except Exception:
                pass

        # Default to public
        if not tenant_id:
            request.tenant_schema = "public"
            with schema_context("public"):
                return self.get_response(request)

        # Try to find tenant schema
        try:
            tenant = self.TenantModel.objects.get(schema_name=tenant_id)
            schema_name = tenant.schema_name
        except self.TenantModel.DoesNotExist:
            return JsonResponse({"error": f"Tenant '{tenant_id}' not found"}, status=404)

        request.tenant_schema = schema_name

        # Smart context switch
        try:
            with schema_context(schema_name):
                response = self.get_response(request)
        except ProgrammingError as e:
            # Handle missing schema or tables
            if 'does not exist' in str(e):
                return JsonResponse({
                    "error": f"Schema '{schema_name}' not initialized. "
                             f"Run migrations for this tenant."
                }, status=500)
            raise e

        return response
