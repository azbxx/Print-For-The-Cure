from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('register/', views.donorRegistration, name='donor registration'),
    path('registrationSuccessful/', views.registrationSuccessful, name='registration sucessful'),
    path('login/', views.donorLogin, name='login'),
    path('request/', views.doctorRequest, name='doctors submit requests'),
    path('requestSubmitSuccessful/', views.requestSubmitSuccessful, name="request submitted successfully"),
    path('requestsVisual/', views.map, name="visual map of requests"),
    path('nearbyRequests/', views.nearbyRequests, name='nearby requests'),
    path('notLoggedIn/', views.notLoggedIn, name='not logged in'),
    path('confirmation/', views.confirmClaim, name='confirmation'),
    path('thankyou/', views.thankYou, name='thank you page'),
]
