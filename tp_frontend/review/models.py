from django.db import models

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    outfile = models.FileField(upload_to='output/%Y/%m/%d')