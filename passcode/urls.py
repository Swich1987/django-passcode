# from django.conf.urls import include
from django.conf.urls import url
# from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt

from passcode.views import register
from passcode.views import verify_and_create

urlpatterns = [
               url(r'^register/$',register),
               url(r'^verify/$', verify_and_create),
]
                       

