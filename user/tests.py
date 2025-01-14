import random
import string
from django.test import TestCase
from user.models import User, AdminMessage
import hashlib
import bcrypt
from utils.utils_time import get_timestamp
import datetime

from utils.utils_require import MAX_PASSWORD_KEY_LENGTH,MAX_TOKEN_LENGTH,MAX_USERNAME_LENGTH

# Create your tests here.

class UserTests(TestCase):
    # Initializer
    def setUp(self):
        User.objects.create(
            userName="alice",
            key=bcrypt.hashpw(hashlib.sha256(b'passwordofalice').hexdigest().encode(),bcrypt.gensalt(8)).decode(),
            token='akdmau1aBm5KpAVyvoDGOPjKD5K6xp1PAkbBQa8z0ITNP9X9lpHQA0BKyY3DqZ2Y',
            adminPrivilege=True,
            uploadPrivilege=True,
            labelPrivilege=True,
            experience=0,
            score=0,
            emailAddress = 'test@test.com',
            checkEmail = True
        )

        User.objects.create(
            userName="bob",
            key=bcrypt.hashpw(hashlib.sha256(b'passwordofbob').hexdigest().encode(),bcrypt.gensalt(8)).decode(),
            token='PEAioV9hMZ9Z8EpdygXSsO2InOBym9cWJJC2HxhPb3LVqNKZ08VBW6B0llUc76N5',
            adminPrivilege=False,
            uploadPrivilege=False,
            labelPrivilege=False,
            experience=0,
            score=0,
            eemailAddress = 'test@test.com',
            code = '123456'
        )

        User.objects.create(
            userName="carol",
            key=bcrypt.hashpw(hashlib.sha256(b'passwordofcarol').hexdigest().encode(),bcrypt.gensalt(8)).decode(),
            token='PEAioV9hMZ9Z8EpdygXSsO2InOBym9cWJJC2H12345LVqNKZ08VBW6B0llUc76N5',
            adminPrivilege=False,
            uploadPrivilege=True,
            labelPrivilege=False,
            experience=0,
            score=0,
            credit=100,
            emailAddress = 'test@test.com',
            checkEmail = True,
            code = '123456',
            codeDeadline = get_timestamp()
        )

        AdminMessage.objects.create(
            targetId = User.objects.filter(userName = "bob").first().id,
            type = "uploadPrivilege",
            sender = User.objects.filter(userName = "bob").first()
        )

        AdminMessage.objects.create(
            targetId = User.objects.filter(userName = "carol").first().id,
            type = "uploadPrivilege",
            sender = User.objects.filter(userName = "carol").first()
        )

        AdminMessage.objects.create(
            targetId = User.objects.filter(userName = "carol").first().id,
            type = "user",
            sender = User.objects.filter(userName = "bob").first()
        )

        AdminMessage.objects.create(
            targetId = User.objects.filter(userName = "bob").first().id,
            type = "wrong message",
            sender = User.objects.filter(userName = "bob").first()
        )

        AdminMessage.objects.create(
            targetId = User.objects.filter(userName = "carol").first().id,
            type = "mediationPrivilege",
            sender = User.objects.filter(userName = "carol").first()
        )

    # Utility functions
    def get_user_index(self, index, sender_id, sender_token):
        payload = {
            "senderId": sender_id,
            "senderToken": sender_token
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/user/{index}", data=payload, content_type="application/json")

    def get_user_login_name(self, user_name, key):
        payload = {
            "key": key
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/user/login/{user_name}", data=payload, content_type="application/json")
    
    def post_user_register(self, user_name, key, email_address):
        payload = {
            "userName": user_name,
            "key": key,
            "emailAddress": email_address
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.post("/user/register", data=payload, content_type="application/json")
    
    def put_user_reset(self, sender_id, sender_token, target_id, new_key):
        payload = {
            "senderId": sender_id,
            "senderToken": sender_token,
            "targetId": target_id,
            "newKey": new_key
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.put("/user/reset", data=payload, content_type="application/json")
    
    def put_user_modify(self, user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id):
        payload = {
            "userName": user_name,
            "adminPrivilege": admin_privilege,
            "uploadPrivilege": upload_privilege,
            "labelPrivilege": label_privilege,
            "mediationPrivilege": mediation_privilege,
            "senderToken": sender_token,
            "senderId": sender_id,
            "targetId": target_id
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.put("/user/modify", data=payload, content_type="application/json")

    def get_user_list(self, sender_id, sender_token, page_id, count, sort_by, sort_by_ascend):
        payload = {
            "senderId": sender_id,
            "senderToken": sender_token,
            "pageId": page_id,
            "count": count,
            "sortBy": sort_by,
            "sortByAscend": sort_by_ascend
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/user/list", data=payload, content_type="application/json")

    def post_user_privilege(self, senderId, senderToken, privilege):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
            "privilege": privilege
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        return self.client.post(f"/user/getprivilege", data=payload, content_type="application/json")

    def post_check_email(self, id, senderId, senderToken, code):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
            "code": code
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        return self.client.post(f"/user/email/{id}", data=payload, content_type="application/json")

    def post_email_reset(self, userName):
        payload = {
            "userName": userName,
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        return self.client.post(f"/user/email/reset", data=payload, content_type="application/json")

    def put_email_reset(self, userName, code, password):
        payload = {
            "userName": userName,
            "code": code,
            "password": password,
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        return self.client.put(f"/user/email/reset", data=payload, content_type="application/json")

    def put_check_request(self, id, senderId, senderToken, accepted):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
            "accepted": accepted,
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        return self.client.put(f"/user/requests/{id}", data=payload, content_type="application/json")
    
    # /user/login/{userName}
    # GET
    # + correct respond
    def test_login(self):
        res = self.get_user_login_name(user_name='alice',key=(hashlib.sha256(b'passwordofalice').hexdigest()))
        self.assertJSONEqual(res.content,{'id':User.objects.get(userName='alice').id,'token':'akdmau1aBm5KpAVyvoDGOPjKD5K6xp1PAkbBQa8z0ITNP9X9lpHQA0BKyY3DqZ2Y','code':0,'info':'Succeed'})
        self.assertEqual(res.status_code,200)

    # + login with no such user
    def test_login_wrong_user(self):
        random.seed(1)
        for _ in range(10):
            userName="".join([random.choice(string.printable) for _ in range(random.randint(2,21))])
            while userName=='alice' or userName=='bob':
                userName="".join([random.choice(string.printable) for _ in range(random.randint(2,21))])
            res = self.get_user_login_name(user_name=userName,key="".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)))
            self.assertEqual(res.status_code,404)
            # self.assertEqual(res.json()['code'],1)
    
    # + login with too long username
    def test_login_long_user(self):
        userName="".join(random.choices(string.printable,k=1025))
        key="".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH))
        res = self.get_user_login_name(userName,key)
        self.assertNotEqual(res.status_code,200)
    
    # + login with chinese username
    def test_login_chinese_user(self):
        userName="".join(random.choices("01中文测试",k=5))
        key="".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH))
        res = self.get_user_login_name(userName,key)
        self.assertNotEqual(res.status_code,200)
    
    # + login with special username
    def test_login_special_user(self):
        res = self.get_user_login_name('alice;DROP TABLE user_user;',"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)))
        self.assertEqual(True,User.objects.filter(userName='alice')!=None)
        self.assertNotEqual(res.status_code,200)

    # + login with wrong key
    def test_login_wrong_key(self):
        res = self.get_user_login_name(user_name='alice',key=hashlib.sha256(b'wrongpassword').hexdigest())
        self.assertEqual(res.status_code,401)
        self.assertEqual(res.json()['code'],2)

        res = self.get_user_login_name(user_name='alice',key=hashlib.sha256(b'passwordofbob').hexdigest())
        self.assertEqual(res.status_code,401)
        self.assertEqual(res.json()['code'],2)
    
    # + login without key
    def test_login_without_key(self):
        res = self.client.get('/user/login/alice')
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-1)
    
    # + login with invalid key characters
    def test_login_with_invalid_key_char(self):
        res = self.get_user_login_name('alice','中文测试')
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)

    # + login with special key
    def test_login_with_special_key(self):
        res = self.get_user_login_name('alice',hashlib.sha256(b'passwordofalice').hexdigest()+';DROP TABLE user_user')
        self.assertNotEqual(res.status_code,200)
        self.assertTrue(User.objects.filter(userName='alice').exists())

    # + login with too long key
    def test_login_with_long_key(self):
        res = self.get_user_login_name('alice',"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH+5)))
        self.assertNotEqual(res.status_code,200)
        self.assertNotEqual(res.status_code,401)

    # + unsupported method
    def test_login_with_wrong_method(self):
        res = self.client.post('/user/login/alice',data={'key':hashlib.sha256(b'passwordofalice').hexdigest()},content_type="application/json")
        self.assertEqual(res.json()['code'],-3)
        self.assertEqual(res.status_code,405)

        res = self.client.put('/user/login/alice',data={'key':hashlib.sha256(b'passwordofalice').hexdigest()},content_type="application/json")
        self.assertEqual(res.json()['code'],-3)
        self.assertEqual(res.status_code,405)

    # /user/register
    # POST
    def test_add_user(self):
        random.seed(1)
        for _ in range(1):
            key = ''.join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH))
            user_name = ''.join([random.choice("zxcvbnm12345678") for _ in range(7)])
            email_address = 'test@test.com'

            res = self.post_user_register(user_name, key, email_address)
            self.assertJSONEqual(res.content, {"code": 0, "info": "Succeed"})
            self.assertTrue(User.objects.filter(userName=user_name).exists())
    
    # + same userName
    def test_add_user_twice(self):
        random.seed(2)
        for _ in range(1):
            user_name = ''.join([random.choice("zxcvbnm12345678") for _ in range(7)])
            key1 = ''.join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH))
            key2 = ''.join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH))
            email_address = 'test@test.com'
            
            res = self.post_user_register(user_name, key = key1, email_address = email_address)
            self.assertJSONEqual(res.content, {"code": 0, "info": "Succeed"})
            self.assertTrue(User.objects.filter(userName=user_name).exists())

            res = self.post_user_register(user_name, key = key2, email_address = email_address)
            self.assertNotEqual(res.json()['code'], 0)
            self.assertNotEqual(res.status_code, 200)
            self.assertFalse(User.objects.filter(key=key2).exists())
    
    # + key missing
    def test_add_user_without_user_name(self):
        random.seed(3)
        for _ in range(50):
            key = ''.join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH))
            user_name = ''.join([random.choice("zxcvbnm12345678") for _ in range(7)])
            email_address = 'test@test.com'

            res = self.post_user_register(None, key, email_address)
            self.assertEqual(res.json()['code'], -2)
            self.assertEqual(res.status_code, 400)
            self.assertFalse(User.objects.filter(key=key).exists())

            res = self.post_user_register(user_name, None, email_address)
            self.assertEqual(res.json()['code'], -2)
            self.assertEqual(res.status_code, 400)
            self.assertFalse(User.objects.filter(userName=user_name).exists())

            res = self.post_user_register(user_name, key, None)
            self.assertEqual(res.json()['code'], -2)
            self.assertEqual(res.status_code, 400)

    # + wrong email format
    def test_add_email_format_incorrect(self):
        key = ''.join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH))
        user_name = ''.join([random.choice("zxcvbnm12345678") for _ in range(21)])
        email_address1 = '1310479068qq.com'
        email_address2 = '1310479068@qq'
        email_address3 = '1310479068$qq.com'

        res = self.post_user_register(user_name, key, email_address1)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.status_code, 400)

        res = self.post_user_register(user_name, key, email_address2)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.status_code, 400)

        res = self.post_user_register(user_name, key, email_address3)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.status_code, 400)

    # + userName key length incorrect
    def test_add_user_name_length_incorrect(self):
        random.seed(4)
        for _ in range(50):
            key = ''.join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH))
            user_name = ''.join([random.choice("zxcvbnm12345678") for _ in range(21)])
            email_address = 'test@test.com'

            res = self.post_user_register(user_name, key, email_address)
            self.assertEqual(res.json()['code'], -2)
            self.assertEqual(res.status_code, 400)
            self.assertFalse(User.objects.filter(userName=user_name).exists())

    # + key length incorrect
    def test_add_user_key_length_incorrect(self):
        random.seed(5)
        for _ in range(50):
            key1 = ''.join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH-2))
            key2 = ''.join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH+2))
            user_name = ''.join([random.choice("zxcvbnm12345678") for _ in range(7)])
            email_address = 'test@test.com'

            res = self.post_user_register(user_name, key1, email_address)
            self.assertEqual(res.json()['code'], -2)
            self.assertEqual(res.status_code, 400)
            self.assertFalse(User.objects.filter(userName=user_name).exists())

            res = self.post_user_register(user_name, key2, email_address)
            self.assertEqual(res.json()['code'], -2)
            self.assertEqual(res.status_code, 400)
            self.assertFalse(User.objects.filter(userName=user_name).exists())

    # + userName with invalid chat
    def test_add_user_name_invalid_char(self):
        random.seed(6)
        for _ in range(50):
            key = ''.join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH))
            user_name = ''.join([random.choice("`~!@#$%^&*()+=-_[]\{\}\\|:;'\",<.>?/") for _ in range(7)])
            email_address = 'test@test.com'

            res = self.post_user_register(user_name, key, email_address)
            self.assertNotEqual(res.json()['code'], 0)
            self.assertNotEqual(res.status_code, 200)
            self.assertFalse(User.objects.filter(userName=user_name).exists())

    # + unsupported method
    def test_add_user_unsupported(self):
        res = self.client.put("/user/register")
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.status_code, 405)

        res = self.client.get("/user/register")
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.status_code, 405)
    
    # /user/{id}
    # GET

    # + normal case to self
    def test_get_info(self):
        user = User.objects.filter(userName="alice").first()
        index = user.id
        sender_id = user.id
        sender_token = user.token

        res = self.get_user_index(index, sender_id, sender_token)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.status_code, 200)

    # + normal case to others
    def test_get_info_other(self):
        user1 = User.objects.filter(userName="alice").first()
        user2 = User.objects.filter(userName="bob").first()
        index = user1.id
        sender_id = user2.id
        sender_token = user2.token

        res = self.get_user_index(index, sender_id, sender_token)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.status_code, 200)

    # + wrong sender token
    def test_get_info_wrong_sender(self):
        user1 = User.objects.filter(userName="alice").first()
        user2 = User.objects.filter(userName="bob").first()
        index = user1.id
        sender_id = user1.id
        sender_token = user2.token

        res = self.get_user_index(index, sender_id, sender_token)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.status_code, 401)

    # + incorrect type of id
    def test_get_info_incorrect_type_of_id(self):
        user = User.objects.filter(userName="alice").first()
        index = "abcbac"
        sender_id = user.id
        sender_token = user.token

        res = self.get_user_index(index, sender_id, sender_token)
        self.assertEqual(res.json()['code'], -1)
        self.assertEqual(res.status_code, 400)

    # + incorrect type of senderId & senderToken
    def test_get_info_incorrect_type_of_query(self):
        user = User.objects.filter(userName="alice").first()
        index = user.id
        sender_id = "abc"
        sender_token = user.token

        res = self.get_user_index(index, sender_id, sender_token)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.status_code, 400)

        index = user.id
        sender_id = user.id
        sender_token = "cba"

        res = self.get_user_index(index, sender_id, sender_token)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(res.status_code, 400)

    # + 404 not found for index
    def test_get_info_404_not_found_index(self):
        user = User.objects.filter(userName="alice").first()
        index = User.objects.count() + 10
        sender_id = user.id
        sender_token = user.token

        res = self.get_user_index(index, sender_id, sender_token)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.status_code, 404)

    # + 404 not found for sender
    def test_get_info_404_not_found_sender(self):
        user = User.objects.filter(userName="alice").first()
        index = user.id
        sender_id = User.objects.count() + 10
        sender_token = user.token

        res = self.get_user_index(index, sender_id, sender_token)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.status_code, 404)

    # + unsupported method
    def test_get_info_unsupported(self):
        index = 1

        res = self.client.put(f"/user/{index}")
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.status_code, 405)

        res = self.client.post(f"/user/{index}")
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(res.status_code, 405)

    # /user/reset
    # PUT
    
    # + normal operation with different password
    def test_password_reset_different(self):
        alice_id=User.objects.filter(userName='alice').first().id
        bob_id=User.objects.filter(userName='bob').first().id
        # Admin modifying self
        new_key=hashlib.sha256(b'newpassswordforalice').hexdigest()
        alice_token=User.objects.filter(userName='alice').first().token
        res = self.put_user_reset(alice_id,alice_token,alice_id,new_key)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.json()['code'],0)
        self.assertTrue(User.objects.filter(userName='alice').exists())
        # self.assertEqual(User.objects.filter(userName='alice').first().key,new_key)
        self.assertTrue(bcrypt.checkpw(new_key.encode(),User.objects.filter(userName='alice').first().key.encode()))
        self.assertNotEqual(User.objects.filter(userName='alice').first().token,alice_token)
        alice_token=User.objects.filter(userName='alice').first().token
        # Admin modifying others
        new_key=hashlib.sha256(b'newpasswordforbob').hexdigest()
        bob_token=User.objects.filter(userName='bob').first().token
        res = self.put_user_reset(alice_id,alice_token,bob_id,new_key)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.json()['code'],0)
        self.assertTrue(User.objects.filter(userName='bob').exists())
        # self.assertEqual(User.objects.filter(userName='bob').first().key,new_key)
        self.assertTrue(bcrypt.checkpw(new_key.encode(),User.objects.filter(userName='bob').first().key.encode()))
        self.assertNotEqual(User.objects.filter(userName='bob').first().token,bob_token)
        # normal modifying self
        new_key=hashlib.sha256(b'newpasswordforbob2').hexdigest()
        bob_token=User.objects.filter(userName='bob').first().token
        res = self.put_user_reset(bob_id,bob_token,bob_id,new_key)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.json()['code'],0)
        self.assertTrue(User.objects.filter(userName='bob').exists())
        # self.assertEqual(User.objects.filter(userName='bob').first().key,new_key)
        self.assertTrue(bcrypt.checkpw(new_key.encode(),User.objects.filter(userName='bob').first().key.encode()))
        self.assertNotEqual(User.objects.filter(userName='bob').first().token,bob_token)

    # + normal operation with same password
    def test_password_reset_same(self):
        alice_id=User.objects.filter(userName='alice').first().id
        bob_id=User.objects.filter(userName='bob').first().id
        # Admin modify self
        new_key=hashlib.sha256(b'passwordofalice').hexdigest()
        alice_token=User.objects.filter(userName='alice').first().token
        res = self.put_user_reset(alice_id,alice_token,alice_id,new_key)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.json()['code'],0)
        self.assertTrue(User.objects.filter(userName='alice').exists())
        # self.assertEqual(User.objects.filter(userName='alice').first().key,new_key)
        self.assertTrue(bcrypt.checkpw(new_key.encode(),User.objects.filter(userName='alice').first().key.encode()))
        self.assertNotEqual(User.objects.filter(userName='alice').first().token,alice_token)
        alice_token=User.objects.filter(userName='alice').first().token
        # normal modify self
        new_key=hashlib.sha256(b'passwordofbob').hexdigest()
        bob_token=User.objects.filter(userName='bob').first().token
        res = self.put_user_reset(bob_id,bob_token,bob_id,new_key)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.json()['code'],0)
        self.assertTrue(User.objects.filter(userName='bob').exists())
        # self.assertEqual(User.objects.filter(userName='bob').first().key,new_key)
        self.assertTrue(bcrypt.checkpw(new_key.encode(),User.objects.filter(userName='bob').first().key.encode()))
        self.assertNotEqual(User.objects.filter(userName='bob').first().token,bob_token)
        # Admin modify others
        alice_token=User.objects.filter(userName='alice').first().token
        res = self.put_user_reset(alice_id,alice_token,bob_id,new_key)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.json()['code'],0)
        self.assertTrue(User.objects.filter(userName='bob').exists())
        # self.assertEqual(User.objects.filter(userName='bob').first().key,new_key)
        self.assertTrue(bcrypt.checkpw(new_key.encode(),User.objects.filter(userName='bob').first().key.encode()))
        self.assertNotEqual(User.objects.filter(userName='bob').first().token,bob_token)
    
    # + wrong token modification with right length
    def test_password_reset_wrong_token(self):
        alice_id=User.objects.filter(userName='alice').first().id
        bob_id=User.objects.filter(userName='bob').first().id
        # Admin modifying self
        old_key=User.objects.filter(userName='alice').first().key
        new_key=hashlib.sha256(b'newpassswordforalice').hexdigest()
        old_token=User.objects.filter(userName='alice').first().token
        alice_token="".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH))
        res = self.put_user_reset(alice_id,alice_token,alice_id,new_key)
        self.assertEqual(res.status_code,401)
        self.assertEqual(res.json()['code'],2)
        self.assertTrue(User.objects.filter(userName='alice').exists())
        self.assertEqual(User.objects.filter(userName='alice').first().key,old_key)
        self.assertEqual(User.objects.filter(userName='alice').first().token,old_token)
        # Admin modifying others
        old_key=User.objects.filter(userName='bob').first().key
        new_key=hashlib.sha256(b'newpasswordforbob').hexdigest()
        bob_token=User.objects.filter(userName='bob').first().token
        res = self.put_user_reset(alice_id,alice_token,bob_id,new_key)
        self.assertEqual(res.status_code,401)
        self.assertEqual(res.json()['code'],2)
        self.assertTrue(User.objects.filter(userName='bob').exists())
        self.assertEqual(User.objects.filter(userName='bob').first().key,old_key)
        self.assertEqual(User.objects.filter(userName='bob').first().token,bob_token)
        # normal modifying self
        old_key=User.objects.filter(userName='bob').first().key
        new_key=hashlib.sha256(b'newpasswordforbob2').hexdigest()
        old_token=User.objects.filter(userName='bob').first().token
        res = self.put_user_reset(bob_id,"".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH)),bob_id,new_key)
        self.assertEqual(res.status_code,401)
        self.assertEqual(res.json()['code'],2)
        self.assertTrue(User.objects.filter(userName='bob').exists())
        self.assertEqual(User.objects.filter(userName='bob').first().key,old_key)
        self.assertEqual(User.objects.filter(userName='bob').first().token,bob_token)
    
    # + wrong token modification with short token length
    def test_password_reset_wrong_short_token(self):
        alice_id=User.objects.filter(userName='alice').first().id
        bob_id=User.objects.filter(userName='bob').first().id
        # Admin modifying self
        old_key=User.objects.filter(userName='alice').first().key
        new_key=hashlib.sha256(b'newpassswordforalice').hexdigest()
        old_token=User.objects.filter(userName='alice').first().token
        alice_token="".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH-2))
        res = self.put_user_reset(alice_id,alice_token,alice_id,new_key)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertTrue(User.objects.filter(userName='alice').exists())
        self.assertEqual(User.objects.filter(userName='alice').first().key,old_key)
        self.assertEqual(User.objects.filter(userName='alice').first().token,old_token)
        # Admin modifying others
        old_key=User.objects.filter(userName='bob').first().key
        new_key=hashlib.sha256(b'newpasswordforbob').hexdigest()
        bob_token=User.objects.filter(userName='bob').first().token
        res = self.put_user_reset(alice_id,alice_token,bob_id,new_key)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertTrue(User.objects.filter(userName='bob').exists())
        self.assertEqual(User.objects.filter(userName='bob').first().key,old_key)
        self.assertEqual(User.objects.filter(userName='bob').first().token,bob_token)
        # normal modifying self
        old_key=User.objects.filter(userName='bob').first().key
        new_key=hashlib.sha256(b'newpasswordforbob2').hexdigest()
        old_token=User.objects.filter(userName='bob').first().token
        res = self.put_user_reset(bob_id,"".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH-2)),bob_id,new_key)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertTrue(User.objects.filter(userName='bob').exists())
        self.assertEqual(User.objects.filter(userName='bob').first().key,old_key)
        self.assertEqual(User.objects.filter(userName='bob').first().token,bob_token)

    # + wrong token modification with long token length
    def test_password_reset_wrong_long_token(self):
        alice_id=User.objects.filter(userName='alice').first().id
        bob_id=User.objects.filter(userName='bob').first().id
        # Admin modifying self
        old_key=User.objects.filter(userName='alice').first().key
        new_key=hashlib.sha256(b'newpassswordforalice').hexdigest()
        old_token=User.objects.filter(userName='alice').first().token
        alice_token="".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH*32))
        res = self.put_user_reset(alice_id,alice_token,alice_id,new_key)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertTrue(User.objects.filter(userName='alice').exists())
        self.assertEqual(User.objects.filter(userName='alice').first().key,old_key)
        self.assertEqual(User.objects.filter(userName='alice').first().token,old_token)
        # Admin modifying others
        old_key=User.objects.filter(userName='bob').first().key
        new_key=hashlib.sha256(b'newpasswordforbob').hexdigest()
        bob_token=User.objects.filter(userName='bob').first().token
        res = self.put_user_reset(alice_id,alice_token,bob_id,new_key)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertTrue(User.objects.filter(userName='bob').exists())
        self.assertEqual(User.objects.filter(userName='bob').first().key,old_key)
        self.assertEqual(User.objects.filter(userName='bob').first().token,bob_token)
        # normal modifying self
        old_key=User.objects.filter(userName='bob').first().key
        new_key=hashlib.sha256(b'newpasswordforbob2').hexdigest()
        old_token=User.objects.filter(userName='bob').first().token
        res = self.put_user_reset(bob_id,"".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH*32)),bob_id,new_key)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertTrue(User.objects.filter(userName='bob').exists())
        self.assertEqual(User.objects.filter(userName='bob').first().key,old_key)
        self.assertEqual(User.objects.filter(userName='bob').first().token,bob_token)
    
    # + sender not found
    def test_password_reset_sender_not_found(self):
        for _ in range(10):
            senderId=random.randint(1,65536)
            while User.objects.filter(id=senderId).exists():
                senderId=random.randint()
            res=self.put_user_reset(senderId,"".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH)),1,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)))
            self.assertEqual(res.status_code,404)
            self.assertEqual(res.json()['code'],1)
            self.assertFalse(User.objects.filter(id=senderId).exists())

    # + sender id is not int
    def test_password_reset_sender_not_int(self):
        senderId='alice'
        oldKey=User.objects.get(userName='alice').key
        res=self.put_user_reset(senderId,User.objects.get(userName='alice').token,1,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)))
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertEqual(oldKey,User.objects.get(userName='alice').key)
        for _ in range(50):
            senderId="".join(random.choices(string.printable,k=random.randint(2,MAX_USERNAME_LENGTH)))
            try:
                intOfSenderId=int(senderId)
            except:
                res=self.put_user_reset(senderId,"".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH)),1,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)))
                self.assertEqual(res.status_code,400)
                self.assertEqual(res.json()['code'],-2)
        senderId='alice;DROP TABLE user_user;'
        res=self.put_user_reset(senderId,User.objects.get(userName='alice').token,1,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)))
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertTrue(User.objects.filter(userName='alice').exists())
        self.assertEqual(oldKey,User.objects.get(userName='alice').key)

    # + sender token is not string
    def test_password_reset_sender_token_not_string(self):
        aliceId=User.objects.get(userName='alice').id
        oldKey=User.objects.get(userName='alice').key
        res=self.put_user_reset(aliceId,123,1,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)))
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertEqual(oldKey,User.objects.get(userName='alice').key)
    
    # + special sender token
    def test_password_reset_special_sender_token(self):
        aliceId=User.objects.get(userName='alice').id
        oldKey=User.objects.get(userName='alice').key
        res=self.put_user_reset(aliceId,'DROP DATABASE user_user',aliceId,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)))
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertEqual(oldKey,User.objects.get(userName='alice').key)
        res=self.put_user_reset(aliceId,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa;DROP DATABASE user_user;',aliceId,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)),)
        self.assertEqual(res.status_code,401)
        self.assertEqual(res.json()['code'],2)
        self.assertEqual(oldKey,User.objects.get(userName='alice').key)
    
    # + wrong sender token length
    def test_password_reset_wrong_token_length(self):
        aliceId=User.objects.get(userName='alice').id
        oldKey=User.objects.get(userName='alice').key
        res=self.put_user_reset(aliceId,''.join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH-2)),aliceId,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)))
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertEqual(oldKey,User.objects.get(userName='alice').key)
        res=self.put_user_reset(aliceId,''.join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH+2)),aliceId,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)),)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertEqual(oldKey,User.objects.get(userName='alice').key)
    
    # + target not found
    def test_password_reset_target_not_found(self):
        aliceId=User.objects.get(userName='alice').id
        aliceToken=User.objects.get(userName='alice').token
        targetId=random.randint(1,65536)
        while User.objects.filter(id=targetId).exists():
            targetId=random.randint()
        res=self.put_user_reset(aliceId,aliceToken,targetId,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)))
        self.assertEqual(res.status_code,404)
        self.assertEqual(res.json()['code'],1)
    
    # + target id not int
    def test_password_reset_target_id_not_int(self):
        aliceId=User.objects.get(userName='alice').id
        aliceToken=User.objects.get(userName='alice').token
        targetId='bob'
        res=self.put_user_reset(aliceId,aliceToken,targetId,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)))
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        targetId='bob;DROP DATABASE user_user;'
        res=self.put_user_reset(aliceId,aliceToken,targetId,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH)))
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
    # + target key length incorrect
    def test_password_reset_target_key_length_incorrect(self):
        aliceId=User.objects.get(userName='alice').id
        aliceToken=User.objects.get(userName='alice').token
        targetId=aliceId
        res=self.put_user_reset(aliceId,aliceToken,targetId,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH-2)))
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        res=self.put_user_reset(aliceId,aliceToken,targetId,"".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH+2)))
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
    # + special target key
    def test_password_reset_special_target_key(self):
        aliceId=User.objects.get(userName='alice').id
        aliceToken=User.objects.get(userName='alice').token
        targetId=aliceId
        res=self.put_user_reset(aliceId,aliceToken,targetId,'a;DROP TABLE user_user')
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
    # + missing params
    def test_password_reset_missing_params(self):
        aliceId=User.objects.get(userName='alice').id
        aliceToken=User.objects.get(userName='alice').token
        targetId=aliceId
        key="".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH))
        res=self.put_user_reset(None,None,None,None)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        res=self.put_user_reset(None,aliceToken,targetId,key)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        res=self.put_user_reset(aliceId,None,targetId,key)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        res=self.put_user_reset(aliceId,aliceToken,None,key)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        res=self.put_user_reset(aliceId,aliceToken,targetId,None)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
    # + wrong method
    def test_password_reset_wrong_method(self):
        aliceId=User.objects.get(userName='alice').id
        aliceToken=User.objects.get(userName='alice').token
        targetId=aliceId
        key="".join(random.choices(string.hexdigits,k=MAX_PASSWORD_KEY_LENGTH))
        payload={
            'senderId':aliceId,
            'senderToken':aliceToken,
            'targetId':targetId,
            'newKey':key
        }
        res=self.client.get('/user/reset',data=payload)
        self.assertEqual(res.status_code,405)
        self.assertEqual(res.json()['code'],-3)
        res=self.client.post('/user/reset',data=payload)
        self.assertEqual(res.status_code,405)
        self.assertEqual(res.json()['code'],-3)

    # /user/modify
    # PUT
    # + normal case for username
    def test_modify_userName_information(self):
        random.seed(7)
        userId = User.objects.get(userName = "bob").id
        for i in range(50):
            user = User.objects.get(id=userId)
            user_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
            admin_privilege = user.adminPrivilege
            upload_privilege = user.uploadPrivilege
            label_privilege = user.labelPrivilege
            mediation_privilege = user.mediationPrivilege
            sender_token = user.token
            sender_id = userId
            target_id = userId
            last_name = user.userName

            res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()['code'], 0)
            self.assertTrue(User.objects.filter(userName = user_name).exists())
            self.assertFalse(User.objects.filter(userName = last_name).exists())
            
    # + normal case for adminPrivilege
    def test_modify_adminPrivilege_information(self):
        for _ in range(2):
            user = User.objects.filter(userName = "alice").first()
            user2 = User.objects.filter(userName = "bob").first()
            user_name = user2.userName

            if user2.adminPrivilege: 
                admin_privilege = False
            else:
                admin_privilege = True

            upload_privilege = user2.uploadPrivilege
            label_privilege = user2.labelPrivilege
            mediation_privilege = user2.mediationPrivilege
            sender_token = user.token
            sender_id = User.objects.get(userName='alice').id
            target_id = User.objects.get(userName='bob').id

            res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()['code'], 0)
            self.assertTrue(User.objects.filter(userName = "bob").first().adminPrivilege == admin_privilege)

    # + normal case for uploadPrivilege
    def test_modify_uploadPrivilege_information(self):
        for _ in range(2):
            user = User.objects.filter(userName = "alice").first()
            user2 = User.objects.filter(userName = "bob").first()
            user_name = user2.userName
            admin_privilege = user2.adminPrivilege

            if user2.uploadPrivilege: 
                upload_privilege = False
            else:
                upload_privilege = True

            label_privilege = user2.labelPrivilege
            mediation_privilege = user2.mediationPrivilege
            sender_token = user.token
            sender_id = User.objects.get(userName='alice').id
            target_id = User.objects.get(userName='bob').id

            res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()['code'], 0)
            self.assertTrue(User.objects.filter(userName = "bob").first().uploadPrivilege == upload_privilege)

    # + normal case for labelPrivilege
    def test_modify_labelPrivilege_information(self):
        for _ in range(2):
            user = User.objects.filter(userName = "alice").first()
            user2 = User.objects.filter(userName = "bob").first()
            user_name = user2.userName
            admin_privilege = user2.adminPrivilege
            upload_privilege = user2.uploadPrivilege

            if user2.labelPrivilege: 
                label_privilege = False
            else:
                label_privilege = True
                
            mediation_privilege = user2.mediationPrivilege

            sender_token = user.token
            sender_id = User.objects.get(userName='alice').id
            target_id = User.objects.get(userName='bob').id

            res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()['code'], 0)
            self.assertTrue(User.objects.filter(userName = "bob").first().labelPrivilege == label_privilege)

    # + normal case for mediationPrivilege
    def test_modify_mediationPrivilege_information(self):
        for _ in range(2):
            user = User.objects.filter(userName = "alice").first()
            user2 = User.objects.filter(userName = "bob").first()
            user_name = user2.userName
            admin_privilege = user2.adminPrivilege
            upload_privilege = user2.uploadPrivilege
            label_privilege = user2.labelPrivilege

            if user2.mediationPrivilege: 
                mediation_privilege = False
            else:
                mediation_privilege = True
                
            sender_token = user.token
            sender_id = User.objects.get(userName='alice').id
            target_id = User.objects.get(userName='bob').id

            res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()['code'], 0)
            self.assertTrue(User.objects.filter(userName = "bob").first().mediationPrivilege == mediation_privilege)
        
    # + normal case for Admin
    def test_modify_Admin(self):
        user = User.objects.filter(userName = "alice").first()
        user2 = User.objects.filter(userName = "bob").first()
        user_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        admin_privilege = user2.adminPrivilege
        upload_privilege = user2.uploadPrivilege
        label_privilege = user2.labelPrivilege
        mediation_privilege = user2.mediationPrivilege
        sender_token = user.token
        sender_id = User.objects.get(userName='alice').id
        target_id = User.objects.get(userName='bob').id
        last_name = user2.userName

        res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertTrue(User.objects.filter(userName = user_name).exists())
        self.assertFalse(User.objects.filter(userName = last_name).exists())

    # + token does not match user
    def test_modify_invalid_token(self):
        for i in range(50):
            user = User.objects.filter(userName = "bob").first()
            user_name = user.userName
            admin_privilege = user.adminPrivilege
            upload_privilege = user.uploadPrivilege
            label_privilege = user.labelPrivilege
            mediation_privilege = user.mediationPrivilege
            sender_token = ''.join([random.choice("qwertyuiop12345678") for _ in range(64)])
            sender_id = User.objects.get(userName='alice').id
            target_id = User.objects.get(userName='alice').id

            res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
            self.assertEqual(res.status_code, 401)
            self.assertEqual(res.json()['code'], 2)

    # + changeId not equal TargetId
    def test_modify_invalid_user(self):
        user = User.objects.filter(userName = "alice").first()
        user2 = User.objects.filter(userName = "bob").first()
        user_name = user.userName
        admin_privilege = user.adminPrivilege
        upload_privilege = user.uploadPrivilege
        label_privilege = user.labelPrivilege
        mediation_privilege = user.mediationPrivilege
        sender_token = user2.token
        sender_id = User.objects.get(userName='bob').id
        target_id = User.objects.get(userName='alice').id

        res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + invalid char in useName
    def test_modify_userName_invalid_char(self):
        random.seed(8)
        for i in range(50):
            user = User.objects.filter(userName = "bob").first()
            user_name = ''.join([random.choice("/*-+@#$%^") for _ in range(7)])
            admin_privilege = user.adminPrivilege
            upload_privilege = user.uploadPrivilege
            label_privilege = user.labelPrivilege
            mediation_privilege = user.mediationPrivilege
            sender_token = user.token
            sender_id = User.objects.get(userName='bob').id
            target_id = User.objects.get(userName='bob').id

            res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
            self.assertEqual(res.status_code, 400)
            self.assertEqual(res.json()['code'], -2)

    # + bad length of username
    def test_modify_userName_bad_length(self):
        random.seed(8)
        for i in range(50):
            user = User.objects.filter(userName = "bob").first()
            user_name = ''.join([random.choice("abcdefghijklmn0123456") for _ in range(21)])
            admin_privilege = user.adminPrivilege
            upload_privilege = user.uploadPrivilege
            label_privilege = user.labelPrivilege
            mediation_privilege = user.mediationPrivilege
            sender_token = user.token
            sender_id = User.objects.get(userName='bob').id
            target_id = User.objects.get(userName='bob').id

            res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
            self.assertEqual(res.status_code, 400)
            self.assertEqual(res.json()['code'], -1)

    # + bad length of token
    def test_modify_token_bad_length(self):
        random.seed(9)
        for i in range(50):
            user = User.objects.filter(userName = "bob").first()
            user_name = user.userName
            admin_privilege = user.adminPrivilege
            upload_privilege = user.uploadPrivilege
            label_privilege = user.labelPrivilege
            mediation_privilege = user.mediationPrivilege
            sender_token = ''.join([random.choice("abcdefghijklmn0123456") for _ in range(70)])
            sender_id = User.objects.get(userName='alice').id
            target_id = User.objects.get(userName='alice').id

            res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
            self.assertEqual(res.status_code, 400)
            self.assertEqual(res.json()['code'], -1)
            
    # + no permission of adminPrivilege
    def test_modify_adminPrivilege_no_permission(self):
        user = User.objects.filter(userName = "bob").first()
        user_name = user.userName

        if user.adminPrivilege: 
            admin_privilege = False
        else:
            admin_privilege = True

        upload_privilege = user.uploadPrivilege
        label_privilege = user.labelPrivilege
        mediation_privilege = user.mediationPrivilege
        sender_token = user.token
        sender_id = User.objects.get(userName='bob').id
        target_id = User.objects.get(userName='bob').id

        res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)
            
    # + no permission of uploadPrivilege
    def test_modify_uploadPrivilege_no_permission(self):
        user = User.objects.filter(userName = "bob").first()
        user_name = user.userName
        admin_privilege = user.adminPrivilege

        if user.uploadPrivilege: 
            upload_privilege = False
        else:
            upload_privilege = True

        label_privilege = user.labelPrivilege
        mediation_privilege = user.mediationPrivilege
        sender_token = user.token
        sender_id = User.objects.get(userName='bob').id
        target_id = User.objects.get(userName='bob').id

        res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)
            
    # + no permission of labelPrivilege
    def test_modify_labelPrivilege_no_permission(self):
        user = User.objects.filter(userName = "bob").first()
        user_name = user.userName
        admin_privilege = user.adminPrivilege
        upload_privilege = user.uploadPrivilege

        if user.labelPrivilege: 
            label_privilege = False
        else:
            label_privilege = True

        mediation_privilege = user.mediationPrivilege

        sender_token = user.token
        sender_id = User.objects.get(userName='bob').id
        target_id = User.objects.get(userName='bob').id

        res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)
            
    # + no permission of mediationPrivilege
    def test_modify_mediationPrivilege_no_permission(self):
        user = User.objects.filter(userName = "bob").first()
        user_name = user.userName
        admin_privilege = user.adminPrivilege
        upload_privilege = user.uploadPrivilege
        label_privilege = user.labelPrivilege

        if user.mediationPrivilege: 
            mediation_privilege = False
        else:
            mediation_privilege = True

        sender_token = user.token
        sender_id = User.objects.get(userName='bob').id
        target_id = User.objects.get(userName='bob').id

        res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)
            
    # + target not found
    def test_modify_target_not_found(self):
        user = User.objects.filter(userName = "alice").first()
        user2 = User.objects.filter(userName = "bob").first()
        user_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        admin_privilege = user2.adminPrivilege
        upload_privilege = user2.uploadPrivilege
        label_privilege = user2.labelPrivilege
        mediation_privilege = user2.mediationPrivilege
        sender_token = user.token
        sender_id = User.objects.get(userName='alice').id
        target_id = 100000

        res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)
            
    # + sender not found
    def test_modify_sender_not_found(self):
        user = User.objects.filter(userName = "alice").first()
        user2 = User.objects.filter(userName = "bob").first()
        user_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        admin_privilege = user2.adminPrivilege
        upload_privilege = user2.uploadPrivilege
        label_privilege = user2.labelPrivilege
        mediation_privilege = user2.mediationPrivilege
        sender_token = user.token
        sender_id = 100000
        target_id = User.objects.get(userName='bob').id

        res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)
            
    # + missing params
    def test_modify_missing_params(self):
        user = User.objects.filter(userName = "bob").first()
        user_name = user.userName
        admin_privilege = user.adminPrivilege
        upload_privilege = user.uploadPrivilege
        label_privilege = user.labelPrivilege
        mediation_privilege = user.mediationPrivilege
        sender_token = user.token
        sender_id = User.objects.get(userName='bob').id
        target_id = User.objects.get(userName='bob').id

        res = self.put_user_modify(None, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
        res = self.put_user_modify(user_name, None, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
        res = self.put_user_modify(user_name, admin_privilege, None, label_privilege, mediation_privilege, sender_token, sender_id, target_id)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
        res = self.put_user_modify(user_name, admin_privilege, upload_privilege, None, mediation_privilege, sender_token, sender_id, target_id)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
        res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, None, sender_id, target_id)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
        res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, None, target_id)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
        res = self.put_user_modify(user_name, admin_privilege, upload_privilege, label_privilege, mediation_privilege, sender_token, sender_id, None)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)

    # + wrong method
    def test_modify_wrong_method(self):
        user = User.objects.filter(userName = "bob").first()
        user_name = user.userName
        admin_privilege = user.adminPrivilege
        upload_privilege = user.uploadPrivilege
        label_privilege = user.labelPrivilege
        mediation_privilege = user.mediationPrivilege
        sender_token = user.token
        sender_id = User.objects.get(userName='alice').id
        target_id = User.objects.get(userName='alice').id

        payload={
            'userName':user_name,
            'adminPrivilege': admin_privilege,
            'uploadPrivilege': upload_privilege,
            'labelPrivilege': label_privilege,
            'mediationPrivilege': mediation_privilege,
            'senderToken':sender_token,
            'senderId':sender_id,
            'targetId':target_id,
        }

        res=self.client.get('/user/modify',data=payload)
        self.assertEqual(res.status_code,405)
        self.assertEqual(res.json()['code'],-3)
        res=self.client.post('/user/modify',data=payload)
        self.assertEqual(res.status_code,405)
        self.assertEqual(res.json()['code'],-3)

    # /user/list
    # GET
    # + nomal case for get user list
    def test_user_list1(self):
        sender = User.objects.filter(userName = "alice").first()
        page_id = 1
        count = 100
        sort_by = "id"
        sort_by_ascend = 1

        res = self.get_user_list(sender.id, sender.token, page_id, count, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertTrue(res.json()['pageCount'] >= 0)

        if res.json()['pageCount'] <= page_id:
            self.assertTrue(len(res.json()['userList']) <= count)
        else:
            self.assertTrue(len(res.json()['userList']) == count)
        
        last = -1
        for uni in res.json()['userList']:
            self.assertTrue("id" in uni)
            self.assertTrue("userName" in uni)
            self.assertTrue("adminPrivilege" in uni)
            self.assertTrue("uploadPrivilege" in uni)
            self.assertTrue("labelPrivilege" in uni)
            self.assertTrue("experience" in uni)
            self.assertTrue("score" in uni)
            self.assertTrue(last < uni['id'])
            last = uni['id']
            
    # + nomal case for get user list
    def test_user_list2(self):
        sender = User.objects.filter(userName = "alice").first()
        page_id = 1
        count = 100
        sort_by = "score"
        sort_by_ascend = 1

        res = self.get_user_list(sender.id, sender.token, page_id, count, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertTrue(res.json()['pageCount'] >= 0)

        if res.json()['pageCount'] <= page_id:
            self.assertTrue(len(res.json()['userList']) <= count)
        else:
            self.assertTrue(len(res.json()['userList']) == count)
        
        last = -1
        for uni in res.json()['userList']:
            self.assertTrue("id" in uni)
            self.assertTrue("userName" in uni)
            self.assertTrue("adminPrivilege" in uni)
            self.assertTrue("uploadPrivilege" in uni)
            self.assertTrue("labelPrivilege" in uni)
            self.assertTrue("experience" in uni)
            self.assertTrue("score" in uni)
            self.assertTrue(last <= uni['score'])
            last = uni['score']
    
    # + no permissions case for get user list
    def test_user_list_no_premissions1(self):
        sender_id = User.objects.get(userName='alice').id
        sender_token = ''.join([random.choice("abcdefg12345678") for _ in range(64)])
        page_id = 1
        count = 100
        sort_by = "id"
        sort_by_ascend = 0

        res = self.get_user_list(sender_id, sender_token, page_id, count, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)
    
    # + unfound case for get user list
    def test_user_list_unfound(self):
        sender_id = 10
        sender_token = ''.join([random.choice("abcdefg12345678") for _ in range(64)])
        page_id = 1
        count = 100
        sort_by = "id"
        sort_by_ascend = 0

        res = self.get_user_list(sender_id, sender_token, page_id, count, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)
    
    # + invalid pageId case for get user list
    def test_user_list_invalid_pageId(self):
        sender = User.objects.filter(userName = "alice").first()
        page_id = 0
        count = 100
        sort_by = "id"
        sort_by_ascend = 0

        res = self.get_user_list(sender.id, sender.token, page_id, count, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
    
    # + invalid count case for get user list
    def test_user_list_invalid_count1(self):
        sender = User.objects.filter(userName = "alice").first()
        page_id = 1
        count = 200
        sort_by = "id"
        sort_by_ascend = 0

        res = self.get_user_list(sender.id, sender.token, page_id, count, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
    
    # + invalid count case for get user list
    def test_user_list_invalid_count2(self):
        sender = User.objects.filter(userName = "alice").first()
        page_id = 1
        count = 0
        sort_by = "id"
        sort_by_ascend = 0

        res = self.get_user_list(sender.id, sender.token, page_id, count, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
    
    # + invalid sortBy case for get user list
    def test_user_list_invalid_sortBy(self):
        sender = User.objects.filter(userName = "alice").first()
        page_id = 1
        count = 100
        sort_by = "userName"
        sort_by_ascend = 0

        res = self.get_user_list(sender.id, sender.token, page_id, count, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
    
    # + invalid sortByAscend case for get user list
    def test_user_list_invalid_sortByAscend(self):
        sender = User.objects.filter(userName = "alice").first()
        page_id = 1
        count = 100
        sort_by = "id"
        sort_by_ascend = 2

        res = self.get_user_list(sender.id, sender.token, page_id, count, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + missing params
    def test_user_list_missing_params(self):
        sender = User.objects.filter(userName = "alice").first()
        page_id = 1
        count = 100
        sort_by = "id"
        sort_by_ascend = 2

        res = self.get_user_list(None, sender.token, page_id, count, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

        res = self.get_user_list(sender.id, None, page_id, count, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

        res = self.get_user_list(sender.id, sender.token, None, count, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

        res = self.get_user_list(sender.id, sender.token, page_id, None, sort_by, sort_by_ascend)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

        res = self.get_user_list(sender.id, sender.token, page_id, count, None, sort_by_ascend)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

        res = self.get_user_list(sender.id, sender.token, page_id, count, sort_by, None)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + wrong methods
    def test_user_list_wrong_methods(self):
        sender = User.objects.filter(userName = "alice").first()
        page_id = 1
        count = 100
        sort_by = "id"
        sort_by_ascend = 2

        payload = {
            "senderId": sender.id,
            "senderToken": sender.token,
            "pageId": page_id,
            "count": count,
            "sortBy": sort_by,
            "sortByAscend": sort_by_ascend
        }
        
        res=self.client.get('/user/modify',data=payload)
        self.assertEqual(res.status_code,405)
        self.assertEqual(res.json()['code'],-3)
        
        res=self.client.post('/user/modify',data=payload)
        self.assertEqual(res.status_code,405)
        self.assertEqual(res.json()['code'],-3)

    # POST /user/getprivilege
    # + normal case
    def test_post_privilege(self):
        sender = User.objects.filter(userName = "bob").first()
        privilege = "labelPrivilege"

        res = self.post_user_privilege(sender.id, sender.token, privilege)
        self.assertEqual(res.status_code, 200)
        
    # + invalid privilege
    def test_post_privilege_invalid_privilege(self):
        sender = User.objects.filter(userName = "bob").first()
        privilege = "uploadPrivilege"

        res = self.post_user_privilege(sender.id, sender.token, privilege)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["code"], -2)
        
    # + invalid privilege
    def test_post_privilege_invalid_privilege2(self):
        sender = User.objects.filter(userName = "bob").first()
        privilege = "upload"

        res = self.post_user_privilege(sender.id, sender.token, privilege)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["code"], -2)
        
    # + invalid privilege
    def test_post_privilege_invalid_privilege2(self):
        sender = User.objects.filter(userName = "carol").first()
        privilege = "uploadPrivilege"

        res = self.post_user_privilege(sender.id, sender.token, privilege)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["code"], -2)
        
    # + no permission
    def test_post_privilege_no_permission(self):
        sender = User.objects.filter(userName = "bob").first()
        privilege = "labelPrivilege"

        res = self.post_user_privilege(sender.id, "abcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefgh", privilege)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()["code"], 2)

    # + bad methods
    def test_post_privilege_bad_methods(self):
        sender = User.objects.filter(userName = "bob").first()
        privilege = "labelPrivilage"

        payload = {
            "senderId": sender.id,
            "senderToken": sender.token,
            "privilege": privilege
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        res = self.client.get(f"/user/getprivilege", data=payload, content_type="application/json")
        self.assertEqual(res.status_code, 405)
        
        payload = {k:v for k,v in payload.items() if v is not None}
        res = self.client.put(f"/user/getprivilege", data=payload, content_type="application/json")
        self.assertEqual(res.status_code, 405)

        payload = {k:v for k,v in payload.items() if v is not None}
        res = self.client.delete(f"/user/getprivilege", data=payload, content_type="application/json")
        self.assertEqual(res.status_code, 405)

    # POST /user/email/{id}
    # + normal case
    def test_post_check_email(self):
        sender = User.objects.filter(userName = "bob").first()

        res = self.post_check_email(sender.id, sender.id, sender.token, sender.code)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(User.objects.filter(userName = "bob").first().checkEmail)
        self.assertEqual(User.objects.filter(userName = "bob").first().code, '')
        
        sender = User.objects.filter(userName = "bob").first()
        
        res = self.post_check_email(sender.id, sender.id, sender.token, sender.code)
        self.assertEqual(res.status_code, 400)
        self.assertTrue(User.objects.filter(userName = "bob").first().checkEmail)
        self.assertEqual(User.objects.filter(userName = "bob").first().code, '')
        
    # + user has already check email
    def test_post_check_email_user_has_already_check_email(self):
        sender = User.objects.filter(userName = "alice").first()

        res = self.post_check_email(sender.id, sender.id, sender.token, "123456")
        self.assertEqual(res.status_code, 400)
        self.assertTrue(User.objects.filter(userName = "alice").first().checkEmail)
        self.assertEqual(User.objects.filter(userName = "alice").first().code, '')
        
    # + user has already check email
    def test_post_check_email_user_has_already_check_email2(self):
        sender = User.objects.filter(userName = "carol").first()

        res = self.post_check_email(sender.id, sender.id, sender.token, "123456")
        self.assertEqual(res.status_code, 400)
        self.assertTrue(User.objects.filter(userName = "carol").first().checkEmail)
        self.assertEqual(User.objects.filter(userName = "carol").first().code, '123456')
        
    # + wrong code
    def test_post_check_email_wrong_code(self):
        sender = User.objects.filter(userName = "bob").first()

        res = self.post_check_email(sender.id, sender.id, sender.token, "123457")
        self.assertEqual(res.status_code, 400)
        self.assertFalse(User.objects.filter(userName = "bob").first().checkEmail)
        self.assertEqual(User.objects.filter(userName = "bob").first().code, "123456")

    # + wrong code
    def test_post_check_email_wrong_code2(self):
        sender = User.objects.filter(userName = "bob").first()

        res = self.post_check_email(sender.id, sender.id, sender.token, "12345786")
        self.assertEqual(res.status_code, 400)
        self.assertFalse(User.objects.filter(userName = "bob").first().checkEmail)
        self.assertEqual(User.objects.filter(userName = "bob").first().code, "123456")

    # + no permission
    def test_post_check_email_no_permission(self):
        sender = User.objects.filter(userName = "bob").first()

        res = self.post_check_email(User.objects.get(userName= "alice").id, sender.id, sender.token, "123456")
        self.assertEqual(res.status_code, 401)
        self.assertFalse(User.objects.filter(userName = "bob").first().checkEmail)
        self.assertEqual(User.objects.filter(userName = "bob").first().code, "123456")

    # + no permission
    def test_post_check_email_no_permission2(self):
        sender = User.objects.filter(userName = "bob").first()

        res = self.post_check_email(sender.id, sender.id, "abcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefgh", "123456")
        self.assertEqual(res.status_code, 401)
        self.assertFalse(User.objects.filter(userName = "bob").first().checkEmail)
        self.assertEqual(User.objects.filter(userName = "bob").first().code, "123456")

    # + not found
    def test_post_check_email_not_found(self):
        sender = User.objects.filter(userName = "bob").first()

        res = self.post_check_email(100000, sender.id, sender.token, "123456")
        self.assertEqual(res.status_code, 404)
        self.assertFalse(User.objects.filter(userName = "bob").first().checkEmail)
        self.assertEqual(User.objects.filter(userName = "bob").first().code, "123456")

    # + bad params
    def test_post_check_email_bad_params(self):
        sender = User.objects.filter(userName = "bob").first()

        res = self.post_check_email(sender.id, None, sender.token, "123456")
        self.assertEqual(res.status_code, 400)

        res = self.post_check_email(sender.id, sender.id, None, "123456")
        self.assertEqual(res.status_code, 400)

        res = self.post_check_email(sender.id, sender.id, sender.token, None)
        self.assertEqual(res.status_code, 400)

    # + bad methods
    def test_post_check_email_bad_methods(self):
        sender = User.objects.filter(userName = "bob").first()
        payload = {
            "senderId": sender.id,
            "senderToken": sender.token,
            "code": "123456"
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        
        res = self.client.get(f"/user/email/{sender.id}", data=payload, content_type="application/json")
        self.assertTrue(res.status_code, 405)
        
        res = self.client.put(f"/user/email/{sender.id}", data=payload, content_type="application/json")
        self.assertTrue(res.status_code, 405)
        
        res = self.client.delete(f"/user/email/{sender.id}", data=payload, content_type="application/json")
        self.assertTrue(res.status_code, 405)

    # POST /user/email/reset
    # + normal case
    def test_post_email_reset(self):
        userName = "alice"

        res = self.post_email_reset(userName)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(User.objects.filter(userName = "alice").first().code != "")
        
    # + normal case
    def test_post_email_reset2(self):
        userName = "carol"

        res = self.post_email_reset(userName)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(User.objects.filter(userName = "carol").first().code != "123456")

    # + unverified email
    def test_post_email_reset_unverified_email(self):
        userName = "bob"

        res = self.post_email_reset(userName)
        self.assertEqual(res.status_code, 400)
        self.assertTrue(User.objects.filter(userName = "bob").first().code == "123456")

    # + not found
    def test_post_email_reset_not_found(self):
        userName = "bob2"

        res = self.post_email_reset(userName)
        self.assertEqual(res.status_code, 404)

    # + bad params
    def test_post_email_reset_bad_params(self):
        res = self.post_email_reset(None)
        self.assertEqual(res.status_code, 400)
        
    # PUT /user/email/reset
    # + normal case
    def test_put_email_reset(self):
        userName = "carol"
        code = "123456"
        password = "carol123"
        user = User.objects.filter(userName = "carol").first()
        user.codeDeadline = (datetime.datetime.now() + datetime.timedelta(minutes = 5)).timestamp()
        user.save()

        res = self.put_email_reset(userName, code, password)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(User.objects.filter(userName = "carol").first().code == "")
        self.assertTrue(bcrypt.checkpw(password.encode(), User.objects.filter(userName = "carol").first().key.encode()))
        
    # + unverified email
    def test_put_email_reset_unverified_email(self):
        userName = "bob"
        code = "123456"
        password = "carol123"

        res = self.put_email_reset(userName, code, password)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(bcrypt.checkpw(password.encode(), User.objects.filter(userName = "bob").first().key.encode()))
    
    # + wrong code
    def test_put_email_reset_wrong_code(self):
        userName = "carol"
        code = "123457"
        password = "carol123"

        res = self.put_email_reset(userName, code, password)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(bcrypt.checkpw(password.encode(), User.objects.filter(userName = "carol").first().key.encode()))
    
    # + not found
    def test_put_email_reset_not_found(self):
        userName = "qcarol"
        code = "123457"
        password = "carol123"

        res = self.put_email_reset(userName, code, password)
        self.assertEqual(res.status_code, 404)
    
    # + bad params
    def test_put_email_reset_bad_params(self):
        userName = "carol"
        code = "123457"
        password = "carol123"

        res = self.put_email_reset(None, code, password)
        self.assertEqual(res.status_code, 400)

        res = self.put_email_reset(userName, None, password)
        self.assertEqual(res.status_code, 400)

        res = self.put_email_reset(userName, code, None)
        self.assertEqual(res.status_code, 400)

    # + bad methods
    def test_put_email_reset_bad_methods(self):
        userName = "carol"
        code = "123457"
        password = "carol123"

        payload = {
            "userName": userName,
            "code": code,
            "password": password,
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        
        res = self.client.get(f"/user/email/reset", data=payload, content_type="application/json")
        self.assertTrue(res.status_code, 405)
        
        res = self.client.delete(f"/user/email/reset", data=payload, content_type="application/json")
        self.assertTrue(res.status_code, 405)

    # PUT /user/requests/{id}
    # + noraml case
    def test_put_check_request(self):
        id = AdminMessage.objects.first().id
        sender = User.objects.filter(userName = "alice").first()
        accepted = True

        res = self.put_check_request(id, sender.id, sender.token, accepted)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(User.objects.filter(userName = "bob").first().uploadPrivilege)
        user = User.objects.filter(userName = "bob").first()
        self.assertTrue(len(user.systemMessage) != 0)
        
    # + noraml case
    def test_put_check_request2(self):
        id = AdminMessage.objects.first().id+1
        sender = User.objects.filter(userName = "alice").first()
        accepted = False

        res = self.put_check_request(id, sender.id, sender.token, accepted)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(User.objects.filter(userName = "carol").first().uploadPrivilege)
        user = User.objects.filter(userName = "carol").first()
        self.assertTrue(len(user.systemMessage) != 0)
        
    # + noraml case
    def test_put_check_request3(self):
        id = AdminMessage.objects.first().id+2
        sender = User.objects.filter(userName = "alice").first()
        accepted = True

        res = self.put_check_request(id, sender.id, sender.token, accepted)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(User.objects.filter(userName = "carol").first().credit, 80)
        user = User.objects.filter(userName = "carol").first()
        self.assertTrue(len(user.systemMessage) != 0)
        user = User.objects.filter(userName = "bob").first()
        self.assertTrue(len(user.systemMessage) != 0)
        
    # + noraml case
    def test_put_check_request4(self):
        id = AdminMessage.objects.first().id+2
        sender = User.objects.filter(userName = "alice").first()
        accepted = False

        res = self.put_check_request(id, sender.id, sender.token, accepted)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(User.objects.filter(userName = "carol").first().credit, 100)
        user = User.objects.filter(userName = "carol").first()
        self.assertTrue(len(user.systemMessage) == 0)
        user = User.objects.filter(userName = "bob").first()
        self.assertTrue(len(user.systemMessage) != 0)
        
    # + noraml case
    def test_put_check_request5(self):
        id = AdminMessage.objects.first().id+4
        sender = User.objects.filter(userName = "alice").first()
        accepted = True

        res = self.put_check_request(id, sender.id, sender.token, accepted)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(User.objects.filter(userName = "carol").first().uploadPrivilege)
        user = User.objects.filter(userName = "carol").first()
        self.assertTrue(len(user.systemMessage) != 0)

    # + no permissions
    def test_put_check_request_no_permissions(self):
        id = AdminMessage.objects.first().id+2
        sender = User.objects.filter(userName = "bob").first()
        accepted = True

        res = self.put_check_request(id, sender.id, sender.token, accepted)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(User.objects.filter(userName = "carol").first().credit, 100)
        user = User.objects.filter(userName = "carol").first()
        self.assertTrue(len(user.systemMessage) == 0)

    # + no permissions
    def test_put_check_request_no_permissions2(self):
        id = AdminMessage.objects.first().id+2
        sender = User.objects.filter(userName = "alice").first()
        accepted = True

        res = self.put_check_request(id, sender.id, "abcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefgh", accepted)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(User.objects.filter(userName = "carol").first().credit, 100)
        user = User.objects.filter(userName = "carol").first()
        self.assertTrue(len(user.systemMessage) == 0)

    # + not found
    def test_put_check_request_not_found(self):
        id = 100000
        sender = User.objects.filter(userName = "alice").first()
        accepted = True

        res = self.put_check_request(id, sender.id, sender.token, accepted)
        self.assertEqual(res.status_code, 404)

    # + not found2
    def test_put_check_request_not_found2(self):
        id = AdminMessage.objects.first().id+2
        sender = User.objects.filter(userName = "alice").first()
        accepted = True

        res = self.put_check_request(id, 10, sender.token, accepted)
        self.assertEqual(res.status_code, 404)

    # + wrong type
    def test_put_check_request_wrong_type(self):
        id = AdminMessage.objects.first().id+3
        sender = User.objects.filter(userName = "alice").first()
        accepted = True

        res = self.put_check_request(id, sender.id, sender.token, accepted)
        self.assertEqual(res.status_code, 500)

    # + bad params
    def test_put_check_request_bad_params(self):
        id = AdminMessage.objects.first().id+2
        sender = User.objects.filter(userName = "alice").first()
        accepted = True

        res = self.put_check_request(id, None, sender.token, accepted)
        self.assertEqual(res.status_code, 400)

        res = self.put_check_request(id, sender.id, None, accepted)
        self.assertEqual(res.status_code, 400)

        res = self.put_check_request(id, sender.id, sender.token, None)
        self.assertEqual(res.status_code, 400)