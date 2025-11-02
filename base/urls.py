from django.urls import path
from base.views.items.item_view import ItemInfoDetailView, ItemInfoListCreateView
from  base.views.users.views import create_user, list_users
from base.views.customers import customer_view

urlpatterns = [
    path('users/create/', create_user, name='create_user'),
    path('users/', list_users, name='list_users'),
    path('customers/', customer_view.CustomerInfoListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', customer_view.CustomerInfoDetailView.as_view(), name='customer-detail'),
    path('items/', ItemInfoListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemInfoDetailView.as_view(), name='item-detail'),
]
