from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from base.utils.response_handler import api_response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from base.serializers.quotation.quotation_serializers import (
    QuotationCreateSerializer,
    QuotationListSerializer,
    QuotationDetailSerializer
)
from base.models import Quotation


class QuotationCreateAPIView(APIView):

    def post(self, request):
        serializer = QuotationCreateSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            quotation = serializer.save()
            return api_response(
                status="success",
                message="Quotation created successfully",
                data={"quotation_no": quotation.quotation_no},
                status_code=status.HTTP_201_CREATED
            )

        return api_response(
            status="fail",
            message="Invalid data",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class QuotationListAPIView(APIView):

    def get(self, request):
        quotations = Quotation.objects.all().order_by("-id")
        serializer = QuotationListSerializer(quotations, many=True)

        return api_response(
            status="success",
            message="Quotations retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class QuotationDetailAPIView(APIView):

    def get(self, request, pk):
        try:
            quotation = Quotation.objects.get(id=pk)
        except Quotation.DoesNotExist:
            return api_response(
                status="fail",
                message="Quotation not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = QuotationDetailSerializer(quotation)

        return api_response(
            status="success",
            message="Quotation details retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


