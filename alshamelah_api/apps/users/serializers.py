from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions
from rolepermissions.checkers import has_permission
from rolepermissions.roles import assign_role

from .models import Note, NotificationSetting, Notification
from .roles import AppPermissions

# Get the UserModel
UserModel = get_user_model()
try:
    from allauth.account import app_settings as allauth_settings
    from allauth.utils import (email_address_exists,
                               get_username_max_length)
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.socialaccount.helpers import complete_social_login
    from allauth.socialaccount.models import SocialAccount
    from allauth.socialaccount.providers.base import AuthProcess
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")


class NotificationSettingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = NotificationSetting
        fields = ['device_id', 'enabled', 'user', 'book_added', 'book_approved', 'audio_approved']

    def create(self, validated_data):
        setting, created = NotificationSetting.objects.update_or_create(
            user=validated_data.get('user', None),
            defaults=validated_data)
        return setting


class UserSerializer(serializers.ModelSerializer):
    email_verified = serializers.SerializerMethodField('is_email_verified')
    permissions = serializers.SerializerMethodField('get_permissions')
    notification_settings = NotificationSettingSerializer(source='notification_setting')

    class Meta:
        model = UserModel
        read_only_fields = ['email_verified', 'phone_verified']
        fields = ['id', 'email', 'name', 'birthday', 'phone', 'gender', 'country', 'address', 'photo',
                  'email_verified', 'phone_verified', 'permissions', 'notification_settings']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(make_password(password))
        user.save()
        assign_role(user, 'user')
        return user

    def is_email_verified(self, user):
        if user and user.id:
            email = EmailAddress.objects.filter(user_id=user.id, email=user.email).first()
            if email and email.verified: return True
        return False

    def get_permissions(self, user):
        return {
            'can_submit_book': has_permission(user, AppPermissions.submit_books),
            'can_submit_audio': has_permission(user, AppPermissions.submit_audio),
            'can_create_chatroom': has_permission(user, AppPermissions.create_chat_room),
        }


class LoginSerializer(serializers.Serializer):
    # username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        # username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            # if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
            user = self._validate_email(email, password)

            # Authentication through username
            # elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
            #     user = self._validate_username(username, password)

            # Authentication through either username or email
            # else:
            #     user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            username = None
            if email:
                try:
                    username = UserModel.objects.get(email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=True
    )
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password = serializers.CharField(write_only=True)
    passwordConfirm = serializers.CharField(write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password'] != data['passwordConfirm']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        data['password1'] = data['password']
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'name': self.validated_data.get('name', ''),
            'password': self.validated_data.get('password', ''),
            'password1': self.validated_data.get('password', ''),
            'email': self.validated_data.get('email', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()

        adapter.save_user(request, user, self)
        self.custom_signup(request, user)

        setup_user_email(request, user, [])
        assign_role(user, 'user')

        return user


class NoteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Note
        fields = ['id', 'note', 'user']


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Notification
        fields = ['id', 'title', 'type', 'user', 'message', 'read', 'creation_time']
        read_only_fields = ['id', 'title', 'type', 'user', 'message', 'creation_time']
