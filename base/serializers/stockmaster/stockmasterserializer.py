from rest_framework import serializers
from base.models import ItemStockMaster

class ItemStockMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemStockMaster
        fields = '__all__'
        read_only_fields = ['last_updated']
