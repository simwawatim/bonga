from base.models import Purchase, PurchaseItem
from base.views.purchase.callers.manual_purchase import PurchaseInvoiceCreation
from base.views.sale.validations.item import ValidateItem
from base.utils.response_handler import api_response

MANUAL_PURCHASE_INSTANCE = PurchaseInvoiceCreation()


class PurchaseHelper():

    def safe_decimal(self, value):
        if value in ["", None]:
            return 0
        return value

    def safe_string(self, value):
        if value is None:
            return ""
        return value


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
                return api_response(status="error",
                                    message=f"Item '{itemCode}' does not exist.",
                                    status_code=404)

            item_details = itemValidate.get_item_details(itemCode)
            if not item_details:
                return api_response(status="error",
                                    message=f"Item details not found for '{itemCode}'.",
                                    status_code=404)

            if not quantity or quantity <= 0:
                return api_response(status="error",
                                    message=f"Invalid quantity for '{itemCode}'.",
                                    status_code=400)

            if not unitPrice or unitPrice <= 0:
                return api_response(status="error",
                                    message=f"Invalid unit price for '{itemCode}'.",
                                    status_code=400)

            VAT_LIST = ["A", "B", "C1", "C2", "C3", "D", "E", "RVAT"]
            if vatCd not in VAT_LIST:
                return api_response(status="error",
                                    message=f"Invalid VAT code '{vatCd}'.",
                                    status_code=400)

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

        results = MANUAL_PURCHASE_INSTANCE.create_manual_purchase_invoice(
            purchase_invoice_payload
        )

        payload = results.get("data", {}).get("payload", {})
        print("Returned payload: ", payload)

        if not payload:
            return results

        purchase_obj = Purchase.objects.create(
            cisInvcNo=payload.get("cisInvcNo"),
            orgInvcNo=0,
            spplrTpin=payload.get("spplrTpin"),
            spplrBhfId=payload.get("bhfId"),
            spplrNm=payload.get("spplrNm"),
            spplrInvcNo=payload.get("spplrInvcNo"),
            regTyCd=payload.get("regTyCd"),
            pchsTyCd=payload.get("pchsTyCd"),
            rcptTyCd=payload.get("rcptTyCd"),
            pmtTyCd=payload.get("pmtTyCd"),
            pchsSttsCd=payload.get("pchsSttsCd"),
            cfmDt=payload.get("cfmDt"),
            pchsDt=payload.get("pchsDt"),
            cnclReqDt=self.safe_string(payload.get("cnclReqDt")),
            cnclDt=self.safe_string(payload.get("cnclDt")),
            totItemCnt=payload.get("totItemCnt"),
            totTaxblAmt=self.safe_decimal(payload.get("totTaxblAmt")),
            totTaxAmt=self.safe_decimal(payload.get("totTaxAmt")),
            totAmt=self.safe_decimal(payload.get("totAmt")),
            remark=self.safe_string(payload.get("remark")),
            regrNm=payload.get("regrNm"),
            regrId=payload.get("regrId"),
            modrNm=payload.get("modrNm"),
            modrId=payload.get("modrId"),
        )

        for item in payload.get("itemList", []):

            PurchaseItem.objects.create(
                purchase=purchase_obj,
                itemSeq=item.get("itemSeq"),
                itemCd=item.get("itemCd"),
                itemClsCd=item.get("itemClsCd"),
                itemNm=item.get("itemNm"),
                bcd=item.get("bcd", ""),
                pkgUnitCd=item.get("pkgUnitCd"),
                pkg=self.safe_decimal(item.get("pkg")),
                qtyUnitCd=item.get("qtyUnitCd"),
                qty=self.safe_decimal(item.get("qty")),
                prc=self.safe_decimal(item.get("prc")),
                splyAmt=self.safe_decimal(item.get("splyAmt")),
                dcRt=self.safe_decimal(item.get("dcRt")),
                dcAmt=self.safe_decimal(item.get("dcAmt")),
                taxTyCd=item.get("vatCatCd"),
                taxblAmt=self.safe_decimal(item.get("taxblAmt")),
                vatCatCd=item.get("vatCatCd"),
                taxAmt=self.safe_decimal(item.get("taxAmt")),
                totAmt=self.safe_decimal(item.get("totAmt")),
                iplCatCd=item.get("iplCatCd"),
                tlCatCd=item.get("tlCatCd"),
                exciseCatCd=item.get("exciseCatCd"),
                iplTaxblAmt=self.safe_decimal(item.get("iplTaxblAmt")),
                tlTaxblAmt=self.safe_decimal(item.get("tlTaxblAmt")),
                exciseTaxblAmt=self.safe_decimal(item.get("exciseTaxblAmt")),
                iplAmt=self.safe_decimal(item.get("iplAmt")),
                tlAmt=self.safe_decimal(item.get("tlAmt")),
                exciseTxAmt=self.safe_decimal(item.get("exciseTxAmt")),
            )

        return results
