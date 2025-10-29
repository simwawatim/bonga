from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from zra_client.create_user import CreateUser
from .models import Client, Domain
from .serializers import ClientSerializer

class ClientCreate(generics.CreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        client = serializer.save()

        Domain.objects.create(domain=client.schema_name + ".localhost", tenant=client)
        return client
    
class ClientList(generics.ListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]


class ClientDetail(generics.RetrieveAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]

class ClientUpdate(generics.UpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]

class ClientDelete(generics.DestroyAPIView):
    queryset = Client.objects.all()
    lookup_field = 'id'
    permission_classes = [AllowAny]
