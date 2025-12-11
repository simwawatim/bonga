from flask import Blueprint, request, jsonify
def get_headers(tenant_id=None):
    tenant_id = tenant_id or request.user.get("tenant_id")
    jwt_token = request.headers.get("Authorization")
    return {"X-Tenant-ID": tenant_id, "Authorization": jwt_token}
