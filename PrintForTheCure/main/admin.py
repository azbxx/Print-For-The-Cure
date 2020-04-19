from django.contrib import admin

from .models import Donor
from .models import RequestModel
# Register your models here.
admin.site.register(Donor)
admin.site.register(RequestModel)
