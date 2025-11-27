from base.models import Sale
from django.core.exceptions import ObjectDoesNotExist
from base.utils.response_handler import api_response


class ValidateSale:

    def validate_if_sale_exists(self, sale_id):
        try:
            sale = Sale.objects.get(id=sale_id)
            print("Sale Found:", sale)
            return sale   
        except ObjectDoesNotExist:
            return None

        
    def get_sale_zra_rcpt_no(originalInvoice):
        try:
            sale = Sale.objects.get(id=originalInvoice)
            print("Full Sale Data:", sale.__dict__) 
            rcptNo = sale.rcpt_no
            print("Receipt No:", rcptNo)
            return rcptNo
        except ObjectDoesNotExist:
            return None
