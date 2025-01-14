from functools import wraps

from utils.utils_request import request_failed

from enum import Enum

MAX_TOKEN_LENGTH=64

MAX_PASSWORD_KEY_LENGTH=64

MAX_BCRYPTED_PASSWORD_KEY_LENGTH=60

MAX_USERNAME_LENGTH=20

MAX_TASKNAME_LENGTH=30

MAX_TASKDESCRIPTION_LENGTH=4096

MAX_TEMPLATENAME_LENGTH=30

MAX_USER_LIST_COUNT=128

MAX_TASK_LIST_COUNT=20

MAX_TEMPLATE_OBJECT_LIST_LENGTH=8

MAX_TEMPLATE_OBJECT_ROW_LENGTH=8

MAX_TAGS_COUNT=5

MAX_TAG_LENGTH=20

MAX_TEMPLATE_DESCRIPTION_LENGTH=4096

INVITATION_CODE_LENGTH=10

SUPPORTED_CONTENTS = {"text","image","textinput","singlechoice","multiplechoice","imageinput","video","audio","multimedia"}

SUPPORTED_CONTENTS_WITHOUT_INPUTFILE = {"textinput","singlechoice","multiplechoice"}

SUPPORTED_CONTENTS_WITHOUT_OUTPUTFILE = {"text","image","video","audio","multimedia"}

SUPPORTED_CONTENTS_WITH_DEFAULT = {"text"}

MAX_UPLOAD_ZIP_SIZE = 1073741824

MAX_TEXT_CONTENT_LENGTH = 32768

MAX_SYSTEM_MESSAGE = 10

MOBILE_VERIFICATION_CODE_LENGTH = 32

SUPPORTED_USER_SORTING = {"id","score","experience","labelCount"}

from functools import wraps

from utils.utils_request import request_failed
from functools import wraps

# A decorator function for processing `require` in view function.
def CheckRequire(check_fn):
    @wraps(check_fn)
    def decorated(*args, **kwargs):
        try:
            return check_fn(*args, **kwargs)
        except Exception as e:
            # Handle exception e
            error_code = -2 if len(e.args) < 2 else e.args[1]
            return request_failed(error_code, e.args[0], 400)  # Refer to below
    return decorated


# Here err_code == -2 denotes "Error in request body"
# And err_code == -1 denotes "Error in request URL parsing"
def require(body, key, type="string", err_msg=None, err_code=-2):
    
    if key not in body.keys():
        raise KeyError(err_msg if err_msg is not None 
                       else f"Invalid parameters. Expected `{key}`, but not found.", err_code)
    
    val = body[key]
    
    err_msg = f"Invalid parameters. Expected `{key}` to be `{type}` type."\
                if err_msg is None else err_msg
    
    if type == "int":
        try:
            val = int(val)
            return val
        except:
            raise KeyError(err_msg, err_code)
    
    elif type == "float":
        try:
            val = float(val)
            return val
        except:
            raise KeyError(err_msg, err_code)
    
    elif type == "string":
        try:
            val = str(val)
            return val
        except:
            raise KeyError(err_msg, err_code)
    
    elif type == "bool":
        try:
            val = bool(val)
            return val
        except:
            raise KeyError(err_msg, err_code)
    
    elif type == "list":
        try:
            assert isinstance(val, list)
            return val
        except:
            raise KeyError(err_msg, err_code)
    
    elif type == "dict":
        try:
            assert isinstance(val, dict)
            return val
        except:
            raise KeyError(err_msg, err_code)
    
    elif type == "set":
        try:
            assert isinstance(val, set)
            return val
        except:
            raise KeyError(err_msg, err_code)

    else:
        raise NotImplementedError(f"Type `{type}` not implemented.", err_code)