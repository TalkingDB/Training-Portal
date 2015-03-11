from django.db import models
from django.core.urlresolvers import reverse

class ProgressStats(models.Model):
    started = models.DateTimeField()
    done = models.DateTimeField()
    step = models.TextField()
    percentage_done = models.FloatField()
    remaining_time = models.FloatField()