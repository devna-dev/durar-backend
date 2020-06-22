from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.sites.shortcuts import get_current_site

from .models import EmailOTP


class UserAdapter(DefaultAccountAdapter):

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        current_site = get_current_site(request)
        # activate_url = self.get_email_confirmation_url(
        #     request,
        #     emailconfirmation)
        otp = EmailOTP.objects.generate(emailconfirmation.email_address.user.id)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "current_site": current_site,
            "key": otp.code,
        }
        if signup:
            email_template = 'account/email/email_confirmation_signup'
        else:
            email_template = 'account/email/email_confirmation'
        self.send_mail(email_template,
                       emailconfirmation.email_address.email,
                       ctx)
