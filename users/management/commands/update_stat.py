from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from users.models import Profile

import json


class Command(BaseCommand):
    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        now = datetime.now()
        for profile in profiles:
            words = json.loads(profile.learned_words)
            for word in words:
                timepassed = now - datetime.strptime(words[word]['last_repeating'], '%d.%m.%Y %H:%M')
                words[word]['forgeting_coef'] = (1 + 2**words[word]['repeating'] * profile.learning_level * timepassed.total_seconds()/timedelta(hours=1).total_seconds())**(-1/(2**words[word]['repeating']))
            profile.learned_words = json.dumps(words)
            profile.save()
