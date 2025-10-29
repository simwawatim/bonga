from rest_framework import serializers
from .models import Client, Domain

class TenantCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    schema_name = serializers.CharField(max_length=50)
    paid_until = serializers.DateField()
    on_trial = serializers.BooleanField(default=True)
    zra_tpin = serializers.CharField(max_length=20)
    business_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    business_address = serializers.CharField(required=False, allow_blank=True)
    contact_email = serializers.EmailField(required=False, allow_blank=True)
    contact_phone = serializers.CharField(required=False, allow_blank=True)
    domain = serializers.CharField(max_length=100)

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = "__all__"
