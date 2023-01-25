from django.db import models

class Document(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user=models.CharField(max_length=255, blank=True)
    text=models.CharField(max_length=999, blank=True)
    summary=models.CharField(max_length=999, blank=True)
    translated=models.CharField(max_length=999, blank=True)
class User(models.Model):
    username=models.CharField(max_length=255)
    password=models.CharField(max_length=255)