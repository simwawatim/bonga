from celery import shared_task
# from pdf_invoice.build import BuildPdf
from zra_client.client import ZRAClient
from pdf_invoice.make_invoice_pdf import BuildPdf

ZRA_INSTANCE = ZRAClient()

@shared_task
def update_stock_and_stock_master(update_stock_payload, update_stock_master_items):
    response = ZRA_INSTANCE.update_stock_zra_client(update_stock_payload)

    if response.get("resultCd") != "000":
        print(f"Failed to update stock: {response.get('resultMsg')}")
        return "failed"

    print("Stock updated.")
    response = ZRA_INSTANCE.save_stock_master_zra_client(update_stock_master_items)

    if response.get("resultCd") != "000":
        print("Failed to update stock master:", response)
        return "failed"

    print("Stock master updated.")
    return "done"


@shared_task
def generate_invoice_pdf(company_info, customer_info, invoice, pdf_items, sdc_data, payload, tenant_schema):
    builder = BuildPdf()
    builder.build_invoice(company_info, customer_info, invoice, pdf_items, sdc_data, payload, tenant_schema)
    return "PDF generated"
