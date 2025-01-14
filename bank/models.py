from django.db import models
from utils.utils_require import MAX_BCRYPTED_PASSWORD_KEY_LENGTH

# Create your models here.

class Account(models.Model):
    id = models.BigAutoField(primary_key=True)
    serialNumber = models.CharField(max_length=32,default='')
    token = models.CharField(max_length=MAX_BCRYPTED_PASSWORD_KEY_LENGTH,default='')
    balance = models.BigIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["serialNumber"]),
        ]

class VerificationCode(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=8,default='')
    creator = models.ForeignKey(to=Account,on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["code"])
        ]