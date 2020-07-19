from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from rolepermissions.admin import RolePermissionsUserAdminMixin

from .forms import CustomUserChangeForm
from .models import CustomNotification
from .services import FCMService
from ..core.admin import BaseModelAdmin

User = get_user_model()


class CustomUserAdmin(RolePermissionsUserAdminMixin, UserAdmin):
    form = CustomUserChangeForm
    add_fieldsets = (
        (_('Account info'), {'fields': ('email', 'password1', 'password2')}),
        (_('Personal info'), {'fields': ('name', 'gender', 'birthday', 'country', 'address', 'phone', 'photo')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),  # , 'user_permissions'
        }),
    )
    readonly_fields = ('last_login', 'date_joined')
    exclude = ['user_permissions']
    fieldsets = (
        (None, {'fields': ('password', 'email')}),
        (_('Personal info'), {'fields': ('name', 'gender', 'birthday', 'country', 'address', 'phone', 'photo')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),  # , 'user_permissions'
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    model = User
    list_display = ['email', 'name', ]
    list_per_page = settings.ADMIN_LIST_PAGE_SIZE

    def get_queryset(self, request):
        if request.user.email == 'adhm_n4@yahoo.com':
            return super(CustomUserAdmin, self).get_queryset(request)
        return super(CustomUserAdmin, self).get_queryset(request).exclude(email='adhm_n4@yahoo.com')


@admin.register(CustomNotification)
class NotificationAdmin(BaseModelAdmin):
    list_display = (
        'id',
        'title',
        'message',
        'creation_time'
    )

    def has_change_permission(self, request, obj=None):
        return False

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "users":
            kwargs["queryset"] = User.objects.filter(notification_setting__isnull=False,
                                                     notification_setting__enabled=True,
                                                     notification_setting__admin_notifications=True)
        return super(NotificationAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if form.cleaned_data['users']:
            users = list(form.cleaned_data['users'].values_list('id', flat=True))
            FCMService.notify_custom_notification(users, obj)


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.unregister(EmailAddress)
admin.site.unregister(Token)
admin.site.unregister(Site)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialAccount)
