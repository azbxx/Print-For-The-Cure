from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
# Custom imports added
# Need timezone for date/time published
from django.utils import timezone
# These are needed for user authentication and persistence
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def home(request):
    if request.POST:
        if 'login' in request.POST.keys():
            return HttpResponseRedirect("/login/")
        if 'logout' in request.POST.keys():
            logout(request)
            return HttpResponseRedirect("/login/")

    template = loader.get_template('main/home.html')
    context = {     #all inputs for the html go in these brackets
        'authenticated': request.user.is_authenticated
    }
    return HttpResponse(template.render(context, request))

def catalogue(request):
    template = loader.get_template('main/catalogue.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

def donorRegistration(request):
    newUser = User.objects.create_user('myusername', 'myemail@crazymail.com', 'mypassword')
    # Update fields and then save again
    newUser.first_name = 'John'
    newUser.last_name = 'Citizen'
    newUser.save()

    template = loader.get_template('main/register.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

def donorLogin(request):
    if request.method == "POST":
        # This tests if the form is the log *in* form
        if 'username' in request.POST.keys():
            # IF so, try to authentircate
            user = authenticate(username=request.POST['username'],
                password=request.POST['password'])
            if user is not None:
                # IF success, then use the login function so the session persists.
                login(request, user)
                return HttpResponseRedirect("/")
            else:
                pass
    # After we check the forms, set a flag for use in the template.
    if request.user.is_authenticated:
        template = loader.get_template('main/home.html')
        authenticated = True
    else:
        template = loader.get_template('main/donorLogin.html')
        authenticated = False
    # Find the template
    context = {
        'authenticated': authenticated
    }
    return HttpResponse(template.render(context, request))

def doctorRequest(request):
    template = loader.get_template('main/submitRequest.html')
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
