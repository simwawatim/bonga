from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

DJANGO_BASE_URL = "http://localhost:8000" 
BASE_API = f"{DJANGO_BASE_URL}/api/v1/customers"


@app.route("/api/users/", methods=["GET", "POST"])
def users():
    tenant_id = request.args.get("tenant_id") or request.headers.get("X-Tenant-ID")
    if request.method == "GET":
        if not tenant_id:
            return jsonify({"error": "Missing tenant_id"}), 400
        headers = {"X-Tenant-ID": tenant_id}
        try:
            django_response = requests.get(f"{DJANGO_BASE_URL}/users/", params=dict(request.args), headers=headers)
            return jsonify(django_response.json()), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400
        tenant_id = data.get("tenant_id") or request.headers.get("X-Tenant-ID")
        if not tenant_id:
            return jsonify({"error": "Missing tenant_id"}), 400
        headers = {"X-Tenant-ID": tenant_id}
        try:
            django_response = requests.post(f"{DJANGO_BASE_URL}/users/create/", json=data, headers=headers)
            return jsonify(django_response.json()), django_response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/tenants/create/", methods=["POST"])
def create_tenant():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    try:
        django_response = requests.post(f"{BASE_API}/create-tenant/", json=data)
        return jsonify(django_response.json()), django_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tenants/", methods=["GET"])
def list_tenants():
    try:
        django_response = requests.get(f"{BASE_API}/tenants/")
        return jsonify(django_response.json()), django_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tenants/<int:id>/", methods=["GET", "PUT", "DELETE"])
def tenant_detail(id):
    data = request.get_json(silent=True)
    method = request.method

    try:
        if method == "GET":
            django_response = requests.get(f"{BASE_API}/tenants/{id}/")
        elif method == "PUT":
            django_response = requests.put(f"{BASE_API}/tenants/{id}/update/", json=data)
        elif method == "DELETE":
            django_response = requests.delete(f"{BASE_API}/tenants/{id}/delete/")
        else:
            return jsonify({"error": "Method not allowed"}), 405

        return jsonify(django_response.json()), django_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
