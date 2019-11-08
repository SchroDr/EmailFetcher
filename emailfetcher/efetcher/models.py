from django.db import models
from django.utils import timezone

class User(models.Model):
    useId = models.CharField(max_length=128, primary_key=True)
    count = models.IntegerField(default=0)
# Create your models here.


class ContentMail(models.Model):
    mailId = models.CharField(max_length=255,primary_key=True)
    name = models.TextField(default='n')
    content = models.TextField(default='n')
    add_date = models.DateTimeField(default=timezone.now())
