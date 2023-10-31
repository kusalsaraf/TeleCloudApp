import logging
import json
import sys
import asyncio
import telegram
from TeleCloudApp.utils import *
from TeleCloudApp.utils_validation import *
from TeleCloudApp.utils_encryption import *
from TeleCloudApp.captcha_key import *
from TeleCloudApp.models import *
from django.contrib.auth.views import PasswordResetView
from datetime import datetime, timedelta
from rest_framework.views import APIView
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from telegram.error import TelegramError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


logger = logging.getLogger(__name__)


def LoginPage(request):
    logger.info("Inside the LoginPage view")
    try:
        if request.user.is_authenticated:
            return HttpResponseRedirect("/cloud/folder-root-view/")
        captcha_image = get_random_captcha_image()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            f"Error in LoginPage view [{e}] at line {exc_tb.tb_lineno}")

    return render(request, 'login/login.html', {"captcha_image": captcha_image})


class PasswordResetAPI(PasswordResetView):
    template_name = 'login/password_change_request.html'
    try:
        def post(self, *args, **kwargs):
            is_new_user = False
            is_new_user = self.request.POST.get("is_new_user")

            if is_new_user == "false":
                self.email_template_name = 'login/password_reset_custom_message_old_user.html'
            else:
                self.email_template_name = 'login/password_reset_custom_message_new_user.html'

            return super().post(self.request, *args, **kwargs)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            f"Error in PasswordResetAPI [{e}] at line {exc_tb.tb_lineno}")


PasswordReset = PasswordResetAPI.as_view()


class UserAuthAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        temp_user = None
        try:
            data = request.data

            if not isinstance(data, dict):
                data = json.loads(data)

            data = decrypt_variable(data["Request"])
            data = json.loads(data)
            validation_obj = TeleCloudInputValidation()

            email_id = data['email']
            password = data['password']
            captcha = data["captcha_image_input"]

            if not validation_obj.is_valid_email(email_id) or email_id.strip() == "":
                return encrpt_data(response, 300, "Please enter a valid first name")

            if password.strip() == "":
                return encrpt_data(response, 300, "Please enter a valid password")

            if captcha.strip() == "" or len(captcha) != 6:
                return encrpt_data(response, 300, "Please enter a valid capcha")

            captcha_key = data["captcha_image"]
            captcha_key = captcha_key.split("/")[6].split(".")[0]
            captcha_key = next(
                item for item in captcha_data if item["name"] == captcha_key)
            captcha_key = captcha_key["text"]

            temp_user = User.objects.filter(username=email_id).first()
            if not temp_user:
                return encrpt_data(response, 300, "Incorrect email/password")

            time_difference = (
                timezone.now() - temp_user.last_attempt_datetime).seconds

            if temp_user.failed_attempts > 25:
                time_minutes = time_difference / 60
                if time_minutes >= 60:
                    temp_user.failed_attempts = 0
                    temp_user.save(update_fields=['failed_attempts'])
                else:
                    return encrpt_data(response, 300, "You have failed your login more than 5 times. Kindly contact administrator or try after some time.")

            if str(captcha) == str(captcha_key):
                user = authenticate(username=email_id, password=password)

                if user:
                    login(request, user,
                          backend='django.contrib.auth.backends.ModelBackend')
                    response["username"] = request.user.username
                    return encrpt_data(response, 200, "Welcome user")
                else:
                    temp_user.last_attempt_datetime = timezone.now()
                    temp_user.failed_attempts = temp_user.failed_attempts + 1
                    temp_user.save(
                        update_fields=['failed_attempts', 'last_attempt_datetime'])
                    return encrpt_data(response, 300, "Incorrect email/password")

            else:
                return encrpt_data(response, 300, "Please enter correct captcha.")

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in UserAuthAPI [{e}] at line {exc_tb.tb_lineno}")

        return encrpt_data(response, 500, "Internal server error! Please try later.")


UserAuth = UserAuthAPI.as_view()


class SignUpAPI(APIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'login/sign_up.html')

    def post(self, request, *args, **kwargs):
        from urllib.parse import quote_plus, unquote
        response = {}
        try:
            validation_obj = TeleCloudInputValidation()
            tele_cloud_encrypt_obj = TeleCloudEncrypt()
            data = request.data
            json_string = tele_cloud_encrypt_obj.decrypt(data['json_string'])
            data = json.loads(json_string)

            firstname = data["first_name"]
            lastname = data["last_name"]
            email_id = data["email_id"]

            if not validation_obj.is_valid_name(firstname) or firstname.strip() == "":
                return encrpt_data(response, 300, "Please enter a valid first name")

            if not validation_obj.is_valid_name(lastname) or lastname.strip() == "":
                return encrpt_data(response, 300, "Please enter a valid last name")

            if User.objects.filter(username=email_id):
                return encrpt_data(response, 300, "Email id already exists!")

            User.objects.create(
                first_name=firstname, last_name=lastname, username=email_id, email=email_id)

            return encrpt_data(response, 200, "User created!")

        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in SignUpAPI [{e}] at line {exc_tb.tb_lineno}")

        return encrpt_data(response, 500, "Internal server error! Please try later")


SignUp = SignUpAPI.as_view()


class RandomCaptchaAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data
            old_captcha_image = data["captcha_image"]
            old_captcha_image = decrypt_variable(old_captcha_image)
            old_captcha_image = old_captcha_image.split("/")[6].split(".")[0]
            old_captcha_image = str(old_captcha_image + ".png")
            captcha_image = get_random_captcha_image()
            while (str(captcha_image) == str(old_captcha_image)):
                captcha_image = get_random_captcha_image()
            captcha_image = str(
                "/static/TeleCloudApp/captcha_images/" + captcha_image)
            response["captcha_image"] = captcha_image
            return encrpt_data(response, 200, "Success")
        except Exception as e:  # noqa: F841
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in RandomCaptchaAPI [{e}] at line {exc_tb.tb_lineno}")

        return encrpt_data(response, 500, "Internal server error! Please try later")


RandomCaptcha = RandomCaptchaAPI.as_view()


def DashBoard(request):
    try:
        if request.user.is_authenticated:
            return render(request, 'home/dashboard.html')
        else:
            return HttpResponseRedirect("/cloud/login/")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f"Error in DashBoard [{e}] at line {exc_tb.tb_lineno}")


class LogOutAPI(APIView):
    def post(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                user = User.objects.get(username=request.user.username)
                user.failed_attempts = 0
                user.save(update_fields=['failed_attempts'])
                logout(request)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in LogOutAPI [{e}] at line {exc_tb.tb_lineno}")

        return HttpResponseRedirect("/cloud/login/")


LogOut = LogOutAPI.as_view()


class FileUploadApi(APIView):
    async def send_photos(self, request, folder_path, file, files_data, bot_token, chat_id):
        try:
            bot = telegram.Bot(token=bot_token) 
            response = await bot.send_photo(chat_id=chat_id, photo=file)
            message_id = response.message_id
            image_file_id = response.photo[-1].file_id
            file_data = await bot.get_file(image_file_id)
            image_file_url = file_data.file_path
            files_data.append({
                "name": file.name,
                "type": "image",
                "size": file.size,
                "file_id": image_file_id,
                "file_url": image_file_url,
                "message_id": message_id
            })
        
        except TelegramError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f"Error in send_photo [{e}] at line {exc_tb.tb_lineno}")
                    
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f"Error in send_photo [{e}] at line {exc_tb.tb_lineno}")
    
    async def process_files(self, request, folder_path, files, bot_token, chat_id):
        try:
            tasks = []
            files_data = []
            
            for file in files:
                content_type = file.content_type
                
                if "image" in content_type:
                    task = asyncio.create_task(self.send_photos(request, folder_path, file, files_data, bot_token, chat_id))
                    tasks.append(task)

            await asyncio.gather(*tasks)
            return files_data
                
        except Exception as e:
            print(f"Error in process_files: {e}")

    def post(self, request, *args, **kwargs):
        bot_token = request.user.bot_token
        chat_id = request.user.chat_id
        result = {}
        result["status"] = 500
        
        if not bot_token and not chat_id:
            logger.error(f"Error invalid bot_token or chat_id")
            result["status"] = 300
            result["message"] = "Error invalid bot_token or chat_id"
            return Response(json.dumps(result))
        
        try:
            data = request.data
            if "folder_path" in data:
                folder_path = data['folder_path']
            if "files" in data:
                files = data.getlist("files")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            files_data = loop.run_until_complete(self.process_files(request, folder_path, files, bot_token, chat_id))
            
            for file in files_data:
                if folder_path == "root":
                    file_obj = File.objects.create(name=file["name"], type=file["type"], size=file["size"], file_id=file["file_id"], file_url=file["file_url"],
                                        chat_id=chat_id, message_id=file["message_id"], user=request.user, folder=None)
                    file["file_pk"] = file_obj.pk
                else:
                    folder_name = folder_path.split("/")[-1]
                    folder_actual_path = os.path.dirname(folder_path)
                    folder_obj = Folder.objects.get(name=folder_name, user=request.user, directory=folder_actual_path)
                    
                    file_obj = File.objects.create(name=file["name"], type=file["type"], size=file["size"], file_id=file["file_id"], file_url=file["file_url"],
                                        chat_id=chat_id, message_id=file["message_id"], user=request.user, folder=folder_obj)
                    file["file_pk"] = file_obj.pk
            
            result["status"] = 200
            result["files_data"] = files_data
            return Response(json.dumps(result))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f"Error in FileUploadApi [{e}] at line {exc_tb.tb_lineno}")

        return Response(status=500)

FileUpload = FileUploadApi.as_view()


class FileRenameAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data
            file_pk = data["file_pk"]
            new_file_name = data["new_file_name"]
            file_obj = File.objects.get(pk=file_pk)
            file_obj.name = new_file_name
            file_obj.save(update_fields=['name'])
            response["status"] = 200
            return Response(json.dumps(response))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in FileRenameAPI [{e}] at line {exc_tb.tb_lineno}")
            
FileRename = FileRenameAPI.as_view()

class FileTempDeleteAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data
            file_delete_pk = data["file_delete_pk"]
            file_obj = File.objects.get(pk=file_delete_pk)
            file_obj.is_deleted = True
            file_obj.save(update_fields=['is_deleted'])
            response["status"] = 200
            return Response(json.dumps(response))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in FileTempDeleteAPI [{e}] at line {exc_tb.tb_lineno}")
            
FileTempDelete = FileTempDeleteAPI.as_view()

class RecycleBinAPI(APIView):
    def get(self, request, *args, **kwargs):
        try:
            folder_obj = Folder.objects.filter(
                user=request.user, is_deleted=True)
            
            file_obj = File.objects.filter(user=request.user, is_deleted=True)

            return render(request, 'home/recycle_bin.html', {
                "folder_obj": folder_obj,
                "file_obj": file_obj
            })
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in RecycleBinAPI [{e}] at line {exc_tb.tb_lineno}")
            
RecycleBin = RecycleBinAPI.as_view()


class FileRestoreAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data
            file_restore_pk = data["file_restore_pk"]
            file_obj = File.objects.get(pk=file_restore_pk)
            file_obj.is_deleted = False
            file_obj.save(update_fields=['is_deleted'])
            response["status"] = 200
            return Response(json.dumps(response))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in FileRestoreAPI [{e}] at line {exc_tb.tb_lineno}")

FileRestore = FileRestoreAPI.as_view()


class EmptyRecycleBinAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        try:
            File.objects.filter(user=request.user, is_deleted=True).delete()
            folder_obj = Folder.objects.filter(user=request.user, is_deleted=True)
            for folder in folder_obj:
                folder.delete()

            response["status"] = 200
            return Response(json.dumps(response))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in EmptyRecycleBinAPI [{e}] at line {exc_tb.tb_lineno}")

EmptyRecycleBin = EmptyRecycleBinAPI.as_view()


class FavoritesAPI(APIView):
    def get(self, request, *args, **kwargs):
        try:
            
            file_obj = File.objects.filter(user=request.user, is_favorite=True, is_deleted=False)

            return render(request, 'home/favorites.html', {
                "file_obj": file_obj
            })
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in FavoritesAPI [{e}] at line {exc_tb.tb_lineno}")
            
Favorites = FavoritesAPI.as_view()


class FavoriteToggleAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        try:     
            data = request.data
            file_favorite_pk = data["file_favorite_pk"]
            file_obj = File.objects.get(pk=file_favorite_pk)
            if file_obj.is_favorite:
                file_obj.is_favorite = False
            else:
                file_obj.is_favorite = True
            file_obj.save(update_fields=['is_favorite'])
            response["status"] = 200
            response["is_favorite"] = file_obj.is_favorite
            return Response(json.dumps(response))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in FavoritesAPI [{e}] at line {exc_tb.tb_lineno}")
            
FavoriteToggle = FavoriteToggleAPI.as_view()


def SettingPage(request):
    try:
        if request.user.is_authenticated:
            bot_token = request.user.bot_token
            chat_id = request.user.chat_id
            return render(request, 'home/settings.html', {"bot_token": bot_token,
                                                          "chat_id": chat_id,
                                                        })
        else:
            return HttpResponseRedirect("/cloud/login/")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(
            f"Error in SettingPage view [{e}] at line {exc_tb.tb_lineno}")


# class FileViewApi(APIView):
#     def get(self, request, *args, **kwargs):
#         logger.info("Inside FileViewApi... ", extra={'AppName': 'TeleCloudApp'})
#         response = {}
#         files_data = []
#         try:
#             bot_token = '6289800090:AAEh6Kpjb2zoQG1mjhOl-Ybi9SoCBzYX2H8'
#             for file in File.objects.filter(is_deleted=False).iterator():

#                 api_url = f'https://api.telegram.org/bot{bot_token}/getFile?file_id={file.file_id}'

#                 response = requests.get(api_url)
#                 file_data = response.json()

#                 if file_data['ok']:
#                     file_path = file_data['result']['file_path']
#                     file_url = 'https://api.telegram.org/file/bot' + bot_token + "/" + file_path
#                     files_data.append({
#                         "file_url": file_url,
#                         "file_id": file.file_id,
#                     })
#             return render(request, "files.html", {
#                 "files_data": files_data
#             })

#         except Exception as e:  # noqa: F841
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("Error in FileViewApi... %s line %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'TeleCloudApp'})

# FileView = FileViewApi.as_view()

# class FileTempDeleteApi(APIView):
#     def get(self, request, message_id, *args, **kwargs):
#         logger.info("Inside FileTempDeleteApi... ", extra={'AppName': 'TeleCloudApp'})
#         type=True
#         file_id = ""
#         try:
#             if not type:
#                 File.objects.filter(file_id=file_id).update(is_deleted=True)
#             else:
#                 bot_token = '6289800090:AAEh6Kpjb2zoQG1mjhOl-Ybi9SoCBzYX2H8'
#                 chat_id = '-1001850005126'
#                 url = f'https://api.telegram.org/bot{bot_token}/deleteMessage'

#                 params = {
#                     'chat_id': chat_id,
#                     'message_id': message_id
#                 }
#                 response = requests.post(url, params=params)
#                 print("response",response)
#                 if response.status_code == 200:
#                     File.objects.filter(file_id=file_id).delete()
#                     print("Message deleted successfully.")
#                 else:
#                     print("Error deleting message:", response.text)

#         except Exception as e:  # noqa: F841
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("Error in FileTempDeleteApi... %s line %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'TeleCloudApp'})

# FileTempDelete = FileTempDeleteApi.as_view()


