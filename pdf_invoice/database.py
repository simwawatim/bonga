from django_tenants.utils import schema_context

from django.core.exceptions import ObjectDoesNotExist

class UpdateRecieptUrl:
    def update_invoice(self, invoice_name, file_url, tenant_schema):
        with schema_context(tenant_schema):
            try:
                from base.models import Sale
                sale = Sale.objects.get(id=invoice_name)
                sale.generated_invoice = file_url
                sale.save()
                return "Done"
            except ObjectDoesNotExist:
                return f"Error: Sale with id '{invoice_name}' does not exist."
            except Exception as e:
                return f"Error: {str(e)}"
