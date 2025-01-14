from django.apps import AppConfig
import random,string,hashlib
import utils.utils_require


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
