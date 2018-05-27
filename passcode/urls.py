from django.conf.urls import url

from passcode.views import register
from passcode.views import verify_and_create

urlpatterns = [
               url(r'^register/$',register),
               url(r'^verify/$', verify_and_create),
]
                       

