import random
import string
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from base.models import Profile
from base.serializers.users.serializers import LoginSerializer, ProfileSerializer
from django_tenants.utils import connection, get_tenant_model
from django.contrib.auth import authenticate
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django_tenants.utils import connection, get_tenant_model
from zra_client.create_user import CreateUser
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication



def generate_random_username(length=8):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
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
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_users(request):
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

class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=user_obj.username, password=password)
        if not user:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            tenant_model = get_tenant_model()
            tenant = tenant_model.objects.get(schema_name=connection.schema_name)
        except tenant_model.DoesNotExist:
            return Response({"error": "Tenant not found"}, status=status.HTTP_404_NOT_FOUND)

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        access_token["tenant_id"] = str(tenant.id)
        access_token["tenant_name"] = getattr(tenant, "name", connection.schema_name)

        return Response({
            "access": str(access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "tenant": {
                "id": str(tenant.id),
                "name": getattr(tenant, "name", connection.schema_name)
            }
        }, status=status.HTTP_200_OK)