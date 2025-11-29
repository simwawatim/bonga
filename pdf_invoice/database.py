from django_tenants.utils import schema_context


class UpdateRecieptUrl:
    def update_invoice(self, invoice_name, file_url, tenant_schema):
        try:
            with schema_context(tenant_schema):
                from base.models import Sale
                sale = Sale.objects.get(cis_invc_no=invoice_name)
                sale.generated_invoice = file_url
                sale.save()
            return "Done"
        except Sale.DoesNotExist:
            return f"Sale with invoice {invoice_name} does not exist in schema {tenant_schema}"
        except Exception as e:
            return f"Error updating invoice: {str(e)}"
