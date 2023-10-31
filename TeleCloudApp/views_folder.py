import logging
import json
import sys
import asyncio
import telegram
import urllib
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
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, ExpressionWrapper, FloatField
from django.db.models.functions import Round


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class FolderRootViewAPI(APIView):
    permission_classes = [IsAuthenticated]

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        try:
            folder_obj = Folder.objects.filter(
                user=request.user, directory="root", is_deleted=False)

            file_obj = File.objects.filter(
                user=request.user, folder=None, is_deleted=False)
            
            file_obj = file_obj.annotate(file_size_mb=Round(F('size') / 1048576.0, 2, output_field=FloatField()))

            paginator = Paginator(
                file_obj, 4)
            page = request.GET.get('page')

            try:
                file_obj = paginator.page(page)
            except PageNotAnInteger:
                file_obj = paginator.page(1)
            except EmptyPage:
                file_obj = paginator.page(paginator.num_pages)

            return render(request, 'home/folder.html', {
                "folder_obj": folder_obj,
                "file_obj": file_obj
            })
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in FolderRootViewAPI [{e}] at line {exc_tb.tb_lineno}")


FolderRootView = FolderRootViewAPI.as_view()


class FolderSubViewAPI(APIView):
    permission_classes = [IsAuthenticated]

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            tele_cloud_encrypt_obj = TeleCloudEncrypt()
            data = request.data
            json_string = tele_cloud_encrypt_obj.decrypt(data['json_string'])
            data = json.loads(json_string)
            folder_pk = data["folder_pk"]
            file_data = []
            folder_data = []
            parent_folder_obj = Folder.objects.get(
                pk=folder_pk, is_deleted=False)
            file_obj = File.objects.filter(
                user=request.user, folder=parent_folder_obj, is_deleted=False)
            for file in file_obj:
                file_data.append({
                    "name": file.name,
                    "type": file.type,
                    "size": file.size,
                    "file_pk": file.pk,
                    "file_url": file.file_url,
                    "is_favorite": file.is_favorite
                })
            folder_obj = parent_folder_obj.get_children()
            for folder in folder_obj:
                folder_data.append({
                    "name": folder.name,
                    "folder_pk": folder.pk,
                    "numchild": folder.numchild,
                    "file_count": folder.file_count,
                    "is_deleted": folder.is_deleted
                })

            response["folder_data"] = folder_data
            response["file_data"] = file_data
            return encrpt_data(response, 200, "Folder Child View Rendered Success")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in FolderSubViewAPI [{e}] at line {exc_tb.tb_lineno}")

        return encrpt_data(response, 500, "Internal server error! Please try later")


FolderSubView = FolderSubViewAPI.as_view()


class FolderAddAPI(APIView):
    permission_classes = [IsAuthenticated]

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            tele_cloud_encrypt_obj = TeleCloudEncrypt()
            tele_cloud_validation_obj = TeleCloudInputValidation()
            data = request.data
            json_string = tele_cloud_encrypt_obj.decrypt(data['json_string'])
            data = json.loads(json_string)
            parent_folder_pk = tele_cloud_validation_obj.remo_html_from_string(str(data["parent_folder_pk"]))
            name = tele_cloud_validation_obj.remo_html_from_string(data["folder_name"])
            directary = tele_cloud_validation_obj.remo_html_from_string(data["folder_path"])
            new_folder_data = []
            if int(parent_folder_pk) == -1:
                folder_child_name_exists = Folder.objects.filter(name=name, directory="root", user=request.user, is_deleted=False)
                if folder_child_name_exists:
                    return encrpt_data(response, 300, "Dublicate name found!")
                new_folder_obj = Folder.add_root(
                    name=name, user=request.user, directory="root")
            else:
                folder_parent_obj = Folder.objects.get(
                    pk=int(parent_folder_pk))
                folder_child_name_exists = folder_parent_obj.get_children().filter(name=name)
                if folder_child_name_exists:
                    return encrpt_data(response, 300, "Dublicate folder name found!")
                
                new_folder_obj = folder_parent_obj.add_child(
                    name=name, user=request.user, directory=directary)
                new_folder_obj.save()

            new_folder_data.append({
                "name": new_folder_obj.name,
                "folder_pk": new_folder_obj.id,
                "numchild": new_folder_obj.numchild,
                "file_count": new_folder_obj.file_count
            })

            response["new_folder_data"] = new_folder_data
            return encrpt_data(response, 200, "Folder created successfully")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in FolderAddAPI [{e}] at line {exc_tb.tb_lineno}")

        return encrpt_data(response, 500, "Internal server error! Please try later")


FolderAdd = FolderAddAPI.as_view()


class FolderRenameAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        try:
            tele_cloud_encrypt_obj = TeleCloudEncrypt()
            tele_cloud_validation_obj = TeleCloudInputValidation()
            data = request.data
            json_string = tele_cloud_encrypt_obj.decrypt(data['json_string'])
            data = json.loads(json_string)
            
            if tele_cloud_validation_obj.is_numeric(data["folder_pk"]):
                folder_pk = data["folder_pk"]
            else:
                return encrpt_data(response, 300, "Invalid folder pk")
                
            new_folder_name = tele_cloud_validation_obj.remo_html_from_string(data["new_folder_name"])
            
            if not tele_cloud_validation_obj.is_valid_name(new_folder_name):
                return encrpt_data(response, 300, "Folder name cannot contain special character except _")
            
            parent_folder_obj = Folder.objects.get(pk=folder_pk)
            parent_folder_obj_exists = parent_folder_obj.get_children().filter(name=new_folder_name)
            if parent_folder_obj_exists:
                return encrpt_data(response, 300, "Dublicate folder name found!")
            
            parent_folder_obj.name = new_folder_name
            parent_folder_obj.save(update_fields=['name'])
            return encrpt_data(response, 200, "Folder renamed successfully")
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in RenameFolderAPI [{e}] at line {exc_tb.tb_lineno}")
            
        return encrpt_data(response, 500, "Internal server error! Please try later")
            
FolderRename = FolderRenameAPI.as_view()


class FolderTempDeleteAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        try:
            tele_cloud_encrypt_obj = TeleCloudEncrypt()
            tele_cloud_validation_obj = TeleCloudInputValidation()
            data = request.data
            json_string = tele_cloud_encrypt_obj.decrypt(data['json_string'])
            data = json.loads(json_string)
            if tele_cloud_validation_obj.is_numeric(data["folder_delete_pk"]):
                folder_delete_pk = data["folder_delete_pk"]
            else:
                return encrpt_data(response, 300, "Invalid folder pk")
            
            folder_obj = Folder.objects.get(pk=folder_delete_pk)
            folder_obj.is_deleted = True
            folder_obj.save(update_fields=['is_deleted'])
            return encrpt_data(response, 200, "Folder moved to bin successfully")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in FolderTempDeleteAPI [{e}] at line {exc_tb.tb_lineno}")
        
        return encrpt_data(response, 500, "Internal server error! Please try later")
            
FolderTempDelete = FolderTempDeleteAPI.as_view()


class FolderRestoreAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        try:
            tele_cloud_encrypt_obj = TeleCloudEncrypt()
            tele_cloud_validation_obj = TeleCloudInputValidation()
            data = request.data
            json_string = tele_cloud_encrypt_obj.decrypt(data['json_string'])
            data = json.loads(json_string)
            
            if tele_cloud_validation_obj.is_numeric(data["folder_restore_pk"]):
                folder_restore_pk = data["folder_restore_pk"]
            else:
                return encrpt_data(response, 300, "Invalid folder pk")
            
            folder_obj = Folder.objects.get(pk=int(folder_restore_pk))
            folder_obj.is_deleted = False
            folder_obj.save(update_fields=['is_deleted'])
            return encrpt_data(response, 200, "Folder restore from bin successfully")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in FolderRestoreAPI [{e}] at line {exc_tb.tb_lineno}")
        
        return encrpt_data(response, 500, "Internal server error! Please try later")

FolderRestore = FolderRestoreAPI.as_view()


class FolderBackViewAPI(APIView):
    def post(self, request, *args, **kwargs):
        response = {}
        try:
            tele_cloud_encrypt_obj = TeleCloudEncrypt()
            tele_cloud_validation_obj = TeleCloudInputValidation()
            data = request.data
            json_string = tele_cloud_encrypt_obj.decrypt(data['json_string'])
            data = json.loads(json_string)
            
            if tele_cloud_validation_obj.is_numeric(data["parent_folder_pk"]):
                parent_folder_pk = data["parent_folder_pk"]
            else:
                return encrpt_data(response, 300, "Invalid folder pk")
            
            file_data = []
            folder_data = []
            parent_folder_obj = Folder.objects.get(pk=parent_folder_pk, is_deleted=False)
            
            if not parent_folder_obj.get_parent():
                response["parent_folder_pk"] = -1
                folder_obj = parent_folder_obj.get_siblings()
                file_obj = File.objects.filter(user=request.user, folder=None, is_deleted=False)
            else:
                parent_folder_obj = parent_folder_obj.get_parent()
                folder_obj = parent_folder_obj.get_children()
                response["parent_folder_pk"] = parent_folder_obj.pk
                file_obj = File.objects.filter(user=request.user, folder=parent_folder_obj, is_deleted=False)
            
            for file in file_obj:
                file_data.append({
                    "name": file.name,
                    "type": file.type,
                    "size": file.size,
                    "file_pk": file.pk,
                    "file_url": file.file_url,
                    "is_favorite": file.is_favorite
                })
            
            for folder in folder_obj:
                folder_data.append({
                    "name": folder.name,
                    "folder_pk": folder.pk,
                    "numchild": folder.numchild,
                    "file_count": folder.file_count,
                    "is_deleted": folder.is_deleted
                })

            response["folder_data"] = folder_data
            response["file_data"] = file_data
            
            return encrpt_data(response, 200, "Folder back success")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(
                f"Error in FolderBackViewAPI [{e}] at line {exc_tb.tb_lineno}")

        return encrpt_data(response, 500, "Internal server error! Please try later")


FolderBackView = FolderBackViewAPI.as_view()
