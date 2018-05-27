import datetime

from django.db import models
from django.utils import timezone
from django.conf import settings

from knox.auth import AuthToken

PASSCODE_EXPIRE_MIN = getattr(settings, "PASSCODE_EXPIRE_MIN", 5)
TIME_BETWEEN_PASSCODE = getattr(settings, "TIME_BETWEEN_PASSCODE", 1)


class PasscodeChecksLog(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    phone_device = models.ForeignKey('PhoneDevice', on_delete=models.CASCADE)
    passcode = models.CharField(max_length=4,default='0000')
    used = models.BooleanField(default=False)

    def __str__(self):
        return ', '.join((str(self.created), str(self.phone_device), self.passcode))

    @property
    def expired_passcode(self):
        return self.created <= timezone.now() - datetime.timedelta(minutes=PASSCODE_EXPIRE_MIN)

    @property
    def passcode_sended_recently(self):
        return self.created >= timezone.now() - datetime.timedelta(minutes=TIME_BETWEEN_PASSCODE)


class PhoneDeviceManager(models.Manager):
    def get_by_natural_key(self, mobile, device_id):
        return self.get(mobile=mobile, device_id=device_id)


class PhoneDevice(models.Model):
    mobile = models.CharField(max_length=10)
    device_id= models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    token = models.OneToOneField(AuthToken, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.mobile) + ', ' + str(self.device_id)

    def natural_key(self):
        return (self.mobile, self.device_id)

    class Meta:
        unique_together = (('mobile', 'device_id'), )
