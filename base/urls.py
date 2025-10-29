from django.urls import path
from  base.views.users.views import create_user, list_users

urlpatterns = [
    path('users/create/', create_user, name='create_user'),
    path('users/', list_users, name='list_users'),
]
