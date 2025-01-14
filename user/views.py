import json
import random,string
from django.http import HttpRequest, HttpResponse
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_TOKEN_LENGTH, MAX_PASSWORD_KEY_LENGTH, MAX_USERNAME_LENGTH, MAX_USER_LIST_COUNT, CheckRequire, require
from utils.utils_require import MAX_TAGS_COUNT,MAX_TAG_LENGTH,INVITATION_CODE_LENGTH,MOBILE_VERIFICATION_CODE_LENGTH,SUPPORTED_USER_SORTING
from utils.utils_time import get_timestamp
from advertise.models import Advertise
from user.models import User,AdminMessage,VerificationCode
from task.models import TaskPackage,TaskTemplate
from utils.utils_require import MAX_SYSTEM_MESSAGE
from user.userauth import userAuth
from django.core.paginator import Paginator,EmptyPage
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import bcrypt, requests, cv2, face_recognition, datetime
from math import ceil
from utils.utils_user import scoreDifference
import numpy as np
import base64
import datetime

# Create your views here.
def send_message_to_user(targetId:int,message:str):
    targetUser = User.objects.get(id=targetId)
    if len(targetUser.systemMessage)>=MAX_SYSTEM_MESSAGE:
        targetUser.systemMessage = targetUser.systemMessage[1:MAX_SYSTEM_MESSAGE-1]
    targetUser.systemMessage.append({"message":message,"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    targetUser.save()

# @CheckRequire
def check_for_register_data(body):
    user_name = require(body, "userName", "string", err_msg = "Missing or error type of [userName]")
    key = require(body, "key", "string", err_msg = "Missing or error type of [userName]")
    email_address = require(body, "emailAddress", "string", err_msg = "Missing or error type of [emailAddress]")

    assert 0 < len(user_name) <= MAX_USERNAME_LENGTH, "Bad length of [userName]"
    assert len(key) == MAX_PASSWORD_KEY_LENGTH, "Bad length of [key]"

    base_str = string.ascii_letters+string.digits+'_'
    
    for i in range(len(user_name)):
        assert user_name[i] in base_str, "Invalid char in [userName]"
    
    return user_name, key, email_address

# @CheckRequire
def check_for_reset_data(body):
    sender_id = require(body, "senderId", "int", err_msg = "Missing or error type of [senderId]")
    sender_token = require(body, "senderToken", "string", err_msg = "Missing or error type of [senderToken]")
    target_id = require(body, "targetId", "int", err_msg = "Missing or error type of [targetId]")
    newKey = require(body, "newKey", "string", err_msg = "Missing or error type of [newKey]")
    
    assert len(newKey) == MAX_PASSWORD_KEY_LENGTH, "Bad length of [key]"
    assert len(sender_token) == MAX_TOKEN_LENGTH, "Bad length of [token]"
    
    return sender_id, sender_token, target_id, newKey

def create_token():
    random_str =""
    base_str = string.ascii_letters+string.digits
    random_str = "".join(random.choices(base_str,k=MAX_TOKEN_LENGTH))
    return random_str

@CheckRequire
def register(req: HttpRequest):
    if req.method == "POST":
        body = json.loads(req.body.decode("utf-8"))
        user_name, key, email_address = check_for_register_data(body)
        user = User.objects.filter(userName = user_name).first()

        try:
            validate_email(email_address)
        except ValidationError:
            return request_failed(-2, "Email address format is invalid", status_code = 400)
        if User.objects.filter(emailAddress=email_address).count()>=4:
            return request_failed(-2, "The Email has been registered by too many users.")
        
        if 'invitationCode' in body:
            invitationCode = require(body,'invitationCode',err_msg='bad param [invitationCode]')
            if len(invitationCode) != INVITATION_CODE_LENGTH:
                return request_failed(-2,"Bad length of invitationCode")
            invitation = User.objects.filter(invitationCode=invitationCode).first()
            if invitation != None:
                invitation.score += 20
                invitation.save()
                send_message_to_user(invitation.id,"您成功邀请了一位用户！")
        if user:
            return request_failed(-2, "User name already exists", status_code = 400)
        
        code = ''.join([random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for _ in range(6)])
        try:
            send_mail(
                '确认信息邮件',
                f'这是一封确认邮件，验证码为：{code}',
                '[CENSORED]',
                [email_address]
            )
        except Exception as e:
            return request_failed(-2, f"Error sending email: {str(e)}", status_code = 400)

        user = User(userName = user_name, key = bcrypt.hashpw(key.encode(),bcrypt.gensalt(8)).decode(), token = create_token(), 
                    invitationCode = "".join(random.choices(string.ascii_letters+string.digits,k=INVITATION_CODE_LENGTH)), lastupdatedtime = get_timestamp(), emailAddress = email_address, code = code)
        user.save()
        user = User.objects.filter(userName = user_name).first()
        send_message_to_user(user.id, "请尽快完成邮箱验证，验证码已经发送至邮箱中！")
        return request_success()
    else:
        return BAD_METHOD

@CheckRequire
def check_email(req: HttpRequest, id: any):
    if req.method == "POST":
        id = require({"id": id}, "id", "int", err_msg = "Missing or error type of [id]")
        
        body = json.loads(req.body.decode("utf-8"))
        sender_id = require(body, "senderId", "int", err_msg = "Missing or error type of [senderId]")
        sender_token = require(body, "senderToken", "string", err_msg = "Missing or error type of [senderToken]")
        code = require(body, "code", "string", err_msg = "Missing or error type of [code]")

        user = User.objects.filter(id = id).first()
        if not user:
            return request_failed(1, "user does not exist", status_code = 404)

        if user.token != sender_token:
            return request_failed(2, "No permissions", status_code = 401)
        if sender_id != id:
            return request_failed(2, "No permissions", status_code = 401)

        if user.checkEmail == True:
            return request_failed(-2, "user has already check email", status_code = 400)
        if user.code != code:
            return request_failed(-2, "wrong code", status_code = 400)

        user.code = ''
        user.checkEmail = True
        user.lastupdatedtime = get_timestamp()
        user.save()
        return request_success()
    else:
        return BAD_METHOD

# GET /user/{id} API
@CheckRequire
def getUserBasicInfo(req: HttpRequest, id: any):
    if req.method=='GET':
        # Authenticate
        body = req.GET.dict()
        
        senderId = require(body,'senderId','int',err_msg='Bad param [senderId]')
        senderUser = User.objects.filter(id=senderId).first()
        if senderUser == None:
            return request_failed(code=1,info='User Requesting Information Not Found',status_code=404)
        senderToken = require(body,'senderToken','string',err_msg='Bad param [senderToken]')
        if len(senderToken) != MAX_TOKEN_LENGTH:
            return request_failed(code=-2,info='Bad senderToken length')
        if senderUser.token != senderToken:
            return request_failed(code=2,info='Token Does not Match',status_code=401)

        userId = require({'id':id},'id','int',err_msg='Bad param [id]',err_code=-1)

        senderId = require(body,"senderId","int","bad param [senderId]")

        targetUser = User.objects.filter(id=userId).first()

        if targetUser == None:
            return request_failed(code=1,info='User not Found',status_code=404)

        return request_success(targetUser.serialize()|({} if userId != senderId and not senderUser.adminPrivilege else targetUser.serialize_private()))

    else:
        return BAD_METHOD

@CheckRequire
def reset(req: HttpRequest):
    if req.method == "PUT":
        body = json.loads(req.body.decode("utf-8"))
        sender_id, sender_token, target_id, newKey = check_for_reset_data(body)

        change_user = User.objects.filter(id = sender_id).first()
        target_user = User.objects.filter(id = target_id).first()

        if not change_user:
            return request_failed(1, "sender does not exist", status_code = 404)
        if not target_user:
            return request_failed(1, "Target does not exist", status_code = 404)

        if change_user.token != sender_token:
            return request_failed(2, "No permissions", status_code = 401)
        if sender_id != target_id and change_user.adminPrivilege == False:
            return request_failed(2, "No permissions", status_code = 401)

        target_user.key = bcrypt.hashpw(newKey.encode(),bcrypt.gensalt(8)).decode()
        target_user.token = create_token()
        if target_user.id != change_user.id:
            change_user.lastupdatedtime = get_timestamp()
        else:
            target_user.lastupdatedtime = get_timestamp()
        target_user.save()
        if target_user.id != change_user.id:
            change_user.save()
        return request_success({})
    else:
        return BAD_METHOD

@CheckRequire
def modify_information(req: HttpRequest):
    if req.method == "PUT":
        body = json.loads(req.body.decode("utf-8"))

        sender_token = require(body, "senderToken", "string", err_msg="Missing or error type of [senderToken]")
        if len(sender_token) != MAX_TOKEN_LENGTH:
            return request_failed(-1, "Bad length of [senderToken]", status_code=400)
        
        sender_id = require(body, "senderId", "int", err_msg="Missing or error type of [senderId]")
        target_id = require(body, "targetId", "int", err_msg="Missing or error type of [targetId]")
        
        sender = User.objects.filter(id=sender_id).first()
        target = User.objects.filter(id=target_id).first()

        if not sender:
            return request_failed(1, info="sender not found", status_code=404)
        if not target:
            return request_failed(1, info="Target not found", status_code=404)
        if sender_token != sender.token:
            return request_failed(2, info="No permission", status_code=401)
        if sender_id != target_id and not sender.adminPrivilege:
            return request_failed(2, info="No permission", status_code=401)
        
        user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
        admin_privilege = require(body, "adminPrivilege", "bool", err_msg="Missing or error type of [adminPrivilege]")
        upload_privilege = require(body, "uploadPrivilege", "bool", err_msg="Missing or error type of [uploadPrivilege]")
        label_privilege = require(body, "labelPrivilege", "bool", err_msg="Missing or error type of [labelPrivilege]")
        if "mediationPrivilege" in body:
            mediation_privilege = require(body, "mediationPrivilege", "bool", err_msg="Missing or error type of [mediationPrivilege]")
        else:
            mediation_privilege = False

        if "advertisePrivilege" in body:
            advertise_privilege = require(body, "advertisePrivilege", "bool", err_msg="Missing or error type of [advertisePrivilege]")
        else:
            advertise_privilege = False

        # check userName
        if not (0 < len(user_name) <= MAX_USERNAME_LENGTH):
            return request_failed(-1, "Bad length of [userName]", status_code=400)

        base_str = string.ascii_letters+string.digits+'_'
        for i in range(len(user_name)):
            assert user_name[i] in base_str, "Invalid char in [userName]"
        
        target.userName = user_name

        if target.adminPrivilege != admin_privilege and sender.adminPrivilege == False:
            return request_failed(2, info="No permission", status_code=401)
        if target.uploadPrivilege != upload_privilege and sender.adminPrivilege == False:
            return request_failed(2, info="No permission", status_code=401)
        if target.labelPrivilege != label_privilege and sender.adminPrivilege == False:
            return request_failed(2, info="No permission", status_code=401)
        if target.mediationPrivilege != mediation_privilege and sender.adminPrivilege == False:
            return request_failed(2, info="No permission", status_code=401)
        if target.advertisePrivilege != advertise_privilege and sender.adminPrivilege == False:
            return request_failed(2, info="No permission", status_code=401)

        if 'bankAccount' in body:
            bankAccount = require(body,'bankAccount',err_msg='bad param [bankAccount]')
            if len(bankAccount)>32:
                return request_failed(-2,"Too long bankaccount")
            target.bankAccount=bankAccount

        
        if 'preferTags' in body:
            preferTags = require(body,'preferTags','list',"bad param [preferTags]")
            if len(preferTags)>MAX_TAGS_COUNT:
                return request_failed(-2,"bad param [preferTags]:Too much preferred tags")
            for s in preferTags:
                s = require({"s":s},"s",err_msg="bad param [preferTags]:Not convertable to string")
                if len(s)>MAX_TAG_LENGTH:
                    return request_failed(-2,"bad param [prefertags]:too long tags")
            
        target.adminPrivilege = admin_privilege
        target.uploadPrivilege = upload_privilege
        target.labelPrivilege = label_privilege
        target.mediationPrivilege = mediation_privilege
        target.advertisePrivilege = advertise_privilege
        if target.id != sender.id:
            sender.lastupdatedtime = get_timestamp()
        else:
            target.lastupdatedtime = get_timestamp()
        if 'preferTags' in body:
            target.preferTags=preferTags
        target.save()
        if target.id != sender.id:
            sender.save()
        
        return request_success()
    else:
        return BAD_METHOD

@CheckRequire
def get_login_information(req: HttpRequest, userName: any):
    if req.method == "GET":
        body = req.GET.dict()

        user_name = require({"userName": userName}, "userName", "string", err_msg="Bad param [userName]", err_code=-1)
        key = require(body, "key", "string", err_msg="Missing or error type of [key]", err_code=-1)

        if not (0 < len(user_name) <= MAX_USERNAME_LENGTH):
            return request_failed(-1, "Bad length of [userName]", status_code=400)
        if len(key) != MAX_PASSWORD_KEY_LENGTH:
            return request_failed(-2, "Bad length of [key]", status_code=400)
        user = User.objects.filter(userName=user_name).first()

        if not user:
            return request_failed(1, "User not found", status_code=404)
        
        if bcrypt.checkpw(key.encode(),user.key.encode()) == False:
            return request_failed(2, "Incorrect password", status_code=401)
        return_data = {'id':user.id,'token':user.token}
        return request_success(return_data)
    else:
        return BAD_METHOD

@CheckRequire
def get_user_list(req: HttpRequest):
    if req.method == "GET":
        body = req.GET.dict()
        authres = userAuth(body)
        if authres != None:
            return authres
        pageId = require(body,'pageId','int',err_msg="bad param [pageId]")
        if pageId <= 0:
            return request_failed(-2,"bad param [pageId] with pageId leq to 0")
        count = require(body,'count','int',err_msg='bad param [cound]')
        if count <=0:
            return request_failed(-2,"bad param [count] with count leq to 0")
        if count > MAX_USER_LIST_COUNT:
            return request_failed(-2,"bad param [count] with too large count")
        sortBy = require(body,'sortBy',err_msg='bad param [sortBy]')
        sortByAscend = require(body,'sortByAscend','int',err_msg='bad param [sortByAscend]')
        if not sortBy in SUPPORTED_USER_SORTING:
            return request_failed(-2,'[sortBy] should be id or score')
        if sortByAscend != 0 and sortByAscend != 1:
            return request_failed(-2,'bad param [sortByAscend] with value other than 0 and 1')
        if sortByAscend == 0:
            sortBy = f"-{sortBy}"
        sender = User.objects.get(id=body['senderId'])
        if not sender.adminPrivilege:
            users = User.objects.exclude(adminPrivilege=False,uploadPrivilege=False,labelPrivilege=False,mediationPrivilege=False,advertisePrivilege=False)\
                .order_by(sortBy)
        else:
            users = User.objects.all().order_by(sortBy)
        userPages = Paginator(users,count)
        try:
            page = userPages.page(pageId)
        except EmptyPage:
            page = userPages.page(userPages.num_pages)
        
        sender = User.objects.get(id=body['senderId'])
        sender.lastupdatedtime = get_timestamp()
        sender.save()

        return request_success({'pageCount':userPages.num_pages,'userList':[u.serialize() for u in page.object_list]})
    else:
        return BAD_METHOD

@CheckRequire
def get_user_list_availble(req: HttpRequest):
    if req.method == "GET":
        body = req.GET.dict()
        authres = userAuth(body)
        if authres != None:
            return authres
        sender = User.objects.get(id=body['senderId'])
        if not sender.adminPrivilege and not sender.mediationPrivilege:
            return request_failed(2,"No permission",401)
        users = User.objects.filter(labelPrivilege=True,currentTaskPackage=None,credit__gt=75)
        
        sender = User.objects.get(id=body['senderId'])
        sender.lastupdatedtime = get_timestamp()
        sender.save()

        return request_success({'userList':[u.serialize() for u in users]})
    else:
        return BAD_METHOD

@CheckRequire
def billing(req: HttpRequest):
    if req.method == 'PUT':
        body = json.loads(req.body.decode())
        authRes = userAuth(body)
        if authRes != None:
            return authRes
        sender = User.objects.get(id=body['senderId'])
        amount = require(body,'amount','int','bad param [amount]')
        if amount < 0:
            return request_failed(-2,"Amount less than 0")
        isPayment = require(body,'isPayment','bool','bad param [isPayment]')
        if sender.bankAccount == '':
            return request_failed(-2,"You haven't provided your bank account. Modify it at the user info page.")
        serialNumber = sender.bankAccount
        if isPayment:
            verificationCode = require(body,'verificationCode',err_msg='bad param [verificationCode]')
            bankRes = requests.put('http://127.0.0.1:8000/bank/withdraw',json={"serialNumber":serialNumber,"verificationCode":verificationCode,"amount":amount})
            if bankRes.status_code != 200:
                return request_failed(-2,"Request failed from bank with message:["+str(bankRes.status_code)+'] '+(bankRes.json()['info'] if 'info' in bankRes.json() else ''))
            sender.score += amount
            sender.experience += amount * 5
            sender.lastupdatedtime = get_timestamp()
            sender.save()
            return request_success()
        else:
            if sender.availbleScore < amount:
                return request_failed(-2,"You don't have enough score to withdraw")
            bankRes = requests.put('http://127.0.0.1:8000/bank/deposit',json={"serialNumber":serialNumber,"amount":amount})
            if bankRes.status_code != 200:
                return request_failed(-2,"Request failed from bank with message:["+str(bankRes.status_code)+'] '+(bankRes.json()['info'] if 'info' in bankRes.json() else ''))
            sender.score -= amount
            sender.availbleScore -= amount
            sender.lastupdatedtime = get_timestamp()
            sender.save()
            return request_success()
    else:
        return BAD_METHOD

@CheckRequire
def handle_requests(req: HttpRequest,id: any):
    if req.method == "PUT":
        body = json.loads(req.body.decode())
        authRes = userAuth(body)
        if authRes != None:
            return authRes
        sender = User.objects.get(id=body['senderId'])
        if not sender.adminPrivilege:
            return request_failed(2,"No admin privilge",401)
        id = require({"id":id},"id","int","bad param [id]",-1)
        message = AdminMessage.objects.filter(id=id).first()
        if message == None:
            return request_failed(1,"Message not found",404)
        accepted = require(body,"accepted","bool","bad param [accepted]")

        if message.type == "user":
            targetUser = User.objects.get(id=message.targetId)
            if accepted:
                targetUser.credit -= 20
                targetUser.save()
                send_message_to_user(message.targetId,f"您被其他用户举报，举报理由为：{message.message}，经审核通过，已扣除信用分。")
                send_message_to_user(message.sender.id,f"您举报编号为{message.targetId}的用户审核通过。")
            else:
                send_message_to_user(message.sender.id,f"您举报编号为{message.targetId}的用户审核未通过。")
        elif message.type == "package":
            targetPackage = TaskPackage.objects.get(id=message.targetId)
            if accepted:
                targetPackage.verified=True
                targetPackage.save()
                send_message_to_user(message.sender.id,f"您编号为{message.targetId}的任务审核已通过。")
            else:
                targetPackage.distributed=False
                targetPackage.availbleCount=0
                targetPackage.save()
                send_message_to_user(message.sender.id,f"您编号为{message.targetId}的任务审核未通过，请修改后重新发布。")
                sender.refresh_from_db()
                sender.score += ceil(targetPackage.score*targetPackage.maxDistributedUser*scoreDifference)
                sender.save()
        elif message.type == "template":
            targetTemplate = TaskTemplate.objects.get(id=message.targetId)
            if accepted:
                targetTemplate.verified=True
                targetTemplate.save()
                send_message_to_user(message.sender.id,f"您编号为{message.targetId}的模板已审核通过")
            else:
                send_message_to_user(message.sender.id,f"您编号为{message.targetId}的模板未审核通过")
            
        elif message.type == "advertisementText":
            ad = Advertise.objects.get(id = message.targetId)
            if accepted:
                ad.examination = True
                ad.save()
                send_message_to_user(ad.creator.id, "您的文字广告申请已通过。")
            else:
                send_message_to_user(ad.creator.id, "您的文字广告申请未通过。")
            
        elif message.type == "advertisementImage":
            ad = Advertise.objects.get(id = message.targetId)
            if accepted:
                ad.examination = True
                ad.save()
                send_message_to_user(ad.creator.id, "您的图片广告申请已通过。")
            else:
                send_message_to_user(ad.creator.id, "您的图片广告申请未通过。")

        elif message.type == "uploadPrivilege":
            targetUser = User.objects.get(id=message.targetId)
            if accepted:
                targetUser.uploadPrivilege=True
                targetUser.save()
                send_message_to_user(message.targetId,"您的上传权限申请已通过。")
            else:
                send_message_to_user(message.targetId,"您的上传权限申请未通过。")
            
        elif message.type == "labelPrivilege":
            targetUser = User.objects.get(id=message.targetId)
            if accepted:
                targetUser.labelPrivilege=True
                targetUser.save()
                send_message_to_user(message.targetId,"您的标注权限申请已通过。")
            else:
                send_message_to_user(message.targetId,"您的标注权限申请未通过。")
            
        elif message.type == "mediationPrivilege":
            targetUser = User.objects.get(id=message.targetId)
            if accepted:
                targetUser.mediationPrivilege=True
                targetUser.save()
                send_message_to_user(message.targetId,"您的中介权限申请已通过。")
            else:
                send_message_to_user(message.targetId,"您的中介权限申请未通过。")
            
        elif message.type == "advertisePrivilege":
            targetUser = User.objects.get(id=message.targetId)
            if accepted:
                targetUser.advertisePrivilege=True
                targetUser.save()
                send_message_to_user(message.targetId,"您的广告商权限申请已通过。")
            else:
                send_message_to_user(message.targetId,"您的广告商权限申请未通过。")
        else:
            return request_failed(-3,"Unknown message type detected. Contact admin about this.",500)
        sender.refresh_from_db()
        sender.lastupdatedtime=get_timestamp()
        sender.save()
        message.delete()
        return request_success()
    else:
        return BAD_METHOD

@CheckRequire
def require_privilege(req: HttpRequest):
    if req.method == "POST":
        body = json.loads(req.body.decode())
        authRes = userAuth(body)
        if authRes != None:
            return authRes
        sender = User.objects.get(id=body['senderId'])
        privilege = require(body,"privilege",err_msg="bad param [privilege]")
        if privilege != "uploadPrivilege" and privilege != "labelPrivilege" and privilege != "mediationPrivilege" and privilege != "advertisePrivilege":
            return request_failed(-2,"Unsupported privilege type")
        if privilege == "uploadPrivilege" and sender.uploadPrivilege  == True:
            return request_failed(-2,"Privilege type is already true")
        if privilege == "labelPrivilege" and sender.labelPrivilege  == True:
            return request_failed(-2,"Privilege type is already true")
        if privilege == "mediationPrivilege" and sender.mediationPrivilege  == True:
            return request_failed(-2,"Privilege type is already true")
        if privilege == "advertisePrivilege" and sender.advertisePrivilege  == True:
            return request_failed(-2,"Privilege type is already true")
        if AdminMessage.objects.filter(sender=sender,type=privilege).exists():
            return request_failed(-2,"You have requested the privilege before. Please wait patiently for reply.")
        message=AdminMessage(targetId = sender.id,type=privilege,sender=sender)
        message.save()
        sender.lastupdatedtime=get_timestamp()
        sender.save()
        return request_success()
    else:
        return BAD_METHOD

@CheckRequire
def requests_list(req: HttpRequest):
    if req.method == "GET":
        body = req.GET.dict()
        authRes = userAuth(body)
        if authRes != None:
            return authRes
        pageId = require(body,'pageId','int',err_msg="bad param [pageId]")
        if pageId <= 0:
            return request_failed(-2,"bad param [pageId] with pageId leq to 0")
        count = require(body,'count','int',err_msg='bad param [cound]')
        if count <=0:
            return request_failed(-2,"bad param [count] with count leq to 0")
        if count > MAX_USER_LIST_COUNT:
            return request_failed(-2,"bad param [count] with too large count")
        messages = AdminMessage.objects.all().order_by("id")
        pages = Paginator(messages,count)
        try:
            page = pages.page(pageId)
        except EmptyPage:
            page = pages.page(pages.num_pages)
        
        sender = User.objects.get(id=body['senderId'])
        sender.lastupdatedtime=get_timestamp()
        sender.save()
        return request_success({"messages":[r.serialize() for r in page.object_list],"pageCount":pages.num_pages})

    else:
        return BAD_METHOD

@CheckRequire
def user_report(req: HttpRequest):
    if req.method == "POST":
        body = json.loads(req.body.decode())
        authRes = userAuth(body)
        if authRes != None:
            return authRes
        sender = User.objects.get(id=body['senderId'])
        if not sender.adminPrivilege and not sender.uploadPrivilege and not sender.labelPrivilege and not sender.mediationPrivilege:
            return request_failed(-3,"You don't have any privilege. Request for a privilege and report users then.")
        targetId = require(body,"targetId","int","bad param [targetId]")
        target = User.objects.filter(id=targetId).first()
        if target == None:
            return request_failed(1,"Target user not found",404)
        messageText = require(body,"message",err_msg="bad param [message]")
        messages = AdminMessage.objects.filter(sender=sender,type="user")
        if messages.count()>=5:
            return request_failed(-3,"You reported too much users at the same time")
        messages=messages.filter(targetId=targetId)
        if messages.exists():
            return request_failed(-3,"You already reported this user")
        message = AdminMessage(targetId=targetId,sender=sender,message=messageText,type="user")
        message.save()
        sender.lastupdatedtime=get_timestamp()
        sender.save()
        return request_success()
    else:
        return BAD_METHOD

@CheckRequire
def get_facelogin_information(req: HttpRequest, userName: any):
    if req.method == "POST":
        user_name = require({"userName": userName}, "userName", "string", err_msg = "Bad param [userName]", err_code = -1)

        if not (0 < len(user_name) <= MAX_USERNAME_LENGTH):
            return request_failed(-1, "Bad length of [userName]", status_code = 400)

        user = User.objects.filter(userName=user_name).first()
        if not user:
            return request_failed(1, "User not found", status_code = 404)
        if user.faceEncoding == '':
            return request_failed(-3,"User haven't updated face information")
        body = json.loads(req.body.decode())
        video_data = body['videoData']
        video_binary = base64.b64decode(video_data.split(',')[1])
        video_np = np.frombuffer(video_binary, dtype=np.uint8)
        video_img = cv2.imdecode(video_np, cv2.IMREAD_COLOR)
        face_locations = face_recognition.face_locations(video_img)

        if len(face_locations) > 0:
            known_face_encodings = [np.fromstring(user.faceEncoding, dtype=float, sep=',')]

            for face_location in face_locations:
                face_encoding = face_recognition.face_encodings(video_img,[face_location],2)

                if len(face_encoding) > 0:
                    match_results = face_recognition.compare_faces(known_face_encodings, face_encoding[0], 0.4)

                    if True in match_results:
                        return_data = {'id':user.id,'token':user.token}
                        return request_success(return_data)
        
        else:
            return request_failed(-2, "No face in vedio", status_code=400)
        
        return request_failed(2, "Incorrect face", status_code=401)
    else:
        return BAD_METHOD

@CheckRequire
def faceupdate(req: HttpRequest, id: any):
    if req.method == "POST":
        id = require({"id": id}, "id", "int", err_msg = "Bad param [id]", err_code = -1)

        body = json.loads(req.body.decode("utf-8"))
        senderId = require(body, "senderId", "int", err_msg = "Bad param [senderId]", err_code = -2)
        senderToken = require(body, "senderToken", "string", err_msg = "Bad param [senderToken]", err_code = -2)

        user = User.objects.filter(id = id).first()
        if not user:
            return request_failed(1, "User not found", status_code = 404)

        if id != senderId:
            return request_failed(2, "SenderId should be euqal to id", status_code = 401)
        if user.token != senderToken:
            return request_failed(2, info="No permission", status_code=401)

        video_data = body['videoData']
        video_binary = base64.b64decode(video_data.split(',')[1])
        video_np = np.frombuffer(video_binary, dtype=np.uint8)
        video_img = cv2.imdecode(video_np, cv2.IMREAD_COLOR)
        face_locations = face_recognition.face_locations(video_img)

        if len(face_locations) > 0:
            max_face_size = 0
            max_face_index = -1
            for i, face_location in enumerate(face_locations):
                top, right, bottom, left = face_location
                face_size = (bottom - top) * (right - left)
                if face_size > max_face_size:
                    max_face_size = face_size
                    max_face_index = i
            
            if max_face_index >= 0:
                # 计算最大面部与用户已知的人脸的相似度
                max_face_location = face_locations[max_face_index]
                top, right, bottom, left = max_face_location
                max_face_encoding = face_recognition.face_encodings(video_img,[max_face_location],2)

                user_face_encoding_str = ','.join([str(val) for val in max_face_encoding[0]])
                user.faceEncoding = user_face_encoding_str
                user.lastupdatedtime = get_timestamp()
                user.save()
        
        else:
            return request_failed(-2, "No face in vedio", status_code=400)
        
        return request_success()
    else:
        return BAD_METHOD

@CheckRequire
def reset_by_email(req: HttpRequest):
    if req.method == "POST":
        body = json.loads(req.body.decode("utf-8"))

        user_name = require(body, "userName", "string", err_msg = "Bad param [userName]", err_code = -2)
        user = User.objects.filter(userName = user_name).first()
        if not user:
            return request_failed(1, "User not found", status_code = 404)
        if user.checkEmail == False:
            return request_failed(-2, "Email is not checked", status_code = 400)

        code = ''.join([random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for _ in range(6)])
        try:
            send_mail(
                '修改密码邮件',
                f'这是一封修改密码邮件，验证码为：{code}，验证码有效时间为5分钟',
                '[CENSORED]',
                [user.emailAddress]
            )
        except Exception as e:
            return request_failed(-2, f"Error sending email: {str(e)}", status_code = 400)

        user.code = code
        user.lastupdatedtime = get_timestamp()
        user.codeDeadline = (datetime.datetime.now() + datetime.timedelta(minutes = 5)).timestamp()
        user.save()

        return request_success()
    
    elif req.method == "PUT":
        body = json.loads(req.body.decode("utf-8"))

        user_name = require(body, "userName", "string", err_msg = "Bad param [userName]", err_code = -2)
        user = User.objects.filter(userName = user_name).first()
        if not user:
            return request_failed(1, "User not found", status_code = 404)
        if user.checkEmail == False:
            return request_failed(-2, "Email is not checked", status_code = 400)
        if user.code == '':
            return request_failed(-2, "No code has been sended in email", status_code = 400)
        
        code = require(body, "code", "string", err_msg = "Bad param [code]", err_code = -2)
        if user.code != code:
            return request_failed(-2, "Wrong code", status_code = 400)

        if get_timestamp() > user.codeDeadline:
            return request_failed(-2, "The verification code has expired", status_code = 400)

        password = require(body, "password", "string", err_msg = "Bad param [password]", err_code = -2)
        user.key = bcrypt.hashpw(password.encode(),bcrypt.gensalt(8)).decode()
        user.code = ''
        user.lastupdatedtime = get_timestamp()
        user.save()

        return request_success()

    else:
        return BAD_METHOD

@CheckRequire
def get_vip(req: HttpRequest):
    if req.method == "POST":
        body = json.loads(req.body.decode())
        authRes = userAuth(body)
        if authRes != None:
            return authRes
        sender = User.objects.get(id=body['senderId'])
        type = require(body, "type", "int", err_msg="bad param [type]")
        if type < 0 or type > 2:
            return request_failed(-2, "bad param [type]")
        if type == 0:
            if sender.score < 15:
                return request_failed(2, "You don't have enough score")
            sender.score -= 15
            if sender.vipExpireTime < get_timestamp():
                sender.vipExpireTime = get_timestamp()
            sender.vipExpireTime += 15
        elif type == 1:
            if sender.score < 30:
                return request_failed(2, "You don't have enough score")
            sender.score -= 30
            if sender.vipExpireTime < get_timestamp():
                sender.vipExpireTime = get_timestamp()
            sender.vipExpireTime += 30
        elif type == 2:
            if sender.score < 60:
                return request_failed(2, "You don't have enough score")
            sender.score -= 60
            if sender.vipExpireTime < get_timestamp():
                sender.vipExpireTime = get_timestamp()
            sender.vipExpireTime += 60
        sender.lastupdatedtime = get_timestamp()
        sender.save()
        return request_success()
    else:
        return BAD_METHOD
    
@CheckRequire
def mobile_scan(req: HttpRequest):
    if req.method == 'POST':
        body = json.loads(req.body.decode())
        authRes = userAuth(body)
        if authRes != None:
            return authRes
        code = require(body,'code',err_msg='bad param [code]')
        if len(code) != MOBILE_VERIFICATION_CODE_LENGTH:
            return request_failed(-2,'bad param [code]: wrong length')
        code = VerificationCode(code=code,senderId=body['senderId'],senderToken=body['senderToken'])
        code.save()
        return request_success()
    else:
        return BAD_METHOD

@CheckRequire
def check_scan_verification_code(req: HttpRequest):
    if req.method == 'GET':
        body = req.GET.dict()
        code = require(body,'code',err_msg='bad param [code]')
        if len(code) != MOBILE_VERIFICATION_CODE_LENGTH:
            return request_failed(-2,'bad param [code]: wrong length')
        Code = VerificationCode.objects.filter(code=code).first()
        if Code == None:
            return request_success({'scanned':False})
        else:
            id = Code.senderId
            token = Code.senderToken
            Code.delete()
            return request_success({'scanned':True,'id':id,'token':token})
    else:
        return BAD_METHOD