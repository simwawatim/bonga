from base.serializers.stock.stock_item_serializer import StockItemSerializer
from base.utils.response_handler import api_response
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db.models import ProtectedError
from base.models import StockItem, ItemInfo
from rest_framework.views import APIView
from rest_framework import status





class StockItemListCreateView(APIView):
    def get(self, request):
        stock_items = StockItem.objects.select_related('stock_item', 'created_by').all()
        serializer = StockItemSerializer(stock_items, many=True)
        return api_response("success", serializer.data, status_code=200)

    def post(self, request):
        try:
            item = ItemInfo.objects.filter(pk=request.data.get("item")).first()
            if not item:
                return api_response(
                    "error",
                    "Invalid item specified.",
                    status_code=400,
                    is_error=True
                )

            serializer = StockItemSerializer(data=request.data)
            if not serializer.is_valid():
                field, messages = next(iter(serializer.errors.items()))
                return api_response(
                    "error",
                    f"{field}: {messages[0]}",
                    status_code=400,
                    is_error=True
                )

            serializer.save(created_by=request.user if request.user.is_authenticated else None)
            return api_response("success", serializer.data, status_code=201)

        except Exception as e:
            return api_response(
                "error",
                f"Internal server error: {str(e)}",
                status_code=500,
                is_error=True
            )


class StockItemDetailView(APIView):
    def get(self, request, pk):
        stock_item = get_object_or_404(StockItem, pk=pk)
        serializer = StockItemSerializer(stock_item)
        return api_response("success", serializer.data, status_code=200)

    def put(self, request, pk):
        stock_item = get_object_or_404(StockItem, pk=pk)
        serializer = StockItemSerializer(stock_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return api_response("success", serializer.data)
        field, messages = next(iter(serializer.errors.items()))
        return api_response("error", f"{field}: {messages[0]}", status_code=400, is_error=True)

    def delete(self, request, pk):
        try:
            stock_item = get_object_or_404(StockItem, pk=pk)
            stock_item.delete()
            return api_response("success", "Stock item deleted successfully.", status_code=200)
        except ProtectedError:
            return api_response(
                "error",
                "Cannot delete stock item because it is referenced in other records.",
                status_code=400,
                is_error=True
            )
        except Exception as e:
            return api_response(
                "error",
                f"Internal server error during delete: {str(e)}",
                status_code=500,
                is_error=True
            )
