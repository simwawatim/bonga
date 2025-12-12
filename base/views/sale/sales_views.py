from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from base.models import Sale, SaleItem
from base.serializers.sales.sales_serializers import (
    SaleDetailSerializer,
    SaleSerializer,
    SaleItemSerializer,
    SaleSummarySerializer,
)
from base.utils.response_handler import api_response
from base.views.sale.debit_sale_helper import DebitSaleHelper
from base.views.sale.sales_helper import NormalSaleHelper
from base.views.sale.credit_sale_helper import CreditSaleHelper


# ------------------ Sale Views ------------------ #

class SaleListCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sales = Sale.objects.all()
        serializer = SaleSummarySerializer(sales, many=True)
        return api_response(
            status="success",
            message="Sales retrieved successfully",
            data=serializer.data,
            status_code=200
        )

    def post(self, request):
        data = request.data
        result = NormalSaleHelper().process_sale(data)

        if isinstance(result, Response):
            return result
        return api_response(
            status="success",
            message="Sale created successfully",
            data={},
            status_code=201
        )


class SaleCreditNoteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        result = CreditSaleHelper().process_credit_note(data)

        if isinstance(result, Response):
            return result
        return api_response(
            status="success",
            message="Credit note created successfully",
            data=result,
            status_code=201
        )


class SaleDebitNoteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        result = DebitSaleHelper().process_debit_note(data)

        if isinstance(result, Response):
            return result
        return api_response(
            status="success",
            message="Debit note created successfully",
            data=result,
            status_code=201
        )


class SaleRetrieveAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk)
        serializer = SaleSerializer(sale)
        return api_response(
            status="success",
            message="Sale retrieved successfully",
            data=serializer.data,
            status_code=200
        )


# ------------------ Sale Item Views ------------------ #

class SaleItemListCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = SaleItem.objects.all()
        serializer = SaleDetailSerializer(items, many=True)
        return api_response(
            status="success",
            message="Sale items retrieved successfully",
            data=serializer.data,
            status_code=200
        )

    def post(self, request):
        serializer = SaleItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response(
                status="success",
                message="Sale item created successfully",
                data=serializer.data,
                status_code=201
            )
        return api_response(
            status="error",
            message="Failed to create sale item",
            data=serializer.errors,
            status_code=400
        )


class SaleItemRetrieveAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(SaleItem, pk=pk)
        serializer = SaleItemSerializer(item)
        return api_response(
            status="success",
            message="Sale item retrieved successfully",
            data=serializer.data,
            status_code=200
        )
