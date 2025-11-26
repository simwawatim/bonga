from base.views.sale.validations.customer import ValidateCustomer
from base.views.sale.validations.item import ValidateItem
from base.utils.response_handler import api_response
from base.views.sale.callers.normal_sale import NormaSale
NORMAL_SALE_INSTANCE = NormaSale()
class NormalSaleHelper:
    def process_sale(self, sale_data):
        customerId = sale_data.get("customerId")
        currencyCd = sale_data.get("currencyCd")
        exchangeRt = sale_data.get("exchangeRt")
        createBy = sale_data.get("createBy")
        lpoNumber = sale_data.get("lpoNumber")
        destnCountryCd = sale_data.get("destnCountryCd")
        items = sale_data.get("items", [])

        if not items or not isinstance(items, list):
            return api_response(
                status="error",
                message="At least one sale item is required.",
                status_code=400,
                is_error=True
            )

        if not exchangeRt:
            exchangeRt = 1

        if not createBy:
            return api_response(
                status="error",
                message="Creator information is required.",
                status_code=400,
                is_error=True
            )
        if not currencyCd:
            return api_response(
                status="error",
                message="Currency code is required.",
                status_code=400,
                is_error=True
            )

        allowedCurrencies = ["ZMW", "USD", "ZRA", "GBP", "CNY", "EUR"]

        if currencyCd not in allowedCurrencies:
            return api_response(
                status="error",
                message=f"Currency code '{currencyCd}' is not supported.",
                status_code=400,
                is_error=True
            )

        if not customerId:
            return api_response(
                status="error",
                message="Customer ID is required.",
                status_code=400,
                is_error=True
            )
        
        validate_customer = ValidateCustomer()
        customer_exists = validate_customer.validate_if_customer_exists(customerId)
        if not customer_exists:
            return api_response(
                status="error",
                message="Customer does not exist.",
                status_code=404,
                is_error=True
            )

        sale_payload_items = []
        for item in items:
            itemCode = item.get("itemCode")
            quantity = item.get("quantity")
            unitPrice = item.get("unitPrice")
            vatCd = item.get("vatCd")
            iplCd = item.get("iplCd")
            tlCd = item.get("tlCd")
            itemValidate = ValidateItem()
            item_exists = itemValidate.validate_if_item_exists(itemCode)

            if not item_exists:
                return api_response(
                    status="error",
                    message=f"Item with code '{itemCode}' does not exist.",
                    status_code=404,
                    is_error=True
                )
            
            if not itemCode:
                return api_response(
                    status="error",
                    message="Item code is required for each sale item.",
                    status_code=400,
                    is_error=True
                )
            item_details = itemValidate.get_item_details(itemCode)
            if not item_details:
                return api_response(
                    status="error",
                    message=f"Item details not found for item code '{itemCode}'.",
                    status_code=404,
                    is_error=True
                )
            if not quantity or quantity <= 0:
                return api_response(
                    status="error",
                    message=f"Invalid quantity for item '{itemCode}'.",
                    status_code=400,
                    is_error=True
                )
            if not unitPrice or unitPrice <= 0:
                return api_response(
                    status="error",
                    message=f"Invalid unit price for item '{itemCode}'.",
                    status_code=400,
                    is_error=True
                )
            if not vatCd:
                return api_response(
                    status="error",
                    message=f"VAT code is required for item '{itemCode}'.",
                    status_code=400,
                    is_error=True
                )
            VAT_LIST = ["A", "B", "C1", "C2", "C3", "D", "E", "RVAT"]
            if vatCd not in VAT_LIST:
                return api_response(
                    status="error",
                    message=f"Invalid VAT code '{vatCd}' for item '{itemCode}'.",
                    status_code=400,
                    is_error=True
                )
            if vatCd == "C2":
                if not lpoNumber:
                    return api_response(
                        status="error",
                        message=f"LPO number is required for VAT code 'C2' on item '{itemCode}'.",
                        status_code=400,
                        is_error=True
                    )
            if vatCd == "C1":
                if destnCountryCd is None or destnCountryCd == "":
                    return api_response(
                        status="error",
                        message=f"Destination country code is required for VAT code 'C1' on item '{itemCode}'.",
                        status_code=400,
                        is_error=True
                    )
        
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
            
            getCustomerData = validate_customer.get_customer_details(customerId)
            sale_payload = {
                "name": 1,
                "customerName": getCustomerData.get("customer_name"),
                "customer_tpin": getCustomerData.get("custom_customer_tpin"),
                "destnCountryCd": destnCountryCd,
                "lpoNumber": lpoNumber,
                # "isExport": isExport,
                # "isRvatAgent": isRvatSale,
                # "principalId": principalId,
                "currencyCd": currencyCd,
                "exchangeRt": exchangeRt,
                "created_by": createBy,
                "items": sale_payload_items
            }
            

        print("Sale data:", sale_data)
        print("Prepared sale items:", sale_payload_items)
        result = NORMAL_SALE_INSTANCE.send_sale_data(sale_payload)
        print("results :", result)
        if result.get("resultCd") != "000":
            return api_response(
                status="fail",
                message=result.get("resultMsg", "Unknown error from ZRA"),
                status_code=400,
                
            )
        return api_response(
            status="success",
            message="All Sales Invoice created successfully",
            status_code=200,
        
        )
