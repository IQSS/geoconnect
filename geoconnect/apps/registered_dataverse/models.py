from django.db import models

from apps.core.models import TimeStampedModel


class RegisteredDataverse(TimeStampedModel):
    """
    Dataverses that are allowed to use this "Geoconnect" installation
    """
    name = models.CharField(unique=True, max_length=255)
    dataverse_url = models.URLField(unique=True, help_text='No trailing slash. Examples: "http://dvn-build.hmdc.harvard.edu", "https://dataverse-demo.iq.harvard.edu"')
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text='optional')

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.dataverse_url)

    def save(self, *args, **kwargs):

        while self.dataverse_url.endswith('/'):
            self.dataverse_url = self.dataverse_url[:-1]

        super(RegisteredDataverse, self).save(*args, **kwargs)

    class Meta:
        ordering = ('name',)