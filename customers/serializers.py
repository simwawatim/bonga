from rest_framework import serializers
from .models import Client, Domain
from datetime import date


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

    def validate_schema_name(self, value):
        if Client.objects.filter(schema_name=value).exists():
            raise serializers.ValidationError("Schema name already exists.")
        return value

    def validate_paid_until(self, value):
        if value < date.today():
            raise serializers.ValidationError("paid_until must be a future date.")
        return value

    def validate_zra_tpin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("ZRA TPIN must be numeric.")
        if len(value) != 10:
            raise serializers.ValidationError("ZRA TPIN must be 10 digits.")
        return value

    def validate_domain(self, value):
        if Domain.objects.filter(domain=value).exists():
            raise serializers.ValidationError("Domain already exists.")
        return value


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = "__all__"
