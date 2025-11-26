from base.serializers.sales.sales_serializers import SaleSerializer, SaleItemSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from base.models import Sale, SaleItem
from rest_framework import status
from django.shortcuts import get_object_or_404

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

class SaleRetrieveAPIView(APIView):
    def get(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk)
        serializer = SaleSerializer(sale)
        return Response(serializer.data)

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

class SaleItemRetrieveAPIView(APIView):
    def get(self, request, pk):
        item = get_object_or_404(SaleItem, pk=pk)
        serializer = SaleItemSerializer(item)
        return Response(serializer.data)
