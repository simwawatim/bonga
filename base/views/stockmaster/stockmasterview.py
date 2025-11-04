from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from base.models import ItemStockMaster, ItemInfo
from base.serializers.stockmaster.stockmasterserializer import ItemStockMasterSerializer


class ItemStockMasterListCreateAPIView(APIView):
    def get(self, request):
        stock_masters = ItemStockMaster.objects.all()
        serializer = ItemStockMasterSerializer(stock_masters, many=True)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = ItemStockMasterSerializer(data=request.data)
        if serializer.is_valid():
            item_id = request.data.get("item")
            item = ItemInfo.objects.filter(pk=item_id).first()
            print(item)
            if not item:
                return Response(
                    {"status": "error", "message": "Invalid item ID"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if ItemStockMaster.objects.filter(item=item).exists():
                return Response(
                    {"status": "error", "message": "Stock master already exists for this item"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class ItemStockMasterRetrieveUpdateDestroyAPIView(APIView):

    def get_object(self, pk):
        return get_object_or_404(ItemStockMaster, pk=pk)

    def get(self, request, pk):
        stock_master = self.get_object(pk)
        serializer = ItemStockMasterSerializer(stock_master)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        stock_master = self.get_object(pk)
        serializer = ItemStockMasterSerializer(stock_master, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        stock_master = self.get_object(pk)
        serializer = ItemStockMasterSerializer(stock_master, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(
                {"status": "success", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        stock_master = self.get_object(pk)
        stock_master.delete()
        return Response(
            {"status": "success", "message": "Stock master deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
