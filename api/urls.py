from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.hello_world),
]