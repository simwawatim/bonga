from base.serializers.sales.sales_serializers import SaleSerializer, SaleItemSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from base.models import Sale, SaleItem
from rest_framework import status

class SaleListCreateAPIView(APIView):
    def get(self, request):
        sales = Sale.objects.all()
        serializer = SaleSerializer(sales, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SaleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SaleItemListCreateAPIView(APIView):
    def get(self, request):
        items = SaleItem.objects.all()
        serializer = SaleItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SaleItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
