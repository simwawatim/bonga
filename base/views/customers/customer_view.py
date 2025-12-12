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
        response = api_response("success", serializer.data, status_code=200)
        
        # Print response for debugging
        print("GET /customers/ response:", response.data)
        
        return response

    def post(self, request):
        serializer = CustomerInfoSerializer(data=request.data)
        if serializer.is_valid():
            zra_client = CreateUser()
            zra_response = zra_client.prepare_save_customer_payload()
            data = zra_response.json()

            print("ZRA response:", data)

            if data.get("resultCd") != "000":
                error_response = Response(
                    {   
                        "error": "ZRA customer creation failed",
                        "zra_result": data
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
                print("POST /customers/ error response:", error_response.data)
                return error_response

            serializer.save(created_by=request.user, updated_by=request.user)
            response = api_response("success", serializer.data, status_code=201)
            print("POST /customers/ response:", response.data)
            return response

        first_field, messages = next(iter(serializer.errors.items()))
        response = api_response("error", f"{first_field}: {messages[0]}", status_code=400, is_error=True)
        print("POST /customers/ validation error response:", response.data)
        return response


class CustomerInfoDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        customer = get_object_or_404(CustomerInfo, pk=pk)
        serializer = CustomerInfoSerializer(customer)
        response = api_response("success", serializer.data, status_code=200)
        print(f"GET /customers/{pk}/ response:", response.data)
        return response

    def put(self, request, pk):
        customer = get_object_or_404(CustomerInfo, pk=pk)
        serializer = CustomerInfoSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            response = api_response("success", serializer.data)
            print(f"PUT /customers/{pk}/ response:", response.data)
            return response

        first_field, messages = next(iter(serializer.errors.items()))
        response = api_response("error", f"{first_field}: {messages[0]}", status_code=400, is_error=True)
        print(f"PUT /customers/{pk}/ validation error response:", response.data)
        return response

    def delete(self, request, pk):
        customer = get_object_or_404(CustomerInfo, pk=pk)
        customer.delete()
        response = api_response("success", "Customer deleted successfully.", status_code=204, is_error=False)
        print(f"DELETE /customers/{pk}/ response:", response.data)
        return response
