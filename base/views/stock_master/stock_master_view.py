from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from base.serializers.stock_master.stock_master_serializer import ItemStockMasterSerializer
from base.utils.response_handler import api_response
from base.models import ItemInfo, ItemStockMaster
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class StockMasterByItemCode(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, code):
        try:
            item = ItemInfo.objects.get(code=code)
        except ItemInfo.DoesNotExist:
            return api_response(
                status="fail",
                message=f"Item with code '{code}' not found",
                data={},
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        master, _ = ItemStockMaster.objects.get_or_create(item=item)
        serializer = ItemStockMasterSerializer(master)
        return api_response(
            status="success",
            message="Stock master retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
