from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['email', 'name', ]


admin.site.register(User, CustomUserAdmin)
registred = admin.site._registry.items()
admin.site.unregister(SocialToken)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialAccount)
