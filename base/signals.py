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

    stock_item = instance
    item = stock_item.item
    master, _ = ItemStockMaster.objects.get_or_create(item=item)

    total_qty = item.details.aggregate(total=models.Sum("qty"))["total"] or 0

    master.available_qty = total_qty
    master.updated_by = stock_item.created_by
    master.save()
