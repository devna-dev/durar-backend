import json
from datetime import datetime

from rest_framework import views, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import SMS


class TwilioStatusView(views.APIView):
    permission_classes = [AllowAny]

    def get_object(self):
        sid = self.request.data.get('MessageSid', None)
        if sid is None: return SMS.objects.none()
        return SMS.objects.filter(sid=sid).first()

    def post(self, request, *args, **kwargs):
        sms = self.get_object()
        if sms:
            sms_status = self.request.data.get('MessageStatus')
            sms_status_update = {
                'date': str(datetime.now()),
                'status': sms_status
            }
            responses = sms.response_data
            if responses and responses.get('status_update', None):
                responses['status_update'] += [sms_status_update]
            elif responses:
                responses['status_update'] = [sms_status_update]
            else:
                responses = {
                    'status_update': [sms_status_update]
                }
            sms.response = json.dumps(responses)
            sms.status = sms_status
            sms.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
