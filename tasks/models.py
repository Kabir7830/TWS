from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    class Meta:
        db_table = "task"

    title = models.CharField(max_length=100,unique=True)
    description = models.TextField()
    due_date = models.DateTimeField()
    allowed_users = models.ManyToManyField(User,null=True,blank=True)
    status = models.CharField(choices=(('Todo','Todo'),('Inprogress','Inprogress'),('Done','Done')),max_length=100)