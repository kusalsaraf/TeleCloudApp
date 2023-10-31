from django.urls import path
from TeleCloudApp.views import *
from TeleCloudApp.views_folder import *
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.views.generic import TemplateView


urlpatterns = [
    path('file/upload/', FileUpload, name='file_upload'),
    # path('file/view/', FileView, name='file_view'),
    # path('file/tempdelete/<str:file_id>', FileTempDelete, name='file_temp_delete'),
    # path('sendmail/', SendMail, name='send_mail'),
    path('signup/', SignUp, name="sign_up"),
    path('userauth/', UserAuth, name="user_auth"),
    path('login/', LoginPage, name="login_page"),
    path('logout/', LogOut, name="logout_page"),
    path('dashboard/', DashBoard, name="dashboard"),
    path('recycle-bin/', RecycleBin, name="recycle_bin"),
    path('favorites/', Favorites, name="favorites"),
    path('settings/', SettingPage, name="settings_page"),
    path('favorite-toggle/', FavoriteToggle, name="favorite_toggle"),
    path('empty-recycle-bin/', EmptyRecycleBin, name="empty_recycle_bin"),
    path('folder-root-view/', FolderRootView, name="folder_root_view"),
    path('folder-sub-view/', FolderSubView, name="folder_sub_view"),
    path('folder-back-view/', FolderBackView, name="folder_back_view"),
    path('folder-add/', FolderAdd, name="folder_add"),
    path('folder-rename/', FolderRename, name="folder_rename"),
    path('folder-restore/', FolderRestore, name="folder_restore"),
    path('file-restore/', FileRestore, name="file_restore"),
    path('file-rename/', FileRename, name="file_rename"),
    path('folder-temp-delete/', FolderTempDelete, name="folder_temp_delete"),
    path('file-temp-delete/', FileTempDelete, name="file_temp_delete"),
    path('random-captch/', RandomCaptcha, name="random_captcha"),
    path('reset-password/', PasswordReset, name='reset_password'),
    path('reset_password_sent/', TemplateView.as_view(template_name='login/password_reset_mail_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='login/password_reset.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='login/password_reset_done.html'), name='password_reset_complete'),
    # path('accounts/google/login/', google_login, name='google_login'),
    # path('accounts/google/login/callback/', google_callback, name='google_callback'),
]

