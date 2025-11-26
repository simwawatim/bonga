from base.views.stockmaster.stockmasterview import ItemStockMasterListCreateAPIView, ItemStockMasterRetrieveUpdateDestroyAPIView
from base.views.supplier.supplier_view import SupplierDetailAPIView, SupplierListCreateAPIView
from base.views.stock.stock_item_view import StockItemDetailView, StockItemListCreateView
from base.views.items.item_view import ItemInfoDetailView, ItemInfoListCreateView
from main.base.views.sale.sales_views import SaleListCreateAPIView
from  base.views.users.views import create_user, list_users
from base.views.customers import customer_view
from django.urls import path


urlpatterns = [
    path('users/', list_users, name='list_users'),
    path('users/create/', create_user, name='create_user'),
    path('items/', ItemInfoListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemInfoDetailView.as_view(), name='item-detail'),
    path('sales/', SaleListCreateAPIView.as_view(), name='sale-list-create'),
    path('stockitems/', StockItemListCreateView.as_view(), name='stockitem-list'),
    path('stockitems/<int:pk>/', StockItemDetailView.as_view(), name='stockitem-detail'),
    path('suppliers/', SupplierListCreateAPIView.as_view(), name='supplier-list-create'),
    path('suppliers/<int:pk>/', SupplierDetailAPIView.as_view(), name='supplier-detail'),
    path('customers/', customer_view.CustomerInfoListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', customer_view.CustomerInfoDetailView.as_view(), name='customer-detail'),
    path('stock-masters/', ItemStockMasterListCreateAPIView.as_view(), name='stock-master-list-create'),
    path('stock-masters/<int:pk>/', ItemStockMasterRetrieveUpdateDestroyAPIView.as_view(), name='stock-master-detail'),
    
]
