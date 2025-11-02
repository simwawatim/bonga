from rest_framework import serializers
from base.models import ItemInfo

class ItemInfoSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=False, allow_blank=True) 

    class Meta:
        model = ItemInfo
        fields = '__all__'

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_qty(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

    def validate_code(self, value):
        if value and not value.strip():
            raise serializers.ValidationError("Item code cannot be blank.")
        return value
