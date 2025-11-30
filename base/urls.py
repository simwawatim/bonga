from base.views.stockmaster.stockmasterview import ItemStockMasterListCreateAPIView, ItemStockMasterRetrieveUpdateDestroyAPIView
from base.views.supplier.supplier_view import SupplierDetailAPIView, SupplierListCreateAPIView
from base.views.stock.stock_item_view import StockItemDetailView, StockItemListCreateView
from base.views.items.item_view import ItemInfoDetailView, ItemInfoListCreateView
from base.views.sale.sales_views import SaleCreditNoteAPIView, SaleDebitNoteAPIView, SaleListCreateAPIView, SaleRetrieveAPIView
from base.views.stock_master.stock_master_view import StockMasterByItemCode
from  base.views.users.views import create_user, list_users
from base.views.customers import customer_view
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('users/', list_users, name='list_users'),
    path('users/create/', create_user, name='create_user'),
    path('items/', ItemInfoListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemInfoDetailView.as_view(), name='item-detail'),
    path('sales/', SaleListCreateAPIView.as_view(), name='sale-list-create'),
    path('sales/<int:pk>/', SaleRetrieveAPIView.as_view(), name='sale-detail'),
    path('stockitems/', StockItemListCreateView.as_view(), name='stockitem-list'),
    path('stockitems/<int:pk>/', StockItemDetailView.as_view(), name='stockitem-detail'),
    path('suppliers/', SupplierListCreateAPIView.as_view(), name='supplier-list-create'),
    path('suppliers/<int:pk>/', SupplierDetailAPIView.as_view(), name='supplier-detail'),
    path('sale/credit-note-create/', SaleCreditNoteAPIView.as_view(), name='sale-credit-note-create'),
    path('sale/debit-note-create/', SaleDebitNoteAPIView.as_view(), name='sale-debit-note-create'),
    path('customers/', customer_view.CustomerInfoListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', customer_view.CustomerInfoDetailView.as_view(), name='customer-detail'),
    path(
        'stock-master/item/<str:code>/',
        StockMasterByItemCode.as_view(),
        name='stock-master-by-item-code'
    ),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

