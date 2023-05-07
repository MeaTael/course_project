from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('learn/', views.learn, name="learn"),
    path('repeat/', views.repeat, name="repeat"),
    path('compete/', views.compete, name="compete"),
    path('profile/', views.profile, name="profile")
]