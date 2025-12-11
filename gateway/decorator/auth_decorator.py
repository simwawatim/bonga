from functools import wraps
from flask import Blueprint, request, jsonify
import requests
import jwt
from datetime import datetime, timezone
from config import DJANGO_BASE_URL

JWT_SECRET_KEY = "aP9v3x!2rTq7LzF8uWk6sN1bG4yH0jD5"
JWT_ALGORITHM = "HS256"

# ---------------- JWT DECORATOR ----------------
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "message": "Authorization header missing or invalid",
                "status": "fail",
                "data": None
            }), 401

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(tz=timezone.utc):
                return jsonify({
                    "message": "Token has expired",
                    "status": "fail",
                    "data": None
                }), 401

            tenant_id = payload.get("tenant_id")
            if not tenant_id:
                return jsonify({
                    "message": "tenant_id missing in token",
                    "status": "fail",
                    "data": None
                }), 401

            # attach user info to request
            request.user = {
                "user_id": payload.get("user_id"),
                "tenant_id": tenant_id,
                "tenant_name": payload.get("tenant_name")
            }

        except jwt.ExpiredSignatureError:
            return jsonify({
                "message": "Token has expired",
                "status": "fail",
                "data": None
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "message": "Invalid token",
                "status": "fail",
                "data": None
            }), 401

        return f(*args, **kwargs)
    return decorated

