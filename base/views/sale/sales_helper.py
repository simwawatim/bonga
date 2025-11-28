from base.views.sale.validations.customer import ValidateCustomer
from base.views.sale.validations.item import ValidateItem
from base.views.sale.callers.normal_sale import NormaSale
from base.utils.response_handler import api_response
from base.models import Sale, SaleItem, ItemInfo
from async_tasks.tasks import sample_task

NORMAL_SALE_INSTANCE = NormaSale()


class NormalSaleHelper:

   

    def process_sale(self, sale_data):
        customerId = sale_data.get("customerId")
        currencyCd = sale_data.get("currencyCd")
        exchangeRt = sale_data.get("exchangeRt") or 1
        createBy = sale_data.get("createBy")
        lpoNumber = sale_data.get("lpoNumber")
        destnCountryCd = sale_data.get("destnCountryCd")
        items = sale_data.get("items", [])

        if not items or not isinstance(items, list):
            return api_response("error", "At least one sale item is required.", 400, True)

        if not createBy:
            return api_response("error", "Creator information is required.", 400, True)

        if not currencyCd:
            return api_response("error", "Currency code is required.", 400, True)

        allowedCurrencies = ["ZMW", "USD", "ZRA", "GBP", "CNY", "EUR"]
        if currencyCd not in allowedCurrencies:
            return api_response("error", f"Currency code '{currencyCd}' is not supported.", 400, True)

        if not customerId:
            return api_response("error", "Customer ID is required.", 400, True)

        validate_customer = ValidateCustomer()
        if not validate_customer.validate_if_customer_exists(customerId):
            return api_response("error", "Customer does not exist.", 404, True)

        customer_details = validate_customer.get_customer_details(customerId)

        # --- Prepare payload items ---
        sale_payload_items = []

        for item in items:
            itemCode = item.get("itemCode")
            quantity = item.get("quantity")
            unitPrice = item.get("unitPrice")
            vatCd = item.get("vatCd")
            iplCd = item.get("iplCd")
            tlCd = item.get("tlCd")

            itemValidate = ValidateItem()
            if not itemValidate.validate_if_item_exists(itemCode):
                return api_response("error", f"Item '{itemCode}' does not exist.", 404, True)

            item_details = itemValidate.get_item_details(itemCode)
            if not item_details:
                return api_response("error", f"Item details not found for '{itemCode}'.", 404, True)

            if not quantity or quantity <= 0:
                return api_response("error", f"Invalid quantity for '{itemCode}'.", 400, True)

            if not unitPrice or unitPrice <= 0:
                return api_response("error", f"Invalid unit price for '{itemCode}'.", 400, True)

            VAT_LIST = ["A", "B", "C1", "C2", "C3", "D", "E", "RVAT"]
            if vatCd not in VAT_LIST:
                return api_response("error", f"Invalid VAT code '{vatCd}'.", 400, True)

            if vatCd == "C2" and not lpoNumber:
                return api_response("error", "LPO number required for VAT C2.", 400, True)

            if vatCd == "C1" and not destnCountryCd:
                return api_response("error", "Destination country required for VAT C1.", 400, True)

            sale_payload_items.append({
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

        sale_payload = {
            "name": 1,
            "customerName": customer_details.get("customerName"),
            "customer_tpin": customer_details.get("custom_customer_tpin"),
            "destnCountryCd": destnCountryCd,
            "lpoNumber": lpoNumber,
            "currencyCd": currencyCd,
            "exchangeRt": exchangeRt,
            "created_by": createBy,
            "items": sale_payload_items
        }

        result = NORMAL_SALE_INSTANCE.send_sale_data(sale_payload)
        returnedPayload = result.get("payload", {})

        if result.get("resultCd") != "000":
            return api_response("fail", result.get("resultMsg", "Unknown error from ZRA"), 400)
        sale = Sale.objects.create(
            org_invc_no=returnedPayload.get("orgInvcNo"),
            cis_invc_no=returnedPayload.get("cisInvcNo"),
            cust_tpin=returnedPayload.get("custTpin"),
            cust_nm=returnedPayload.get("custNm"),
            sales_ty_cd=returnedPayload.get("salesTyCd"),
            rcpt_ty_cd=returnedPayload.get("rcptTyCd"),
            pmt_ty_cd=returnedPayload.get("pmtTyCd"),
            sales_stts_cd=returnedPayload.get("salesSttsCd"),
            cfm_dt=returnedPayload.get("cfmDt"),
            sales_dt=returnedPayload.get("salesDt"),
            tot_item_cnt=returnedPayload.get("totItemCnt"),
            tot_taxbl_amt=returnedPayload.get("totTaxblAmt"),
            tot_tax_amt=returnedPayload.get("totTaxAmt"),
            tot_amt=returnedPayload.get("totAmt"),
            rcpt_no=result.get("zraRcptNo"),
            qr_code_url=result.get("zraQrCodeUrl")
        )

        for item in returnedPayload.get("itemList", []):
            try:
                item_instance = ItemInfo.objects.get(code=item.get("itemCd"))
            except ItemInfo.DoesNotExist:
                return api_response("error", f"Item {item.get('itemCd')} not found in DB", 404, True)

            SaleItem.objects.create(
                sale=sale,
                item=item_instance,
                qty=item.get("qty"),
                prc=item.get("prc"),
                sply_amt=item.get("splyAmt"),
                vat_taxbl_amt=item.get("vatTaxblAmt"),
                vat_amt=item.get("vatAmt"),
                ipl_taxbl_amt=item.get("iplTaxblAmt", 0.0),
                ipl_amt=item.get("iplAmt", 0.0),
                tl_taxbl_amt=item.get("tlTaxblAmt", 0.0),
                tl_amt=item.get("tlAmt", 0.0),
                ecm_taxbl_amt=item.get("ecmTaxblAmt", 0.0),
                ecm_amt=item.get("ecmAmt", 0.0),
                tot_amt=item.get("totAmt"),
            )

        sample_task.delay()
        return api_response("success", "Sales Invoice created successfully", 200)
