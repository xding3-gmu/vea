from django.urls import path

from . import views

urlpatterns = [
    path('vea/', views.HomeView.as_view(), name='home'),
    path('vea/api/', views.get_data, name='api-data'),
]