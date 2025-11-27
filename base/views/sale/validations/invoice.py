from base.models import Sale
from django.core.exceptions import ObjectDoesNotExist

class ValidateSale():
    def validate_if_sale_exists(self, sale_id):
        try:
            Sale.objects.get(id=sale_id)
            return True
        except ObjectDoesNotExist:
            return False
        
    def get_sale_zra_rcpt_no(self, sale_id):
        try:
            sale = Sale.objects.get(id=sale_id)
            return sale.rcpt_no
        except ObjectDoesNotExist:
            return None

