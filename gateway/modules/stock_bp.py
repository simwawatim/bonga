from flask import Blueprint, request, jsonify
import requests
from config import DJANGO_BASE_URL
from decorator.auth_decorator import jwt_required
from utils.header import get_headers

stock_bp = Blueprint("stock_bp", __name__)


def safe_json(response):
    """Safely parse response as JSON, fallback to text or error."""
    try:
        return response.json()
    except ValueError:
        if response.text:
            return {"error": response.text}
        return {"error": "Empty response from server."}



@stock_bp.route("/api/stockitems/", methods=["GET", "POST"])
@jwt_required
def stockitems():
    try:
        headers = get_headers()

        if request.method == "GET":
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/stockitems/",
                params=dict(request.args),
                headers=headers
            )
            return jsonify(safe_json(django_response)), django_response.status_code

        elif request.method == "POST":
            if not request.is_json:
                return jsonify({
                    "status": "error",
                    "message": "Content-Type must be application/json"
                }), 415

            data = request.get_json(silent=True)
            if not data:
                return jsonify({"error": "Missing JSON body"}), 400

            # If tenant_id is in POST data, override headers
            tenant_id = data.get("tenant_id")
            if tenant_id:
                headers = get_headers(tenant_id=tenant_id)

            django_response = requests.post(
                f"{DJANGO_BASE_URL}/stockitems/",
                json=data,
                headers=headers
            )
            return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request to Django API failed: {str(e)}"}), 500


@stock_bp.route("/api/stockitems/<int:stock_id>/", methods=["GET", "PUT", "DELETE"])
@jwt_required
def stockitem_by_id(stock_id):
    headers = get_headers()
    try:
        if request.method == "GET":
            django_response = requests.get(
                f"{DJANGO_BASE_URL}/stockitems/{stock_id}/",
                headers=headers
            )

        elif request.method == "PUT":
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"error": "Missing JSON body"}), 400
            django_response = requests.put(
                f"{DJANGO_BASE_URL}/stockitems/{stock_id}/",
                json=data,
                headers=headers
            )

        elif request.method == "DELETE":
            django_response = requests.delete(
                f"{DJANGO_BASE_URL}/stockitems/{stock_id}/",
                headers=headers
            )

        else:
            return jsonify({"error": "Method not allowed"}), 405

        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request to Django API failed: {str(e)}"}), 500
