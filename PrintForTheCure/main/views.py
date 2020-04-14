from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader

# Create your views here.
def home(request):
    return HttpResponse("home view")

def catalogue(request):
    return HttpResponse("catalogue view")

def donorLogin(request):
    return HttpResponse("login view")

def nearbyRequests(request):
    return HttpResponse("nearby requests view")

def confirmClaim(request):
    return HttpResponse("confirm claim view")

def thankYou(request):
    return HttpResponse("thank you for claiming view")
