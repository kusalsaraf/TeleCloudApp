import hmac
import hashlib
import struct
import requests
import logging
import sys
import random
import os
from TeleCloudApp.models import *
from TeleCloudApp.utils_encryption import *
from rest_framework.response import Response
from django.conf import settings

logger = logging.getLogger(__name__)


def get_random_captcha_image():
    logger.info("Inside the get_random_captcha_image function")
    try:
        files = os.listdir(str(settings.BASE_DIR) + '\TeleCloudApp\static\TeleCloudApp\captcha_images')
        index = random.randrange(0, len(files))
        return files[index]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f"Error in get_random_captcha_image function [{e}] at line {exc_tb.tb_lineno}")
    return files[1]


def decrypt_variable(data):
    logger.info("Inside the decrypt_variable function")
    try:
        tele_cloud_encrypt_obj = TeleCloudEncrypt()
        data = tele_cloud_encrypt_obj.decrypt(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f"Error in decrypt_variable function [{e}] at line {exc_tb.tb_lineno}")
    return data


def encrpt_data(response, status, message):
    logger.info("Inside the encrpt_data function")
    try:
        tele_cloud_encrypt_obj = TeleCloudEncrypt()
        response["status"] = status
        response["message"] = message
        response = tele_cloud_encrypt_obj.encrypt(json.dumps(response))
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f"Error in encrpt_data function [{e}] at line {exc_tb.tb_lineno}")
    
    return Response(data=response)


def generate_folder_name(counter):
    folder_name = f"New Folder {counter}"
    return folder_name
