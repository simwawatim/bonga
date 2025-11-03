import random
import string
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from base.models import Profile
from base.serializers.users.serializers import ProfileSerializer
from django_tenants.utils import connection, get_tenant_model

from zra_client.create_user import CreateUser



def generate_random_username(length=8):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

@api_view(['POST'])
def create_user(request):
    username = generate_random_username()
    email = request.data.get("email")
    password = request.data.get("password")
    is_active = request.data.get("use_yn")
    address = request.data.get("address")

    if not email or not password or address is None or is_active is None:
        return Response(
            {"error": "email, address, password and use_yn are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({"error": "email already exists"}, status=status.HTTP_400_BAD_REQUEST)

    zra_creator = CreateUser()
    last_user = User.objects.last()
    last_id = last_user.id if last_user else 0

    zra_response = zra_creator.prepare_save_user_payload(username, address, is_active, last_id)
    try:
        data = zra_response.json()
    except Exception:
        return Response({"error": "ZRA response is invalid"}, status=status.HTTP_400_BAD_REQUEST)

    if data.get("resultCd") != "000":
        return Response({"error": "ZRA user creation failed", "zra_result": data}, status=status.HTTP_400_BAD_REQUEST)

    from django.db import transaction
    with transaction.atomic():
        user = User.objects.create_user(username=username, email=email, password=password)
        profile = Profile.objects.create(user=user)

    tenant_model = get_tenant_model()
    tenant = tenant_model.objects.get(schema_name=connection.schema_name)

    return Response(
        {
            "message": "User and profile created successfully",
            "tenant_id": str(tenant.id),
            "tenant_name": getattr(tenant, "name", connection.schema_name),
            "user_id": user.id,
            "profile_id": profile.id,
        },
        status=status.HTTP_201_CREATED
    )



@api_view(['GET'])
def list_users(request):
    """
    List all users inside the current tenant schema,
    along with tenant ID for reference.
    """
    users = User.objects.all().values("id", "username", "email")

    tenant_model = get_tenant_model()
    tenant = tenant_model.objects.get(schema_name=connection.schema_name)

    return Response(
        {
            "tenant_id": str(tenant.id),
            "tenant_name": tenant.name if hasattr(tenant, "name") else connection.schema_name,
            "users": list(users),
        },
        status=status.HTTP_200_OK
    )
