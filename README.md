# django-passcode
Django passcode is a project to enable mobile device registration and verification using SMS based passcode. 
This is the totally reworked fork of original [django-passcode](https://github.com/sgurminder/django-passcode).

Here is how it works:
1. User register on the server using POST request with the mobile phone number and device id.
2. Receive in response passcode
2. Send POST request to "verify" endpoint with mobile phone, device_id, and passcode
4. Receive in response token to access API

#Features and concept of work

1. Only 1 token for one set of device_id and phone number. If you request new token for the same set, the old one will be deleted from the system.
2. Full log of every generated passcode
3. You can set how often one passcode for same device_id and phone number can be requested
4. You can set how long time the passcode can be valid
5. For token management used Knox and basic User model in Django. If automatically generate User with username=mobile_number and password=mobile_number+salt. This is useful if you want to use different authentication methods.
6. It uses the one-to-one field in MobileDevice model to connect to token, which is connected to User model. This save all tokens, which is generated outside the passcode. If there is already some token in this field, it will use owner of this token for token generation.  So you can create user on your app, add his mobile phone number, device_id, and token to the table, and it will work with no problem.
7. User created only after successful verification of the passcode

#Requirments
  - Django Rest Framework (rest_framework)
  - Knox
  
This must be in INSTALLED_APPS in settings.py:


#Installation

  - Include ``` passcode ``` in Installed apps of your project
  - Add  ``` url(r'^signup/', include('passcode.urls')) ``` in urls.py of your project
  - Add any settings you wish in settings.py of your Django project


# Usage

API
===

1. Register: POST request to <your_domain>/signup/register/

Post parameters
   - mobile phone
   - Device id

Response: JSON response 
```  
On success : {"code" : "Success"} 
On Error   : {"code" : "Info about error"} 
 ```
 
2. Verify: POST request to <your_domain>/signup/verify/

Post parameters
     - mobile phone
     - Device id
     - passcode

Response : JSON response

On success: 
```  
{"code" : "Success", 
"token": "485288c44d3f37a993a1d7d05ac3ec321016ad14dfffacb26b2e67482079cafc"} 
```  
On Error:
 ```
  {"code" : "Info about error"} 
 ```
 
 Settings
 ===
 You can set these settings in your settings.py:
 
 PASSCODE_SETTINGS = {
     "PASSCODE_SALT": "some random salt for user's password",
     "PASSCODE_LENGTH": 4,
     "PASSCODE_EXPIRE_MIN": 5,
     "TIME_BETWEEN_PASSCODE": 1
     }
