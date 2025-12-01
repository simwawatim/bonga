from base.utils.response_handler import api_response
from base.models import ItemStockMaster, ItemInfo
from rest_framework import status

class CheckStock:

    @staticmethod
    def reduceStock(itemCd, qtyToBeReduced):
        if not itemCd:
            return api_response(
                status="fail",
                message="Item code is missing",
                status_code=400
            )

        if not qtyToBeReduced or qtyToBeReduced <= 0:
            return api_response(
                status="fail",
                message="Quantity to be reduced is missing or invalid",
                status_code=400
            )

        try:
            item = ItemInfo.objects.get(code=itemCd)
        except ItemInfo.DoesNotExist:
            return api_response(
                status="fail",
                message=f"Item '{itemCd}' not found",
                status_code=404
            )

        stock = ItemStockMaster.objects.filter(item=item).first()

        if not stock:
            return api_response(
                status="fail",
                message="Item stock does not exist",
                status_code=404
            )

        if stock.available_qty < qtyToBeReduced:
            return api_response(
                status="fail",
                message=f"Insufficient stock. Available: {stock.available_qty}",
                status_code=400
            )

        # Perform reduction
        stock.available_qty -= qtyToBeReduced
        stock.save()

        return api_response(
            status="success",
            message="Stock reduced successfully",
            data={
                "itemCode": itemCd,
                "reducedQty": qtyToBeReduced,
                "newAvailableQty": stock.available_qty
            },
            status_code=200
        )

    @staticmethod
    def increaseStock(itemCd, qtyToBeIncreased):
        print("started increasing the stock mastet")
        if not itemCd:
            return api_response(
                status="fail",
                message="Item code is missing",
                status_code=400
            )

        if not qtyToBeIncreased or qtyToBeIncreased <= 0:
            return api_response(
                status="fail",
                message="Quantity to be increased is missing or invalid",
                status_code=400
            )

        try:
            item = ItemInfo.objects.get(code=itemCd)
        except ItemInfo.DoesNotExist:
            return api_response(
                status="fail",
                message=f"Item '{itemCd}' not found",
                status_code=404
            )

        stock = ItemStockMaster.objects.filter(item=item).first()

        if not stock:
            return api_response(
                status="fail",
                message="Item stock does not exist",
                status_code=404
            )

        stock.available_qty += qtyToBeIncreased
        stock.save()

        return api_response(
            status="success",
            message="Stock increased successfully",
            data={
                "itemCode": itemCd,
                "increasedQty": qtyToBeIncreased,
                "newAvailableQty": stock.available_qty
            },
            status_code=200
        )

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
                status_code=404
            )

        stock = ItemStockMaster.objects.filter(item=item).first()

        if not stock:
            return api_response(
                status="fail",
                message="Item stock for this item does not exist",
                status_code=404
            )

        if stock.available_qty is None:
            return api_response(
                status="fail",
                message="Stock quantity field missing in DB",
                status_code=500
            )

        if requestQty > stock.available_qty:
            return api_response(
                status="fail",
                message=f"Insufficient stock. Available: {stock.available_qty}, Requested: {requestQty}",
                status_code=400
            )

        return api_response(
            status="success",
            message="Stock available",
            data={
                "itemCode": itemCd,
                "availableQty": stock.available_qty,
                "requestedQty": requestQty
            },
            status_code=200
        )
