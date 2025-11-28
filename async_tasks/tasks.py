from zra_client.client import ZRAClient
from celery import shared_task


class StockWorker(ZRAClient):
    @shared_task(bind=True)
    def sample_task(self, update_stock_payload, update_stock_master_items, created_by):
        try:
            response = self.update_stock_zra_client(update_stock_payload)

            if response.get("resultCd") == "000":
                print("Stock updated.")

                response = self.save_stock_master_zra_client(update_stock_master_items)

                if response.get("resultCd") == "000":
                    print("Stock master updated.")
                    return "done"
                else:
                    print("Failed to update stock master:", response)
                    return "failed"

            else:
                print(f"Failed to update stock: {response.get('resultMsg')}")
                return "failed"

        except Exception as e:
            print(f"Exception in background stock update task: {e}")
            return "error"
