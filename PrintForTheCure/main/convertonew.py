from .models import Donor
from .models import RequestModel
from .models import Stats
import requests
import os

def updateRequests():
    for req in RequestModel.objects.all():
        if req.lat == 0 or req.lng == 0:
            addressList = req.address.split()
            addressFormatted = ""
            for word in addressList:
                addressFormatted += word
                addressFormatted += "+"

            cityList = req.city.split()
            cityFormatted = ""
            for word in cityList:
                addressFormatted += word
                addressFormatted += "+"
            addr = addressFormatted + cityFormatted + req.state + "+" + req.zipCode
            key = os.getenv("GOOGLE_SERVER_API")
            reqres = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(addr, key))
            loc = reqres.json()['results'][0]['geometry']['location']
            req.lat = loc['lat']
            req.lng = loc['lng']
            req.save()

def updateUsers():
    for don in Donor.objects.all():
        if don.lat == 0 or don.lng == 0:
            addressList = don.address.split()
            addressFormatted = ""
            for word in addressList:
                addressFormatted += word
                addressFormatted += "+"

            cityList = don.city.split()
            cityFormatted = ""
            for word in cityList:
                addressFormatted += word
                addressFormatted += "+"

            addr = addressFormatted + cityFormatted + don.state + "+" + don.zipCode
            key = os.getenv("GOOGLE_SERVER_API")
            reqres = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(addr, key))
            loc = reqres.json()['results'][0]['geometry']['location']
            don.lat = loc['lat']
            don.lng = loc['lng']
            don.save()
