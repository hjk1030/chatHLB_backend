import json,bcrypt
import string,random
from django.http import HttpRequest
from utils.utils_request import BAD_METHOD, request_failed, request_success
from utils.utils_require import CheckRequire, require
from bank.models import Account,VerificationCode
from bank.tasks import delete_code_async
# Create your views here.

@CheckRequire
def deposit(req: HttpRequest):
    if req.method == "PUT":
        body = json.loads(req.body.decode())
        serialNumber = require(body,'serialNumber',err_msg='bad param [serialNumber]')
        account = Account.objects.filter(serialNumber=serialNumber).first()
        if account == None:
            return request_failed(1,"Account not found",404)
        amount = require(body,'amount','int','bad param [amount]')
        if amount <= 0:
            return request_failed(-2,"Cannot deposit less than 0 dollars")
        account.balance += amount
        account.save()
        return request_success({})
    else:
        return BAD_METHOD

@CheckRequire
def withdraw(req: HttpRequest):
    if req.method == "PUT":
        body = json.loads(req.body.decode())
        serialNumber = require(body,'serialNumber',err_msg='bad param [serialNumber]')
        account = Account.objects.filter(serialNumber=serialNumber).first()
        if account == None:
            return request_failed(1,"Account not found",404)
        codestr = require(body,'verificationCode','string','bad param [verificationCode]')
        code = VerificationCode.objects.filter(code=codestr,creator=account)
        if not code.exists():
            return request_failed(2,"Code cannot be verified",401)
        code.first().delete()
        amount = require(body,'amount','int','bad param [amount]')
        if amount <= 0:
            return request_failed(-2,"Cannot withdraw less than 0 dollars")
        if account.balance < amount:
            return request_failed(-2,"Do not have enough balance to withdraw")
        account.balance -= amount
        account.save()
        return request_success({})
    else:
        return BAD_METHOD

@CheckRequire
def register(req: HttpRequest):
    if req.method == "POST":
        body = json.loads(req.body.decode())
        key = require(body,'key',err_msg='bad param [key]')
        serialNumber = "621663"+"".join(random.choices(string.digits,k=12))
        sum=0
        for i in range(len(serialNumber)):
            sum+=int(serialNumber[i])*(2 if i%2==0 else 1)
        serialNumber=serialNumber+str(0 if sum%10==0 else 10-sum%10)
        while Account.objects.filter(serialNumber = serialNumber).first():
            serialNumber = "621663"+"".join(random.choices(string.digits,k=12))
            sum=0
            for i in range(len(serialNumber)):
                sum+=int(serialNumber[i])*(2 if i%2==0 else 1)
            serialNumber=serialNumber+str(0 if sum%10==0 else 10-sum%10)
        account = Account(serialNumber=serialNumber,token=bcrypt.hashpw(key.encode(),bcrypt.gensalt(8)).decode())
        account.save()
        return request_success({'serialNumber':serialNumber})
    else:
        return BAD_METHOD

@CheckRequire
def getVerificationCode(req: HttpRequest):
    if req.method == "GET":
        body = req.GET.dict()
        serialNumber = require(body,'serialNumber',err_msg="bad param [serialNumber]")
        key = require(body,'key',err_msg='bad param [key]')
        account = Account.objects.filter(serialNumber=serialNumber)
        if not account.exists():
            return request_failed(1,"Account not found",404)
        account=account.first()
        if not bcrypt.checkpw(key.encode(),account.token.encode()):
            return request_failed(2,"Wrong password or serialNumber",401)
        code = VerificationCode(code="".join(random.choices(string.digits,k=8)),creator=account)
        code.save()
        delete_code_async(code.id)
        return request_success({"verificationCode":code.code})

    else:
        return BAD_METHOD