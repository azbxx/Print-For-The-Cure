from django.contrib import admin

from .models import Donor
from .models import RequestModel
from .models import Stats
# Register your models here.
admin.site.register(Donor)
admin.site.register(RequestModel)
admin.site.register(Stats)
