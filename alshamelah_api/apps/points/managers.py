from datetime import datetime

from django.db import models, connection
from django.db.models import Sum, F, FloatField

from .models import Achievement, UserAchievement
from ..books.models import ListenBook
from ..users.models import User


class UserStatisticsManager(models.Manager):

    def read(self, user_id, book_id, page):
        data = self.get_data(user_id)
        book_pages = data.reads
        if not book_pages:
            book_pages = {book_id: [page]}
            data.page_read_count += 1
            data.book_read_count += 1
        elif book_id not in book_pages.keys():
            book_pages[book_id] = [page]
            data.page_read_count += 1
            data.book_read_count += 1
        elif page not in book_pages[book_id]:
            book_pages[book_id].append(page)
            data.page_read_count += 1
        data.reads = book_pages
        if not data.daily_read:
            data.daily_read = {self.today(): [book_id]}
        elif self.today() in data.daily_read.keys() and book_id not in data.daily_read[self.today()]:
            data.daily_read[self.today()].append(book_id)
        elif self.today() not in data.daily_read.keys():
            data.daily_read[self.today()] = [book_id]
        if len(data.daily_read[self.today()]) > data.max_daily_read:
            data.max_daily_read = len(data.daily_read[self.today()])
        data.save()

        # ------------------------- achievement checks ----------------------------------
        achievement_types = ['pages_read_number', 'books_read_number', 'daily_books_read_number']
        achievement_settings = Achievement.objects.filter(type__in=achievement_types)
        pages_read = achievement_settings.get(type='pages_read_number')
        books_read = achievement_settings.get(type='books_read_number')
        daily_books_read = achievement_settings.get(type='daily_books_read_number')

        if pages_read:
            pages_ach = UserAchievement(user_id=user_id, achievement_id=pages_read.id)
            if data.page_read_count >= pages_read.diamond:
                pages_ach.category = 'diamond'
            elif data.page_read_count >= pages_read.gold:
                pages_ach.category = 'gold'
            elif data.page_read_count >= pages_read.silver:
                pages_ach.category = 'silver'
            elif data.page_read_count >= pages_read.bronze:
                pages_ach.category = 'bronze'
            if pages_ach.category:
                UserAchievement.objects.update_or_create(user_id=user_id, achievement_id=pages_read.id,
                                                         defaults={'category': pages_ach.category,
                                                                   'points': data.page_read_count})
        if books_read:
            books_ach = UserAchievement(user_id=user_id, achievement_id=books_read.id)
            if data.book_read_count >= books_read.diamond:
                books_ach.category = 'diamond'
            elif data.book_read_count >= books_read.gold:
                books_ach.category = 'gold'
            elif data.book_read_count >= books_read.silver:
                books_ach.category = 'silver'
            elif data.book_read_count >= books_read.bronze:
                books_ach.category = 'bronze'
            if books_ach.category:
                UserAchievement.objects.update_or_create(user_id=user_id, achievement_id=books_read.id,
                                                         defaults={'category': books_ach.category,
                                                                   'points': data.book_read_count})
        if daily_books_read:
            daily_books_ach = UserAchievement(user_id=user_id, achievement_id=daily_books_read.id)
            if data.max_daily_read >= daily_books_read.diamond:
                daily_books_ach.category = 'diamond'
            elif data.max_daily_read >= daily_books_read.gold:
                daily_books_ach.category = 'gold'
            elif data.max_daily_read >= daily_books_read.silver:
                daily_books_ach.category = 'silver'
            elif data.max_daily_read >= daily_books_read.bronze:
                daily_books_ach.category = 'bronze'
            if daily_books_ach.category:
                UserAchievement.objects.update_or_create(user_id=user_id, achievement_id=daily_books_read.id,
                                                         defaults={'category': daily_books_ach.category,
                                                                   'points': data.max_daily_read})

    def listen(self, user_id, book_id):
        data = self.get_data(user_id)

        if not data.daily_listen:
            data.daily_listen = {self.today(): [book_id]}
        elif self.today() in data.daily_listen.keys() and book_id not in data.daily_listen[self.today()]:
            data.daily_listen[self.today()].append(book_id)
        elif self.today() not in data.daily_listen.keys():
            data.daily_listen[self.today()] = [book_id]
        if len(data.daily_listen[self.today()]) > data.max_daily_listen:
            data.max_daily_listen = len(data.daily_listen[self.today()])

        book_listened = ListenBook.objects.prefetch_related('book__book_media', 'file_progress') \
            .filter(user_id=user_id, file_progress__progress__gt=0)
        data.book_listened_count = book_listened.count()
        total_minutes_listened = book_listened.aggregate(
            total_minutes=Sum((F('file_progress__progress') * F('file_progress__audio__duration')) / 100,
                              output_field=FloatField()))
        data.minutes_listened = total_minutes_listened['total_minutes'] if total_minutes_listened[
            'total_minutes'] else 0
        data.save()

        # ------------------------- achievement checks ----------------------------------
        achievement_types = ['minutes_listened', 'books_listen_number', 'daily_books_listen_number']
        achievement_settings = Achievement.objects.filter(type__in=achievement_types)
        minutes_listened = achievement_settings.get(type='minutes_listened')
        books_listened = achievement_settings.get(type='books_listen_number')
        daily_books_listened = achievement_settings.get(type='daily_books_listen_number')

        if minutes_listened:
            pages_ach = UserAchievement(user_id=user_id, achievement_id=minutes_listened.id)
            if data.minutes_listened >= minutes_listened.diamond:
                pages_ach.category = 'diamond'
            elif data.minutes_listened >= minutes_listened.gold:
                pages_ach.category = 'gold'
            elif data.minutes_listened >= minutes_listened.silver:
                pages_ach.category = 'silver'
            elif data.minutes_listened >= minutes_listened.bronze:
                pages_ach.category = 'bronze'
            if pages_ach.category:
                UserAchievement.objects.update_or_create(user_id=user_id, achievement_id=minutes_listened.id,
                                                         defaults={'category': pages_ach.category,
                                                                   'points': data.minutes_listened})
        if books_listened:
            books_ach = UserAchievement(user_id=user_id, achievement_id=books_listened.id)
            if data.book_listened_count >= books_listened.diamond:
                books_ach.category = 'diamond'
            elif data.book_listened_count >= books_listened.gold:
                books_ach.category = 'gold'
            elif data.book_listened_count >= books_listened.silver:
                books_ach.category = 'silver'
            elif data.book_listened_count >= books_listened.bronze:
                books_ach.category = 'bronze'
            if books_ach.category:
                UserAchievement.objects.update_or_create(user_id=user_id, achievement_id=books_listened.id,
                                                         defaults={'category': books_ach.category,
                                                                   'points': data.book_listened_count})
        if daily_books_listened:
            daily_books_ach = UserAchievement(user_id=user_id, achievement_id=daily_books_listened.id)
            if data.max_daily_listen >= daily_books_listened.diamond:
                daily_books_ach.category = 'diamond'
            elif data.max_daily_listen >= daily_books_listened.gold:
                daily_books_ach.category = 'gold'
            elif data.max_daily_listen >= daily_books_listened.silver:
                daily_books_ach.category = 'silver'
            elif data.max_daily_listen >= daily_books_listened.bronze:
                daily_books_ach.category = 'bronze'
            if daily_books_ach.category:
                UserAchievement.objects.update_or_create(user_id=user_id, achievement_id=daily_books_listened.id,
                                                         defaults={'category': daily_books_ach.category,
                                                                   'points': data.max_daily_listen})

    def update_finished_read(self, user_id):
        data = self.get_data(user_id)
        user = User.objects.get(pk=user_id)
        finished_books = user.reads.filter(finished=True)
        data.book_finished_count = finished_books.count()
        data.max_book_pages_read = finished_books.order_by('-book__page_count').first().book.page_count
        data.save()

        # ------------------------- achievement checks ----------------------------------
        achievement_types = ['books_with_most_pages_finished', 'books_read_finished']
        achievement_settings = Achievement.objects.filter(type__in=achievement_types)
        most_pages_finished = achievement_settings.get(type='books_with_most_pages_finished')
        finished = achievement_settings.get(type='books_read_finished')

        if most_pages_finished:
            most_pages_ach = UserAchievement(user_id=user_id, achievement_id=most_pages_finished.id)
            if data.max_book_pages_read >= most_pages_finished.diamond:
                most_pages_ach.category = 'diamond'
            elif data.max_book_pages_read >= most_pages_finished.gold:
                most_pages_ach.category = 'gold'
            elif data.max_book_pages_read >= most_pages_finished.silver:
                most_pages_ach.category = 'silver'
            elif data.max_book_pages_read >= most_pages_finished.bronze:
                most_pages_ach.category = 'bronze'
            if most_pages_ach.category:
                UserAchievement.objects.update_or_create(user_id=user_id, achievement_id=most_pages_finished.id,
                                                         defaults={'category': most_pages_ach.category,
                                                                   'points': data.max_book_pages_read})

        if finished:
            book_finished_ach = UserAchievement(user_id=user_id, achievement_id=finished.id)
            if data.book_finished_count >= finished.diamond:
                book_finished_ach.category = 'diamond'
            elif data.book_finished_count >= finished.gold:
                book_finished_ach.category = 'gold'
            elif data.book_finished_count >= finished.silver:
                book_finished_ach.category = 'silver'
            elif data.book_finished_count >= finished.bronze:
                book_finished_ach.category = 'bronze'
            if book_finished_ach.category:
                UserAchievement.objects.update_or_create(user_id=user_id, achievement_id=finished.id,
                                                         defaults={'category': book_finished_ach.category,
                                                                   'points': data.book_finished_count})

    def update_finished_listen(self, user):
        data = self.get_data(user.id)
        finished_audio_books = user.listens.filter(finished=True)
        data.audio_book_finished_count = finished_audio_books.count()
        data.max_book_audio_minutes_listened = finished_audio_books.annotate(
            total_minutes=Sum('book__book_media__duration')).order_by('-total_minutes').first().total_minutes
        data.save()

        # ------------------------- achievement checks ----------------------------------
        achievement_types = ['books_with_most_minutes_finished', 'books_listened']
        achievement_settings = Achievement.objects.filter(type__in=achievement_types)
        most_minutes_finished = achievement_settings.get(type='books_with_most_minutes_finished')
        finished = achievement_settings.get(type='books_listened')

        if most_minutes_finished:
            most_minutes_ach = UserAchievement(user_id=user.id, achievement_id=most_minutes_finished.id)
            if data.max_book_audio_minutes_listened >= most_minutes_finished.diamond:
                most_minutes_ach.category = 'diamond'
            elif data.max_book_audio_minutes_listened >= most_minutes_finished.gold:
                most_minutes_ach.category = 'gold'
            elif data.max_book_audio_minutes_listened >= most_minutes_finished.silver:
                most_minutes_ach.category = 'silver'
            elif data.max_book_audio_minutes_listened >= most_minutes_finished.bronze:
                most_minutes_ach.category = 'bronze'
            if most_minutes_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=most_minutes_finished.id,
                                                         defaults={'category': most_minutes_ach.category,
                                                                   'points': data.max_book_audio_minutes_listened})

        if finished:
            book_finished_ach = UserAchievement(user_id=user.id, achievement_id=finished.id)
            if data.audio_book_finished_count >= finished.diamond:
                book_finished_ach.category = 'diamond'
            elif data.audio_book_finished_count >= finished.gold:
                book_finished_ach.category = 'gold'
            elif data.audio_book_finished_count >= finished.silver:
                book_finished_ach.category = 'silver'
            elif data.audio_book_finished_count >= finished.bronze:
                book_finished_ach.category = 'bronze'
            if book_finished_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=finished.id,
                                                         defaults={'category': book_finished_ach.category,
                                                                   'points': data.audio_book_finished_count})

    def update_reviews(self, user):
        data = self.get_data(user.id)
        count = user.reviews.filter(rating__isnull=False).count()
        if count > data.book_rate_count:
            data.book_rate_count = count
        count = user.reviews.filter(comment__isnull=False).count()
        if count > data.book_review_count:
            data.book_review_count = count
        data.save()

        # ------------------------- achievement checks ----------------------------------
        rate_achievement = Achievement.objects.get(type='rating_book')
        review_achievement = Achievement.objects.get(type='writing_review')

        if rate_achievement:
            rate_ach = UserAchievement(user_id=user.id, achievement_id=rate_achievement.id)
            if data.book_rate_count >= rate_achievement.diamond:
                rate_ach.category = 'diamond'
            elif data.book_rate_count >= rate_achievement.gold:
                rate_ach.category = 'gold'
            elif data.book_rate_count >= rate_achievement.silver:
                rate_ach.category = 'silver'
            elif data.book_rate_count >= rate_achievement.bronze:
                rate_ach.category = 'bronze'
            if rate_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=rate_achievement.id,
                                                         defaults={'category': rate_ach.category,
                                                                   'points': data.book_rate_count})
        if review_achievement:
            review_ach = UserAchievement(user_id=user.id, achievement_id=rate_achievement.id)
            if data.book_review_count >= rate_achievement.diamond:
                review_ach.category = 'diamond'
            elif data.book_review_count >= rate_achievement.gold:
                review_ach.category = 'gold'
            elif data.book_review_count >= rate_achievement.silver:
                review_ach.category = 'silver'
            elif data.book_review_count >= rate_achievement.bronze:
                review_ach.category = 'bronze'
            if review_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=rate_achievement.id,
                                                         defaults={'category': review_ach.category,
                                                                   'points': data.book_review_count})

    def update_notes_and_highlights(self, user):
        data = self.get_data(user.id)
        count = user.book_notes.filter(note__isnull=False).count()
        if count > data.book_note_count:
            data.book_note_count = count
        count = user.book_notes.filter(note__isnull=True).count()
        if count > data.book_highlight_count:
            data.book_highlight_count = count
        count = user.notes.filter(note__isnull=False).count()
        if count > data.user_note_count:
            data.user_note_count = count
        data.save()
        total = data.user_note_count + data.book_note_count
        # ------------------------- achievement checks ----------------------------------
        notes_achievement = Achievement.objects.get(type='writing_note')
        highlight_achievement = Achievement.objects.get(type='highlighting_text')

        if notes_achievement:
            note_ach = UserAchievement(user_id=user.id, achievement_id=notes_achievement.id)
            if total >= notes_achievement.diamond:
                note_ach.category = 'diamond'
            elif total >= notes_achievement.gold:
                note_ach.category = 'gold'
            elif total >= notes_achievement.silver:
                note_ach.category = 'silver'
            elif total >= notes_achievement.bronze:
                note_ach.category = 'bronze'
            if note_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=notes_achievement.id,
                                                         defaults={'category': note_ach.category,
                                                                   'points': total})

        if highlight_achievement:
            highlight_ach = UserAchievement(user_id=user.id, achievement_id=highlight_achievement.id)
            if data.book_highlight_count >= highlight_achievement.diamond:
                highlight_ach.category = 'diamond'
            elif data.book_highlight_count >= highlight_achievement.gold:
                highlight_ach.category = 'gold'
            elif data.book_highlight_count >= highlight_achievement.silver:
                highlight_ach.category = 'silver'
            elif data.book_highlight_count >= highlight_achievement.bronze:
                highlight_ach.category = 'bronze'
            if highlight_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=highlight_achievement.id,
                                                         defaults={'category': highlight_ach.category,
                                                                   'points': data.book_highlight_count})

    def update_bookmarks(self, user):
        data = self.get_data(user.id)
        count = user.book_marks.filter(page__isnull=False).count()
        if count > data.book_mark_count:
            data.book_mark_count = count
        data.save()
        # ------------------------- achievement checks ----------------------------------
        bookmarks_achievement = Achievement.objects.get(type='making_bookmark')

        if bookmarks_achievement:
            bookmark_ach = UserAchievement(user_id=user.id, achievement_id=bookmarks_achievement.id)
            if data.book_mark_count >= bookmarks_achievement.diamond:
                bookmark_ach.category = 'diamond'
            elif data.book_mark_count >= bookmarks_achievement.gold:
                bookmark_ach.category = 'gold'
            elif data.book_mark_count >= bookmarks_achievement.silver:
                bookmark_ach.category = 'silver'
            elif data.book_mark_count >= bookmarks_achievement.bronze:
                bookmark_ach.category = 'bronze'
            if bookmark_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=bookmarks_achievement.id,
                                                         defaults={'category': bookmark_ach.category,
                                                                   'points': data.book_mark_count})

    def donation(self, user):
        data = self.get_data(user.id)
        data.donation_count = user.payments.filter(status='success').count()
        data.save()

        # ------------------------- achievement checks ----------------------------------
        donation_achievement = Achievement.objects.get(type='donation')

        if donation_achievement:
            donation_ach = UserAchievement(user_id=user.id, achievement_id=donation_achievement.id)
            if data.donation_count >= donation_achievement.diamond:
                donation_ach.category = 'diamond'
            elif data.donation_count >= donation_achievement.gold:
                donation_ach.category = 'gold'
            elif data.donation_count >= donation_achievement.silver:
                donation_ach.category = 'silver'
            elif data.donation_count >= donation_achievement.bronze:
                donation_ach.category = 'bronze'
            if donation_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=donation_achievement.id,
                                                         defaults={'category': donation_ach.category,
                                                                   'points': data.donation_count})

    def share_app(self, user):
        data = self.get_data(user.id)
        data.app_share_count += 1
        data.save()

        # ------------------------- achievement checks ----------------------------------
        share_app_achievement = Achievement.objects.get(type='share_app')

        if share_app_achievement:
            share_app_ach = UserAchievement(user_id=user.id, achievement_id=share_app_achievement.id)
            if data.app_share_count >= share_app_achievement.diamond:
                share_app_ach.category = 'diamond'
            elif data.app_share_count >= share_app_achievement.gold:
                share_app_ach.category = 'gold'
            elif data.app_share_count >= share_app_achievement.silver:
                share_app_ach.category = 'silver'
            elif data.app_share_count >= share_app_achievement.bronze:
                share_app_ach.category = 'bronze'
            if share_app_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=share_app_achievement.id,
                                                         defaults={'category': share_app_ach.category,
                                                                   'points': data.app_share_count})

    def share_book(self, user):
        data = self.get_data(user.id)
        data.book_share_count += 1
        data.save()

        # ------------------------- achievement checks ----------------------------------
        share_achievement = Achievement.objects.get(type='share_book')

        if share_achievement:
            share_ach = UserAchievement(user_id=user.id, achievement_id=share_achievement.id)
            if data.book_share_count >= share_achievement.diamond:
                share_ach.category = 'diamond'
            elif data.book_share_count >= share_achievement.gold:
                share_ach.category = 'gold'
            elif data.book_share_count >= share_achievement.silver:
                share_ach.category = 'silver'
            elif data.book_share_count >= share_achievement.bronze:
                share_ach.category = 'bronze'
            if share_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=share_achievement.id,
                                                         defaults={'category': share_ach.category,
                                                                   'points': data.book_share_count})

    def share_lecture(self, user):
        data = self.get_data(user.id)
        data.lecture_share_count += 1
        data.save()

        # ------------------------- achievement checks ----------------------------------
        share_achievement = Achievement.objects.get(type='share_lecture')

        if share_achievement:
            share_ach = UserAchievement(user_id=user.id, achievement_id=share_achievement.id)
            if data.lecture_share_count >= share_achievement.diamond:
                share_ach.category = 'diamond'
            elif data.lecture_share_count >= share_achievement.gold:
                share_ach.category = 'gold'
            elif data.lecture_share_count >= share_achievement.silver:
                share_ach.category = 'silver'
            elif data.lecture_share_count >= share_achievement.bronze:
                share_ach.category = 'bronze'
            if share_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=share_achievement.id,
                                                         defaults={'category': share_ach.category,
                                                                   'points': data.lecture_share_count})

    def share_highlight(self, user):
        data = self.get_data(user.id)
        data.highlight_share_count += 1
        data.save()

        # ------------------------- achievement checks ----------------------------------
        share_achievement = Achievement.objects.get(type='share_highlight')

        if share_achievement:
            share_ach = UserAchievement(user_id=user.id, achievement_id=share_achievement.id)
            if data.highlight_share_count >= share_achievement.diamond:
                share_ach.category = 'diamond'
            elif data.highlight_share_count >= share_achievement.gold:
                share_ach.category = 'gold'
            elif data.highlight_share_count >= share_achievement.silver:
                share_ach.category = 'silver'
            elif data.highlight_share_count >= share_achievement.bronze:
                share_ach.category = 'bronze'
            if share_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=share_achievement.id,
                                                         defaults={'category': share_ach.category,
                                                                   'points': data.highlight_share_count})

    def consecutive_login(self, user):
        data = self.get_data(user.id)

        with connection.cursor() as cursor:
            cursor.execute("""
                WITH pomo_dates AS ( SELECT DISTINCT creation_time :: DATE created_date FROM users_dailylogin WHERE user_id = %s ),
                pomo_date_groups AS ( SELECT created_date, created_date :: DATE - CAST ( ROW_NUMBER ( ) OVER ( ORDER BY created_date ) AS INT ) AS grp FROM pomo_dates ) SELECT MAX
                ( created_date ) - MIN ( created_date ) + 1 AS consecutive_login 
                FROM
                    pomo_date_groups 
                GROUP BY
                    grp 
                ORDER BY
                    consecutive_login DESC 
                    LIMIT 1
            """, [user.id])
            row = cursor.fetchone()

        if row and len(row) > 0:
            data.max_consecutive_login_days = row[0]
            data.save()

        # ------------------------- achievement checks ----------------------------------
        consecutive_login_achievement = Achievement.objects.get(type='consecutive_daily_usage')

        if consecutive_login_achievement:
            consecutive_login_ach = UserAchievement(user_id=user.id, achievement_id=consecutive_login_achievement.id)
            if data.max_consecutive_login_days >= consecutive_login_achievement.diamond:
                consecutive_login_ach.category = 'diamond'
            elif data.max_consecutive_login_days >= consecutive_login_achievement.gold:
                consecutive_login_ach.category = 'gold'
            elif data.max_consecutive_login_days >= consecutive_login_achievement.silver:
                consecutive_login_ach.category = 'silver'
            elif data.max_consecutive_login_days >= consecutive_login_achievement.bronze:
                consecutive_login_ach.category = 'bronze'
            if consecutive_login_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id,
                                                         achievement_id=consecutive_login_achievement.id,
                                                         defaults={'category': consecutive_login_ach.category,
                                                                   'points': data.max_consecutive_login_days})

    def attend_lecture(self, user):
        data = self.get_data(user.id)
        data.lecture_attendance_count += 1
        data.save()

        # ------------------------- achievement checks ----------------------------------
        attendance_achievement = Achievement.objects.get(type='attending_lecture')

        if attendance_achievement:
            attendance_ach = UserAchievement(user_id=user.id, achievement_id=attendance_achievement.id)
            if data.lecture_attendance_count >= attendance_achievement.diamond:
                attendance_ach.category = 'diamond'
            elif data.lecture_attendance_count >= attendance_achievement.gold:
                attendance_ach.category = 'gold'
            elif data.lecture_attendance_count >= attendance_achievement.silver:
                attendance_ach.category = 'silver'
            elif data.lecture_attendance_count >= attendance_achievement.bronze:
                attendance_ach.category = 'bronze'
            if attendance_ach.category:
                UserAchievement.objects.update_or_create(user_id=user.id, achievement_id=attendance_achievement.id,
                                                         defaults={'category': attendance_ach.category,
                                                                   'points': data.lecture_attendance_count})

    def get_data(self, user_id):
        data = self.model.objects.filter(user_id=user_id).first()
        if not data:
            data = self.model.objects.create(user_id=user_id)
        return data

    @staticmethod
    def today():
        return str(datetime.now().date())
