import datetime

from allauth.account.forms import SetPasswordForm
from allauth.account.models import EmailAddress
from dateutil import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from rolepermissions.checkers import has_permission
from rolepermissions.roles import assign_role

from .enums import OTPStatus
from .models import Note, NotificationSetting, Notification, PasswordOTP
from .roles import AppPermissions
# Get the UserModel
from ..points.models import PointBadge, UserPoints, UserStatistics

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
        exclude = ['creation_time', 'last_update_time']

    def create(self, validated_data):
        setting, created = NotificationSetting.objects.update_or_create(
            user=validated_data.get('user', None),
            defaults=validated_data)
        return setting


class UserSerializer(serializers.ModelSerializer):
    email_verified = serializers.SerializerMethodField('is_email_verified')
    permissions = serializers.SerializerMethodField('get_permissions')
    notification_settings = NotificationSettingSerializer(source='notification_setting', read_only=True)
    age = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        read_only_fields = ['email_verified', 'phone_verified', 'photo_url']
        fields = ['id', 'email', 'name', 'birthday', 'phone', 'gender', 'country', 'address', 'photo',
                  'email_verified', 'phone_verified', 'permissions', 'notification_settings', 'age', 'photo_url',
                  'membership']
        extra_kwargs = {
            'photo': {'required': False, 'allow_null': True, 'write_only': True},
            'notification_settings': {'required': False, 'allow_null': True, 'read_only': True},
        }

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

    def get_age(self, user):
        if not user or not user.birthday:
            return None
        # Get the current date
        now = datetime.datetime.utcnow()
        now = now.date()

        # Get the difference between the current date and the birthday
        age = relativedelta.relativedelta(now, user.birthday)
        age = age.years
        return age

    def get_photo_url(self, user):
        if self.context.get('request') is None: return None
        url = self.context.get('request').build_absolute_uri(user.photo_url) if user.photo_url else None
        return url if url else None


class UserProfileSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        read_only_fields = ['photo_url']
        fields = ['id', 'name', 'photo_url']

    def get_photo_url(self, user):
        if self.context.get('request') is None: return None
        url = self.context.get('request').build_absolute_uri(user.photo_url) if user.photo_url else None
        return url if url else None


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

    def create(self, validated_data):
        note = super(NoteSerializer, self).create(validated_data)
        UserStatistics.objects.update_notes_and_highlights(note.user)
        return note

    def update(self, instance, validated_data):
        note = super(NoteSerializer, self).update(instance, validated_data)
        UserStatistics.objects.update_notes_and_highlights(note.user)
        return note


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Notification
        fields = ['id', 'title', 'type', 'user', 'message', 'read', 'creation_time']
        read_only_fields = ['id', 'title', 'type', 'user', 'message', 'creation_time']


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()

    password_reset_form_class = PasswordResetForm

    def get_email_options(self):
        """Override this method to change default e-mail options"""
        return {}

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    def save(self):
        request = self.context.get('request')
        current_site = get_current_site(request)
        # Set some values to trigger the send_email method.
        code = None
        try:
            user = UserModel._default_manager.get(email=self.data['email'])
            code = PasswordOTP.objects.generate(user.id).code
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            # raise ValidationError({'email': ['Invalid value']})
            pass
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,

            'subject_template_name': 'account/email/password_reset_key_subject.txt',
            'email_template_name': 'account/email/password_reset_key_message.txt',
            'html_email_template_name': 'account/email/password_reset_key_message.html',
            'extra_email_context': {
                'key': code,
                "current_site": current_site,
            }
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    email = serializers.EmailField()
    token = serializers.CharField()

    set_password_form_class = SetPasswordForm

    def custom_validation(self, attrs):
        pass

    def validate(self, attrs):
        self._errors = {}

        # Decode the uidb64 to uid to get User object
        try:
            self.user = UserModel._default_manager.get(email=attrs['email'])
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise ValidationError({'email': ['Invalid value']})

        self.custom_validation(attrs)
        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data={'password1': attrs['new_password1'], 'password2': attrs['new_password2']}
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        confirm = PasswordOTP.objects.verify(self.user.id, attrs['token'])
        if confirm.__eq__(OTPStatus.Verified):
            return attrs
        if confirm in [OTPStatus.Expired, OTPStatus.Used]:
            raise ValidationError({'token': ['Code expired']})
        raise ValidationError({'token': ['Invalid value']})

    def save(self):
        return self.set_password_form.save()
