from rest_framework import serializers
from base.models import Supplier

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by', 'updated_by')

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Supplier name is required.")
        if Supplier.objects.filter(name=value).exists():
            raise serializers.ValidationError("Supplier with this name already exists.")
        return value

    def validate_email(self, value):
        if value and Supplier.objects.filter(email=value).exists():
            raise serializers.ValidationError("Supplier with this email already exists.")
        return value
