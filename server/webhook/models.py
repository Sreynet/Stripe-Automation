from django.db import models

import uuid

# Create your models here.
#EMAIL AND ID AND USERCODE MUST BE UNIQUE
class User(models.Model):
    stripeEmail = models.EmailField(null=True)
    userCode = models.CharField(max_length=50, null=True, unique=True, default=uuid.uuid4)  # Unique user code
    discordID = models.CharField(max_length=50,null=True)
    subscriptionStatus = models.CharField(max_length=50, null=True)