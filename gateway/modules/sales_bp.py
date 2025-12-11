from flask import Blueprint, request, jsonify
import requests
from config import DJANGO_BASE_URL
from decorator.auth_decorator import jwt_required
from utils.header import get_headers

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
@jwt_required
def sales_credit_note():
    headers = get_headers()
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400


    try:
        django_response = requests.post(
            f"{DJANGO_BASE_URL}/sale/credit-note-create/", json=data, headers=headers
        )
        return jsonify(safe_json(django_response)), django_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    

@sales_bp.route("/api/sales-debit-note/", methods=["POST"])
@jwt_required
def sale_debit_note():
    headers = get_headers()
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400


    try:
        django_response = requests.post(
            f"{DJANGO_BASE_URL}/sale/debit-note-create/", json=data, headers=headers
        )
        return jsonify(safe_json(django_response)), django_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@sales_bp.route("/api/sales/", methods=["GET", "POST"])
@jwt_required
def sales():
    headers = get_headers()

    if request.method == "GET":
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

        try:
            django_response = requests.post(
                f"{DJANGO_BASE_URL}/sales/", json=data, headers=headers
            )
            return jsonify(safe_json(django_response)), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500



@sales_bp.route("/api/sales/<int:sale_id>/", methods=["GET", "PUT", "DELETE"])
@jwt_required
def sale_by_id(sale_id):
    headers = get_headers()

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
