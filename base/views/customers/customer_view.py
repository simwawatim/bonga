from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from base.models import CustomerInfo
from base.serializers.customers.customer_serializer import CustomerInfoSerializer
from base.utils.response_handler import api_response
from zra_client.create_customer import CreateUser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomerInfoListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        customers = CustomerInfo.objects.all()
        serializer = CustomerInfoSerializer(customers, many=True)
        return api_response("success", serializer.data, status_code=200)

    def post(self, request):
        serializer = CustomerInfoSerializer(data=request.data)
        if serializer.is_valid():

            zra_client = CreateUser()
            zra_response = zra_client.prepare_save_customer_payload()
            data = zra_response.json()

            print(data)

            if data.get("resultCd") != "000":
                return Response(
                    {   
                        "error": "ZRA customer creation failed",
                        "zra_result": zra_response
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return api_response("success", serializer.data, status_code=201)
        first_field, messages = next(iter(serializer.errors.items()))
        return api_response("error", f"{first_field}: {messages[0]}", status_code=400, is_error=True)


class CustomerInfoDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        customer = get_object_or_404(CustomerInfo, pk=pk)
        serializer = CustomerInfoSerializer(customer)
        return api_response("success", serializer.data, status_code=200)

    def put(self, request, pk):
        customer = get_object_or_404(CustomerInfo, pk=pk)
        serializer = CustomerInfoSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return api_response("success", serializer.data)
        # First error only
        first_field, messages = next(iter(serializer.errors.items()))
        return api_response("error", f"{first_field}: {messages[0]}", status_code=400, is_error=True)

    def delete(self, request, pk):
        customer = get_object_or_404(CustomerInfo, pk=pk)
        customer.delete()
        return api_response("success", "Customer deleted successfully.", status_code=204, is_error=False)
