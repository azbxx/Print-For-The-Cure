from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from urllib.parse import urlencode
from django.template import loader
# Custom imports added
from django.db import transaction
# Need timezone for date/time published
from django.utils import timezone
import datetime
# These are needed for user authentication and persistence
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# Google library for address validations (used in doctorRequest)
from i18naddress import InvalidAddress, normalize_address
import math
# Google Distance Matrix API Imports
import googlemaps
import json
import urllib.request
import urllib.parse
import random
import requests
from .models import Donor
from .models import RequestModel
from .models import Stats
import os

from .gmail import *
from .GoogleAPIKey import *
import string
import numpy as np

# Create your views here.
def home(request):
    statsobj = Stats.objects.get(getId=0)
    print(request.user.is_authenticated)
    if request.method == 'POST':
        if 'login' in request.POST.keys():
            return HttpResponseRedirect("/login/")
        if 'logout' in request.POST.keys():
            print(request.user.is_authenticated)
            logout(request)
            return HttpResponseRedirect("/login/")
        elif 'submitRequest' in request.POST.keys():
            return HttpResponseRedirect("/requestPPE/")
        elif 'mapView' in request.POST.keys():
            return HttpResponseRedirect("/requestsVisual/")
        elif 'shield' in request.POST.keys():
            return HttpResponseRedirect("/catalogue-shield/")
        elif 'hook' in request.POST.keys():
            return HttpResponseRedirect("/catalogue-maskstrap/")
        elif 'opener' in request.POST.keys():
            return HttpResponseRedirect("/catalogue-dooropener/")
        elif 'handle' in request.POST.keys():
            return HttpResponseRedirect("/catalogue-handle/")

    template = loader.get_template('main/home.html')
    context = {     #all inputs for the html go in these brackets
        'authenticated': request.user.is_authenticated,
        'claimRate': statsobj.claimrate,
        'claimedPPE': statsobj.claims,
    }
    return HttpResponse(template.render(context, request))

def catalogueShield(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/shield.html')
    context = {}
    return HttpResponse(template.render(context, request))

def catalogueMaskStrap(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/hook.html')
    context = {}
    return HttpResponse(template.render(context, request))

def catalogueDoorOpener(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/opener.html')
    context = {}
    return HttpResponse(template.render(context, request))

def catalogueHandle(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/handle.html')
    context = {}
    return HttpResponse(template.render(context, request))

@transaction.atomic
def donorRegistration(request):
    failMessage = ""
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")
        elif request.POST['password'] == request.POST['passwordConfirm']:
            # try:
            #     address = normalize_address({
            #     'country_code': request.POST['country'],
            #     'country_area': request.POST['state'],
            #     'city': request.POST['city'],
            #     'postal_code': request.POST['zipCode']})
            # except InvalidAddress as e:
            #     print("failed")
            #     print(e.errors)
            #     failMessage += "Sorry, Address Validation failed. Please enter a valid address for delivery.\n"
            users = User.objects.all()
            usernames = []
            for user in users:
                usernames.append(user.username)
            if request.POST['username'] in usernames:
                failMessage += "Sorry, username is already taken! Please choose another one. "
            if (len(request.POST['username']) < 1) or (len(request.POST['password']) < 1) or (len(request.POST['email']) < 1) or (len(request.POST['fName']) < 1) or (len(request.POST['lName']) < 1):
                failMessage += "Please ensure all fields are filled out."
            elif (len(failMessage) == 0):
                newUser = User(username=request.POST['username'], password=request.POST['password'], email=request.POST['email'], first_name=request.POST['fName'], last_name=request.POST['lName'])
                newUser.set_password(request.POST['password'])
                newUser.save()
                newDonor = Donor(user=newUser, address=request.POST['address'], city=request.POST['city'], state=request.POST['state'], country=request.POST['country'], zipCode=request.POST['zipCode'], registrationDate=timezone.now())

                newDonor.save()
                addressList = newDonor.address.split()
                addressFormatted = ""
                for word in addressList:
                    addressFormatted += word
                    addressFormatted += "+"

                cityList = newDonor.city.split()
                cityFormatted = ""
                for word in cityList:
                    addressFormatted += word
                    addressFormatted += "+"

                addr = addressFormatted + cityFormatted + newDonor.state + "+" + newDonor.zipCode
                key = os.getenv("GOOGLE_SERVER_API")
                reqres = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(addr, key))
                loc = reqres.json()['results'][0]['geometry']['location']
                newDonor.lat = loc['lat']
                newDonor.lng = loc['lng']
                newDonor.save()
                user = authenticate(username=request.POST['username'], password=request.POST['password'])
                login(request, user)

                service = getService()
                #Donor Email
                subject = "PrintForTheCure Registration Details"
                message_text = "Thank you for registing with PrintForTheCure! Now you can get started claiming and fulfilling PPE requests on printforthecure.com!\n\nYour Username: %s" % (request.POST['username'])
                message = makeMessage("printforthecure@gmail.com", request.POST['email'], subject, message_text)
                sendMessage(service, 'me', message)

                return HttpResponseRedirect("/registrationSuccessful/")
        else:
            failMessage += "Passwords do not match. "
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
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
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

@transaction.atomic
def doctorRequest(request):
    validationStatus = ""
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")
        print(vars(request.POST))

        validated = True
        try:
            address = normalize_address({
            'country_code': request.POST['country'],
            'country_area': request.POST['state'],
            'city': request.POST['city'],
            'postal_code': request.POST['zipCode'],
            'street_address': request.POST['address']})
        except InvalidAddress as e:
            print("failed")
            print(e.errors)
            validated = False
            validationStatus += "Sorry, Address Validation failed. Please enter a valid address for delivery.\n"
        if (len(request.POST['fName']) < 1) or (len(request.POST['lName']) < 1) or (len(request.POST['email']) < 1):
            validated = False
            validationStatus += "Please ensure all fields are filled out. "
        if timezone.now().date() > datetime.date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day'])):
            validated = False
            validationStatus += "Please set the delivery date later. "
        if validated:
            print("Address Validation Succeeded")

            newRequest = RequestModel(id=RequestModel.objects.latest('orderDate').id + random.randrange(1, 100, 1), status=0, fName=request.POST['fName'], lName=request.POST['lName'], email=request.POST['email'], phone=request.POST['phone'], organization=request.POST['organization'], numPPE=request.POST['numPPE'], typePPE=request.POST['typePPE'], typeHandle=request.POST['typeHandle'], address=request.POST['address'], city=request.POST['city'], state=request.POST['state'], country=request.POST['country'], lat=request.POST['lat'], lng=request.POST['lng'], zipCode=request.POST['zipCode'], delivDate=datetime.date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day'])) , orderDate=timezone.now(), notes=request.POST['otherNotes'])
            print(request.POST['lat'] + ", " + request.POST['lng'])
            newRequest.save()

            requestObj = RequestModel.objects.get(id=newRequest.id)
            service = getService()
            #Donor Email
            subject = "Request For PPE Submitted!"
            ppeType = ""
            if "shield" in requestObj.typePPE:
                ppeType = "3D Printed Face Shields"
            elif "strap" in requestObj.typePPE:
                ppeType = "Face Mask Comfort Strap"
            elif "handle" in requestObj.typePPE:
                ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestObj.typeHandle
            elif "opener" in requestObj.typePPE:
                ppeType = "Personal Touchless Door Opener"
            message_text = "Thank You For Submitting a Request For PPE!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %s\nideal \"Deliver By\" date of requested PPE: %s\n\nOther Notes From the Requester: %s\n\nYou will be emailed again either when a donor chooses to claim and fulfill your request, or if your request expires before any donors get the chance. We hope you you stay protected during these times!" % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, requestObj.delivDate, requestObj.notes)
            message = makeMessage("printforthecure@gmail.com", requestObj.email, subject, message_text)
            sendMessage(service, 'me', message)

            return HttpResponseRedirect("/requestSubmitSuccessful/")

    template = loader.get_template('main/submitRequest.html')
    context = {     #all inputs for the html go in these brackets
        'validationStatus': validationStatus
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
    allUnclaimedRequests = []
    addresses = []
    counter = 0
    for requestModel in RequestModel.objects.all():
        if timezone.now().date() > requestModel.delivDate + datetime.timedelta(days=1) and requestModel.status == 0:
            print("Deleting RequestModel (date passed): " + str(requestModel.delivDate))
            requestModel.status = 1
            requestModel.save()

            service = getService()
            subject = "Request For PPE Expired"
            ppeType = ""
            if "shield" in requestModel.typePPE:
                ppeType = "3D Printed Face Shields"
            elif "strap" in requestModel.typePPE:
                ppeType = "Face Mask Comfort Strap"
            elif "handle" in requestModel.typePPE:
                ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestModel.typeHandle
            elif "opener" in requestModel.typePPE:
                ppeType = "Personal Touchless Door Opener"
            message_text = "We are sorry to notify you that your request for PPE has expired without being claimed. Your request Details:\n\n\nRequester's Name: %s %s\nRequester's Email: %s\nPPE Delivery Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date of requested PPE: %s\n\nOther Notes For the Donor: %s\n\nAs the website is just launching, we are gathering more donors to help ensure our essential workers can get the PPE they need. Please request again on https://printforthecure.com and we will do our best to help you next time. Thank you for your understanding.\n\nPlease contact us at printforthecure@gmail.com with any questions." % (requestModel.fName, requestModel.lName, requestModel.email, requestModel.address, requestModel.city, requestModel.state, requestModel.zipCode, requestModel.country, ppeType, requestModel.numPPE, requestModel.delivDate, requestModel.notes)
            message = makeMessage("printforthecure@gmail.com", requestModel.email, subject, message_text)
            sendMessage(service, 'me', message)

        if requestModel.status == 0:
            address = requestModel.address + " " + requestModel.city + " " + requestModel.state + " " + requestModel.zipCode
            addressId = "address" + str(counter)
            addresses.append({'addressId': addressId, 'address': address})
            allUnclaimedRequests.append(requestModel)
            counter += 1
    # print(addresses)

    if request.method == 'POST':
        if 'requestObjId' in request.POST.keys():
            print("hi")
            if request.user.is_authenticated:
                base_url = '/confirmation1/'  # 1 /products/
                query_string =  urlencode({'requestObjId': request.POST['requestObjId']})  # 2 category=42
                url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
                return HttpResponseRedirect(url)  # 4
            else:
                return HttpResponseRedirect('/notLoggedIn/')

    template = loader.get_template('main/mapView.html')
    context = {     #all inputs for the html go in these brackets
        'authenticated': request.user.is_authenticated,
        'allRequests': allUnclaimedRequests,
        'addresses': addresses,
        'key' : os.getenv("GOOGLE_CLIENT_API")
    }
    return HttpResponse(template.render(context, request))

@transaction.atomic
def requestPopup(request):
    template = loader.get_template('main/requestPopup.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

def nearbyRequests(request):
    # print(request.user.is_authenticated)
    for requestModel in RequestModel.objects.all():
        if timezone.now().date() > requestModel.delivDate + datetime.timedelta(days=1) and requestModel.status == 0:
            print("Deleting RequestModel (date passed): " + str(requestModel.delivDate))
            requestModel.status = 1
            requestModel.save()

            service = getService()
            subject = "Request For PPE Expired"
            ppeType = ""
            if "shield" in requestModel.typePPE:
                ppeType = "3D Printed Face Shields"
            elif "strap" in requestModel.typePPE:
                ppeType = "Face Mask Comfort Strap"
            elif "handle" in requestModel.typePPE:
                ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestModel.typeHandle
            elif "opener" in requestModel.typePPE:
                ppeType = "Personal Touchless Door Opener"
            message_text = "We are sorry to notify you that your request for PPE has expired without being claimed. Your request Details:\n\n\nRequester's Name: %s %s\nRequester's Email: %s\nPPE Delivery Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date of requested PPE: %s\n\nOther Notes For the Donor: %s\n\nAs the website is just launching, we are gathering more donors to help ensure our essential workers can get the PPE they need. Please request again on https://printforthecure.com and we will do our best to help you next time. Thank you for your understading.\n\nPlease contact us at printforthecure@gmail.com with any questions." % (requestModel.fName, requestModel.lName, requestModel.email, requestModel.address, requestModel.city, requestModel.state, requestModel.zipCode, requestModel.country, ppeType, requestModel.numPPE, requestModel.delivDate, requestModel.notes)
            message = makeMessage("printforthecure@gmail.com", requestModel.email, subject, message_text)
            sendMessage(service, 'me', message)

    if not request.user.is_authenticated:
        return HttpResponseRedirect("/notLoggedIn/")
    if request.method == 'POST':
        if request.user.is_authenticated:
            if 'requestObjId' in request.POST.keys():
                # print("Request ID: " + request.POST['requestModelId'])

                # print("Request Object: " + str(vars(requestObj)))
                #return HttpResponseRedirect('/confirmation/' + '?' + "requestId=" + )

                base_url = '/confirmation/'  # 1 /products/
                query_string =  urlencode({'requestObjId': request.POST['requestObjId']})  # 2 category=42
                url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
                return HttpResponseRedirect(url)  # 4
        else:
            print("not authorized")
            return HttpResponseRedirect("/notLoggedIn/")

    #Below uses Google's Distance Matrix API to sort the list of requests from nearest to furthest
    donor = Donor.objects.get(user = request.user)
    print(vars(donor))

    addressList = donor.address.split()
    addressFormatted = ""
    for word in addressList:
        addressFormatted += word
        addressFormatted += "+"

    cityList = donor.city.split()
    cityFormatted = ""
    for word in cityList:
        addressFormatted += word
        addressFormatted += "+"

    origin = addressFormatted + cityFormatted + donor.state + "+" + donor.zipCode
    print(origin)
    key = os.getenv("GOOGLE_SERVER_API")

    destination = []

    reqlist = []
    for requestModel in RequestModel.objects.all():
        if requestModel.status == 0:

            addressList = requestModel.address.split()
            addressFormatted = ""
            for word in addressList:
                addressFormatted += word
                addressFormatted += "+"

            cityList = requestModel.city.split()
            cityFormatted = ""
            for word in cityList:
                addressFormatted += word
                addressFormatted += "+"
            reqlist.append([addressFormatted + cityFormatted + requestModel.state + "+" + requestModel.zipCode, requestModel])

    def dist(origin, destination):
        lat1, lon1 = origin
        lat2, lon2 = destination
        radius = 6371 # km
        dlat = math.radians(lat2-lat1)
        dlon = math.radians(lon2-lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = radius * c
        return d

    for req in reqlist:
        req.append(dist((donor.lat, donor.lng), (req[1].lat, req[1].lng)))

    reqlist.sort(key=lambda x: x[2])

    destinations = [x[0] for x in reqlist[:10]]
    destinationStr = "|".join(destinations)
    print(destinationStr)
    print(destinations)
    key = "AIzaSyAAetUTOB2h4dzuM1rlmWOdHY-ooSypC7I"
    url = ('https://maps.googleapis.com/maps/api/distancematrix/json' + '?origins={}' + '&destinations={}' + '&key={}').format(urllib.parse.quote(origin, safe=""), urllib.parse.quote(destinationStr, safe=""), key)

    response = urllib.request.urlopen(url)
    responseJSON = json.loads(response.read())

    n = 0
    for item in (responseJSON.get("rows", "none")[0].get("elements", "none")):
        if (item.get("status", "none") != 'NOT_FOUND'):
            distance = item.get("distance", "none").get("value", "none")
            reqlist[n][2] = distance
        n += 1

    template = loader.get_template('main/nearbyRequests.html')
    context = {     #all inputs for the html go in these brackets
        'allRequests': [x[1] for x in reqlist],
        'authenticated': request.user.is_authenticated,
    }
    return HttpResponse(template.render(context, request))

def requestDetails(request):
    template = loader.get_template('main/requestDetails.html')
    context = {}
    return HttpResponse(template.render(context, request))

def notLoggedIn(request):
    if request.method == 'POST':
        if 'return' in request.POST.keys():
            return HttpResponseRedirect("/requestsVisual/")

    template = loader.get_template('main/notLoggedIn.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

@transaction.atomic
def confirmClaim(request):
    requestModelId = request.GET.get('requestObjId')  # 5
    print(requestModelId)
    requestObj = RequestModel.objects.get(id=requestModelId)

    if request.method == 'POST':
        if 'yes' in request.POST.keys():

            requestObj.status = 2
            requestObj.save()

            service = getService()
            #Donor Email
            subject = "Claimed Request For PPE"
            ppeType = ""
            if "shield" in requestObj.typePPE:
                ppeType = "3D Printed Face Shields"
            elif "strap" in requestObj.typePPE:
                ppeType = "Face Mask Comfort Strap"
            elif "handle" in requestObj.typePPE:
                ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestObj.typeHandle
            elif "opener" in requestObj.typePPE:
                ppeType = "Personal Touchless Door Opener"
            message_text = "Thank You For Claiming a request for PPE!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Organization: %s\nRequester's Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date for the requested PPE: %s\n\nOther Notes From the Requester: %s\n\nDelivery Instructions: We suggest that you connect with your requester directly. Donors are expected to ship the PPE directly to the requester, however you may use an alternate method of delivery *if you come to an agreement with your requester*. \n\nThank you for contributing to the battle against Covid-19! We hope you continue donating on our platform! : )\nIf you are interested in receiving a donation to cover the cost of fulfilling the request, we suggest that you communicate to your requester directly." % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.organization, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, requestObj.delivDate, requestObj.notes)
            message = makeMessage("printforthecure@gmail.com", request.user.email, subject, message_text)
            sendMessage(service, 'me', message)

            #Doctor Email
            donor = Donor.objects.get(user = request.user)
            subject = "Request For PPE Claimed"
            message_text1 = "Your Request for PPE has been claimed by a donor!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Organization: %s\nRequester's Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date of requested PPE: %s\n\nOther Notes For the Donor: %s\n\nYour Donor's Name: %s\nDonor's Email: %s\n\nWe suggest contacting your donor directly regarding method of delivery for your request PPE. Donors typically ship directly to your given address, however alternate methods can be used if an agreement is reached with the donor.\n\nIt is truly from the generosity of donors that many doctors and essential workers can receive help during these times. We engourage you to send a very nice note, a gift, or even a monetary donation to keep your donor's spirits high, and to help them continue to do good. We hope our platform serves you well! : )" % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.organization, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, requestObj.delivDate, requestObj.notes, request.user.get_full_name(), request.user.email)
            message = makeMessage("printforthecure@gmail.com", requestObj.email, subject, message_text1)
            sendMessage(service, 'me', message)

            base_url = '/thankyou/'  # 1 /products/
            query_string =  urlencode({'requestDetails': message_text})  # 2 category=42
            url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
            return HttpResponseRedirect(url)  # 4
        elif 'no' in request.POST.keys():
            return HttpResponseRedirect("/nearbyRequests/")
    template = loader.get_template('main/confirmClaim.html')
    context = {     #all inputs for the html go in these brackets
        'requestObj': requestObj,
    }
    return HttpResponse(template.render(context, request))

@transaction.atomic
def confirmClaim1(request):
    requestModelId = request.GET.get('requestObjId')  # 5
    print(requestModelId)
    requestObj = RequestModel.objects.get(id=requestModelId)

    if request.method == 'POST':
        if 'yes' in request.POST.keys():

            requestObj.status = 2
            requestObj.save()

            service = getService()
            #Donor Email
            subject = "Claimed Request For PPE"
            ppeType = ""
            if "shield" in requestObj.typePPE:
                ppeType = "3D Printed Face Shields"
            elif "strap" in requestObj.typePPE:
                ppeType = "Face Mask Comfort Strap"
            elif "handle" in requestObj.typePPE:
                ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestObj.typeHandle
            elif "opener" in requestObj.typePPE:
                ppeType = "Personal Touchless Door Opener"
            message_text = "Thank You For Claiming a request for PPE!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Organization: %s\nRequester's Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date for the requested PPE: %s\n\nOther Notes From the Requester: %s\n\nDelivery Instructions: We suggest that you connect with your requester directly. Donors are expected to ship the PPE directly to the requester, however you may use an alternate method of delivery *if you come to an agreement with your requester*. \n\nThank you for contributing to the battle against Covid-19! We hope you continue donating on our platform! : )\nIf you are interested in receiving a donation to cover the cost of fulfilling the request, we suggest that you communicate to your requester directly." % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, requestObj.delivDate, requestObj.notes)
            message = makeMessage("printforthecure@gmail.com", request.user.email, subject, message_text)
            sendMessage(service, 'me', message)

            #Doctor Email
            donor = Donor.objects.get(user = request.user)
            subject = "Request For PPE Claimed"
            message_text1 = "Your Request for PPE has been claimed by a donor!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Organization: %s\nRequester's Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date of requested PPE: %s\n\nOther Notes For the Donor: %s\n\nYour Donor's Name: %s\nDonor's Email: %s\n\nWe suggest contacting your donor directly regarding method of delivery for your request PPE. Donors typically ship directly to your given address, however alternate methods can be used if an agreement is reached with the donor.\n\nIt is truly from the generosity of donors that many doctors and essential workers can receive help during these times. We engourage you to send a very nice note, a gift, or even a monetary donation to keep your donor's spirits high, and to help them continue to do good. We hope our platform serves you well! : )" % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, requestObj.delivDate, requestObj.notes, request.user.get_full_name(), request.user.email)
            message = makeMessage("printforthecure@gmail.com", requestObj.email, subject, message_text1)
            sendMessage(service, 'me', message)

            base_url = '/thankyou/'  # 1 /products/
            query_string =  urlencode({'requestDetails': message_text})  # 2 category=42
            url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
            return HttpResponseRedirect(url)  # 4
        elif 'no' in request.POST.keys():
            return HttpResponseRedirect("/nearbyRequests/")
    template = loader.get_template('main/confirmClaim.html')
    context = {     #all inputs for the html go in these brackets
        'requestObj': requestObj,
    }
    return HttpResponse(template.render(context, request))

def thankYou(request):
    requestDetails = request.GET.get('requestDetail')
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/thankYou.html')
    context = {
        'requestDetails': requestDetails
    }
    return HttpResponse(template.render(context, request))

def terms(request):
    template = loader.get_template('main/terms.html')
    return HttpResponse(template.render({}, request))

def pp(request):
    template = loader.get_template('main/pp.html')
    return HttpResponse(template.render({}, request))

def test(request):
    template = loader.get_template('main/fileName.html')
    context = {}
    return HttpResponse(template.render(context, request))

def status(request):
    return JsonResponse({'online':'true'})
