import random
import re

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes

from knox.models import AuthToken

from passcode.models import PhoneDevice, PasscodeChecksLog
from passcode.models import TIME_BETWEEN_PASSCODE, PASSCODE_EXPIRE_MIN


PASSCODE_SALT = getattr(settings, "PASSCODE_SALT", '61993a48ecb5367b13fed55054f3329c55c1')
PASSCODE_LENGTH = getattr(settings, "PASSCODE_LENGTH", 4)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register(request):
    """Register phone number and device ID, create passcode to verify it."""
    response_data = {'code': 'Invalid Data: need "mobile" and "device_id" parameters.'}
    try:
        mobile = request.POST['mobile']
        device_id = request.POST['device_id']
    except KeyError:
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    validate = re.search('^\d{4,13}$', mobile)
    if validate is None:
        response_data = {'code': 'Invalid Data: invalid phone number.'}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # check if it's old mobile number
    try:
        phone_device_old = PhoneDevice.objects.get(mobile=mobile, device_id=device_id)
    except ObjectDoesNotExist:
        phone_device_old = None

    mobile_log_raw = PasscodeChecksLog.objects.filter(phone_device=phone_device_old).order_by('-created')

    # check if we already sended passcode in TIME_BETWEEN_PASSCODE minutes
    if phone_device_old and mobile_log_raw:
        if mobile_log_raw[0].passcode_sended_recently:
            response_data = {'code': 'Wait %s minutes before request new passcode.' %
                                     TIME_BETWEEN_PASSCODE}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # create or update data about phone number
    phone_device, _ = PhoneDevice.objects.update_or_create(mobile=mobile, device_id=device_id)

    passcode_list = random.sample([1,2,3,4,5,6,7,8,9,0],PASSCODE_LENGTH)
    passcode = ''.join(str(p) for p in passcode_list)

    # create log raw in passcode log table for future verification of passcode
    PasscodeChecksLog.objects.create(phone_device=phone_device, passcode=passcode)

    # Send here SMS with passcode

    response_data['code'] = 'Passcode generation success.'
    return Response(response_data, status = status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def verify_and_create(request):
    """Verify passcode using PasscodeChecksLog and create new token.
    Old token for same phone and device will be deleted."""
    response_data = {}
    try:
        mobile = request.POST['mobile']
        device_id = request.POST['device_id']
        passcode = request.POST['passcode']
    except KeyError:
        response_data['code'] = 'Invalid Data: need mobile, device_id and passcode.'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    try:
        phone_device = PhoneDevice.objects.get(mobile=mobile, device_id=device_id)
        passcode_check_raw = PasscodeChecksLog.objects.get(phone_device=phone_device,
                                                           passcode=passcode)
    except ObjectDoesNotExist:
        response_data['code'] = 'Invalid passcode, phone or device_id.'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    if passcode_check_raw.expired_passcode or passcode_check_raw.used:
        addition = 'passed more than %s minutes' % PASSCODE_EXPIRE_MIN
        if passcode_check_raw.used:
            addition = 'passcode was used'
        response_data['code'] = 'Passcode expired: ' + addition
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    token_key = create_new_token(phone_device=phone_device)
    passcode_check_raw.used = True
    passcode_check_raw.save()

    response_data['code'] = 'Success'
    response_data['token'] = token_key

    return Response(response_data,status=status.HTTP_201_CREATED)


def create_new_token(phone_device):
    """"Create new token. If there was some other before, delete it.
    Also if there is no user with this phone number, create it.
    Token key not saved in database, only hash and start of number."""
    if not phone_device.token:
        mobile = str(phone_device.mobile)
        try:
            user = User.objects.get(username=mobile)
        except ObjectDoesNotExist:
            user = User.objects.create_user(username=mobile, password=mobile+PASSCODE_SALT)
        token_key = AuthToken.objects.create(user=user)
    else:
        # remove old token for this user and create new one
        user = phone_device.token.user
        phone_device.token.delete()
        token_key = AuthToken.objects.create(user=user)

    # find created token and save link to it
    for token in user.auth_token_set.all():
        if token_key.startswith(token.token_key):
            phone_device.token = token
            phone_device.save()
            break

    return token_key
