from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from home.models import EngRusDict
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpeg', upload_to='profile_pics')
    learning_level = models.FloatField(default=1.0)
    rating = models.DecimalField(default=0, max_digits=15, decimal_places=6)
    learning_word = models.CharField(default="")
    repeating_word = models.CharField(default="")

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, **kwargs):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class LearnedWords(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(EngRusDict, on_delete=models.PROTECT)
    forgetting_coef = models.FloatField(default=1.0)
    last_repeating = models.DateTimeField()
    repeating = models.IntegerField(default=1.0)

    def __str__(self):
        return f'User_id: {str(self.user_id)}, Word: {self.word}, coef: {self.forgetting_coef}'

    def save(self, **kwargs):
        super().save()

    class Meta:
        verbose_name = 'LearnedWord'
        verbose_name_plural = 'LearnedWords'
