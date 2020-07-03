from .models import UserPoints, PointSetting
from ..payments.models import Payment
from ..users.services import FCMService


class PointsService(object):
    def __init__(self):
        self.settings = PointSetting.objects.first()

    def book_approval_award(self, user, book_id):
        if self.settings and self.settings.book_approved and not PointsService._awarded(book_id, 'book_approved',
                                                                                        user.id):
            points = UserPoints.objects.create(user=user, point_num=self.settings.book_approved, action_id=book_id,
                                               type='book_approved')
            FCMService.notify_points_awarded(user, points.point_num)

    def paper_approval_award(self, user, paper_id):
        if self.settings and self.settings.paper_approved and not PointsService._awarded(paper_id, 'paper_approved',
                                                                                         user.id):
            points = UserPoints.objects.create(user=user, point_num=self.settings.paper_approved, action_id=paper_id,
                                               type='paper_approved')
            FCMService.notify_points_awarded(user, points.point_num)

    def thesis_approved_award(self, user, thesis_id):
        if self.settings and self.settings.thesis_approved and not PointsService._awarded(thesis_id, 'thesis_approved',
                                                                                          user.id):
            points = UserPoints.objects.create(user=user, point_num=self.settings.thesis_approved, action_id=thesis_id,
                                               type='thesis_approved')
            FCMService.notify_points_awarded(user, points.point_num)

    def audio_approved_award(self, user, audio_id):
        if self.settings and self.settings.audio_approved and not PointsService._awarded(audio_id, 'audio_approved',
                                                                                         user.id):
            points = UserPoints.objects.create(user=user, point_num=self.settings.audio_approved, action_id=audio_id,
                                               type='audio_approved')
            FCMService.notify_points_awarded(user, points.point_num)

    def donation_award(self, user, payment: Payment):
        if self.settings and self.settings.donation and not PointsService._awarded(payment.id, 'donation',
                                                                                   user.id):
            total = self.settings.donation * round(payment.amount)
            points = UserPoints.objects.create(user=user, point_num=total, action_id=payment.id, type='donation')
            FCMService.notify_points_awarded(user, points.point_num)

    def reload_settings(self):
        self.settings = PointSetting.objects.first()

    @staticmethod
    def _awarded(action_id, award_type, user_id):
        return UserPoints.objects.filter(action_id=action_id, type=award_type, user_id=user_id).exists()
