from flask import Blueprint, request, jsonify
import requests
from config import BASE_API, DJANGO_BASE_URL
from decorator.auth_decorator import jwt_required

customers_bp = Blueprint("customers_bp", __name__)

def safe_json(response):
    """Safely parse response as JSON, fallback to text or error."""
    try:
        return response.json()
    except ValueError:

        if response.text:
            return {"error": response.text}
        return {"error": "Empty response from server."}

@customers_bp.route("/api/customers/", methods=["GET", "POST"])
@jwt_required
def customers():
    tenant_id = request.user.get("tenant_id")
    jwt_token = request.headers.get("Authorization")

    headers = {
        "X-Tenant-ID": tenant_id,
        "Authorization": jwt_token  
    }

    if request.method == "GET":
        if not tenant_id:
            return jsonify({"error": "Missing tenant_id"}), 400
        try:
            django_response = requests.get(f"{DJANGO_BASE_URL}/customers/", params=dict(request.args), headers=headers)
            return django_response.json(), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        try:
            django_response = requests.post(f"{DJANGO_BASE_URL}/customers/", json=data, headers=headers)
            return django_response.json(), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

@customers_bp.route("/api/customers/<int:customer_id>/", methods=["GET", "PUT", "DELETE"])
@jwt_required
def customer_by_id(customer_id):
    tenant_id = request.user.get("tenant_id")
    jwt_token = request.headers.get("Authorization")
    headers = {
        "X-Tenant-ID": tenant_id,
        "Authorization": jwt_token  
    }
    try:
        if request.method == "GET":
            django_response = requests.get(f"{DJANGO_BASE_URL}/customers/{customer_id}/", headers=headers)
        elif request.method == "PUT":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing JSON body"}), 400
            django_response = requests.put(f"{DJANGO_BASE_URL}/customers/{customer_id}/", json=data, headers=headers)
        elif request.method == "DELETE":
            django_response = requests.delete(f"{DJANGO_BASE_URL}/customers/{customer_id}/", headers=headers)
        else:
            return jsonify({"error": "Method not allowed"}), 405

        return django_response.json(), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
