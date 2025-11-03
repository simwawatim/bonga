from base.serializers.stockmaster.stockmasterserializer import ItemStockMasterSerializer
from base.models import ItemStockMaster, ItemInfo
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, generics


class ItemStockMasterListCreateAPIView(generics.GenericAPIView):
    serializer_class = ItemStockMasterSerializer
    queryset = ItemStockMaster.objects.all()

    def get(self, request):
        stock_masters = self.get_queryset()
        serializer = self.get_serializer(stock_masters, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemStockMasterRetrieveUpdateDestroyAPIView(generics.GenericAPIView):
    serializer_class = ItemStockMasterSerializer
    queryset = ItemStockMaster.objects.all()

    def get_object(self, pk):
        return get_object_or_404(ItemStockMaster, pk=pk)

    def get(self, request, pk):
        stock_master = self.get_object(pk)
        serializer = self.get_serializer(stock_master)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        stock_master = self.get_object(pk)
        serializer = self.get_serializer(stock_master, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        stock_master = self.get_object(pk)
        serializer = self.get_serializer(stock_master, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        stock_master = self.get_object(pk)
        stock_master.delete()
        return Response({"status": "success", "message": "Stock master deleted"}, status=status.HTTP_204_NO_CONTENT)
