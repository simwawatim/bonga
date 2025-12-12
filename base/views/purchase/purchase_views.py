from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from base.serializers.purchase.purchase_serializers import PurchaseSerializer
from base.views.purchase.helper.purchase_helper import PurchaseHelper
from base.utils.response_handler import api_response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from base.models import Purchase



class PurchaseListCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        purchases = Purchase.objects.all()
        serializer = PurchaseSerializer(purchases, many=True)
        return api_response(
            status="success",
            message="Purchase fetched successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def post(self, request):
        data = request.data
        result = PurchaseHelper().format_purchase_data(data)

        if hasattr(result, "data"):
            return result

        return api_response(
            status=result.get("status"),
            message=result.get("message"),
            data=result.get("data"),
            status_code=200 if result.get("status") == "success" else 400
        )
    
    
class PurchaseDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
                message="Purchase not found",
                data={},
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = PurchaseSerializer(purchase)
        return api_response(
            status="success",
            message="Purchase fetched successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def put(self, request, pk):
        purchase = self.get_object(pk)
        if not purchase:
            return api_response(
                status="fail",
                message="Purchase not found",
                data={},
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = PurchaseSerializer(purchase, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_response(
                status="success",
                message="Purchase updated successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        return api_response(
            status="fail",
            message=serializer.errors,
            data={},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        purchase = self.get_object(pk)
        if not purchase:
            return api_response(
                status="fail",
                message="Purchase not found",
                data={},
                status_code=status.HTTP_404_NOT_FOUND
            )

        purchase.delete()
        return api_response(
            status="success",
            message="Purchase deleted successfully",
            data={},
            status_code=status.HTTP_204_NO_CONTENT
        )
