from rest_framework import serializers
from base.models import Quotation, QuotationItem
from base.models import ItemInfo, CustomerInfo


class QuotationItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = ["item", "qty", "price", "supply_amount", "tax_amount", "total_amount", "vat_category"]


class QuotationCreateSerializer(serializers.ModelSerializer):
    items = QuotationItemCreateSerializer(many=True)

    class Meta:
        model = Quotation
        fields = [
            "customer",
            "quotation_date",
            "expiry_date",
            "remark",
            "items",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        request = self.context["request"]

        # Auto-generate quotation number
        last_q = Quotation.objects.order_by("id").last()
        next_no = f"QT-{(last_q.id + 1) if last_q else 1:05d}"

        quotation = Quotation.objects.create(
            quotation_no=next_no,
            created_by=request.user,
            updated_by=request.user,
            **validated_data
        )

        total_items = 0
        total_taxable = 0
        total_tax = 0
        total_amount = 0

        for item_data in items_data:
            q_item = QuotationItem.objects.create(quotation=quotation, **item_data)

            total_items += 1
            total_taxable += q_item.supply_amount
            total_tax += q_item.tax_amount
            total_amount += q_item.total_amount

        quotation.total_items = total_items
        quotation.total_taxable = total_taxable
        quotation.total_tax = total_tax
        quotation.total_amount = total_amount
        quotation.save()

        return quotation

class QuotationListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Quotation
        fields = [
            "id",
            "quotation_no",
            "customer_name",
            "quotation_date",
            "total_items",
            "total_amount",
            "status",
            "created_at",
        ]


class QuotationItemDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)

    class Meta:
        model = QuotationItem
        fields = [
            "item",
            "item_name",
            "qty",
            "price",
            "supply_amount",
            "tax_amount",
            "total_amount",
            "vat_category",
        ]


class QuotationDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    customer_tpin = serializers.CharField(source="customer.customerTpin", read_only=True)
    items = QuotationItemDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Quotation
        fields = [
            "id",
            "quotation_no",
            "customer",
            "customer_name",
            "customer_tpin",
            "quotation_date",
            "expiry_date",
            "total_items",
            "total_taxable",
            "total_tax",
            "total_amount",
            "status",
            "created_at",
            "updated_at",
            "items"
        ]
