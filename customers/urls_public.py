from django.urls import path
from .views import ClientCreate, ClientDelete, ClientDetail, ClientList, ClientUpdate

urlpatterns = [
    path('', ClientList.as_view(), name='create-tenant'),
    path('customers/create-tenant/', ClientCreate.as_view(), name='create-tenant'),
    path('customers/tenants/', ClientList.as_view(), name='list-tenants'),
    path('customers/tenants/<int:id>/', ClientDetail.as_view(), name='tenant-detail'),
    path('customers/tenants/<int:id>/update/', ClientUpdate.as_view(), name='tenant-update'),
    path('customers/tenants/<int:id>/delete/', ClientDelete.as_view(), name='tenant-delete'),
]
