from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from pyfcm import FCMNotification

from .models import Notification, NotificationSetting


class FCMService(object):

    @staticmethod
    def send(title: str, message: str, device_id=None, device_ids=None):
        if not device_id and not device_ids:
            return None
        result = None
        push_service = FCMNotification(api_key=settings.FCM_API_KEY)

        # OR initialize with proxies

        # Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging

        if device_id:
            result = push_service.notify_single_device(registration_id=device_id, message_title=str(title),
                                                       message_body=str(message))
            print(result)
        elif device_ids:  # Send to multiple devices by passing a list of ids.
            result = push_service.notify_multiple_devices(registration_ids=device_ids, message_title=str(title),
                                                          message_body=str(message))
            print(result)
        return result

    @staticmethod
    def notify_book_approved(user):
        device_id = FCMService._get_device_id(user)
        if not device_id or not user.notification_setting.book_approved:
            return None
        return FCMService.notify(_('Book Approved'), _('Congratulations, your book has been approved'), 'book_approved',
                                 user)

    @staticmethod
    def notify_paper_approved(user):
        device_id = FCMService._get_device_id(user)
        if not device_id or not user.notification_setting.paper_approved:
            return None
        return FCMService.notify(_('Paper Approved'), _('Congratulations, your paper has been approved'),
                                 'paper_approved',
                                 user)

    @staticmethod
    def notify_thesis_approved(user):
        device_id = FCMService._get_device_id(user)
        if not device_id or not user.notification_setting.thesis_approved:
            return None
        return FCMService.notify(_('Thesis Approved'), _('Congratulations, your thesis has been approved'),
                                 'thesis_approved',
                                 user)

    @staticmethod
    def notify_audio_approved(user):
        device_id = FCMService._get_device_id(user)
        if not device_id or not user.notification_setting.audio_approved:
            return None
        return FCMService.notify(_('Audio Approved'), _('Congratulations, your audio file has been approved'),
                                 'audio_approved', user)

    @staticmethod
    def notify_payment_success(user):
        device_id = FCMService._get_device_id(user)
        if not device_id or not user.notification_setting.payment_processed:
            return None
        return FCMService.notify(_('Payment success'), _('Congratulations, your payment has been accepted'),
                                 'payment_success',
                                 user)

    @staticmethod
    def notify_payment_rejected(user):
        device_id = FCMService._get_device_id(user)
        if not device_id or not user.notification_setting.payment_processed:
            return None
        return FCMService.notify(_('Payment rejected'),
                                 _(
                                     'Unfortunately your payment has been rejected, please contact the administrator for more details'),
                                 'payment_rejected',
                                 user)

    @staticmethod
    def notify_support_request(user):
        device_id = FCMService._get_device_id(user)
        if not device_id or not user.notification_setting.support_requested:
            return None
        return FCMService.notify(_('Support Request'),
                                 _('Your support request has been recorded, we will reply as soon as possible'),
                                 'support_request', user)

    @staticmethod
    def notify_points_awarded(user, points):
        device_id = FCMService._get_device_id(user)
        if not device_id or not user.notification_setting.points_awarded:
            return None
        return FCMService.notify(_('Points awarded'), _('Congratulations, you earned {points}'.format(points=points)),
                                 'points_awarded',
                                 user)

    @staticmethod
    def notify_custom_notification(user_ids, notification: Notification):
        return FCMService.notify(notification.title, notification.message, 'admin_notification', user_ids=user_ids)

    @staticmethod
    def notify(title: str, message: str, notification_type: str, user=None, user_ids=None, send=True):
        device_ids = []
        device_id = None
        if not title or not message:
            return None
        if user:
            device_id = FCMService._get_device_id(user)
            Notification.objects.create(title=title, message=message, user_id=user.id, type=notification_type)
        elif user_ids:
            device_ids = NotificationSetting.objects.filter(user_id__in=user_ids, enabled=True,
                                                            admin_notifications=True).values_list('device_id',
                                                                                                  flat=True)
            Notification.objects.bulk_create(list(
                [Notification(title=title, message=message, user_id=pk, type=notification_type) for pk in
                 user_ids]))
            if not device_ids:
                return None
        elif device_id:
            pass
        else:
            return None
        if send:
            try:
                return FCMService.send(title, message, device_id=device_id, device_ids=device_ids)
            except:
                pass
        return None

    @staticmethod
    def _get_device_id(user):
        if user.id and hasattr(user,
                               'notification_setting') and user.notification_setting.device_id and user.notification_setting.enabled:
            return user.notification_setting.device_id
        return None
