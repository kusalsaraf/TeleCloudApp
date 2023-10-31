# def generate_secure_otp(counter, digits=6):
#     try:
#         secret = "$urEC0mPL3xK#y!"
#         counter_bytes = struct.pack(b">Q", counter)
#         secret_bytes = bytes(secret, 'utf-8')
#         hmac_digest = hmac.new(secret_bytes, counter_bytes, hashlib.sha1).digest()
#         offset = hmac_digest[-1] & 0x0F
#         dynamic_code = struct.unpack(b">I", hmac_digest[offset:offset + 4])[0]
#         otp = dynamic_code % (10 ** digits)
#         otp = str(otp).zfill(digits)

#         return otp
#     except Exception as e:
#         otp = "123456"
#         otp = ''.join(random.choices('0123456789', k=digits))    
#     return otp


# def send_otp_email(subject, html_content, sender_email, recipient_email):
#     try:
#         url = "https://api.brevo.com/v3/smtp/email"
#         api_key = "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"

#         headers = {
#             "accept": "application/json",
#             "api-key": api_key,
#             "content-type": "application/json"
#         }

#         data = {
#             "sender": {
#                 "name": "TeleCloud",
#                 "email": sender_email
#             },
#             "to": [
#                 {
#                     "email": recipient_email
#                 }
#             ],
#             "subject": subject,
#             "htmlContent": html_content
#         }

#         response = requests.post(url, headers=headers, json=data)

#         if response.status_code == 201:
#             return True
            
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
        
#     return False


# class FileUploadApi(APIView):
#     def get(self, request, *args, **kwargs):
#         return render(request, "index.html")

#     def post(self, request, *args, **kwargs):
#         logger.info("Inside FileUploadApi... ",
#                     extra={'AppName': 'TeleCloudApp'})
#         response = {}
#         result = {}
#         result["status"] = 500
#         try:
#             data = request.data
#             print("data", data)
#             files_data = []
#             files = []
#             folder_path = "root"
#             if "files" in data:
#                 files = data.getlist("files")
#             if "folder_path" in data:
#                 folder_path = data["folder_path"]

#             bot_token = '6289800090:AAEh6Kpjb2zoQG1mjhOl-Ybi9SoCBzYX2H8'
#             chat_id = '-1001850005126'
#             params = {'chat_id': chat_id}
#             print("files", files)
#             for file in files:
#                 file_content_type = file.content_type
#                 print("type", file.content_type)
#                 if "image" in file_content_type:
#                     url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
#                     response = requests.post(
#                         url, params, files={'photo': file})
#                     print("responsephoto", response.text)
#                     response = json.loads(response.text)
#                     file_id = response['result']['photo'][-1]['file_id']
#                     get_image_api_url = f'https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}'
#                     response_image = requests.get(get_image_api_url)
#                     image_file_data = response_image.json()

#                     if image_file_data['ok']:
#                         image_file_path = image_file_data['result']['file_path']
#                         image_file_url = 'https://api.telegram.org/file/bot' + \
#                             bot_token + "/" + image_file_path

#                 elif "video" in file_content_type:
#                     url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
#                     response = requests.post(
#                         url, params, files={'video': file})
#                     response = json.loads(response.text)
#                     file_id = response['result']['video']['file_id']

#                 else:
#                     url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
#                     response = requests.post(
#                         url, params, files={'document': file})
#                     response = json.loads(response.text)
#                     file_id = response['result']['document']['file_id']

#                 print("response", response)
#                 message_id = response['result']["message_id"]
#                 print("folder_path", folder_path)
#                 file_obj = None
#                 if file_id and chat_id:
#                     if folder_path != "root":
#                         folder_name = folder_path.split("/")[-1]
#                         folder_actual_path = os.path.dirname(folder_path)
#                         print("folder_name", folder_name)
#                         print("folder_actual_path", folder_actual_path)
#                         folder_obj = Folder.objects.get(
#                             name=folder_name, user=request.user, directory=folder_actual_path)
#                         file_obj = File.objects.create(name=file.name, type=file.content_type, size=file.size, file_id=file_id,
#                                                        chat_id=chat_id, message_id=message_id, user=request.user, folder=folder_obj, path=folder_path)
#                     else:
#                         file_obj = File.objects.create(name=file.name, type=file.content_type, size=file.size, file_id=file_id,
#                                                        chat_id=chat_id, message_id=message_id, user=request.user, folder=None, path="root")
#                 print("fileob", type(file_obj))
#                 if "image" in file_content_type:
#                     files_data.append({"name": file.name, "type": file.content_type,
#                                        "size": file.size, "file_id": file_id, "image_file_url": image_file_url})
#                 else:
#                     files_data.append({"name": file.name, "type": file.content_type,
#                                        "size": file.size, "file_id": file_id})

#             result["status"] = 200
#             result["files_data"] = files_data

#             return Response(json.dumps(result))

#         except Exception as e:  # noqa: F841
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error(
#                 f"Error in FileUploadApi [{e}] at line {exc_tb.tb_lineno}")

#         return encrpt_data(response, 500, "Internal server error! Please try later")


# FileUpload = FileUploadApi.as_view()

import time
# class FileUploadApi(APIView):
#     async def send_photo(self, session, file, files_data, bot_token, params):
#         try:
#             url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
#             data = aiohttp.FormData()
#             data.add_field('photo', file.file)
#             print("file:", file.file)
#             async with session.post(url, params=params, data={'photo', file.file}) as response:
#                 response_data = await response.json()
#                 print("response_data111",response_data)
#                 if response_data["ok"]:
#                     file_id = response_data['result']['photo'][-1]['file_id']
#                     get_file_url = f'https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}'

#                     async with session.get(get_file_url) as file_response:
#                         file_data = await file_response.json()
#                         if file_data['ok']:
#                             file_path = file_data['result']['file_path']
#                             file_url = 'https://api.telegram.org/file/bot' + bot_token + "/" + file_path
#                             files_data.append({"name": file.name, "type": file.content_type,
#                                             "size": file.size, "file_id": file_id, "image_file_url": file_url})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             print(f"Error in send_photo [{e}] at line {exc_tb.tb_lineno}")

#     async def send_video(self, session, file, files_data, bot_token, params):
#         url = f'https://api.telegram.org/bot{bot_token}/sendVideo'
#         data = aiohttp.FormData()
#         data.add_field('video', file)

#         async with session.post(url, params=params, data=data) as response:
#             response_data = await response.json()
#             file_id = response_data['result']['video']['file_id']
#             files_data.append({"name": file.name, "type": file.content_type,
#                                "size": file.size, "file_id": file_id})

#     async def send_document(self, session, file, files_data, bot_token, params):
#         try:
#             url = f'https://api.telegram.org/bot{bot_token}/sendDocument'
#             data = aiohttp.FormData()
#             data.add_field('document', file)

#             async with session.post(url, params=params, data=data) as response:
#                 response_data = await response.json()
#                 file_id = response_data['result']['document']['file_id']
#                 files_data.append({"name": file.name, "type": file.content_type,
#                                 "size": file.size, "file_id": file_id})
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             print(f"Error in send_document [{e}] at line {exc_tb.tb_lineno}")

#     async def process_files(self, files, bot_token, chat_id):
#         try:
#             async with requests.Session() as session:
#                 tasks = []
#                 files_data = []
#                 params = {'chat_id': chat_id}
#                 for file in files:
#                     content_type = file.content_type
#                     file.name = file.name.replace(" ", "").replace("(", "").replace(")", "")
#                     print("file name: " + file.name)
#                     if "image" in content_type:
#                         task = asyncio.create_task(self.send_photo(session, file, files_data, bot_token, params))
#                         tasks.append(task)
#                     elif "video" in content_type:
#                         task = asyncio.create_task(self.send_video(session, file, files_data, bot_token, params))
#                         tasks.append(task)
#                     else:
#                         task = asyncio.create_task(self.send_document(session, file, files_data, bot_token, params))
#                         tasks.append(task)

#                 await asyncio.gather(*tasks)
#                 return files_data
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             print(f"Error in process_files [{e}] at line {exc_tb.tb_lineno}")

#     def post(self, request, *args, **kwargs):
#         bot_token = '6289800090:AAEh6Kpjb2zoQG1mjhOl-Ybi9SoCBzYX2H8'
#         chat_id = '-1001850005126'
#         response = {}
#         result = {}
#         result["status"] = 500
#         try:
#             data = request.data
#             files = []
#             if "files" in data:
#                 files = data.getlist("files")
#             print("files",files)
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)
#             files_data = loop.run_until_complete(self.process_files(files, bot_token, chat_id))

#             result["status"] = 200
#             result["files_data"] = files_data

#             return Response(json.dumps(result))

#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             print(f"Error in FileUploadApi [{e}] at line {exc_tb.tb_lineno}")

#         return Response(status=500)

# FileUpload = FileUploadApi.as_view()



# # google auth
# from google_auth_oauthlib.flow import Flow
# from google.oauth2 import id_token
# from google.auth.transport import requests

# def google_login(request):
#     flow = Flow.from_client_config(
#         client_config={
#             'web': {
#                 'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
#                 'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
#                 'redirect_uris': ['http://localhost:8000/cloud/accounts/google/login/callback/'],
#                 'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
#                 'token_uri': 'https://accounts.google.com/o/oauth2/token',
#             }
#         },
#         scopes=['openid', 'email', 'profile'],
#         redirect_uri='http://localhost:8000/cloud/accounts/google/login/callback/'
#     )
#     authorization_url, state = flow.authorization_url(prompt='consent')
#     request.session['state'] = state
#     return redirect(authorization_url)

# def google_callback(request):
#     try:
#         state = request.session.pop('state', None)
#         flow = Flow.from_client_config(
#             client_config={
#                 'web': {
#                     'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
#                     'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
#                     'redirect_uris': ['http://localhost:8000/cloud/accounts/google/login/callback/'],
#                     'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
#                     'token_uri': 'https://accounts.google.com/o/oauth2/token',
#                 }
#             },
#             scopes=['openid', 'email', 'profile'],
#             redirect_uri='http://localhost:8000/cloud/accounts/google/login/callback/'
#         )
#         flow.fetch_token(authorization_response=request.build_absolute_uri(), state=state)
#         credentials = flow.credentials

#         # Get user information from Google
#         userinfo_request = requests.Request()
#         userinfo = id_token.verify_oauth2_token(
#             credentials.id_token, userinfo_request, settings.GOOGLE_OAUTH2_CLIENT_ID
#         )

#         # Check if the user already exists in your user model
#         try:
#             user = User.objects.get(email=userinfo['email'])
#         except User.DoesNotExist:
#             # User does not exist, create a new user
#             user = User.objects.create_user(email=userinfo['email'])

#         # Authenticate the user
#         login(request, user)
#         return redirect('home')
#     except Exception as e:  # noqa: F841
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error(f"Error in DashBoard [{e}] at line {exc_tb.tb_lineno}")




# class SendMailApi(APIView):
#     def get(self, request, *args, **kwargs):
#         logger.info("Inside SendMailApi... ", extra={'AppName': 'TeleCloudApp'})
#         try:
#             otp = generate_secure_otp(2, digits=6)
#             subject = 'Your One-Time Password (OTP) from TeleCloud'
#             html_content = '''<html><head></head>
#                                 <body>
#                                     <p>Dear [user name] </p>

#                                     <p>Thank you for using our system. As part of our security measures,
#                                         we have generated a one-time password (OTP) for you to complete your requested action.</p>

#                                     <p><strong>OTP:  ''' + otp + '''</p></strong>

#                                     <p>Please enter the above OTP within <strong>5 minutes</strong> to proceed with your action.
#                                         Do not share this OTP with anyone, as it is valid for a single use only.</p>

#                                     <p>Thank you,<br>
#                                     TeleCloud</p>
#                                 </body>
#                             </html>'''
#             sender_email = 'telecloudotpsend@gmail.com'
#             recipient_email = 'kusalsaraf5@gmail.com'

#             success = send_otp_email(subject, html_content, sender_email, recipient_email)
#             print("success",success)
#             if success:
#                 OtpDetails.objects.create(otp=otp, email=recipient_email)
#                 return HttpResponse('Email sent successfully')
#             else:
#                 return HttpResponse('Email sending failed')
#         except Exception as e:  # noqa: F841
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("Error in SendMailApi... %s line %s", e, str(exc_tb.tb_lineno), extra={'AppName': 'TeleCloudApp'})

# SendMail = SendMailApi.as_view()


# class SignUpAPI(APIView):
#     def post(self, request, *args, **kwargs):
#         from urllib.parse import quote_plus, unquote
#         response = {}
#         try:
#             validation_obj = TeleCloudInputValidation()
#             tele_cloud_encrypt_obj = TeleCloudEncrypt()
#             data = request.data
#             json_string = tele_cloud_encrypt_obj.decrypt(data['json_string'])
#             data = json.loads(json_string)

#             firstname = data["first_name"]
#             lastname = data["last_name"]
#             email_id = data["email_id"]
#             otp = data["otp"]
#             password = data["password"]

#             if not validation_obj.is_valid_name(firstname) or firstname.strip() == "":
#                 return encrpt_data(response, 300, "Please enter a valid first name")

#             if not validation_obj.is_valid_name(lastname) or lastname.strip() == "":
#                 return encrpt_data(response, 300, "Please enter a valid last name")

#             if User.objects.filter(username=email_id):
#                 response["status"] = 300
#                 response = tele_cloud_encrypt_obj.encrypt(json.dumps(response))
#                 return Response(data=response)

#             otp_obj = OtpDetails.objects.filter(email=email_id, is_expired=False).order_by('-creation_time').first()

#             if otp_obj.exists():
#                 otp_time_diff = (timezone.now() - otp_obj.creation_time).total_seconds()
#                 if otp_time_diff > 5 * 60:
#                     otp_obj.is_expired = True
#                     otp_obj.save(update_fields=['is_expired'])
#                     response["status"] = 300
#                     response = tele_cloud_encrypt_obj.encrypt(json.dumps(response))
#                     return Response(data=response)

#                 if otp_obj.otp == otp:
#                     User.objects.create(firstname=firstname, lastname=lastname, email_id=email_id, password=password)
#             else:
#                 return encrpt_data(response, 300, "Please request otp")

#         except Exception as e:  # noqa: F841
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error("Error SignupAPI %s %s",
#                          str(e), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': '', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})

#         return encrpt_data(response, 500, "Internal server error! Please try later")


# Signup = SignUpAPI.as_view()


# directarynew_folder_obj= data["folder_path"]
# name = data["folder_name"]
# print("directary", directary)
# if directary == "root":
#     Folder.add_root(name=name, user=request.user,
#                     directory=directary)
# else:
#     parent_name = directary.split("/")[-1]
#     parent_path = os.path.dirname(directary)
#     parent_obj = Folder.objects.get(
#         name=parent_name, user=request.user, directory=parent_path)
#     child_folder = parent_obj.add_child(
#         name=name, user=request.user, directory=directary)
#     child_folder.save()


# async def send_video(self, request, folder_path, file, files_data, bot_token, chat_id):
#         try:
#             bot = telegram.Bot(token=bot_token)
#             response = await bot.send_video(chat_id=chat_id, video=file)
#             message_id = response.message_id
#             video_file_id = response['video']['file_id']
#             video_file_data = await bot.get_file(video_file_id)
#             video_file_url = video_file_data.file_path
#             files_data.append({
#                 "name": file.name,
#                 "type": "video",
#                 "size": file.size,
#                 "file_id": video_file_id,
#                 "file_url": video_file_url
#             })
            
#         except TelegramError as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error(f"Error in send_video [{e}] at line {exc_tb.tb_lineno}")
                    
#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             logger.error(f"Error in send_video [{e}] at line {exc_tb.tb_lineno}")

# async def send_document(self, request, folder_path, file, files_data, bot_token, chat_id):
#     try:
#         bot = telegram.Bot(token=bot_token)
#         response = await bot.send_document(chat_id=chat_id, document=file)
#         message_id = response.message_id
#         document_file_id = response.document.file_id
        
#         document_file_data = await bot.get_file(document_file_id)
#         document_file_url = document_file_data.file_path
#         files_data.append({
#             "name": file.name,
#             "type": "document",
#             "size": file.size,
#             "file_id": document_file_id,
#             "file_url": document_file_url
#         })
        
#     except TelegramError as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error(f"Error in send_document [{e}] at line {exc_tb.tb_lineno}")
                
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         logger.error(f"Error in send_document [{e}] at line {exc_tb.tb_lineno}")
