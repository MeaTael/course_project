from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from users.models import Profile, LearnedWords


class Command(BaseCommand):
    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        mails = []
        for profile in profiles:
            words = LearnedWords.objects.all()
            words_to_repeat = 0
            for word in words:
                if word.forgetting_coef < 0.8:
                    words_to_repeat += 1
                word.save()
            if words_to_repeat >= 5:
                mails.append(profile.user.email)
            profile.save()
        send_mail(
            "Вам необходимо повторить выученные слова",
            "У вас есть как минимум 5 слов, которые вы можете забыть в скором времени",
            "englearncp@mail.ru",
            mails
        )
