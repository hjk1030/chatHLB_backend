from django.db import models
from utils.utils_time import get_timestamp
from utils.utils_require import MAX_TASKNAME_LENGTH,MAX_TEMPLATENAME_LENGTH,MAX_TASKDESCRIPTION_LENGTH,MAX_TEMPLATE_DESCRIPTION_LENGTH
from utils.utils_require import MAX_TAG_LENGTH,MAX_TAGS_COUNT

# Create your models here.

class TaskPackage(models.Model):
    id = models.BigAutoField(primary_key=True)
    creator = models.ForeignKey(to='user.User',related_name="createdPackage",on_delete=models.CASCADE)
    template = models.ForeignKey(to='TaskTemplate',on_delete=models.CASCADE)
    distribution = models.IntegerField(default=0)
    maxDistributedUser = models.IntegerField(default=1)
    subtaskLimit = models.FloatField(default=120)
    score = models.IntegerField(default=0)
    uploaded = models.BooleanField(default=False)
    uploadedFileUrl = models.CharField(max_length=64,default="")
    distributed = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    deadline = models.FloatField(default=get_timestamp)
    taskName = models.CharField(max_length=MAX_TASKNAME_LENGTH,default="newTask")
    tags = models.JSONField(default=list)
    description = models.CharField(max_length=MAX_TASKDESCRIPTION_LENGTH,default="")
    completedUser = models.ManyToManyField(to='user.User',related_name='completedPackages',blank=True)
    rejectedUser = models.ManyToManyField(to='user.User',related_name='rejectedPackages',blank=True)
    verifiedUser = models.ManyToManyField(to='user.User',related_name='verifiedPackages',blank=True)
    proxied = models.BooleanField(default=False)
    intermediary = models.ForeignKey(to='user.User',related_name="intermediaryPackage",null=True,blank=True,on_delete=models.CASCADE)
    availbleCount = models.IntegerField(default=0)
    createTime = models.FloatField(default=0)
    tagsField = models.ManyToManyField(to='task.Tags',related_name='packagesWithTag',blank=True)
    completedCount = models.IntegerField(default=0)
    taskCount = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["taskName"]),
        ]
    
    def serialize(self):
        return {
            "id": self.id,
            "creator": {
                "id": self.creator.id,
                "userName": self.creator.userName
            },
            "distribution": self.distribution,
            "maxDistributedUser": self.maxDistributedUser,
            "subtaskLimit": self.subtaskLimit,
            "score": self.score,
            "uploaded":self.uploaded,
            "distributed": self.distributed,
            "verified": self.verified,
            "deadline": self.deadline,
            "taskName": self.taskName,
            "template":{
                "id":self.template.id,
                "templateName":self.template.templateName,
                "description":self.template.description,
            },
            "tags":self.tags,
            "description":self.description,
            "createTime":self.createTime,
            "proxied":self.proxied,
        }

class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    packageBelonging = models.ForeignKey(to=TaskPackage,on_delete=models.CASCADE)
    answers = models.ManyToManyField(to='user.User',through='task.TaskAnswer',related_name="answers",blank=True)
    data = models.JSONField(default=list)
    standardAnswer = models.JSONField(default=list)
    hasStandardAnswer = models.BooleanField(default=False)
    problemId = models.IntegerField(default=0)

    class Meta:
        indexes = [
        ]
    
    def serialize(self):
        return {
            'id':self.id,
            'data': self.data,
            'problemId': self.problemId,
            'packageId': self.packageBelonging.id,
            'templateId': self.packageBelonging.template.id,
        }

class TaskTemplate(models.Model):
    id = models.BigAutoField(primary_key=True)
    objectList = models.JSONField(default=list)
    creator = models.ForeignKey(to='user.User',on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    templateName = models.CharField(max_length=MAX_TEMPLATENAME_LENGTH,default="newTemplate")
    description = models.CharField(max_length=MAX_TEMPLATE_DESCRIPTION_LENGTH,default="")

    class Meta:
        indexes = [
            models.Index(fields=["id"])
            
        ]
        ordering = ['id']

    def serialize(self):
        return {
                "id": self.id,
                "objectList": self.objectList,
                "creator":{
                    "id": self.creator.id,
                    "userName": self.creator.userName,
                },
                "verified": self.verified,
                "templateName": self.templateName,
                "description": self.description,
            }

class TaskAnswer(models.Model):
    id = models.BigAutoField(primary_key=True)
    submitter = models.ForeignKey(to='user.User',on_delete=models.CASCADE)
    task = models.ForeignKey(to=Task,on_delete=models.CASCADE)
    payload = models.JSONField(default=list)
    finished = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    startTime = models.FloatField(default=0)

    class Meta:
        indexes = [
        ]
    
    def serialize(self):
        return {
            "taskInfo":self.task.serialize(),
            "answer":self.payload,
            "taskId":self.id,
        }

def get_upload_directory(instance,filename):
    return "taskData/{0}-{1}".format(instance.id,filename)
class TaskData(models.Model):
    id = models.BigAutoField(primary_key=True)
    config = models.JSONField(default=dict)
    payload = models.FileField(upload_to=get_upload_directory)
    class Meta:
        indexes = [
        ]

class Image(models.Model):
    image = models.ImageField()

class Tags(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=(MAX_TAG_LENGTH+1)*MAX_TAGS_COUNT,default='',unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['name'])
        ]