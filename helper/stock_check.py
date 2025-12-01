from base.utils.response_handler import api_response
from base.models import ItemStockMaster, ItemInfo
from rest_framework import status

class CheckStock:

    @staticmethod
    def check_stock_if_exist(itemCd, requestQty):

        if not itemCd:
            return api_response(
                status="fail",
                message="Item code is missing",
                status_code=404
            )


        if requestQty is None or requestQty == "":
            return api_response(
                status="fail",
                message="Request quantity is missing",
                status_code=400
            )

        try:
            item = ItemInfo.objects.get(code=itemCd)
        except ItemInfo.DoesNotExist:
            return api_response(
                status="fail",
                message=f"Item with code '{itemCd}' not found",
                data={},
                status_code=status.HTTP_404_NOT_FOUND
            )

        stock = ItemStockMaster.objects.filter(item=item).first()

        if not stock:
            return api_response(
                status="fail",
                message="Item stock for this item does not exist",
                status_code=404
            )

        available_qty = stock.available_qty if hasattr(stock, "available_qty") else None

        if available_qty is None:
            return api_response(
                status="fail",
                message="Stock quantity field missing in DB",
                status_code=500
            )


        if requestQty > available_qty:
            return api_response(
                status="fail",
                message=f"Insufficient stock. Available: {available_qty}, Requested: {requestQty}",
                status_code=400
            )

    
        return api_response(
            status="success",
            message="Stock available",
            data={
                "itemCode": itemCd,
                "availableQty": available_qty,
                "requestedQty": requestQty
            },
            status_code=200
        )
