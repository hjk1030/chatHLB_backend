import random,string,hashlib,datetime
from django.test import TestCase
from .models import Task,TaskPackage,TaskTemplate,TaskAnswer
from user.models import User
from utils.utils_require import MAX_TOKEN_LENGTH,MAX_TEMPLATE_DESCRIPTION_LENGTH
from utils.utils_time import get_timestamp
import bcrypt
import json
from django.core.files.uploadedfile import SimpleUploadedFile
import chatHLB_backend.settings
import os

# Create your tests here.
class TaskTests(TestCase):
    # Initializer
    def setUp(self):
        User.objects.create(
            token = "".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH)),
            key = bcrypt.hashpw(hashlib.sha256(b"passwordofalice").hexdigest().encode(),bcrypt.gensalt(8)).decode(),
            userName = "Alice",
            adminPrivilege = True,
            labelPrivilege = True,
            uploadPrivilege = True,
            credit = 100,
        )
        User.objects.create(
            token = "".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH)),
            key = bcrypt.hashpw(hashlib.sha256(b"passwordofbob").hexdigest().encode(),bcrypt.gensalt(8)).decode(),
            userName = "Bob",
            uploadPrivilege = True,
            credit = 100,
        )
        User.objects.create(
            token = "".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH)),
            key = bcrypt.hashpw(hashlib.sha256(b"passwordofcarol").hexdigest().encode(),bcrypt.gensalt(8)).decode(),
            userName = "Carol",
            credit = 100,
        )
        TaskTemplate.objects.create(
            creator = User.objects.get(userName="Alice"),
            templateName = "newTemplate",
            objectList = [
            {"type":"text","count":1},
            {"type":"image","count":2},
            {"type":"textinput","count":1},
            ],
            verified=True,
        )
        TaskTemplate.objects.create(
            creator = User.objects.get(userName="Bob"),
            templateName = "newTemplate2",
            verified = True,
        )
        TaskTemplate.objects.create(
            creator = User.objects.get(userName="Alice"),
            templateName = "newTemplate3",
            objectList = [
            {"type":"text","count":1},
            {"type":"image","count":2},
            {"type":"video","count":2},
            {"type":"audio","count":2},
            {"type":"singlechoice","count":1},
            {"type":"multiplechoice","count":1},
            ],
        )
        TaskPackage.objects.create(
            creator = User.objects.get(userName="Alice"),
            template = TaskTemplate.objects.get(templateName = "newTemplate"),
            taskName = "newTaskPackage1",
            uploaded = True,
            distribution = 0,
        )
        TaskPackage.objects.create(
            creator = User.objects.get(userName="Bob"),
            template = TaskTemplate.objects.get(templateName = "newTemplate"),
            taskName = "newTaskPackage2",
        )
        TaskPackage.objects.create(
            creator = User.objects.get(userName="Bob"),
            template = TaskTemplate.objects.get(templateName = "newTemplate"),
            taskName = "newTaskPackage3",
            uploaded = True,
            distributed = True,
            verified = True,
        )
        TaskPackage.objects.create(
            creator = User.objects.get(userName="Carol"),
            template = TaskTemplate.objects.get(templateName = "newTemplate"),
            taskName = "newTaskPackage4"
        )
        TaskPackage.objects.create(
            creator = User.objects.get(userName="Bob"),
            template = TaskTemplate.objects.get(templateName = "newTemplate"),
            taskName = "newTaskPackage5",
            uploaded = True,
            distributed = True,
            verified = True,
            availbleCount = 1000
        )
        TaskPackage.objects.create(
            creator = User.objects.get(userName="Bob"),
            template = TaskTemplate.objects.get(templateName = "newTemplate"),
            taskName = "newTaskPackage6",
            availbleCount = 1000
        )
        TaskPackage.objects.create(
            creator = User.objects.get(userName="Bob"),
            template = TaskTemplate.objects.get(templateName = "newTemplate"),
            taskName = "newTaskPackage7",
            uploaded = True
        )
        TaskPackage.objects.create(
            creator = User.objects.get(userName="Alice"),
            template = TaskTemplate.objects.get(templateName = "newTemplate3"),
            taskName = "newTaskPackage8",
        )
        User.objects.create(
            token = "".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH)),
            key = bcrypt.hashpw(hashlib.sha256(b"passwordofdave").hexdigest().encode(),bcrypt.gensalt(8)).decode(),
            userName = "Dave",
            labelPrivilege = True
        )
        User.objects.create(
            token = "".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH)),
            key = bcrypt.hashpw(hashlib.sha256(b"passwordofeve").hexdigest().encode(),bcrypt.gensalt(8)).decode(),
            userName = "Eve",
            labelPrivilege = True,
            currentTaskPackage = TaskPackage.objects.filter(taskName = "newTaskPackage4").first()
        )
        User.objects.create(
            token = "".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH)),
            key = bcrypt.hashpw(hashlib.sha256(b"passwordoffrancis").hexdigest().encode(),bcrypt.gensalt(8)).decode(),
            userName = "Francis",
            labelPrivilege = False
        )
        Task.objects.create(
            packageBelonging = TaskPackage.objects.get(taskName = "newTaskPackage1"),
        )
        taskStartId = Task.objects.first().id-1
        TaskAnswer.objects.create(
            submitter = User.objects.get(userName="Alice"),
            task = Task.objects.get(id = taskStartId + 1),
            finished = False,
            verified = False,
        )
        for i in range(2, 7, 1):
            Task.objects.create(
                packageBelonging = TaskPackage.objects.get(taskName = "newTaskPackage1"),
            )
        newTaskPackage1 = TaskPackage.objects.filter(taskName = "newTaskPackage1").first()
        newTaskPackage1.completedUser.add(User.objects.filter(userName = "Dave").first())
        for i in range(7, 12, 1):
            Task.objects.create(
                packageBelonging = TaskPackage.objects.get(taskName = "newTaskPackage2"),
            )
        newTaskPackage2 = TaskPackage.objects.filter(taskName = "newTaskPackage2").first()
        newTaskPackage2.completedUser.add(User.objects.filter(userName = "Dave").first())
        for i in range(12, 15, 1):
            Task.objects.create(
                packageBelonging = TaskPackage.objects.get(taskName = "newTaskPackage3"),
            )
        newTaskPackage3 = TaskPackage.objects.filter(taskName = "newTaskPackage3").first()
        newTaskPackage3.completedUser.add(User.objects.filter(userName = "Dave").first())
        for i in range(2, 15, 1):
            TaskAnswer.objects.create(
                submitter = User.objects.filter(userName = "Dave").first(),
                task = Task.objects.filter(id = taskStartId + i).first(),
            )
        TaskPackage.objects.create(
            creator = User.objects.get(userName="Alice"),
            template = TaskTemplate.objects.get(templateName = "newTemplate"),
            taskName = "TP1",
            uploaded = True,
            distribution = 0,
        )

    
    # Utility functions
    def get_package_info(self, id, senderId, senderToken):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/task/package/{id}", data=payload, content_type='application/json')
    
    def create_package(self, senderId, senderToken, distribution, maxDistributedUser, subtaskLimit, score, deadline, taskName, templateId, tags, description):
        payload = {
            "senderId":senderId,
            "senderToken":senderToken,
            "distribution":distribution,
            "maxDistributedUser":maxDistributedUser,
            "subtaskLimit":subtaskLimit,
            "score":score,
            "deadline":deadline,
            "taskName":taskName,
            "templateId":templateId,
            "tags":tags,
            "description":description,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.post("/task/package", data=payload, content_type="application/json")

    def modify_package(self, id, senderId, senderToken, distribution, maxDistributedUser, subtaskLimit, score, deadline, taskName, templateId, tags, description):
        payload = {
            "senderId":senderId,
            "senderToken":senderToken,
            "distribution":distribution,
            "maxDistributedUser":maxDistributedUser,
            "subtaskLimit":subtaskLimit,
            "score":score,
            "deadline":deadline,
            "taskName":taskName,
            "templateId":templateId,
            "tags":tags,
            "description":description,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.put(f"/task/package/{id}", data=payload, content_type="application/json")

    def delete_package(self, id, senderId, senderToken):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        return self.client.delete(f"/task/package/{id}", data=payload, content_type='application/json')

    def create_template(self, objectList, templateName, description, senderId, senderToken):
        payload = {
            "objectList": objectList,
            "templateName": templateName,
            "description": description,
            "senderId": senderId,
            "senderToken": senderToken
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.post(f"/task/template", data=payload, content_type="application/json")

    def template_list(self, senderId, senderToken, pageId, count, onlyVerified):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
            "pageId": pageId,
            "count": count,
            "onlyVerified": onlyVerified
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/task/template", data=payload, content_type="application/json")

    def get_template(self, id, senderId, senderToken):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/task/template/{id}", data=payload, content_type="application/json")

    def obtain_acceptable_package(self, senderId, senderToken):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/task/package/todo", data=payload, content_type="application/json")

    def accept_package(self, id, senderId, senderToken, accept):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
            "accept": accept
        }
        payload = {k:v for k,v in payload.items() if v is not None}
        return self.client.post(f"/task/package/accept/{id}", data=payload, content_type='application/json')

    def publish_package(self, id, senderId, senderToken):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.post(f"/task/package/publish/{id}", data=payload, content_type="application/json")

    def get_package_list(self, senderId, senderToken, pageId, count):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
            "pageId": pageId,
            "count": count,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/task/package/list", data=payload, content_type="application/json")
    
    def get_created_package_list(self, senderId, senderToken):
        payload = {
            "senderId":senderId,
            "senderToken":senderToken,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/task/package/created", data=payload, content_type="application/json")

    def get_task_info(self, id, senderId, senderToken):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/task/{id}", data=payload, content_type="application/json")
    
    def get_completed_user_list(self, id, senderId, senderToken):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/task/package/completed/{id}", data=payload, content_type="application/json")
    
    def get_manual_check_info(self, id, senderId, senderToken, mode, submitterId):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
            "mode": mode,
            "submitterId": submitterId,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.get(f"/task/package/manualcheck/{id}", data=payload, content_type="application/json")

    def put_manual_check_info(self, id, senderId, senderToken, submitterId, acceptRate):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
            "submitterId": submitterId,
            "acceptRate": acceptRate,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.put(f"/task/package/manualcheck/{id}", data=payload, content_type="application/json")

    def submit_answer(self, id, answers, senderId, senderToken):
        payload = {
            "answers": answers,
            "senderId": senderId,
            "senderToken": senderToken,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.put(f"/task/answer/{id}", data=payload, content_type="application/json")

    def auto_check(self, id, senderId, senderToken):
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        return self.client.put(f"/task/package/autocheck/{id}", data=payload, content_type="application/json")

    # /task/package/{id}
    # POST

    # + normal case
    def test_create_package(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = "PAC1"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PAC1").first().creator, sender)

    # + create without senderId
    def test_create_package_without_sender_id(self):
        sender = User.objects.get(userName="Alice")
        sender_id = None
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = "PAC2"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "description"

        res = self.create_package(None, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertNotEqual(res.status_code, 200)
        self.assertNotEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PAC2").first(), None)

    # + create without senderToken
    def test_create_package_without_sender_token(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = None
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = "PAC3"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "description"

        res = self.create_package(sender_id, None, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertNotEqual(res.status_code, 200)
        self.assertNotEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PAC3").first(), None)

    # + create without distribution
    def test_create_package_without_distribution(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = None
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = "PAC4"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "description"

        res = self.create_package(sender_id, sender_token, None, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertNotEqual(res.status_code, 200)
        self.assertNotEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PAC4").first(), None)

    # + create without subtaskLimit
    def test_create_package_without_subtask_limit(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = None
        score = 10.0
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = "PAC4"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, None, score, deadline, task_name, template_id, tags, description)
        self.assertNotEqual(res.status_code, 200)
        self.assertNotEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PAC4").first(), None)

    # + create without score
    def test_create_package_without_score(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = None
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = "PAC5"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, None, deadline, task_name, template_id, tags, description)
        self.assertNotEqual(res.status_code, 200)
        self.assertNotEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PAC5").first(), None)
    
    # + create without deadline
    def test_create_package_without_deadline(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = None
        task_name = "PAC6"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, None, task_name, template_id, tags, description)
        self.assertNotEqual(res.status_code, 200)
        self.assertNotEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PAC6").first(), None)

    # + create without taskName
    def test_create_package_without_task_name(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = None
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, None, template_id, tags, description)
        self.assertNotEqual(res.status_code, 200)
        self.assertNotEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PAC7").first(), None)

    # + create without templateId
    def test_create_package_without_template_id(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = "PAC8"
        template_id = None
        tags = []
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, None, tags, description)
        self.assertNotEqual(res.status_code, 200)
        self.assertNotEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PAC8").first(), None)

    # + create with wrong type of senderId
    def test_create_package_with_wrong_type_of_sender_id(self):
        sender = User.objects.get(userName="Alice")
        sender_id = "abc"
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = "PACC9"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PACC9").first(), None)

    # + create with wrong type of template id
    def test_create_package_with_wrong_type_of_template_id(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = "PACC10"
        template_id = "abc"
        tags = []
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PACC10").first(), None)

    # + create with wrong type of deadline
    def test_create_package_with_wrong_type_of_deadline(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = "abc"
        task_name = "PACC11"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PACC11").first(), None)

    # + create with too long tag list
    def test_create_package_with_too_long_tag_list(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = "abc"
        task_name = "PACC11"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = ["tag1","tag2","tag3","tag4","tag5","tag6"]
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PACC11").first(), None)
    
    # + create with too long tag string
    def test_create_package_with_too_long_tag_string(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = "abc"
        task_name = "PACC11"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = ["tag_with_loooooooooooooooooog_name"]
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PACC11").first(), None)
    
    # + create too long description
    def test_create_package_with_too_long_description(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = "abc"
        task_name = "PACC11"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "The quick brown fox jumps over the lazy dog.The quick brown fox jumps over the lazy dog.The quick brown fox jumps over the lazy dog.The quick brown fox jumps over the lazy dog.The quick brown fox jumps over the lazy dog.The quick brown fox jumps over the lazy dog."

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PACC11").first(), None)

    # + create with wrong senderId
    def test_create_package_with_wrong_sender_id(self):
        sender = User.objects.get(userName="Alice")
        sender_id = User.objects.count() + 1
        sender_token = sender.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = "PAC9"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PAC9").first(), None)

    # + create with wrong token
    def test_create_package_with_wrong_token(self):
        sender = User.objects.get(userName="Alice")
        sender_wrong = User.objects.get(userName="Bob")
        sender_id = sender.id
        sender_token = sender_wrong.token
        distribution = True
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = 10.0
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = "PACC"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id
        tags = []
        description = "description"

        res = self.create_package(sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PACC").first(), None)

    # + create with wrong mothod
    def test_create_package_with_wrong_method(self):
        sender = User.objects.get(userName="Alice")
        sender_id = sender.id
        sender_token = sender.token
        distribution = True
        subtask_limit = 10.0
        score = 10.0
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = "PACD"
        template_id = TaskTemplate.objects.get(templateName="newTemplate").id

        res = self.client.get('/task/package', {'senderId': sender_id, 'token': sender_token, 'distribution': distribution, 'subtaskLimit': subtask_limit, 'score': score, 'deadline': deadline, 'taskName': task_name, 'templateId': template_id})
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
        self.assertEqual(TaskPackage.objects.filter(taskName = "PACD").first(), None)

    # /task/package/{id}
    # PUT
    # + normal case for subtaskLimit
    def test_modify_subtaskLimit(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = package.score
        deadline = package.deadline
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName="newTaskPackage2").first().subtaskLimit, 10.0)
    
    # + normal case for score
    def test_modify_score(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = package.subtaskLimit
        score = 10.0
        deadline = package.deadline
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName="newTaskPackage2").first().score, 10.0)
    
    # + normal case for deadline
    def test_modify_deadline(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = package.subtaskLimit
        score = package.score
        deadline = (datetime.datetime.now() + datetime.timedelta(days = 2)).timestamp()
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName="newTaskPackage2").first().deadline, deadline)
    
    # + normal case for taskName
    def test_modify_taskName(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = package.subtaskLimit
        score = package.score
        deadline = package.deadline
        task_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        package.refresh_from_db()
        self.assertEqual(package.taskName, task_name)
    
    # + normal case for templateId
    def test_modify_templateId(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = package.subtaskLimit
        score = package.score
        deadline = package.deadline
        task_name = package.taskName
        template_id = TaskTemplate.objects.get(templateName = "newTemplate2").id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName="newTaskPackage2").first().template, TaskTemplate.objects.filter(templateName="newTemplate2").first())

    # + normal case for admin
    def test_modify_admin(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = User.objects.filter(userName = "Alice").first()
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = package.score
        deadline = package.deadline
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName="newTaskPackage2").first().subtaskLimit, 10.0)

    # + normal case for creator
    def test_modify_creator(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage4").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = package.score
        deadline = package.deadline
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(TaskPackage.objects.filter(taskName="newTaskPackage4").first().subtaskLimit, 10.0)

    # + negative case for subtaskLimit
    def test_modify_neg_subtaskLimit(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = -10.0
        score = package.score
        deadline = package.deadline
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
    
    # + negative case for score
    def test_modify_neg_score(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = package.subtaskLimit
        score = -10.0
        deadline = package.deadline
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
    
    # + invalid length case for taskName
    def test_modify_len_taskName(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = package.subtaskLimit
        score = package.score
        deadline = package.deadline
        task_name = ''.join([random.choice("abcdefg12345678") for _ in range(50)])
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
    
    # + invalid length case for tags
    def test_modify_len_tags(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = package.subtaskLimit
        score = package.score
        deadline = package.deadline
        task_name = ''.join([random.choice("abcdefg12345678") for _ in range(50)])
        template_id = package.template.id
        tags = ["tag1","tag2","tag3","tag4","tag5","tag6"]
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

        tags = ["tag_with_loooooooooooooooooog_name"]
        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + invalid length case for description
    def test_modify_len_description(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = package.subtaskLimit
        score = package.score
        deadline = package.deadline
        task_name = ''.join([random.choice("abcdefg12345678") for _ in range(50)])
        template_id = package.template.id
        tags = []
        description = "The quick brown fox jumps over the lazy dog.The quick brown fox jumps over the lazy dog.The quick brown fox jumps over the lazy dog.The quick brown fox jumps over the lazy dog.The quick brown fox jumps over the lazy dog.The quick brown fox jumps over the lazy dog."

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
    
    # + unfound case for templateId
    def test_modify_notfound_templateId(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = package.subtaskLimit
        score = package.score
        deadline = package.deadline
        task_name = package.taskName
        template_id = 10
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)
    
    # + unfound case for senderId
    def test_modify_notfound_senderId(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = 10
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = package.subtaskLimit
        score = package.score
        deadline = package.deadline
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)

    # + no permissions case 1
    def test_modify_no_permissions1(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage4").first()
        sender = User.objects.filter(userName = "Bob").first()
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = package.score
        deadline = package.deadline
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + no permissions case 2
    def test_modify_no_permissions2(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = ''.join([random.choice("abcdefg12345678") for _ in range(64)])
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = package.score
        deadline = package.deadline
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + no permissions case 3
    def test_modify_no_permissions3(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = User.objects.filter(userName = "Alice").first()
        sender_id = sender.id
        sender_token = ''.join([random.choice("abcdefg12345678") for _ in range(64)])
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = package.score
        deadline = package.deadline
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + distributed case1
    def test_modify_distributed1(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage3").first()
        sender = User.objects.filter(userName = "Alice").first()
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = package.score
        deadline = package.deadline
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + distributed case2
    def test_modify_distributed2(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage3").first()
        sender = package.creator
        sender_id = sender.id
        sender_token = sender.token
        distribution = package.distribution
        maxDistributedUser = 5
        subtask_limit = 10.0
        score = package.score
        deadline = package.deadline
        task_name = package.taskName
        template_id = package.template.id
        tags = []
        description = "description"

        res = self.modify_package(package.id, sender_id, sender_token, distribution, maxDistributedUser, subtask_limit, score, deadline, task_name, template_id, tags, description)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
    
    # GET /task/package/{id}
    # Correct respond
    def test_get_package_info(self):
        packageId = TaskPackage.objects.get(taskName='newTaskPackage1').id
        userId = User.objects.get(userName='Alice').id
        userToken = User.objects.get(userName='Alice').token
        timeStamp = User.objects.get(userName='Alice').lastupdatedtime
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,200)
        self.assertJSONEqual(res.content,TaskPackage.objects.get(taskName='newTaskPackage1').serialize()|{'code':0,'info':'Succeed'})
        self.assertNotEqual(timeStamp,User.objects.get(userName='Alice').lastupdatedtime)

        packageId = TaskPackage.objects.get(taskName='newTaskPackage2').id
        timeStamp = User.objects.get(userName='Alice').lastupdatedtime
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,200)
        self.assertJSONEqual(res.content,TaskPackage.objects.get(taskName='newTaskPackage2').serialize()|{'code':0,'info':'Succeed'})
        self.assertNotEqual(timeStamp,User.objects.get(userName='Alice').lastupdatedtime)

        packageId = TaskPackage.objects.get(taskName='newTaskPackage3').id
        userId = User.objects.get(userName='Carol').id
        userToken = User.objects.get(userName='Carol').token
        timeStamp = User.objects.get(userName='Carol').lastupdatedtime
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,200)
        self.assertJSONEqual(res.content,TaskPackage.objects.get(taskName='newTaskPackage3').serialize()|{'code':0,'info':'Succeed'})
        self.assertNotEqual(timeStamp,User.objects.get(userName='Carol').lastupdatedtime)

        packageId = TaskPackage.objects.get(taskName='newTaskPackage2').id
        userId = User.objects.get(userName='Bob').id
        userToken = User.objects.get(userName='Bob').token
        timeStamp = User.objects.get(userName='Bob').lastupdatedtime
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,200)
        self.assertJSONEqual(res.content,TaskPackage.objects.get(taskName='newTaskPackage2').serialize()|{'code':0,'info':'Succeed'})
        self.assertNotEqual(timeStamp,User.objects.get(userName='Carol').lastupdatedtime)
    
    # No Privilege
    def test_get_package_info_no_privilege(self):
        packageId = TaskPackage.objects.get(taskName='newTaskPackage1').id
        userId = User.objects.get(userName='Bob').id
        userToken = User.objects.get(userName='Bob').token
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,401)
        self.assertEqual(res.json()['code'],2)

    # Package Not Found
    def test_get_package_info_package_not_found(self):
        packageId = TaskPackage.objects.count()+2
        userId = User.objects.get(userName='Alice').id
        userToken = User.objects.get(userName='Alice').token
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,404)
        self.assertEqual(res.json()['code'],1)
    
    # Wrong Type of param id
    def test_get_package_info_wrong_type_id(self):
        packageId = 'packageId'
        userId = User.objects.get(userName='Alice').id
        userToken = User.objects.get(userName='Alice').token
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
    
    # sender id and token doesn't match
    def test_get_package_info_id_token_not_matched(self):
        packageId = TaskPackage.objects.get(taskName='newTaskPackage1').id
        userId = User.objects.get(userName='Alice').id
        userToken = User.objects.get(userName='Bob').token
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,401)
        self.assertEqual(res.json()['code'],2)
    
    # wrong type of sender id
    def test_get_package_info_wrong_type_of_senderId(self):
        packageId = TaskPackage.objects.get(taskName='newTaskPackage1').id
        userId = 'idOfAlice'
        userToken = User.objects.get(userName='Alice').token
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
    # sender not found
    def test_get_package_info_sender_not_found(self):
        packageId = TaskPackage.objects.get(taskName='newTaskPackage1').id
        userId = User.objects.count()+2
        userToken = "".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH))
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,404)
        self.assertEqual(res.json()['code'],1)
    
    # wrong token length
    def test_get_package_info_wrong_token_length(self):
        packageId = TaskPackage.objects.get(taskName='newTaskPackage1').id
        userId = User.objects.get(userName='Alice').id
        userToken = "".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH+5))
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)

        userToken = "".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH-5))
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
    # special token
    def test_get_package_info_special_token(self):
        packageId = TaskPackage.objects.get(taskName='newTaskPackage1').id
        userId = User.objects.get(userName='Alice').id
        userToken = "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdab;DROP TABLE user_user;"
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,401)
        self.assertEqual(res.json()['code'],2)
        self.assertTrue(User.objects.exists())
    
    # without senderid
    def test_get_package_info_without_id(self):
        packageId = TaskPackage.objects.get(taskName='newTaskPackage1').id
        userId = None
        userToken = User.objects.get(userName='Alice').token
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
    # without token
    def test_get_package_info_without_token(self):
        packageId = TaskPackage.objects.get(taskName='newTaskPackage1').id
        userId = User.objects.get(userName='Alice').id
        userToken = None
        res = self.get_package_info(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
    
    # DELETE /task/package/{id}
    # correct respond
    def test_delete_package(self):
        # admin delete self
        targetPackage = TaskPackage.objects.get(taskName='newTaskPackage1')
        packageId = targetPackage.id
        userId = User.objects.get(userName='Alice').id
        userToken = User.objects.get(userName='Alice').token
        timeStamp = User.objects.get(userName='Alice').lastupdatedtime
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.json()['code'],0)
        self.assertNotEqual(timeStamp,User.objects.get(userName='Alice').lastupdatedtime)
        self.assertFalse(TaskPackage.objects.filter(taskName='newTaskPackage1').exists())
        targetPackage.save()
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage1').exists())
        # admin delete others
        targetPackage = TaskPackage.objects.get(taskName='newTaskPackage2')
        packageId = targetPackage.id
        userId = User.objects.get(userName='Alice').id
        userToken = User.objects.get(userName='Alice').token
        timeStamp = User.objects.get(userName='Alice').lastupdatedtime
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.json()['code'],0)
        self.assertNotEqual(timeStamp,User.objects.get(userName='Alice').lastupdatedtime)
        self.assertFalse(TaskPackage.objects.filter(taskName='newTaskPackage2').exists())
        targetPackage.save()
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage2').exists())
        # normal delete self
        targetPackage = TaskPackage.objects.get(taskName='newTaskPackage2')
        packageId = targetPackage.id
        userId = User.objects.get(userName='Bob').id
        userToken = User.objects.get(userName='Bob').token
        timeStamp = User.objects.get(userName='Bob').lastupdatedtime
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.json()['code'],0)
        self.assertNotEqual(timeStamp,User.objects.get(userName='Bob').lastupdatedtime)
        self.assertFalse(TaskPackage.objects.filter(taskName='newTaskPackage2').exists())
        targetPackage.save()
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage2').exists())
        # normal without upload privilege delete self
        targetPackage = TaskPackage.objects.get(taskName='newTaskPackage4')
        packageId = targetPackage.id
        userId = User.objects.get(userName='Carol').id
        userToken = User.objects.get(userName='Carol').token
        timeStamp = User.objects.get(userName='Carol').lastupdatedtime
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.json()['code'],0)
        self.assertNotEqual(timeStamp,User.objects.get(userName='Bob').lastupdatedtime)
        self.assertFalse(TaskPackage.objects.filter(taskName='newTaskPackage4').exists())
        targetPackage.save()
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage4').exists())
    
    # No privilege
    def test_delete_package_no_privilege(self):
        targetPackage = TaskPackage.objects.get(taskName='newTaskPackage1')
        packageId = targetPackage.id
        userId = User.objects.get(userName='Bob').id
        userToken = User.objects.get(userName='Bob').token
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,401)
        self.assertEqual(res.json()['code'],2)
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage1').exists())
    
    # Delete a distributed package
    def test_delete_package_distributed(self):
        targetPackage = TaskPackage.objects.get(taskName='newTaskPackage3')
        packageId = targetPackage.id
        userId = User.objects.get(userName='Alice').id
        userToken = User.objects.get(userName='Alice').token
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-1)
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage3').exists())
    
    # package does not exists
    def test_delete_package_not_exist(self):
        packageId = TaskPackage.objects.count()+2
        userId = User.objects.get(userName='Alice').id
        userToken = User.objects.get(userName='Alice').token
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,404)
        self.assertEqual(res.json()['code'],1)
    
    # package id is not int
    def test_delete_package_id_not_int(self):
        packageId = "packageId"
        userId = User.objects.get(userName='Alice').id
        userToken = User.objects.get(userName='Alice').token
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
    
    # user not found
    def test_delete_package_user_not_found(self):
        targetPackage = TaskPackage.objects.get(taskName='newTaskPackage1')
        packageId = targetPackage.id
        userId = User.objects.count()+2
        userToken = User.objects.get(userName='Alice').token
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,404)
        self.assertEqual(res.json()['code'],1)
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage1').exists())
    
    # id and token doesn't match
    def test_delete_package_id_token_mismatch(self):
        targetPackage = TaskPackage.objects.get(taskName='newTaskPackage1')
        packageId = targetPackage.id
        userId = User.objects.get(userName='Alice').id
        userToken = User.objects.get(userName='Bob').token
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,401)
        self.assertEqual(res.json()['code'],2)
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage1').exists())
    
    # id type error
    def test_delete_package_senderId_error_type(self):
        targetPackage = TaskPackage.objects.get(taskName='newTaskPackage1')
        packageId = targetPackage.id
        userId = "AliceId"
        userToken = User.objects.get(userName='Alice').token
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage1').exists())
    
    # token length error
    def test_delete_package_with_error_token_length(self):
        targetPackage = TaskPackage.objects.get(taskName='newTaskPackage1')
        packageId = targetPackage.id
        userId = User.objects.get(userName='Alice').id
        userToken = "".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH+5))
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage1').exists())

        userToken = "".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH-5))
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage1').exists())
        
    # without id or token
    def test_delete_package_without_id(self):
        targetPackage = TaskPackage.objects.get(taskName='newTaskPackage1')
        packageId = targetPackage.id
        userId = None
        userToken = "".join(random.choices(string.ascii_letters+string.digits,k=MAX_TOKEN_LENGTH+5))
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage1').exists())

        userId = User.objects.get(userName='Alice').id
        userToken = None
        res = self.delete_package(packageId,userId,userToken)
        self.assertEqual(res.status_code,400)
        self.assertEqual(res.json()['code'],-2)
        self.assertTrue(TaskPackage.objects.filter(taskName='newTaskPackage1').exists())

    # /task/template
    # POST
    # + normal case for create template
    def test_create_template1(self):
        object_list = [
            {"type": "text", "count": 1, },
            {"type": "image", "count": 2, },
            {"type": "textinput", "count": 3, },
            {"type": "singlechoice", "count": 4, },
            {"type": "imageinput", "count": 5, }
        ]
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(7)])
        sender = User.objects.filter(userName = "Alice").first()
        res = self.create_template(object_list, template_name, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 200)

    # + normal case for create template
    def test_create_template2(self):
        object_list = [
            {"type": "text", "count": 1, },
            {"type": "image", "count": 2, },
            {"type": "textinput", "count": 3, },
            {"type": "singlechoice", "count": 4, },
            {"type": "imageinput", "count": 5, }
        ]
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        description = ''
        sender = User.objects.filter(userName = "Bob").first()
        res = self.create_template(object_list, template_name, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 200)

    # + invalid type case for create template
    def test_invalid_type_case_create_template(self):
        object_list = [
            {
                "type": "string",
                "count": 5,
            }
        ]
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(7)])
        sender = User.objects.filter(userName = "Alice").first()
        res = self.create_template(object_list, template_name, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + invalid count case for create template
    def test_invalid_count_case1_create_template(self):
        object_list = [
            {
                "type": "text",
                "count": 0,
            }
        ]
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(7)])
        sender = User.objects.filter(userName = "Alice").first()
        res = self.create_template(object_list, template_name, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + invalid count case for create template
    def test_invalid_count_case2_create_template(self):
        object_list = [
            {
                "type": "text",
                "count": 9,
            }
        ]
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(7)])
        sender = User.objects.filter(userName = "Alice").first()
        res = self.create_template(object_list, template_name, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + invalid objectList length case for create template
    def test_invalid_name_length_case1_create_template(self):
        object_list = []
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(7)])
        sender = User.objects.filter(userName = "Alice").first()
        res = self.create_template(object_list, template_name, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + invalid objectList length case for create template
    def test_invalid_name_length_case2_create_template(self):
        object_list = [
            {"type": "text", "count": 1, },
            {"type": "text", "count": 1, },
            {"type": "text", "count": 1, },
            {"type": "text", "count": 1, },
            {"type": "text", "count": 1, },
            {"type": "text", "count": 1, },
            {"type": "text", "count": 1, },
            {"type": "text", "count": 1, },
            {"type": "text", "count": 1, }
        ]
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(7)])
        sender = User.objects.filter(userName = "Alice").first()
        res = self.create_template(object_list, template_name, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + invalid templateName length case for create template
    def test_invalid_templateName_length_case1_create_template(self):
        object_list = [
            {
                "type": "text",
                "count": 5,
            }
        ]
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(31)])
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(7)])
        sender = User.objects.filter(userName = "Alice").first()
        res = self.create_template(object_list, template_name, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + invalid templateName length case for create template
    def test_invalid_templateName_length_case2_create_template(self):
        object_list = [
            {
                "type": "text",
                "count": 5,
            }
        ]
        template_name = ''
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(7)])
        sender = User.objects.filter(userName = "Alice").first()
        res = self.create_template(object_list, template_name, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + invalid description length case for create template
    def test_invalid_description_length_case_create_template(self):
        object_list = [
            {
                "type": "text",
                "count": 5,
            }
        ]
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(MAX_TEMPLATE_DESCRIPTION_LENGTH+10)])
        sender = User.objects.filter(userName = "Alice").first()
        res = self.create_template(object_list, template_name, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + no permissions case for create template
    def test_no_permissions_case1_create_template(self):
        object_list = [
            {
                "type": "text",
                "count": 5,
            }
        ]
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(20)])
        sender = User.objects.filter(userName = "Carol").first()
        res = self.create_template(object_list, template_name, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + no permissions case for create template
    def test_no_permissions_case2_create_template(self):
        object_list = [
            {
                "type": "text",
                "count": 5,
            }
        ]
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(20)])
        sender = User.objects.filter(userName = "Alice").first()
        res = self.create_template(object_list, template_name, description, sender.id, ''.join([random.choice("abcdefg12345678 ") for _ in range(64)]))
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + no permissions case for create template
    def test_no_permissions_case3_create_template(self):
        object_list = [
            {
                "type": "text",
                "count": 5,
            }
        ]
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(20)])
        sender = User.objects.filter(userName = "Alice").first()
        res = self.create_template(object_list, template_name, description, 10, sender.token)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)

    # + missing params
    def test_missing_params_create_template(self):
        object_list = [
            {
                "type": "text",
                "count": 5,
            }
        ]
        template_name = ''.join([random.choice("abcdefg12345678") for _ in range(7)])
        description = ''.join([random.choice("abcdefg12345678 ") for _ in range(20)])
        sender = User.objects.filter(userName = "Alice").first()
        
        res = self.create_template(None, template_name, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
        
        res = self.create_template(object_list, None, description, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
        
        res = self.create_template(object_list, template_name, None, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
        
        res = self.create_template(object_list, template_name, description, None, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
        
        res = self.create_template(object_list, template_name, description, sender.id, None)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # /task/template
    # GET

    # + normal case
    def test_template_list_normal_case_template(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.template_list(sender.id, sender.token, 1, 50, 1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
    
    # + check the number of templates
    def test_template_list_check_number_template(self):
        sender = User.objects.filter(userName = "Alice").first()
        num = TaskTemplate.objects.count()
        res = self.template_list(sender.id, sender.token, 1, num, 0)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(len(res.json()['templateList']), num)

    # + query with large page id
    def test_template_list_large_page_id_template(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.template_list(sender.id, sender.token, 100000, 50, 1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)

    # + query with large count
    def test_template_list_large_count_template(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.template_list(sender.id, sender.token, 1, 50000, 1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)

    # + query with negative or zero page id
    def test_template_list_negative_page_id_template(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.template_list(sender.id, sender.token, -1, 50, 1)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

        sender = User.objects.filter(userName = "Alice").first()
        res = self.template_list(sender.id, sender.token, 0, 50, 1)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + query with negative or zero count
    def test_template_list_negative_count_template(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.template_list(sender.id, sender.token, 1, -50, 1)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

        sender = User.objects.filter(userName = "Alice").first()
        res = self.template_list(sender.id, sender.token, 1, 0, 1)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + query with wrong sender token
    def test_template_list_wrong_token_template(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.template_list(sender.id, ''.join([random.choice("abcdefg12345678 ") for _ in range(64)]), 1, 50, 1)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)
    
    # + query with wrong verification code
    def test_template_list_wrong_verification_code_template(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.template_list(sender.id, sender.token, 1, 50, -1)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

        sender = User.objects.filter(userName = "Alice").first()
        res = self.template_list(sender.id, sender.token, 1, 50, -1)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + query with 404 user
    def test_template_list_404_user_template(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.template_list(User.objects.count() + 1, sender.token, 1, 50, 1)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)

    # + query without sender token
    def test_template_list_no_token_template(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.template_list(sender.id, None, 1, 50, 1)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + method not allowed
    def test_template_list_method_not_allowed_template(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.client.put('/task/template', {'id': sender.id, 'token': sender.token, 'page': 1, 'size': 50, 'status': 1})
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
    
    # /task/template/{id}
    # GET
    # + normal case for get tasktemplate
    def test_get_tasktemplate(self):
        id = TaskTemplate.objects.get(templateName = "newTemplate").id
        sender = User.objects.filter(userName = "Alice").first()
        res = self.get_template(id, sender.id, sender.token)
        self.assertEqual(res.status_code, 200)

    # + no permission case for get tasktemplate
    def test_no_permission_get_tasktemplate(self):
        id = TaskTemplate.objects.get(templateName = "newTemplate").id
        sender = User.objects.filter(userName = "Alice").first()
        res = self.get_template(id, sender.id, ''.join([random.choice("abcdefg12345678 ") for _ in range(64)]))
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + unfound case for get tasktemplate
    def test_unfound_get_tasktemplate(self):
        id = 100000
        sender = User.objects.filter(userName = "Alice").first()
        res = self.get_template(id, sender.id, sender.token)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)

    # + unfound case for get tasktemplate
    def test_unfound_get_tasktemplate(self):
        id = TaskTemplate.objects.get(templateName = "newTemplate").id
        sender = User.objects.filter(userName = "Alice").first()
        res = self.get_template(id, 10, sender.token)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)

    # + unfound case for get tasktemplate
    def test_unfound_get_tasktemplate(self):
        id = TaskTemplate.objects.get(templateName = "newTemplate").id
        sender = User.objects.filter(userName = "Alice").first()
        res = self.get_template(id, 10, sender.token)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)

    # + missing params
    def test_missing_params_get_tasktemplate(self):
        id = TaskTemplate.objects.get(templateName = "newTemplate").id
        sender = User.objects.filter(userName = "Alice").first()
        
        res = self.get_template(None, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        
        res = self.get_template(id, None, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
        
        res = self.get_template(id, sender.id, None)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # /task/package/todo
    # GET
    
    # + normal case for obtain acceptable package
    def test_get_acceptable_package(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.obtain_acceptable_package(sender.id, sender.token)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)
    
    # + no permission case for obtain acceptable package
    def test_get_acceptable_package_no_permission(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.obtain_acceptable_package(sender.id, ''.join([random.choice("abcdefg12345678 ") for _ in range(64)]))
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + without sender id
    def test_get_acceptable_package_no_id(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.obtain_acceptable_package(None, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + bad method
    def test_get_acceptable_package_bad_method(self):
        sender = User.objects.filter(userName = "Alice").first()
        res = self.client.post('/task/package/todo', {'id': sender.id, 'token': sender.token, 'page': 1, 'size': 20})
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)

    # /task/package/accept/{id}
    # POST
    # + normal case for accept package
    def test_accept_package(self):
        sender = User.objects.filter(userName = "Dave").first()
        package = TaskPackage.objects.filter(taskName = "newTaskPackage5").first()
        accept = True

        res = self.accept_package(package.id, sender.id, sender.token, accept)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(User.objects.filter(userName = "Dave").first().currentTaskPackage, TaskPackage.objects.filter(taskName = "newTaskPackage5").first())

    # + normal case for refuse package
    def test_refuse_package(self):
        sender = User.objects.filter(userName = "Dave").first()
        package = TaskPackage.objects.filter(taskName = "newTaskPackage5").first()
        accept = False

        res = self.accept_package(package.id, sender.id, sender.token, accept)
        self.assertEqual(res.status_code, 200)

    # + no premission case1 for accept package
    def test_no_permission_accept_package1(self):
        sender = User.objects.filter(userName = "Dave").first()
        package = TaskPackage.objects.filter(taskName = "newTaskPackage5").first()
        accept = True

        res = self.accept_package(package.id, sender.id, ''.join([random.choice("abcdefg12345678 ") for _ in range(64)]), accept)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + no premission case2 for accept package
    def test_no_permission_accept_package2(self):
        sender = User.objects.filter(userName = "Francis").first()
        package = TaskPackage.objects.filter(taskName = "newTaskPackage5").first()
        accept = True

        res = self.accept_package(package.id, sender.id, sender.token, accept)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + assigned task case for accept package
    def test_assigned_task_accept_package(self):
        sender = User.objects.filter(userName = "Eve").first()
        package = TaskPackage.objects.filter(taskName = "newTaskPackage5").first()
        accept = True

        res = self.accept_package(package.id, sender.id, sender.token, accept)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + unuploaded case for accept package
    def test_unuploaded_accept_package(self):
        sender = User.objects.filter(userName = "Dave").first()
        package = TaskPackage.objects.filter(taskName = "newTaskPackage6").first()
        accept = True

        res = self.accept_package(package.id, sender.id, sender.token, accept)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -1)

    # + insufficient number of people case for accept package
    def test_insufficient_number_accept_package(self):
        sender = User.objects.filter(userName = "Dave").first()
        package = TaskPackage.objects.filter(taskName = "newTaskPackage7").first()
        accept = True

        res = self.accept_package(package.id, sender.id, sender.token, accept)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -1)

    # + unfound case1 for accept package
    def test_unfound_accept_package1(self):
        sender = User.objects.filter(userName = "Dave").first()
        package = TaskPackage.objects.filter(taskName = "newTaskPackage5").first()
        accept = True

        res = self.accept_package(package.id, 10, sender.token, accept)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)

    # + unfound case2 for accept package
    def test_unfound_accept_package2(self):
        sender = User.objects.filter(userName = "Dave").first()
        package = TaskPackage.objects.filter(taskName = "newTaskPackage5").first()
        accept = True

        res = self.accept_package(10, sender.id, sender.token, accept)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)

    # + missing params
    def test_missing_params_accept_package(self):
        sender = User.objects.filter(userName = "Dave").first()
        package = TaskPackage.objects.filter(taskName = "newTaskPackage5").first()
        accept = True

        res = self.accept_package(None, sender.id, sender.token, accept)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -1)

        res = self.accept_package(package.id, None, sender.token, accept)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

        res = self.accept_package(package.id, sender.id, None, accept)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

        res = self.accept_package(package.id, sender.id, sender.token, None)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + bad method
    def test_bad_method_accept_package(self):
        sender = User.objects.filter(userName = "Dave").first()
        package = TaskPackage.objects.filter(taskName = "newTaskPackage5").first()
        accept = True

        payload = {
            "senderId": sender.id,
            "senderToken": sender.token,
            "accept": accept
        }

        res = self.client.get(f'/task/package/accept/{id}', data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)

        res = self.client.put(f'/task/package/accept/{id}', data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)

        res = self.client.delete(f'/task/package/accept/{id}', data=payload, content_type='application/json')
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
    
    # /task/package/publish/{id}
    # POST

    # + normal case
    def test_publish_package(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage1").first()
        package.distributed = False
        package.save()
        sender = package.creator
        res = self.publish_package(TaskPackage.objects.get(taskName="newTaskPackage1").id, sender.id, sender.token)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)

    # + have no permission
    def test_publish_package_no_permission(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage1").first()
        sender = package.creator
        res = self.publish_package(TaskPackage.objects.get(taskName="newTaskPackage1").id, sender.id, ''.join([random.choice("abcdefg12345678 ") for _ in range(64)]))
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)
    
    # + without sender id
    def test_publish_package_no_id(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage1").first()
        sender = package.creator
        res = self.publish_package(TaskPackage.objects.get(taskName="newTaskPackage1").id, None, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + wrong id
    def test_publish_package_wrong_id(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage1").first()
        sender = package.creator
        res = self.publish_package(-1, sender.id, sender.token)
        self.assertEqual(res.status_code, 404)

    # + wrong sender id
    def test_publish_package_wrong_sender_id(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage1").first()
        sender = package.creator
        res = self.publish_package(TaskPackage.objects.get(taskName="newTaskPackage1").id, -1, sender.token)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)

    # + without sender token
    def test_publish_package_no_token(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage1").first()
        sender = package.creator
        res = self.publish_package(TaskPackage.objects.get(taskName="newTaskPackage1").id, sender.id, None)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)
    
    # + unfound package
    def test_publish_package_unfound(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage1").first()
        sender = package.creator
        res = self.publish_package(100000, sender.id, sender.token)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)
    
    # + not uploaded
    def test_publish_package_not_uploaded(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage2").first()
        sender = package.creator
        res = self.publish_package(TaskPackage.objects.get(taskName="newTaskPackage2").id, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -1)

    # + redistribution
    def test_publish_package_redistribution(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage1").first()
        package.distributed = True
        package.save()
        sender = package.creator
        res = self.publish_package(TaskPackage.objects.get(taskName="newTaskPackage1").id, sender.id, sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -1)

    # + bad method
    def test_publish_package_bad_method(self):
        package = TaskPackage.objects.filter(taskName="newTaskPackage1").first()
        sender = package.creator
        res = self.client.get(f'/task/package/publish/{TaskPackage.objects.get(taskName="newTaskPackage1").id}', {'id': sender.id, 'token': sender.token})
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
    
    # GET /task/package/list
    # + normal
    def test_get_package_list(self):
        sender = User.objects.get(userName='Alice')
        res = self.get_package_list(sender.id, sender.token, 1, 20)
        self.assertEqual(res.status_code, 200)
        packageIds ={u.id for u in list(TaskPackage.objects.all())}
        retIds = {u['id'] for u in json.loads(res.content.decode())['packageList']}
        self.assertSetEqual(packageIds,retIds)
    
    # + without permission
    def test_get_package_list_without_permission(self):
        sender = User.objects.get(userName='Bob')
        res = self.get_package_list(sender.id, sender.token, 1, 20)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'],2)
    
    # + with wrong token
    def test_get_package_list_with_wrong_token(self):
        sender = User.objects.get(userName='Alice')
        res = self.get_package_list(sender.id, "".join(random.choices(string.digits+string.ascii_letters,k=MAX_TOKEN_LENGTH)),1, 20)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'],2)
    
    # with count leq to 0
    def test_get_package_list_with_count_leq_0(self):
        sender = User.objects.get(userName='Alice')
        res = self.get_package_list(sender.id, sender.token, 1, 0)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'],-2)
    
    # with pageid leq 0
    def test_get_package_list_with_pageid_leq_0(self):
        sender = User.objects.get(userName='Alice')
        res = self.get_package_list(sender.id, sender.token, 0, 20)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'],-2)
    
    # wrong method
    def test_get_package_list_wrong_method(self):
        sender = User.objects.get(userName='Alice')
        res = self.client.post('/task/package/list',{
            "senderId":sender.id,
            "senderToken":sender.token,
            "pageId":1,
            "count":20,
        })
        self.assertEqual(res.status_code, 405)
    
    # GET /task/package/created
    # + normal
    def test_get_created_package_list(self):
        sender = User.objects.get(userName='Bob')
        res = self.get_created_package_list(sender.id,sender.token)
        self.assertEqual(res.status_code,200)
        packageIds ={u.id for u in list(TaskPackage.objects.filter(creator=sender,uploaded=False))}
        retIds = {u['id'] for u in json.loads(res.content.decode())['notUploaded']}
        self.assertSetEqual(packageIds,retIds)
        packageIds ={u.id for u in list(TaskPackage.objects.filter(creator=sender,uploaded=True,distributed=False))}
        retIds = {u['id'] for u in json.loads(res.content.decode())['notDistributed']}
        self.assertSetEqual(packageIds,retIds)
        packageIds ={u.id for u in list(TaskPackage.objects.filter(creator=sender,distributed=True))}
        retIds = {u['id'] for u in json.loads(res.content.decode())['Distributed']}
        self.assertSetEqual(packageIds,retIds)
    
    # + with wrong token
    def test_get_created_package_list_with_wrong_token(self):
        sender = User.objects.get(userName='Alice')
        res = self.get_created_package_list(sender.id, "".join(random.choices(string.digits+string.ascii_letters,k=MAX_TOKEN_LENGTH)))
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'],2)
    
    # + wrong method
    def test_get_created_package_list_wrong_method(self):
        sender = User.objects.get(userName='Alice')
        res = self.client.post('/task/package/created',{
            "senderId":sender.id,
            "senderToken":sender.token,
        })
        self.assertEqual(res.status_code, 405)

    # /task/{id}
    # GET

    # + normal case
    def test_get_task_info(self):
        package = TaskPackage.objects.get(taskName = "newTaskPackage1")
        package.creator = User.objects.get(userName="Bob")
        package.save()
        user = User.objects.get(userName="Bob")
        user.currentTaskPackage = TaskPackage.objects.get(taskName = "newTaskPackage1")
        user.deadline = get_timestamp() + 10000
        user.labelPrivilege=True
        user.save()

        sender = User.objects.filter(userName="Bob").first()
        taskStartId = Task.objects.first().id-1
        task = Task.objects.filter(id=taskStartId+1).first()
        res = self.get_task_info(id=task.id, senderId=sender.id, senderToken=sender.token)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['code'], 0)

    def test_get_task_info_with_uncomplete_task(self):
        package = TaskPackage.objects.get(taskName = "newTaskPackage1")
        package.creator = User.objects.get(userName="Alice")
        package.save()
        user = User.objects.get(userName="Alice")
        user.currentTaskPackage = TaskPackage.objects.get(taskName = "newTaskPackage1")
        user.deadline = get_timestamp() + 10000
        user.save()

        sender = User.objects.filter(userName="Alice").first()
        taskStartId = Task.objects.first().id-1
        task = Task.objects.filter(id=taskStartId+2).first()
        res = self.get_task_info(id=task.id, senderId=sender.id, senderToken=sender.token)
        self.assertEqual(res.status_code, 400)

    # + wrong id
    def test_get_task_info_wrong_id(self):
        sender = User.objects.filter(userName="Alice").first()
        taskStartId = Task.objects.first().id-1
        task = Task.objects.filter(id=taskStartId+1).first()
        res = self.get_task_info(id=None, senderId=sender.id, senderToken=sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -1)

    # + user with wrong token
    def test_get_task_info_no_permission(self):
        sender = User.objects.filter(userName="Alice").first()
        taskStartId = Task.objects.first().id-1
        task = Task.objects.filter(id=taskStartId+1).first()
        res = self.get_task_info(id=task.id, senderId=sender.id, senderToken=''.join([random.choice("abcdefg12345678 ") for _ in range(64)]))
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + wrong type of sender id
    def test_get_task_info_wrong_type_id(self):
        sender = User.objects.filter(userName="Alice").first()
        taskStartId = Task.objects.first().id-1
        task = Task.objects.filter(id=taskStartId+1).first()
        res = self.get_task_info(id=task.id, senderId='a', senderToken=sender.token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['code'], -2)

    # + unfound user
    def test_get_task_info_unfound_user(self):
        sender = User.objects.filter(userName="Alice").first()
        taskStartId = Task.objects.first().id-1
        task = Task.objects.filter(id=taskStartId+1).first()
        res = self.get_task_info(id=task.id, senderId=User.objects.count() + 1, senderToken=sender.token)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)

    # + user without permission
    def test_get_task_info_wrong_token(self):
        sender = User.objects.filter(userName="Carol").first()
        taskStartId = Task.objects.first().id-1
        task = Task.objects.filter(id=taskStartId+1).first()
        res = self.get_task_info(id=task.id, senderId=sender.id, senderToken=sender.token)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + not the current one
    def test_get_task_info_not_current(self):
        package = TaskPackage.objects.get(taskName = "newTaskPackage1")
        package.creator = User.objects.get(userName="Alice")
        package.save()
        user = User.objects.get(userName="Dave")
        user.currentTaskPackage = TaskPackage.objects.get(taskName = "newTaskPackage2")
        user.deadline = get_timestamp() + 10000
        user.save()

        sender = User.objects.filter(userName="Dave").first()
        taskStartId = Task.objects.first().id-1
        task = Task.objects.filter(id=taskStartId+1).first()
        res = self.get_task_info(id=task.id, senderId=sender.id, senderToken=sender.token)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + miss the deadline
    def test_get_task_info_miss_deadline(self):
        package = TaskPackage.objects.get(taskName = "newTaskPackage1")
        package.creator = User.objects.get(userName="Alice")
        package.save()
        user = User.objects.get(userName="Alice")
        user.currentTaskPackage = TaskPackage.objects.get(taskName = "newTaskPackage1")
        user.deadline = get_timestamp() - 10000
        user.save()

        sender = User.objects.filter(userName="Alice").first()
        taskStartId = Task.objects.first().id-1
        task = Task.objects.filter(id=taskStartId+1).first()
        res = self.get_task_info(id=task.id, senderId=sender.id, senderToken=sender.token)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json()['code'], 2)

    # + 404 for unfound task
    def test_get_task_info_unfound(self):
        sender = User.objects.filter(userName="Alice").first()
        taskStartId = Task.objects.first().id-1
        task = Task.objects.filter(id=taskStartId+1).first()
        res = self.get_task_info(id=Task.objects.count() + 1, senderId=sender.id, senderToken=sender.token)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()['code'], 1)

    # + unsupport method
    def test_get_task_info_unsupport_method(self):
        sender = User.objects.filter(userName="Alice").first()
        taskStartId = Task.objects.first().id-1
        task = Task.objects.filter(id=taskStartId+1).first()
        res = self.client.post('/task/1', {'id': sender.id, 'token': sender.token})
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()['code'], -3)
    
    # POST /task/package/upload/{id}
    # + normal
    def test_upload_file_without_answer(self):
        sender = User.objects.get(userName="Bob")
        package = TaskPackage.objects.get(taskName="newTaskPackage2")
        fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_upload_without_answer.zip"),"rb")
        file = SimpleUploadedFile("1.zip",fp.read(),"application/zip")
        res = self.client.post(f"/task/package/upload/{package.id}",
                               {
            "uploadFile":file,
            "senderId":sender.id,
            "senderToken":sender.token,
        },
        )
        self.assertEqual(res.status_code,200)
        package.refresh_from_db()
        self.assertTrue(package.uploaded)
    
    def test_upload_file_with_answer(self):
        sender = User.objects.get(userName="Bob")
        package = TaskPackage.objects.get(taskName="newTaskPackage2")
        fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_upload_with_answer.zip"),"rb")
        file = SimpleUploadedFile("1.zip",fp.read(),"application/zip")
        res = self.client.post(f"/task/package/upload/{package.id}",
                               {
            "uploadFile":file,
            "senderId":sender.id,
            "senderToken":sender.token,
        },
        )
        self.assertEqual(res.status_code,200)
        package.refresh_from_db()
        self.assertTrue(package.uploaded)
    
    def test_upload_file_lack_file(self):
        sender = User.objects.get(userName="Bob")
        package = TaskPackage.objects.get(taskName="newTaskPackage2")
        fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_upload_lack_file.zip"),"rb")
        file = SimpleUploadedFile("1.zip",fp.read(),"application/zip")
        res = self.client.post(f"/task/package/upload/{package.id}",
                               {
            "uploadFile":file,
            "senderId":sender.id,
            "senderToken":sender.token,
        },
        )
        self.assertEqual(res.status_code,400)
        package.refresh_from_db()
        self.assertFalse(package.uploaded)
    
    def test_upload_file_not_a_zip(self):
        sender = User.objects.get(userName="Bob")
        package = TaskPackage.objects.get(taskName="newTaskPackage2")
        fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_upload_not_a_zip.7z"),"rb")
        file = SimpleUploadedFile("1.zip",fp.read(),"application/zip")
        res = self.client.post(f"/task/package/upload/{package.id}",
                               {
            "uploadFile":file,
            "senderId":sender.id,
            "senderToken":sender.token,
        },
        )
        self.assertEqual(res.status_code,400)
        package.refresh_from_db()
        self.assertFalse(package.uploaded)
    
    def test_upload_file_redundant_file(self):
        sender = User.objects.get(userName="Bob")
        package = TaskPackage.objects.get(taskName="newTaskPackage2")
        fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_upload_redundant_file.zip"),"rb")
        file = SimpleUploadedFile("1.zip",fp.read(),"application/zip")
        res = self.client.post(f"/task/package/upload/{package.id}",
                               {
            "uploadFile":file,
            "senderId":sender.id,
            "senderToken":sender.token,
        },
        )
        self.assertEqual(res.status_code,400)
        package.refresh_from_db()
        self.assertFalse(package.uploaded)
    
    def test_upload_wrong_file_format(self):
        sender = User.objects.get(userName="Bob")
        package = TaskPackage.objects.get(taskName="newTaskPackage2")
        fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_upload_wrong_file_format.zip"),"rb")
        file = SimpleUploadedFile("1.zip",fp.read(),"application/zip")
        res = self.client.post(f"/task/package/upload/{package.id}",
                               {
            "uploadFile":file,
            "senderId":sender.id,
            "senderToken":sender.token,
        },
        )
        self.assertEqual(res.status_code,400)
        package.refresh_from_db()
        self.assertFalse(package.uploaded)
    
    def test_upload_wrong_folder_name(self):
        sender = User.objects.get(userName="Bob")
        package = TaskPackage.objects.get(taskName="newTaskPackage2")
        fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_upload_wrong_folder_name.zip"),"rb")
        file = SimpleUploadedFile("1.zip",fp.read(),"application/zip")
        res = self.client.post(f"/task/package/upload/{package.id}",
                               {
            "uploadFile":file,
            "senderId":sender.id,
            "senderToken":sender.token,
        },
        )
        self.assertEqual(res.status_code,400)
        package.refresh_from_db()
        self.assertFalse(package.uploaded)
    
    def test_upload_not_sender(self):
        sender = User.objects.get(userName="Carol")
        package = TaskPackage.objects.get(taskName="newTaskPackage2")
        fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_upload_without_answer.zip"),"rb")
        file = SimpleUploadedFile("1.zip",fp.read(),"application/zip")
        res = self.client.post(f"/task/package/upload/{package.id}",
                               {
            "uploadFile":file,
            "senderId":sender.id,
            "senderToken":sender.token,
        },
        )
        self.assertEqual(res.status_code,401)
        package.refresh_from_db()
        self.assertFalse(package.uploaded)
    
    def test_upload_with_all_types(self):
        sender = User.objects.get(userName="Alice")
        package = TaskPackage.objects.get(taskName="newTaskPackage8")
        fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_upload_with_all_types.zip"),"rb")
        file = SimpleUploadedFile("1.zip",fp.read(),"application/zip")
        res = self.client.post(f"/task/package/upload/{package.id}",
                               {
            "uploadFile":file,
            "senderId":sender.id,
            "senderToken":sender.token,
        },
        )
        self.assertEqual(res.status_code,200)
        package.refresh_from_db()
        self.assertTrue(package.uploaded)
    
    # GET /task/package/completed/{id}
    # + normal case
    def test_get_completed_user_list(self):
        sender = User.objects.get(userName="Bob")
        senderId = sender.id
        senderToken = sender.token
        package = TaskPackage.objects.get(taskName="newTaskPackage2")
        package.completedUser.add(User.objects.get(userName="Carol"))
        package.completedUser.add(User.objects.get(userName="Alice"))
        res = self.get_completed_user_list(package.id,senderId,senderToken)
        self.assertEqual(res.status_code,200)
        stdUsers = {u.id for u in list(package.completedUser.all())}
        testUsers = {u["id"] for u in res.json()["userList"]}
        self.assertSetEqual(stdUsers,testUsers)

    # - no such package
    def test_get_completed_user_list_no_package(self):
        sender = User.objects.get(userName="Bob")
        senderId = sender.id
        senderToken = sender.token
        res = self.get_completed_user_list(TaskPackage.objects.count()+5,senderId,senderToken)
        self.assertEqual(res.status_code,404)
    
    # - no privilege
    def test_get_completed_user_list_no_privilege(self):
        sender = User.objects.get(userName="Bob")
        senderId = sender.id
        senderToken = sender.token
        package = TaskPackage.objects.get(taskName="newTaskPackage1")
        package.completedUser.add(User.objects.get(userName="Carol"))
        package.completedUser.add(User.objects.get(userName="Bob"))
        res = self.get_completed_user_list(package.id,senderId,senderToken)
        self.assertEqual(res.status_code,401)

    # PUT /task/answer/{id}

    # + normal case
    def test_put_answer_normal(self):
        sender = User.objects.get(userName="Alice")
        senderId = sender.id
        senderToken = sender.token
        res = self.submit_answer(id=Task.objects.first().id, answers=[[],[],[{"data":"123"}]], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code,200)

    def test_put_answer_without_upload_privilege(self):
        sender = User.objects.get(userName="Bob")
        senderId = sender.id
        senderToken = sender.token
        res = self.submit_answer(id=Task.objects.first().id, answers=[[],[],[{"data":"123"}]], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code, 401)

    def test_put_answer_with_wrong_format_1(self):
        sender = User.objects.get(userName="Alice")
        senderId = sender.id
        senderToken = sender.token
        res = self.submit_answer(id=Task.objects.first().id, answers=[[],[],[]], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code, 400)

    def test_put_answer_with_wrong_format_2(self):
        sender = User.objects.get(userName="Alice")
        senderId = sender.id
        senderToken = sender.token
        res = self.submit_answer(id=Task.objects.first().id, answers=[[],[],["123"]], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code, 400)
    
    def test_put_answer_with_wrong_format_3(self):
        sender = User.objects.get(userName="Alice")
        senderId = sender.id
        senderToken = sender.token
        res = self.submit_answer(id=Task.objects.first().id, answers=[[],[{"data": "123"}],[]], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code, 400)

    def test_put_answer_with_wrong_format_4(self):
        sender = User.objects.get(userName="Alice")
        senderId = sender.id
        senderToken = sender.token
        res = self.submit_answer(id=Task.objects.first().id, answers=[[],[],{"data": "123"}], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code, 400)

    def test_put_answer_with_wrong_format_5(self):
        sender = User.objects.get(userName="Alice")
        senderId = sender.id
        senderToken = sender.token
        res = self.submit_answer(id=Task.objects.first().id, answers=[[],[{"data": "123"}]], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code, 400)

    def test_put_answer_with_wrong_type(self):
        sender = User.objects.get(userName="Alice")
        senderId = sender.id
        senderToken = sender.token
        res = self.submit_answer(id=Task.objects.first().id, answers=[[],[],[["data"]]], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code, 400)
    
    def test_put_answer_with_redundant_information_1(self):
        sender = User.objects.get(userName="Alice")
        senderId = sender.id
        senderToken = sender.token
        res = self.submit_answer(id=Task.objects.first().id, answers=[[],[],[{"data": "123", "id": 1}]], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code, 400)

    def test_put_answer_with_redundant_information_2(self):
        sender = User.objects.get(userName="Alice")
        senderId = sender.id
        senderToken = sender.token
        res = self.submit_answer(id=Task.objects.first().id, answers=[[],[{"data": "123"}],[{"data": "123"}]], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code, 400)

    def test_put_answer_with_not_started_task(self):
        newTask=Task(
            packageBelonging = TaskPackage.objects.get(taskName = "newTaskPackage2"),
        )
        newTask.save()
        sender = User.objects.get(userName="Alice")
        senderId = sender.id
        senderToken = sender.token
        res = self.submit_answer(id=newTask.id, answers=[[],[],[{"data":"123"}]], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code, 400)

    def test_put_answer_with_finished_task(self):
        sender = User.objects.get(userName="Alice")
        senderId = sender.id
        senderToken = sender.token
        res = self.submit_answer(id=Task.objects.first().id, answers=[[],[],[{"data":"123"}]], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code, 200)
        res = self.submit_answer(id=Task.objects.first().id, answers=[[],[],[{"data":"123"}]], senderId=senderId, senderToken=senderToken)
        self.assertEqual(res.status_code, 400)

    def test_put_answer_with_wrong_method(self):
        sender = User.objects.get(userName="Alice")
        senderId = sender.id
        senderToken = sender.token
        answers=[[],[],[{"data":"123"}]]
        payload = {
            "answers": answers,
            "senderId": senderId,
            "senderToken": senderToken,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        id=Task.objects.first().id

        res = self.client.get(f"/task/answer/{id}", data=payload, content_type="application/json")
        self.assertEqual(res.status_code, 405)

        res = self.client.post(f"/task/answer/{id}", data=payload, content_type="application/json")
        self.assertEqual(res.status_code, 405)
        
        res = self.client.delete(f"/task/answer/{id}", data=payload, content_type="application/json")
        self.assertEqual(res.status_code, 405)
        
    # GET /task/package/manualcheck/{id}
    # + normal case 1
    def test_get_manual_verify_info_all(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        mode = "all"
        submitterId = User.objects.filter(userName = "Dave").first().id
        res = self.get_manual_check_info(id, senderId, senderToken, mode, submitterId)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["tasks"]), 5)

    # + normal case 2
    def test_get_manual_verify_info_all2(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage3").first().id
        sender = User.objects.filter(userName = "Bob").first()
        senderId = sender.id
        senderToken = sender.token
        mode = "all"
        submitterId = User.objects.filter(userName = "Dave").first().id
        res = self.get_manual_check_info(id, senderId, senderToken, mode, submitterId)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["tasks"]), 3)

    # + normal case 3
    def test_get_manual_verify_info_sampling(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        mode = "sampling"
        submitterId = User.objects.filter(userName = "Dave").first().id
        res = self.get_manual_check_info(id, senderId, senderToken, mode, submitterId)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["tasks"]), 4)

    # + normal case 4
    def test_get_manual_verify_info_sampling2(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage3").first().id
        sender = User.objects.filter(userName = "Bob").first()
        senderId = sender.id
        senderToken = sender.token
        mode = "sampling"
        submitterId = User.objects.filter(userName = "Dave").first().id
        res = self.get_manual_check_info(id, senderId, senderToken, mode, submitterId)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["tasks"]), 3)
    
    # + too much problems
    # def test_get_manual_verify_info_too_much_problems(self):
    #     id = TaskPackage.objects.filter(taskName = "newTaskPackage2").first().id
    #     sender = User.objects.filter(userName = "Bob").first()
    #     senderId = sender.id
    #     senderToken = sender.token
    #     mode = "all"
    #     submitterId = User.objects.filter(userName = "Dave").first().id
    #     res = self.get_manual_check_info(id, senderId, senderToken, mode, submitterId)
    #     self.assertEqual(res.status_code, 400)

    # + invalid mode
    def test_get_manual_verify_info_invalid_mode(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        mode = "all2"
        submitterId = User.objects.filter(userName = "Dave").first().id
        res = self.get_manual_check_info(id, senderId, senderToken, mode, submitterId)
        self.assertEqual(res.status_code, 400)

    # + no permissions
    def test_get_manual_verify_info_no_permissons(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = User.objects.filter(userName = "Bob").first().id
        senderToken = sender.token
        mode = "all"
        submitterId = User.objects.filter(userName = "Dave").first().id
        res = self.get_manual_check_info(id, senderId, senderToken, mode, submitterId)
        self.assertEqual(res.status_code, 401)

    # + no permissions
    def test_get_manual_verify_info_no_permissons2(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Bob").first()
        senderId = sender.id
        senderToken = sender.token
        mode = "all"
        submitterId = User.objects.filter(userName = "Dave").first().id
        res = self.get_manual_check_info(id, senderId, senderToken, mode, submitterId)
        self.assertEqual(res.status_code, 401)

    # + no permissions
    def test_get_manual_verify_info_no_permissons3(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = "abcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefgh"
        mode = "all"
        submitterId = User.objects.filter(userName = "Dave").first().id
        res = self.get_manual_check_info(id, senderId, senderToken, mode, submitterId)
        self.assertEqual(res.status_code, 401)

    # + not found
    def test_get_manual_verify_info_not_found(self):
        id = 100000
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        mode = "all"
        submitterId = User.objects.filter(userName = "Dave").first().id
        res = self.get_manual_check_info(id, senderId, senderToken, mode, submitterId)
        self.assertEqual(res.status_code, 404)

    # + not found
    def test_get_manual_verify_info_not_found2(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        mode = "all"
        submitterId = 100000
        res = self.get_manual_check_info(id, senderId, senderToken, mode, submitterId)
        self.assertEqual(res.status_code, 404)

    # + not in the validation list
    def test_get_manual_verify_info_not_in_the_validation_list(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        mode = "all"
        submitterId = User.objects.filter(userName = "Eve").first().id
        res = self.get_manual_check_info(id, senderId, senderToken, mode, submitterId)
        self.assertEqual(res.status_code, 400)

    # PUT /task/package/manualcheck/{id}
    # + normal case
    def test_put_manual_verify_info(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        submitterId = User.objects.filter(userName = "Dave").first().id
        acceptRate = 0.75
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["accepted"])

    # + normal case
    def test_put_manual_verify_info2(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        submitterId = User.objects.filter(userName = "Dave").first().id
        acceptRate = 1
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["accepted"])

    # + normal case
    def test_put_manual_verify_info3(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        submitterId = User.objects.filter(userName = "Dave").first().id
        acceptRate = 0.74
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()["accepted"])

    # + normal case
    def test_put_manual_verify_info4(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        submitterId = User.objects.filter(userName = "Dave").first().id
        acceptRate = 0
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()["accepted"])

    # + invalid acceptRate
    def test_put_manual_verify_info_invalid_acceptRate(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        submitterId = User.objects.filter(userName = "Dave").first().id
        acceptRate = -0.2
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 400)

    # + invalid acceptRate
    def test_put_manual_verify_info_invalid_acceptRate2(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        submitterId = User.objects.filter(userName = "Dave").first().id
        acceptRate = 1.2
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 400)

    # + no permissions
    def test_put_manual_verify_info_no_permissons(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = User.objects.filter(userName = "Bob").first().id
        senderToken = sender.token
        submitterId = User.objects.filter(userName = "Dave").first().id
        acceptRate = 0.8
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 401)

    # + no permissions
    def test_put_manual_verify_info_no_permissons2(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Bob").first()
        senderId = sender.id
        senderToken = sender.token
        submitterId = User.objects.filter(userName = "Dave").first().id
        acceptRate = 0.8
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 401)

    # + no permissions
    def test_put_manual_verify_info_no_permissons3(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = "abcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefghabcdefgh"
        submitterId = User.objects.filter(userName = "Dave").first().id
        acceptRate = 0.8
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 401)

    # + not found
    def test_put_manual_verify_info_not_found(self):
        id = 10
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        submitterId = User.objects.filter(userName = "Dave").first().id
        acceptRate = 0.8
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 404)

    # + not found
    def test_put_manual_verify_info_not_found2(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        submitterId = 100000
        acceptRate = 0.8
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 404)

    # + not in the validation list
    def test_put_manual_verify_info_not_in_the_validation_list(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        submitterId = User.objects.filter(userName = "Eve").first().id
        acceptRate = 0.8
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 400)

    # + bad params
    def test_put_manual_verify_info_bad_params(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        submitterId = User.objects.filter(userName = "Dave").first().id
        acceptRate = 0.75
        res = self.put_manual_check_info(None, senderId, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 400)
        res = self.put_manual_check_info(id, None, senderToken, submitterId, acceptRate)
        self.assertEqual(res.status_code, 400)
        res = self.put_manual_check_info(id, senderId, None, submitterId, acceptRate)
        self.assertEqual(res.status_code, 400)
        res = self.put_manual_check_info(id, senderId, senderToken, None, acceptRate)
        self.assertEqual(res.status_code, 400)
        res = self.put_manual_check_info(id, senderId, senderToken, submitterId, None)
        self.assertEqual(res.status_code, 400)
    
    # + bad methods
    
    def test_put_manual_verify_info_bad_params(self):
        id = TaskPackage.objects.filter(taskName = "newTaskPackage1").first().id
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        submitterId = User.objects.filter(userName = "Dave").first().id
        acceptRate = 0.75
        
        payload = {
            "senderId": senderId,
            "senderToken": senderToken,
            "submitterId": submitterId,
            "acceptRate": acceptRate,
        }
        payload = { k:v for k,v in payload.items() if v is not None}
        
        res = self.client.post(f"/task/package/manualcheck/{id}", data=payload, content_type="application/json")
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()["code"], -3)
        
        res = self.client.delete(f"/task/package/manualcheck/{id}", data=payload, content_type="application/json")
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()["code"], -3)

    # PUT /task/package/autocheck/{id}
    # + normal case
    def test_put_auto_verify_info_with_no_user(self):
        package = TaskPackage.objects.filter(taskName = "TP1").first()
        package.distributed = True
        package.save()
        newTask = Task(
            packageBelonging = package,
            hasStandardAnswer = True,
            standardAnswer = [[],[{"data": "123"}],[]],
        )
        newTask.save()
        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        res = self.auto_check(package.id, senderId, senderToken)
        self.assertEqual(res.status_code, 200)
    
    def test_put_auto_verify_info_with_user(self):
        package = TaskPackage.objects.filter(taskName = "TP1").first()
        package.distributed = True
        package.save()

        package.completedUser.add(User.objects.filter(userName = "Bob").first())
        package.save()
        newTask1 = Task(
            packageBelonging = package,
            hasStandardAnswer = True,
            standardAnswer = [[],[{"data": "123"}],[]],
        )
        newTask1.save()
        newTask2 = Task(
            packageBelonging = package,
        )
        newTask2.save()
        TaskAnswer.objects.create(
            submitter = User.objects.filter(userName = "Bob").first(),
            task = newTask1,
            payload = [[],[{"data": "123"}],[]],
            finished = True,
        )
        task = newTask2
        task.answers.add(User.objects.filter(userName = "Bob").first())
        task.save()

        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        res = self.auto_check(package.id, senderId, senderToken)
        self.assertEqual(res.status_code, 200)
    
    def test_put_auto_verify_info_without_permission(self):
        package = TaskPackage.objects.filter(taskName = "TP1").first()
        package.distributed = True
        package.save()

        package.completedUser.add(User.objects.filter(userName = "Bob").first())
        package.save()
        newTask1 = Task(
            packageBelonging = package,
            hasStandardAnswer = True,
            standardAnswer = [[],[{"data": "123"}],[]],
        )
        newTask1.save()
        newTask2 = Task(
            packageBelonging = package,
        )
        newTask2.save()
        TaskAnswer.objects.create(
            submitter = User.objects.filter(userName = "Bob").first(),
            task = newTask1,
            payload = [[],[{"data": "123"}],[]],
            finished = True,
        )
        task = newTask2
        task.answers.add(User.objects.filter(userName = "Bob").first())
        task.save()

        sender = User.objects.filter(userName = "Bob").first()
        senderId = sender.id
        senderToken = sender.token
        res = self.auto_check(package.id, senderId, senderToken)
        self.assertEqual(res.status_code, 401)
    
    def test_put_auto_verify_info_without_answer(self):
        package = TaskPackage.objects.filter(taskName = "TP1").first()
        package.distributed = True
        package.save()

        package.completedUser.add(User.objects.filter(userName = "Bob").first())
        package.save()
        newTask1=Task(
            packageBelonging = package,
            hasStandardAnswer = True,
            standardAnswer = [[],[{"data": "123"}],[]],
        )
        newTask1.save()
        newTask2=Task(
            packageBelonging = package,
        )
        newTask2.save()

        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        res = self.auto_check(package.id, senderId, senderToken)
        self.assertEqual(res.status_code, 500)

    def test_put_auto_verify_info_with_no_standard_answer(self):
        package = TaskPackage.objects.filter(taskName = "TP1").first()
        package.distributed = True
        package.save()

        package.completedUser.add(User.objects.filter(userName = "Bob").first())
        package.save()
        newTask1=Task(
            packageBelonging = package,
            hasStandardAnswer = False,
        )
        newTask1.save()
        newTask2=Task(
            packageBelonging = package,
        )
        newTask2.save()
        TaskAnswer.objects.create(
            submitter = User.objects.filter(userName = "Bob").first(),
            task = newTask1,
            payload = [[],[{"data": "123"}],[]],
            finished = True,
        )
        task = newTask2
        task.answers.add(User.objects.filter(userName = "Bob").first())
        task.save()

        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        res = self.auto_check(package.id, senderId, senderToken)
        self.assertEqual(res.status_code, 400)

    def test_put_auto_verify_info_with_wrong_method(self):
        package = TaskPackage.objects.filter(taskName = "TP1").first()
        package.distributed = True
        package.save()

        package.completedUser.add(User.objects.filter(userName = "Bob").first())
        package.save()
        newTask1 = Task(
            packageBelonging = package,
            hasStandardAnswer = True,
            standardAnswer = [[],[{"data": "123"}],[]],
        )
        newTask1.save()
        newTask2 = Task(
            packageBelonging = package,
        )
        newTask2.save()
        TaskAnswer.objects.create(
            submitter = User.objects.filter(userName = "Bob").first(),
            task = newTask1,
            payload = [[],[{"data": "123"}],[]],
            finished = True,
        )
        task = newTask2
        task.answers.add(User.objects.filter(userName = "Bob").first())
        task.save()

        sender = User.objects.filter(userName = "Alice").first()
        senderId = sender.id
        senderToken = sender.token
        res = self.client.get(f"/task/package/autocheck/{package.id}", data={
            "senderId": senderId,
            "senderToken": senderToken,
        })
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()["code"], -3)
    
    # /task/excel
    # POST

    # def test_post_excel(self):
    #     # sender = User.objects.get(userName="Bob")
    #     # answers = TaskAnswer.objects.filter(submitter=sender)
    #     # for answer in answers:
    #     #     template = answer.task.packageBelonging.template
    #     #     print(template.objectList)
    #     # return
    #     sender = User.objects.get(userName = "Alice")
    #     fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_post_excel.xlsx"),"rb")
    #     file = SimpleUploadedFile("1.xlsx",fp.read(),"application/vnd.ms-excel")
    #     res = self.client.post(f"/task/excel",
    #                            {
    #         "uploadFile":file,
    #         "senderId":sender.id,
    #         "senderToken":sender.token,
    #     },
    #     )
    #     print(res.content)
    #     self.assertEqual(res.status_code,200)

    # def test_post_excel_with_wrong_format_1(self):
    #     sender = User.objects.get(userName = "Alice")
    #     fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_post_excel_with_wrong_format_1.xlsx"),"rb")
    #     file = SimpleUploadedFile("1.xlsx",fp.read(),"application/vnd.ms-excel")
    #     res = self.client.post(f"/task/excel",
    #                            {
    #         "uploadFile":file,
    #         "senderId":sender.id,
    #         "senderToken":sender.token,
    #     },
    #     )
    #     self.assertEqual(res.status_code,400)

    # def test_post_excel_with_wrong_format_2(self):
    #     sender = User.objects.get(userName = "Alice")
    #     fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_post_excel_with_wrong_format_2.xlsx"),"rb")
    #     file = SimpleUploadedFile("1.xlsx",fp.read(),"application/vnd.ms-excel")
    #     res = self.client.post(f"/task/excel",
    #                            {
    #         "uploadFile":file,
    #         "senderId":sender.id,
    #         "senderToken":sender.token,
    #     },
    #     )
    #     self.assertEqual(res.status_code,400)

    # def test_post_excel_with_complex_answers(self):
    #     sender = User.objects.get(userName = "Alice")
    #     answer = TaskAnswer.objects.filter(submitter = sender).first()
    #     template = answer.task.packageBelonging.template
    #     template.objectList = [
    #         {"type":"text","count":1},
    #         {"type":"image","count":2},
    #         {"type":"textinput","count":1},
    #         {"type":"singlechoice","count":2},
    #         {"type":"multiplechoice","count":2},
    #         ]
    #     template.save()
    #     fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_post_excel_with_complex_answers.xlsx"),"rb")
    #     file = SimpleUploadedFile("1.xlsx",fp.read(),"application/vnd.ms-excel")
    #     res = self.client.post(f"/task/excel",
    #                            {
    #         "uploadFile":file,
    #         "senderId":sender.id,
    #         "senderToken":sender.token,
    #     },
    #     )
    #     self.assertEqual(res.status_code,200)

    # def test_post_excel_with_bad_method(self):
    #     sender = User.objects.get(userName = "Alice")
    #     fp = open(os.path.join(chatHLB_backend.settings.BASE_DIR,"test_files","test_post_excel.xlsx"),"rb")
    #     file = SimpleUploadedFile("1.xlsx",fp.read(),"application/vnd.ms-excel")
    #     res = self.client.get(f"/task/excel",
    #                            {
    #         "uploadFile":file,
    #         "senderId":sender.id,
    #         "senderToken":sender.token,
    #     },
    #     )
    #     self.assertEqual(res.status_code,405)