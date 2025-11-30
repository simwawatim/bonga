from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StockItem, ItemStockMaster
from base import models

@receiver(post_save, sender=StockItem)
def update_stock_master(sender, instance, created, **kwargs):
    """
    Whenever a StockItem (new purchase or sale) is created,
    update ItemStockMaster available quantity.
    """

    print("\n--- STOCK MASTER SIGNAL TRIGGERED ---")
    print(f"StockItem ID: {instance.id}")
    print(f"Created: {created}")
    print(f"Item: {instance.item} (ID: {instance.item.id})")

    stock_item = instance
    item = stock_item.item

    # Get or create master
    master, created_master = ItemStockMaster.objects.get_or_create(item=item)
    print(f"ItemStockMaster found or created: {master.id}, new={created_master}")

    # Aggregate qty from details
    total_qty = item.details.aggregate(total=models.Sum("qty"))["total"] or 0
    print(f"Total aggregated qty: {total_qty}")

    # Update master
    master.available_qty = total_qty
    master.updated_by = stock_item.created_by

    master.save()

    print(f"Updated master.available_qty = {master.available_qty}")
    print(f"Updated master.updated_by   = {master.updated_by}")
    print("--- STOCK MASTER SIGNAL END ---\n")
