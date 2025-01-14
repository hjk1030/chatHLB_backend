from django.db import models
import utils.utils_require
import utils.utils_time
from utils.utils_user import defaultCredit

# Create your models here.

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    token = models.CharField(max_length=utils.utils_require.MAX_TOKEN_LENGTH, unique=True)
    key = models.CharField(max_length=utils.utils_require.MAX_BCRYPTED_PASSWORD_KEY_LENGTH)
    userName = models.CharField(max_length=utils.utils_require.MAX_USERNAME_LENGTH, unique=True)
    adminPrivilege = models.BooleanField(default=False)
    uploadPrivilege = models.BooleanField(default=False)
    labelPrivilege = models.BooleanField(default=False)
    mediationPrivilege = models.BooleanField(default=False)
    advertisePrivilege = models.BooleanField(default=False)
    experience = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    lastupdatedtime = models.FloatField(default=0)
    currentTaskPackage = models.ForeignKey(to="task.TaskPackage",on_delete=models.CASCADE,null=True,blank=True)
    deadline = models.FloatField(default=1e15)
    credit = models.IntegerField(default=defaultCredit)
    systemMessage = models.JSONField(default=list)
    faceEncoding = models.CharField(max_length=100000,default='')
    invitationCode = models.CharField(max_length=32,default='')
    packageAcceptTime = models.JSONField(default=list)
    bankAccount = models.CharField(max_length=32,default='')
    preferTags = models.JSONField(default=list)
    emailAddress = models.CharField(max_length=100,default='')
    code = models.CharField(max_length=10,default='')
    codeDeadline = models.FloatField(default=0)
    checkEmail = models.BooleanField(default=False)
    vipExpireTime = models.FloatField(default=0)
    availbleScore = models.IntegerField(default=0)
    labelCount = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["userName"]),
            models.Index(fields=["invitationCode"]),
            models.Index(fields=["emailAddress"]),
        ]
        
    def serialize(self):
        return {
            "id": self.id,
            "userName": self.userName,
            "adminPrivilege": self.adminPrivilege,
            "uploadPrivilege": self.uploadPrivilege,
            "labelPrivilege": self.labelPrivilege,
            "mediationPrivilege": self.mediationPrivilege,
            "advertisePrivilege": self.advertisePrivilege,
            "experience": self.experience,
            "score": self.score,
            "credit": self.credit,
            "labelCount": self.labelCount,
        }
    
    def serialize_private(self):
        return {
            "deadline": self.deadline,
            "systemMessage": self.systemMessage,
            "bankAccount": self.bankAccount,
            "preferTags": self.preferTags,
            "emailAddress": self.emailAddress,
            "checkEmail": self.checkEmail,
            "invitationCode": self.invitationCode,
            "vipExpireTime": self.vipExpireTime if self.vipExpireTime > utils.utils_time.get_timestamp() else 0,
            "availbleScore": self.availbleScore,
        }

class AdminMessage(models.Model):
    id = models.BigAutoField(primary_key=True)
    targetId = models.IntegerField(default=0)
    type = models.CharField(max_length=32,default='')
    message = models.CharField(max_length=300,default='')
    sender = models.ForeignKey(to=User,on_delete=models.CASCADE)

    class Meta:
        indexes = []
    
    def serialize(self):
        return {
            "targetId":self.targetId,
            "type":self.type,
            "message":self.message,
            "sender":{
                "id":self.sender.id,
                "userName":self.sender.userName,
                "credit":self.sender.credit,
            },
            "id":self.id,
        }
    
class VerificationCode(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=utils.utils_require.MOBILE_VERIFICATION_CODE_LENGTH,default='chatHLBVerificationCode')
    senderId = models.IntegerField(default=0)
    senderToken = models.CharField(max_length=utils.utils_require.MAX_TOKEN_LENGTH,default='')

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
        ]