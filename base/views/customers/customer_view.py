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
        response = api_response(
            status="success",
            message="Customers fetched successfully",
            data=serializer.data,
            status_code=200
        )
        print("GET /customers/ response:", response.data)
        return response

    def post(self, request):
        try:
            data = request.data
            serializer = CustomerInfoSerializer(data=data)
            if serializer.is_valid():
                zra_client = CreateUser()
                zra_response = zra_client.prepare_save_customer_payload(data, request)
                zra_data = zra_response.json()
                print("ZRA response:", zra_data)

                if zra_data.get("resultCd") != "000":
                    return api_response(
                        status="fail",
                        message=zra_data.get("resultMsg"),
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                serializer.save(created_by=request.user, updated_by=request.user)
                return api_response(
                    status="success",
                    message="Customer created successfully",
                    status_code=201
                )
            else:
                first_field, messages = next(iter(serializer.errors.items()))
                error_message = f"{first_field}: {messages[0]}"
                return api_response(
                    status="fail",
                    message=error_message,
                    data={},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print("POST /customers/ exception:", str(e))
            return api_response(
                status="error",
                message=f"Internal server error: {str(e)}",
                data={},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomerInfoDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        customer = get_object_or_404(CustomerInfo, pk=pk)
        serializer = CustomerInfoSerializer(customer)
        response = api_response(
            status="success",
            message="Customer fetched successfully",
            data=serializer.data,
            status_code=200
        )
        print(f"GET /customers/{pk}/ response:", response.data)
        return response

    def put(self, request, pk):
        customer = get_object_or_404(CustomerInfo, pk=pk)
        serializer = CustomerInfoSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            response = api_response(
                status="success",
                message="Customer updated successfully",
                status_code=200
            )
            print(f"PUT /customers/{pk}/ response:", response.data)
            return response

        first_field, messages = next(iter(serializer.errors.items()))
        response = api_response(
            status="fail",
            message=f"{first_field}: {messages[0]}",
            data={},
            status_code=400
        )
        print(f"PUT /customers/{pk}/ validation error response:", response.data)
        return response

    def delete(self, request, pk):
        customer = get_object_or_404(CustomerInfo, pk=pk)
        customer.delete()
        response = api_response(
            status="success",
            message="Customer deleted successfully.",
            data={},
            status_code=200
        )
        print(f"DELETE /customers/{pk}/ response:", response.data)
        return response
