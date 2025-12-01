from base.serializers.purchase.purchase_serializers import PurchaseSerializer
from base.utils.response_handler import api_response
from rest_framework.views import APIView
from rest_framework import status
from base.models import Purchase



class PurchaseListCreateAPIView(APIView):

    def get(self, request):
        purchases = Purchase.objects.all()
        serializer = PurchaseSerializer(purchases, many=True)
        return api_response(
            status="success",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = PurchaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response(
                status="success",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return api_response(
            status="fail",
            is_error=True,
            message="Validation failed",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class PurchaseDetailAPIView(APIView):

    def get_object(self, pk):
        try:
            return Purchase.objects.get(pk=pk)
        except Purchase.DoesNotExist:
            return None

    def get(self, request, pk):
        purchase = self.get_object(pk)
        if not purchase:
            return api_response(
                status="fail",
                is_error=True,
                message="Purchase not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = PurchaseSerializer(purchase)
        return api_response(
            status="success",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def put(self, request, pk):
        purchase = self.get_object(pk)
        if not purchase:
            return api_response(
                status="fail",
                is_error=True,
                message="Purchase not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = PurchaseSerializer(purchase, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response(
                status="success",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        return api_response(
            status="fail",
            is_error=True,
            message="Validation failed",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        purchase = self.get_object(pk)
        if not purchase:
            return api_response(
                status="fail",
                is_error=True,
                message="Purchase not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        purchase.delete()
        return api_response(
            status="success",
            message="Purchase deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )
