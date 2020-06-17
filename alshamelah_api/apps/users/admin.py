from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from rolepermissions.admin import RolePermissionsUserAdminMixin

from .forms import CustomUserCreationForm, CustomUserChangeForm

User = get_user_model()


class CustomUserAdmin(RolePermissionsUserAdminMixin, UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    readonly_fields = ('last_login', 'date_joined')
    exclude = ['user_permissions']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),  # , 'user_permissions'
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    model = User
    list_display = ['email', 'name', ]

    def get_form(self, request, obj=None, **kwargs):
        # Get form from original UserAdmin.
        form = super(CustomUserAdmin, self).get_form(request, obj, **kwargs)
        # if 'user_permissions' in form.base_fields:
        #     permissions = form.base_fields['user_permissions']
        #     role_permissions = {}
        #     role_permissions.update(UserRole.available_permissions)
        #     role_permissions.update(AdminRole.available_permissions)
        #
        #     permissions.queryset = permissions.queryset.filter(codename__in=list(role_permissions.keys()))
        return form


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.unregister(Token)
admin.site.unregister(Site)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialAccount)
