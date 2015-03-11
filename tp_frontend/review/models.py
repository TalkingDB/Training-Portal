from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
 
class Entity(models.Model):
    frequency = models.IntegerField()
    entity_url = models.CharField(max_length=100)
    surface_text = models.TextField()
    processed = models.BooleanField(default=False)
    occupied = models.BooleanField(default=False)

class EntityText(models.Model):
    entity_url = models.CharField(max_length=100)
    text = models.CharField(max_length=100)
    text_type = models.IntegerField()


class NoTag(models.Model):
    label = models.CharField(max_length=100)
    frequency = models.IntegerField()

class Result(models.Model):
    entity_url = models.CharField(max_length=100)
    text = models.CharField(max_length=100)
    text_id = models.TextField()
    user_defined = models.BooleanField()
    user = models.ForeignKey(User)

class Progress(models.Model):
    name = models.CharField(max_length=100)
    progress = models.BooleanField(default=False)