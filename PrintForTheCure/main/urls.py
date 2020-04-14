from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('login/', views.donorLogin, name='login'),
    path('nearbyRequests/', views.nearbyRequests, name='nearby requests'),
    path('confirmation/', views.confirmClaim, name='confirmation'),
    path('thankyou/', views.thankYou, name='thank you page'),
]
