from django.http import HttpRequest, HttpResponse
from utils.utils_require import require,MAX_TOKEN_LENGTH,CheckRequire
from utils.utils_request import request_failed
from user.models import User

# Check whether senderId and senderToken match. Returns None if Everything is fine, else return a response.
@CheckRequire
def userAuth(body : dict, err_code=-2):
    senderId = require(body,'senderId','int',err_msg='Bad param [senderId]',err_code=err_code)
    senderUser = User.objects.filter(id=senderId).first()

    if senderUser == None:
        return request_failed(code=1,info='User Requesting Information Not Found',status_code=404)
        
    senderToken = require(body,'senderToken','string',err_msg='Bad param [senderToken]',err_code=err_code)
    if len(senderToken) != MAX_TOKEN_LENGTH:
        return request_failed(code=-2,info='Bad senderToken length',status_code=400)
    if senderUser.token != senderToken:
        return request_failed(code=2,info='Token Does not Match',status_code=401)
    return None    