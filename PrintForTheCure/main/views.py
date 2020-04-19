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

import random
from .models import Donor
from .models import RequestModel
from .gmail import *

# Create your views here.
def home(request):
    if request.method == 'POST':
        if 'login' in request.POST.keys():
            return HttpResponseRedirect("/login/")
        if 'logout' in request.POST.keys():
            logout(request)
            return HttpResponseRedirect("/login/")
        elif 'submitRequest' in request.POST.keys():
            return HttpResponseRedirect("/request/")
        elif 'mapView' in request.POST.keys():
            return HttpResponseRedirect("/requestsVisual/")
        elif 'catalogueView' in request.POST.keys():
            print("hu")
            return HttpResponseRedirect("/catalogue/")

    template = loader.get_template('main/home.html')
    context = {     #all inputs for the html go in these brackets
        'authenticated': request.user.is_authenticated
    }
    return HttpResponse(template.render(context, request))

def catalogue(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/catalogue.html')
    context = {}
    return HttpResponse(template.render(context, request))

def donorRegistration(request):
    failMessage = ""
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")
        elif request.POST['password'] == request.POST['passwordConfirm']:
            newUser = User(username=request.POST['username'], password=request.POST['password'], email=request.POST['email'], first_name=request.POST['fName'], last_name=request.POST['lName'])
            newUser.set_password(request.POST['password'])
            newUser.save()
            newDonor = Donor(user=newUser, address=request.POST['address'], state=request.POST['state'], country=request.POST['country'], zipCode=request.POST['zipCode'], registrationDate=timezone.now())
            newDonor.save()
            return HttpResponseRedirect("/registrationSuccessful/")
        else:
            failMessage = "Passwords do not match."
    template = loader.get_template('main/register.html')
    context = {     #all inputs for the html go in these brackets
        'failMessage': failMessage
    }
    return HttpResponse(template.render(context, request))

def registrationSuccessful(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/registrationSuccessful.html')
    context = {}
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
        elif 'register' in request.POST.keys():
            return HttpResponseRedirect("/register")
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
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")
        print(vars(request.POST))
        newRequest = RequestModel(idNum=RequestModel.objects.latest('orderDate').idNum + random.randrange(1, 100, 1), status=0, fName=request.POST['fName'], lName=request.POST['lName'], email=request.POST['email'], numPPE=request.POST['numPPE'], typePPE=request.POST['typePPE'], address=request.POST['address'], state=request.POST['state'], country=request.POST['country'], zipCode=request.POST['zipCode'], delivDate=timezone.now(), orderDate=timezone.now(), notes=request.POST['otherNotes'])
        newRequest.save()
        return HttpResponseRedirect("/requestSubmitSuccessful/")
    template = loader.get_template('main/submitRequest.html')
    context = {     #all inputs for the html go in these brackets
    }
    return HttpResponse(template.render(context, request))

def requestSubmitSuccessful(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/requestSubmitSuccessful.html')
    context = {}
    return HttpResponse(template.render(context, request))

def map(request):
    template = loader.get_template('main/mapView.html')
    context = {     #all inputs for the html go in these brackets
        'authenticated': request.user.is_authenticated
    }
    return HttpResponse(template.render(context, request))

def nearbyRequests(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            return HttpResponseRedirect("/confirmation/")
        else:
            return HttpResponseRedirect("/notLoggedIn/")

    allRequests = RequestModel.objects.all()
    print(allRequests)

    template = loader.get_template('main/nearbyRequests.html')
    context = {     #all inputs for the html go in these brackets
        'allRequests': allRequests
    }
    return HttpResponse(template.render(context, request))

def notLoggedIn(request):
    if request.method == 'POST':
        if 'return' in request.POST.keys():
            return HttpResponseRedirect("/requestsVisual/")

    template = loader.get_template('main/notLoggedIn.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

def confirmClaim(request):
    if request.method == 'POST':
        if 'yes' in request.POST.keys():
            service = getService()
            #Donor Email
            subject = "Claimed Request For PPE"
            message_text = "Thank You For Claiming a request!"
            message = makeMessage("printforthecure@gmail.com", request.user.email, subject, message_text)
            sendMessage(service, 'me', message)
            #Doctor Email
            subject = "Request For PPE Claimed"
            message_text = "Hello %s,\n \nA gracious donor has claimed your request for %d of type %s PPE!\n \nYour donor is expected to deliver the requested PPE to your address. You may contact your donor here: %s\n Once you have received your PPE, we strongly urge you to leave your donor a monetary donation; they have taken the time, effort, and materials to help you!!!" % ("name", 10, "yes",  request.user.email)
            message = makeMessage("printforthecure@gmail.com", request.user.email, subject, message_text)

            return HttpResponseRedirect("/thankyou/")
        elif 'no' in request.POST.keys():
            return HttpResponseRedirect("/requestsVisual/")
    template = loader.get_template('main/confirmClaim.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

def thankYou(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/thankYou.html')
    context = {}
    return HttpResponse(template.render(context, request))

def test(request):
    template = loader.get_template('main/fileName.html')
    context = {}
    return HttpResponse(template.render(context, request))
