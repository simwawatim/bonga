from flask import Blueprint, request, jsonify
import requests
from config import DJANGO_BASE_URL

sales_bp = Blueprint("sales_bp", __name__)

def safe_json(response):
    """Safely parse response as JSON, fallback to text or error."""
    try:
        return response.json()
    except ValueError:
        if response.text:
            return {"error": response.text}
        return {"error": "Empty response from server."}


@sales_bp.route("/api/sales-credit-note/", methods=["GET", "POST"])
def sales_credit_note():
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")
    headers = {"X-Tenant-ID": tenant_id} if tenant_id else {}
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    tenant_id = data.get("tenant_id")
    if not tenant_id:
        return jsonify({"status": "error", "message": "Missing tenant_id in body"}), 400
    headers = {"X-Tenant-ID": tenant_id}

    try:
        django_response = requests.post(
            f"{DJANGO_BASE_URL}/sale/credit-note-create/", json=data, headers=headers
        )
        return jsonify(safe_json(django_response)), django_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    

@sales_bp.route("/api/sales-debit-note/", methods=["POST"])
def sale_debit_note():
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")
    headers = {"X-Tenant-ID": tenant_id} if tenant_id else {}
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    tenant_id = data.get("tenant_id")
    if not tenant_id:
        return jsonify({"status": "error", "message": "Missing tenant_id in body"}), 400
    headers = {"X-Tenant-ID": tenant_id}

    try:
        django_response = requests.post(
            f"{DJANGO_BASE_URL}/sale/credit-note-create/", json=data, headers=headers
        )
        return jsonify(safe_json(django_response)), django_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@sales_bp.route("/api/sales/", methods=["GET", "POST"])
def sales():
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")
    headers = {"X-Tenant-ID": tenant_id} if tenant_id else {}

    if request.method == "GET":
        if not tenant_id:
            return jsonify({"error": "Missing tenant_id"}), 400
        try:
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/sales/", params=dict(request.args), headers=headers
            )
            return jsonify(safe_json(django_response)), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400
        tenant_id = data.get("tenant_id")
        if not tenant_id:
            return jsonify({"status": "error", "message": "Missing tenant_id in body"}), 400
        headers = {"X-Tenant-ID": tenant_id}

        try:
            django_response = requests.post(
                f"{DJANGO_BASE_URL}/sales/", json=data, headers=headers
            )
            return jsonify(safe_json(django_response)), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500



@sales_bp.route("/api/sales/<int:sale_id>/", methods=["GET", "PUT", "DELETE"])
def sale_by_id(sale_id):
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if not tenant_id:
        return jsonify({"error": "Missing tenant_id"}), 400
    headers = {"X-Tenant-ID": tenant_id}

    try:
        if request.method == "GET":
            django_response = requests.get(f"{DJANGO_BASE_URL}/sales/{sale_id}/", headers=headers)
        elif request.method == "PUT":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing JSON body"}), 400
            django_response = requests.put(
                f"{DJANGO_BASE_URL}/sales/{sale_id}/", json=data, headers=headers
            )
        elif request.method == "DELETE":
            django_response = requests.delete(f"{DJANGO_BASE_URL}/sales/{sale_id}/", headers=headers)
        else:
            return jsonify({"error": "Method not allowed"}), 405

        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
