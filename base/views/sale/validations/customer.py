from base.models import CustomerInfo
from django.core.exceptions import ObjectDoesNotExist

class ValidateCustomer:
    def validate_if_customer_exists(self, customer_id):
        try:
            CustomerInfo.objects.get(id=customer_id)
            return True
        except ObjectDoesNotExist:
            return False
    def get_customer_details(self, customer_id):
        try:
            customer = CustomerInfo.objects.get(id=customer_id)
            return {
                "customerName": customer.name,
                "customerTpin": customer.customerTpin,
            }
        except ObjectDoesNotExist:
            return None