from celery import shared_task
from zra_client.client import ZRAClient

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
