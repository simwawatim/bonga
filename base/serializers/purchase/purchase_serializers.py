from rest_framework import serializers
from base.models import Purchase, PurchaseItem


class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = '__all__'
        read_only_fields = ['purchase']


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True)

    class Meta:
        model = Purchase
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase = Purchase.objects.create(**validated_data)

        for item in items_data:
            PurchaseItem.objects.create(purchase=purchase, **item)

        return purchase

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()


        if items_data is not None:
            instance.items.all().delete() 
            for item in items_data:
                PurchaseItem.objects.create(purchase=instance, **item)

        return instance
