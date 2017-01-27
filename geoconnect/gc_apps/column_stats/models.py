from django.db import models

from gc_apps.core.models import TimeStampedModel


class BaseColumnStats(TimeStampedModel):
    
    name = models.CharField(max_length=255)
    num_vals = models.IntegerField()

    num_blanks = models.IntegerField()
    num_errs = models.IntegerField()

    class Meta:
        abstract = True



class StringColumnStats(BaseColumnStats):
    """Store statistics related to string values"""
    frequency_dict = models.TextField(blank=True, help_text='python dict stored as a string')
