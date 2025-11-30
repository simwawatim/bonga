from rest_framework import serializers
from base.models import ItemStockMaster

class ItemStockMasterSerializer(serializers.ModelSerializer):
    item_code = serializers.CharField(source="item.code", read_only=True)
    item_name = serializers.CharField(source="item.name", read_only=True)

    class Meta:
        model = ItemStockMaster
        fields = [
            "id",
            "item_code",
            "item_name",
            "available_qty",
            "last_updated",
            "updated_by",
        ]
