from django.db import models

# Create your models here.

class Advertise(models.Model):
    id = models.BigAutoField(primary_key=True)
    creator = models.ForeignKey(to='user.User',related_name="createdAdvertise",on_delete=models.CASCADE,null=True)
    kind = models.CharField(max_length=32,default='')
    url = models.CharField(max_length=2048,default='')
    text = models.CharField(max_length=2048,default='')
    expirationTime = models.FloatField(default=0)
    examination = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["expirationTime"]),
        ]
    
    def serialize(self):
        return {
            "id": self.id,
            "kind": self.kind,
            "url": self.url,
            "text": self.text,
        }