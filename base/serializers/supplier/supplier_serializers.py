from rest_framework import serializers
from base.models import Supplier 

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by', 'updated_by')
