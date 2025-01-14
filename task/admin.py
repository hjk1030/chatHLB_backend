from django.contrib import admin
import task.models

# Register your models here.

admin.site.register(task.models.Task)
admin.site.register(task.models.TaskPackage)
admin.site.register(task.models.TaskTemplate)