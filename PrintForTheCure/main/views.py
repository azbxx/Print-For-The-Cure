from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader

# Create your views here.
def home(request):
    template = loader.get_template('main/home.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

def catalogue(request):
    template = loader.get_template('main/catalogue.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

def donorLogin(request):
    template = loader.get_template('main/donorLogin.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

def nearbyRequests(request):
    template = loader.get_template('main/nearbyRequests.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

def confirmClaim(request):
    template = loader.get_template('main/confirmClaim.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

def thankYou(request):
    template = loader.get_template('main/thankYou.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))
