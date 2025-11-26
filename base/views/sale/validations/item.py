from base.models import ItemInfo
from django.core.exceptions import ObjectDoesNotExist

class ValidateItem:
    def validate_if_item_exists(self, item_id):
        try:
            ItemInfo.objects.get(code=item_id)
            return True
        except ObjectDoesNotExist:
            return False
    def get_item_details(self, item_id):
        try:
            item = ItemInfo.objects.get(code=item_id)
            return {
                "itemName": item.name,
                "itemClassCd": item.itemClassCode,
                "itemPackingUnitCd": item.pkgUnitCd,
                "itemUnitCd": item.qtyUnitCd,
        
            }
        except ObjectDoesNotExist:
            return None