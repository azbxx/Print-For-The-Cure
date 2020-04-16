import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=500, default='')
    state = models.CharField(max_length=2, default='')
    country = models.CharField(max_length=100, default='')
    zipCode = models.CharField(max_length=10, default='')
    registrationDate = models.DateTimeField('date registered')

class Request(models.Model):
    def __str__(self):
        return self.post_text
    fName = models.CharField(max_length=100)
    lName = models.CharField(max_length=100)
    email = models.CharField(max_length=300)
    numPPE = models.IntegerField(default=0)
    typePPE = models.IntegerField(default = 0)
    address = models.CharField(max_length=500)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=10)
    delivDate = models.DateTimeField('date for delivery')
    orderDate = models.DateTimeField('date ordered')
    notes = models.CharField(max_length=4000)
