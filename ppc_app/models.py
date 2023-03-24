from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class customerRevice (models.Model):
    created_at                  = models.DateTimeField('created_at', auto_now_add=True)
    updated_at                  = models.DateTimeField('updated_at', auto_now=True)

class customerReviceAttachment (models.Model):
    customerRevice  = models.ForeignKey(customerRevice, on_delete=models.CASCADE, blank=True, null=True)
    created_at      = models.DateTimeField('created_at', auto_now_add=True)
    updated_at      = models.DateTimeField('updated_at', auto_now=True)
    attachment      = models.FileField(upload_to='customerReviceAttachments/', null=False, blank=True)

class millingSchedule (models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at  = models.DateTimeField('created_at', auto_now_add=True)
    updated_at  = models.DateTimeField('updated_at', auto_now=True)
    attachment  = models.FileField(upload_to='millingSchedules/', null=False, blank=True)
