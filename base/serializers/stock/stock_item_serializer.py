from rest_framework import serializers
from django_tenants.utils import get_tenant_model, schema_context
from base.models import StockItem

class StockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem
        fields = '__all__'

    def validate_stock_item(self, value):
        tenant = get_tenant_model().objects.get(schema_name=self.context['tenant_id'])
        with schema_context(tenant.schema_name):
            if not StockItem.objects.filter(pk=value.pk).exists():
                raise serializers.ValidationError("Stock item does not exist in this tenant.")
        return value