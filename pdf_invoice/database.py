
class UpdateRecieptUrl():
    def update_invoice(self, invoice_name, file_url):
        from base.models import Sale
        sale = Sale.objects.get(id = invoice_name)
        sale.generated_invoice = file_url
        sale.save()

        return "Done"