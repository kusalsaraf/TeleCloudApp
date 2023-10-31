from django.contrib import admin
from django.contrib.auth.models import Group
from TeleCloudApp.models import *

admin.site.unregister(Group)
admin.site.register(File)
admin.site.register(User)
admin.site.register(Folder)
