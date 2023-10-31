from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cloud/', include('TeleCloudApp.urls')),
    path('', lambda request: redirect('login_page'), name='root'),
]
