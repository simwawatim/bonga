from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from base.models import CustomerInfo
from base.serializers.customers.customer_serializer import CustomerInfoSerializer

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def customer_list_create(request):
    if request.method == 'GET':
        customers = CustomerInfo.objects.all()
        serializer = CustomerInfoSerializer(customers, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CustomerInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def customer_detail(request, pk):
    try:
        customer = CustomerInfo.objects.get(pk=pk)
    except CustomerInfo.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CustomerInfoSerializer(customer)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CustomerInfoSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
