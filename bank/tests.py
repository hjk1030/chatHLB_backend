import random,string,hashlib,datetime
from django.test import TestCase
from .models import Account,VerificationCode
import bcrypt
import json
import chatHLB_backend.settings
import os

# Create your tests here.
class TaskTests(TestCase):
    # Initializer
    def setUp(self):
        Account.objects.create(
            serialNumber = "621663123456123456",
            token = bcrypt.hashpw(hashlib.sha256(b"password1").hexdigest().encode(),bcrypt.gensalt(8)).decode(),
            balance = 100
        )
        Account.objects.create(
            serialNumber = "621663123456123457",
            token = bcrypt.hashpw("password2".encode(),bcrypt.gensalt(8)).decode(),
            balance = 500
        )
        VerificationCode.objects.create(
            code = "123456",
            creator = Account.objects.filter(serialNumber = "621663123456123456").first()
        )

    # Utility functions
    def put_bank_deposit(self, serialNumber, amount):
        payload = {
            "serialNumber": serialNumber,
            "amount": amount,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.put(f"/bank/deposit", data=payload, content_type='application/json')

    def put_bank_withdraw(self, serialNumber, verification, amount):
        payload = {
            "serialNumber": serialNumber,
            "verificationCode": verification,
            "amount": amount,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.put(f"/bank/withdraw", data=payload, content_type='application/json')

    def post_bank_register(self, key):
        payload = {
            "key": key,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.post(f"/bank/register", data=payload, content_type='application/json')

    def get_bank_verificationcode(self, serialNumber, key):
        payload = {
            "serialNumber": serialNumber,
            "key": key,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/bank/verificationcode", data=payload, content_type='application/json')

    # PUT /bank/deposit
    # + normal case
    def test_put_bank_deposit(self):
        serialNumber = "621663123456123456"
        amount = 100

        res = self.put_bank_deposit(serialNumber, amount)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Account.objects.filter(serialNumber = "621663123456123456").first().balance, 200)

    # + invalid amount
    def test_put_bank_deposit_invalid_amount1(self):
        serialNumber = "621663123456123456"
        amount = 0

        res = self.put_bank_deposit(serialNumber, amount)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(Account.objects.filter(serialNumber = "621663123456123456").first().balance, 100)

    # + invalid amount
    def test_put_bank_deposit_invalid_amount2(self):
        serialNumber = "621663123456123456"
        amount = -10

        res = self.put_bank_deposit(serialNumber, amount)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(Account.objects.filter(serialNumber = "621663123456123456").first().balance, 100)
   
    # + not found
    def test_put_bank_deposit_not_found(self):
        serialNumber = "6216631234561234562"
        amount = 10

        res = self.put_bank_deposit(serialNumber, amount)
        self.assertEqual(res.status_code, 404)
    
    # + bad params
    def test_put_bank_deposit_bad_params(self):
        serialNumber = "621663123456123456"
        amount = 10

        res = self.put_bank_deposit(None, amount)
        self.assertEqual(res.status_code, 400)

        res = self.put_bank_deposit(serialNumber, None)
        self.assertEqual(res.status_code, 400)

    # + bad methods
    def test_put_bank_deposit_bad_methods(self):
        payload = {
            "serialNumber": "621663123456123456",
            "amount": 10,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        
        res = self.client.post(f"/bank/deposit", data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        
        res = self.client.get(f"/bank/deposit", data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        
        res = self.client.delete(f"/bank/deposit", data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 405)

    # PUT /bank/withdraw
    # + normal case
    def test_put_bank_withdraw(self):
        serialNumber = "621663123456123456"
        verificationCode = "123456"
        amount = 100

        res = self.put_bank_withdraw(serialNumber, verificationCode, amount)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Account.objects.filter(serialNumber = "621663123456123456").first().balance, 0)

    # + invalid amount
    def test_put_bank_withdraw_invalid_amount(self):
        serialNumber = "621663123456123456"
        verificationCode = "123456"
        amount = 120

        res = self.put_bank_withdraw(serialNumber, verificationCode, amount)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(Account.objects.filter(serialNumber = "621663123456123456").first().balance, 100)

    # + invalid amount
    def test_put_bank_withdraw_invalid_amount2(self):
        serialNumber = "621663123456123456"
        verificationCode = "123456"
        amount = -10

        res = self.put_bank_withdraw(serialNumber, verificationCode, amount)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(Account.objects.filter(serialNumber = "621663123456123456").first().balance, 100)

    # + invalid amount
    def test_put_bank_withdraw_invalid_amount3(self):
        serialNumber = "621663123456123456"
        verificationCode = "123456"
        amount = 0

        res = self.put_bank_withdraw(serialNumber, verificationCode, amount)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(Account.objects.filter(serialNumber = "621663123456123456").first().balance, 100)

    # + no permissions
    def test_put_bank_withdraw_no_premissions(self):
        serialNumber = "621663123456123456"
        verificationCode = "123457"
        amount = 100

        res = self.put_bank_withdraw(serialNumber, verificationCode, amount)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(Account.objects.filter(serialNumber = "621663123456123456").first().balance, 100)

    # + no permissions
    def test_put_bank_withdraw_no_premissions2(self):
        serialNumber = "621663123456123457"
        verificationCode = "123456"
        amount = 100

        res = self.put_bank_withdraw(serialNumber, verificationCode, amount)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(Account.objects.filter(serialNumber = "621663123456123457").first().balance, 500)

    # + not found
    def test_put_bank_withdraw_not_found(self):
        serialNumber = "621663123456123458"
        verificationCode = "123456"
        amount = 100

        res = self.put_bank_withdraw(serialNumber, verificationCode, amount)
        self.assertEqual(res.status_code, 404)
        
    # + bad_params
    def test_put_bank_withdraw_bad_params(self):
        serialNumber = "621663123456123456"
        verificationCode = "123456"
        amount = 100

        res = self.put_bank_withdraw(None, verificationCode, amount)
        self.assertEqual(res.status_code, 400)

        res = self.put_bank_withdraw(serialNumber, None, amount)
        self.assertEqual(res.status_code, 400)

        res = self.put_bank_withdraw(serialNumber, verificationCode, None)
        self.assertEqual(res.status_code, 400)

    # + bad methods
    def test_put_bank_withdraw_bad_methods(self):
        payload = {
            "serialNumber": "621663123456123456",
            "verificationCode": "123456",
            "amount": 100,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        
        res = self.client.post(f"/bank/withdraw", data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        
        res = self.client.delete(f"/bank/withdraw", data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        
        res = self.client.get(f"/bank/withdraw", data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 405)

    # POST /bank/register
    # + normal case
    def test_post_bank_register(self):
        key = "123456"
        res = self.post_bank_register(key)
        self.assertEqual(res.status_code, 200)

    # + bad params
    def test_post_bank_register_bad_params(self):
        key = "123456"
        res = self.post_bank_register(None)
        self.assertEqual(res.status_code, 400)

    # GET /bank/verificationcode
    # + normal case
    def test_get_bank_verificationcode(self):
        serialNumber = "621663123456123457"
        key = "password2"

        res = self.get_bank_verificationcode(serialNumber, key)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(VerificationCode.objects.filter(creator = Account.objects.filter(serialNumber = "621663123456123457").first()).first() != None)

    # + wrong password
    def test_get_bank_verificationcode_wrong_password(self):
        serialNumber = "621663123456123457"
        key = "password"

        res = self.get_bank_verificationcode(serialNumber, key)
        self.assertEqual(res.status_code, 401)
        self.assertTrue(VerificationCode.objects.filter(creator = Account.objects.filter(serialNumber = "621663123456123457").first()).first() == None)

    # + not found
    def test_get_bank_verificationcode_not_found(self):
        serialNumber = "621663123456123458"
        key = "password2"

        res = self.get_bank_verificationcode(serialNumber, key)
        self.assertEqual(res.status_code, 404)

    # + bad params
    def test_get_bank_verificationcode_bad_params(self):
        serialNumber = "621663123456123457"
        key = "password2"

        res = self.get_bank_verificationcode(None, key)
        self.assertEqual(res.status_code, 400)

        res = self.get_bank_verificationcode(serialNumber, None)
        self.assertEqual(res.status_code, 400)
