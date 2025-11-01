from django.urls import path
from  base.views.users.views import create_user, list_users
from base.views.customers import customer_view

urlpatterns = [
    path('users/create/', create_user, name='create_user'),
    path('users/', list_users, name='list_users'),
    path('customers/', customer_view.customer_list_create, name='customer-list-create'),
    path('customers/<int:pk>/', customer_view.customer_detail, name='customer-detail'),
]
