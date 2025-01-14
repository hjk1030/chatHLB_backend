import json, bcrypt, os
import string, random, datetime
from django.http import HttpRequest
from utils.utils_request import BAD_METHOD, request_failed, request_success
from utils.utils_require import CheckRequire, require
from advertise.models import Advertise
from user.models import User, AdminMessage
from utils.utils_time import get_timestamp
from django.conf import settings

# Create your views here.

@CheckRequire
def upload(req: HttpRequest):
    if req.method == "POST":
        sender_id = req.POST.get("senderId", None)
        sender_token = req.POST.get("senderToken", None)
        sender = User.objects.filter(id = sender_id).first()

        if sender_id == None:
            return request_failed(-2, "bad param [senderId]", status_code = 400)
        if sender_token == None:
            return request_failed(-2, "bad param [senderToken]", status_code = 400)

        if not sender:
            return request_failed(1, "Sender not found", status_code = 404)
        if sender.token != sender_token:
            return request_failed(2, "No permissions", status_code = 401)
        if sender.advertisePrivilege == False and sender.adminPrivilege == False:
            return request_failed(2, "No permissions", status_code = 401)

        time = req.POST.get("duration", None)
        if time == None:
            return request_failed(-2, "bad param [duration]", status_code = 400)
        time = int(time)
        if sender.score < time * 200:
            return request_failed(-2, "Score is not enough", status_code = 400)

        kind = req.POST.get("kind")
        if kind == "text":
            text = req.POST.get("text", None)
            if not text:
                return request_failed(-3, "Upload file without text", status_code = 400)
            time_ = (datetime.datetime.now() + datetime.timedelta(hours = time)).timestamp()
            ad = Advertise(creator = sender, kind = "text", text = text, expirationTime = time_)
            ad.save()

            message = AdminMessage(targetId = ad.id, type = "advertisementText", message = ad.text, sender = sender)
            message.save()
        
        elif kind == "image":
            image = req.FILES.get("image", None)
            if not image:
                return request_failed(-3, "Upload file without image", status_code = 400)
            
            if ".jpg" in image.name:
                new_name = "".join(random.choices(string.digits+string.ascii_letters,k=32))+".jpg"
            elif ".png" in image.name:
                new_name = "".join(random.choices(string.digits+string.ascii_letters,k=32))+".png"
            else:
                return request_failed(-3, "Wrong kind of image", status_code = 400)
            file_path = os.path.join(settings.MEDIA_ROOT, new_name)

            upload_file = open(file_path, "wb")
            for chunk in image.chunks():
                upload_file.write(chunk)
            upload_file.close()

            time_ = (datetime.datetime.now() + datetime.timedelta(hours = time)).timestamp()
            ad = Advertise(creator = sender, kind = "text", url = os.path.join(settings.MEDIA_URL, new_name), expirationTime = time_)
            ad.save()

            message = AdminMessage(targetId = ad.id, type = "advertisementImage", message = ad.url, sender = sender)
            message.save()

        else:
            return request_failed(-3, "Wrong kind of advertising", status_code = 400)

        sender.lastupdatedtime = get_timestamp()
        sender.save()
        
        return request_success()

    else:
        return BAD_METHOD

@CheckRequire
def getinfo(req: HttpRequest, id: any):
    if req.method == 'GET':
        id = require({"id": id}, "id", "int", err_msg = "Bad param [id]", err_code = -1)
        ad = Advertise.objects.filter(id = id).first()
        if not ad:
            return request_failed(1, "Advertisement not found", status_code = 404)

        body = req.GET.dict()
        sender_id = require(body, "senderId", "int", err_msg = "Missing or error type of [senderId]", err_code = -2)
        sender_token = require(body, "senderToken", "string", err_msg = "Missing or error type of [senderToken]", err_code = -2)
        sender = User.objects.filter(id = sender_id).first()
        if not sender:
            return request_failed(1, "Sender not found", status_code = 404)
        if sender.token != sender_token:
            return request_failed(2, "Token not match", status_code = 401)

        sender.lastupdatedtime = get_timestamp()
        sender.save()

        return request_success(ad.serialize())
    
    else:
        return BAD_METHOD

@CheckRequire
def getlist(req: HttpRequest):
    if req.method == 'GET':
        body = req.GET.dict()
        sender_id = require(body, "senderId", "int", err_msg = "Missing or error type of [senderId]", err_code = -2)
        sender_token = require(body, "senderToken", "string", err_msg = "Missing or error type of [senderToken]", err_code = -2)
        sender = User.objects.filter(id = sender_id).first()
        if not sender:
            return request_failed(1, "Sender not found", status_code = 404)
        if sender.token != sender_token:
            return request_failed(2, "Token not match", status_code = 401)

        ad_list = Advertise.objects.filter(examination = True, expirationTime__gte = get_timestamp())
        if len(ad_list) == 0:
            ad_list = Advertise.objects.filter(examination = True, expirationTime = -1)

        sender.lastupdatedtime = get_timestamp()
        sender.save()

        return request_success({'adList':[u.serialize() for u in ad_list]})
    
    else:
        return BAD_METHOD