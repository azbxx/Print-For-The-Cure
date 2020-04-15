from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# Custom imports added
# Need timezone for date/time published
from django.utils import timezone
# These are needed for user authentication and persistence
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

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
    if request.POST:
        # This tests if the form is the log *in* form
        if 'username' in request.POST.keys():
            # IF so, try to authentircate
            user = authenticate(username=request.POST['username'],
                password=request.POST['password'])
            if user is not None:
                # IF success, then use the login function so the session persists.
                login(request, user)
            else:
                pass
        elif 'logout' in request.POST.keys():
            # If so, don't need to check anything else, just kill the session.
            logout(request)
            print("logged out successfully")
    # After we check the forms, set a flag for use in the template.
    if request.user.is_authenticated:
        template = loader.get_template('main/home.html')
        print("login successful")
    else:
        template = loader.get_template('main/donorLogin.html')
        print("login unsuccessful")
    # Find the template
    context = {
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
