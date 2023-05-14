from datetime import datetime, timedelta, timezone

from django.core.management.base import BaseCommand

from users.models import Profile, LearnedWords


class Command(BaseCommand):
    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        now = datetime.now(timezone.utc)
        for profile in profiles:
            rating = 0
            words = LearnedWords.objects.all()
            for word in words:
                timepassed = now - word.last_repeating
                word.forgetting_coef = (1 + 2 ** word.repeating * profile.learning_level *
                                        timepassed.total_seconds()/timedelta(hours=1)
                                        .total_seconds()) ** (-1 / (2 ** word.repeating))
                rating += word.forgetting_coef * 10
                word.save()
            profile.rating = rating
            profile.save()
