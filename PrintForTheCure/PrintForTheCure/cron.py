from ..main.models import Donor
from ..main.models import RequestModel
from ..main.models import Stats
import decimal

import numpy as np

def getStats():
    for requestModel in RequestModel.objects.all():
        if requestModel.status == 2:
            claimedPPE += requestModel.numPPE

    claimedPPEMod = claimedPPE - np.mod(claimedPPE, 10)

    totalRequests = 0
    claimedRequests = 0
    for requestModel in RequestModel.objects.all():
        if requestModel.status == 1 or requestModel.status == 2:
            totalRequests += 1
        if requestModel.status == 2:
            claimedRequests += 1
            totalRequests += 1

    claimRate = claimedRequests/totalRequests
    obj = Stats.objects.get_or_create(getId=0)
    obj.claimRate = claimRate
    obj.claims = claimedPPEMod
