from django.db import models


class EngRusDict(models.Model):
    rus = models.CharField('rus')
    eng = models.CharField('eng')
    complexity = models.FloatField(default=1)

    def __str__(self):
        return self.rus + "-" + self.eng

