from .views import home, rides_list,summary,edit_ride,delete_ride
from django.urls import path

urlpatterns = [
    path('', home, name='home'),
    path('rides/', rides_list, name='rides_list'),
    path('rides/<int:ride_id>/edit/', edit_ride, name='edit_ride'),
    path('rides/<int:ride_id>/delete/', delete_ride, name='delete_ride'),
    path('summary/', summary, name='summary'),  # Example additional path
]