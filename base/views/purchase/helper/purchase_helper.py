from base.views.purchase.callers.manual_purchase import PurchaseInvoiceCreation
from base.views.sale.validations.item import ValidateItem
from base.utils.response_handler import api_response

MANUAL_PURCHASE_INSTANCE = PurchaseInvoiceCreation()

class PurchaseHelper():
    def format_purchase_data(self, data):
        
        supplierId = data.get("supplierId")
        spplrInvcNo = data.get("spplrInvcNo")
        pchsTyCd = data.get("pchsTyCd")
        regTyCd = data.get("regTyCd")
        pmtTyCd = data.get("pmtTyCd")
        pchsSttsCd = data.get("pchsSttsCd")
        items = data.get("items", [])

        if not items:
            return api_response("error", "No items provided.", 400, True)

        purchase_invoice_items = []

        for item in items:
            itemCode = item.get("itemCode")
            quantity = item.get("quantity")
            unitPrice = item.get("unitPrice")
            vatCd = item.get("vatCd")
            iplCd = item.get("iplCd")
            tlCd = item.get("tlCd")
            

            itemValidate = ValidateItem()
            if not itemValidate.validate_if_item_exists(itemCode):
                return api_response(status="error", message=f"Item '{itemCode}' does not exist.", status_code=404)

            

            item_details = itemValidate.get_item_details(itemCode)
            if not item_details:
                return api_response(status="error", message=f"Item details not found for '{itemCode}'.", status_code=404)

            if not quantity or quantity <= 0:
                return api_response(status="error", message=f"Invalid quantity for '{itemCode}'.", status_code=400)

            if not unitPrice or unitPrice <= 0:
                return api_response(status="error", message=f"Invalid unit price for '{itemCode}'.", status_code=400)

            VAT_LIST = ["A", "B", "C1", "C2", "C3", "D", "E", "RVAT"]
            if vatCd not in VAT_LIST:
                return api_response(status="error", message=f"Invalid VAT code '{vatCd}'.", status_code=400)

            
            purchase_invoice_items.append({
                "itemCode": itemCode,
                "itemName": item_details.get("itemName"),
                "qty": quantity,
                "itemClassCode": item_details.get("itemClassCd"),
                "product_type": item.get("product_type", "Finished Goods"),
                "packageUnitCode": item_details.get("itemPackingUnitCd"),
                "price": unitPrice,
                "VatCd": vatCd,
                "unitOfMeasure": item_details.get("itemUnitCd"),
                "IplCd": iplCd,
                "TlCd": tlCd
            })


            purchase_invoice_payload = {
                "supplierId": supplierId,
                "spplrInvcNo": spplrInvcNo,
                "pchsTyCd": pchsTyCd,
                "regTyCd": regTyCd,
                "pmtTyCd": pmtTyCd,
                "pchsSttsCd": pchsSttsCd,
                "purchase_invoice_items": purchase_invoice_items
            }

        results = MANUAL_PURCHASE_INSTANCE.create_manual_purchase_invoice(purchase_invoice_payload)
        return results
