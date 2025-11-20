from .views import home, rides_list
from django.urls import path

urlpatterns = [
    path('', home, name='home'),
    path('rides/', rides_list, name='rides_list'),
]