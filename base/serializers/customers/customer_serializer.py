from rest_framework import serializers
from base.models import CustomerInfo

class CustomerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerInfo
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by', 'created_at')
