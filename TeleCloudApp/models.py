import re
import json
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from treebeard.mp_tree import MP_Node

class User(AbstractUser):
    chat_id = models.CharField(max_length=255)
    bot_token = models.CharField(max_length=255)
    timestamp_user_creation = models.DateTimeField(auto_now_add=True)
    total_attempts = models.IntegerField(default=0)
    failed_attempts = models.IntegerField(default=0, help_text="This number of times user failed to login.")
    last_attempt_datetime = models.DateTimeField(default=timezone.now, null=True, blank=True, help_text="Date and time of user last login attempt.")
    
    def name(self):
        return self.first_name + ' ' + self.last_name
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Folder(MP_Node):
    name = models.CharField(default="",max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    directory = models.TextField(default="root")
    is_deleted = models.BooleanField(default=False)
    file_count = models.IntegerField(default=0)
    def __str__(self):
        return str(self.directory + " ----> " + self.name)


class File(models.Model):
    name = models.CharField(max_length=255, db_index=True, default="")
    type = models.CharField(max_length=50, default="")
    size = models.IntegerField(default=0)
    file_id = models.CharField(max_length=255, db_index=True, default="")
    chat_id = models.CharField(max_length=255, default="")
    message_id = models.IntegerField(null=True, default="")
    file_url = models.TextField(default="")
    is_deleted = models.BooleanField(default=False)
    uploaded_date = models.DateTimeField(default=timezone.now, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.name)
