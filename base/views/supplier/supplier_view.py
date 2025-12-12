from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from base.models import Supplier
from base.serializers.supplier.supplier_serializers import SupplierSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class SupplierListCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response({
                "status": "success",
                "message": "Supplier created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "fail",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class SupplierDetailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        return get_object_or_404(Supplier, pk=pk)

    def get(self, request, pk):
        supplier = self.get_object(pk)
        serializer = SupplierSerializer(supplier)
        return Response({
            "status": "success",
            "data": serializer.data
        })

    def put(self, request, pk):
        supplier = self.get_object(pk)
        serializer = SupplierSerializer(supplier, data=request.data,  partial=True)
        if serializer.is_valid():
            serializer.save(updated_by= request.user)
            return Response({
                "status": "success",
                "message": "Supplier updated successfully",
                "data": serializer.data
            })
        return Response({
            "status": "fail",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        supplier = self.get_object(pk)
        supplier.delete()
        return Response({
            "status": "success",
            "message": "Supplier deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)
