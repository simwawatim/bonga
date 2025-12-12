from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from base.utils.response_handler import api_response
from .models import Client, Domain
from .serializers import ClientSerializer, TenantCreateSerializer


def flatten_errors(errors_dict):
    error_list = []

    for field, messages in errors_dict.items():
        if isinstance(messages, (list, tuple)):
            for msg in messages:
                error_list.append(str(msg))
        else:
            error_list.append(str(messages))


    return " ".join(error_list)


class ClientCreate(generics.CreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = TenantCreateSerializer(data=request.data)

        if not serializer.is_valid():
            message = flatten_errors(serializer.errors)
            return api_response(
                message=message,
                data={},
                status="error",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        valid_data = serializer.validated_data
        domain_value = valid_data.pop("domain")
        client = Client.objects.create(**valid_data)
        Domain.objects.create(
            domain=domain_value,
            tenant=client
        )

        return api_response(
            status="success",
            message="Tenant created successfully",
            data=ClientSerializer(client).data,
            status_code=status.HTTP_201_CREATED
        )


class ClientList(generics.ListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return api_response(
            status="success",
            message="Client list fetched",
            data=serializer.data,
            status_code=200
        )

class ClientDetail(generics.RetrieveAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return api_response(
            status="success",
            message="Client details",
            data=ClientSerializer(instance).data,
            status_code=200
        )


class ClientUpdate(generics.UpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ClientSerializer(instance, data=request.data, partial=True)

        if not serializer.is_valid():
            message = flatten_errors(serializer.errors)
            return api_response(
                message=message,
                data={},
                status="error",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return api_response(
            status="success",
            message="Client updated successfully",
            data={},
            status_code=200
        )


class ClientDelete(generics.DestroyAPIView):
    queryset = Client.objects.all()
    lookup_field = 'id'
    permission_classes = [AllowAny]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        return api_response(
            status="success",
            message="Client deleted successfully",
            data={},
            status_code=200
        )
