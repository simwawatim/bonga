from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/public/', include('customers.urls_public')),
    path('', include('base.urls')),
]
