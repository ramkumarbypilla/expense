from .views import home, view_rides
from django.urls import path

urlpatterns = [
    path('', home, name='home'),
    path('rides/', view_rides, name='view_rides'),
]