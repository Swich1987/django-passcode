from django.contrib import admin

from .models import PhoneDevice, PasscodeChecksLog

admin.site.register(PhoneDevice)
admin.site.register(PasscodeChecksLog)
