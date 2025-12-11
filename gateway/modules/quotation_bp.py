from flask import Blueprint, request, jsonify
import requests
from config import DJANGO_BASE_URL
from decorator.auth_decorator import jwt_required
from utils.header import get_headers

quotation_bp = Blueprint("quotation_bp", __name__)

def safe_json(response):
    """Safely parse response as JSON, fallback to text or error."""
    try:
        return response.json()
    except ValueError:
        if response.text:
            return {"error": response.text}
        return {"error": "Empty response from server."}

@quotation_bp.route("/api/quotation-create/", methods=["POST"])
@jwt_required
def quotation_create():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    headers = get_headers()

    try:
        django_response = requests.post(
            f"{DJANGO_BASE_URL}/quotations/create/",
            json=data,
            headers=headers
        )
        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500



@quotation_bp.route("/api/quotations/", methods=["GET"])
@jwt_required
def quotation_list():
    headers = get_headers()

    try:
        django_response = requests.get(
            f"{DJANGO_BASE_URL}/quotations/",
            params=dict(request.args),
            headers=headers
        )
        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500



@quotation_bp.route("/api/quotations/<int:quotation_id>/", methods=["GET"])
@jwt_required
def quotation_detail(quotation_id):
    headers = get_headers()

    try:
        django_response = requests.get(
            f"{DJANGO_BASE_URL}/quotations/{quotation_id}/",
            headers=headers
        )
        return jsonify(safe_json(django_response)), django_response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
