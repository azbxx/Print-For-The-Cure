from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogue/', views.catalogue, name='home'),
    path('login/', views.donorLogin, name='home'),
    path('nearbyRequests/', views.nearbyRequests, name='home'),
    path('confirmation/', views.confirmClaim, name='home'),
    path('thankyou/', views.thankYou, name='home'),
]
