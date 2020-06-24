from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import (
    logout as django_logout
)
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from munch import munchify
from rest_framework import viewsets, status, views, mixins
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .adapter import UserAdapter
from .enums import OTPStatus
from .models import EmailOTP, User, Note, NotificationSetting, Notification
from .permissions import CanConfirmEmail
from .serializers import UserSerializer, NoteSerializer, NotificationSerializer, NotificationSettingSerializer


# Create your views here.


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        return User.objects.filter(user_id=self.request.user.id)

    # def retrieve(self, request):
    #     return super(UserViewSet, self).retrieve(request, pk=request.user.id)


class ConfirmEmailView(views.APIView):
    permission_classes = [CanConfirmEmail]

    def put(self, *args, **kwargs):
        if not self.request.user or not self.request.user.id:
            return Response(_('Invalid request'),
                            status=status.HTTP_400_BAD_REQUEST)
        user_id = self.request.user.id
        self.object = confirmation = self.get_object()

        if confirmation == OTPStatus.Verified:
            email = EmailAddress.objects.filter(user_id=user_id, primary=True).first()
            email.verified = True
            email.save()
            return Response(True)
        if confirmation in [OTPStatus.Expired, OTPStatus.Used]:
            EmailOTP.objects.generate(user_id)
            email = EmailAddress.objects.filter(user_id=user_id, primary=True).first()
            if not email:
                return Response(_('Invalid verification code'),
                                status=status.HTTP_400_BAD_REQUEST)
            data = munchify({'email_address': email})
            UserAdapter(self.request).send_confirmation_mail(self.request, data, False)
            return Response(_('Verification code expired, we have sent another code to your email'),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(_('Invalid verification code'),
                        status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, queryset=None):
        key = self.kwargs['key']
        confirm = EmailOTP.objects.verify(self.request.user.id, key)
        return confirm

    queryset = EmailOTP.objects.all()


confirm_email = ConfirmEmailView.as_view()


class LogoutView(APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        if getattr(settings, 'REST_SESSION_LOGIN', True):
            django_logout(request)

        response = Response({"detail": _("Successfully logged out.")},
                            status=status.HTTP_200_OK)
        if getattr(settings, 'REST_USE_JWT', False):
            from rest_framework_jwt.settings import api_settings as jwt_settings
            if jwt_settings.JWT_AUTH_COOKIE:
                response.delete_cookie(jwt_settings.JWT_AUTH_COOKIE)
        return response


logout_view = LogoutView.as_view()


class UserNoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer

    def get_queryset(self):
        return Note.objects.filter(user_id=self.request.user.id)


class UserNotificationSettingViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSettingSerializer

    def get_queryset(self):
        return NotificationSetting.objects.filter(user_id=self.request.user.id)


class UserNotificationsViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user_id=self.request.user.id)
