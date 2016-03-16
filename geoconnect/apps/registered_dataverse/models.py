from django.db import models
from django.template.defaultfilters import slugify

from apps.core.models import TimeStampedModel
from apps.layer_types.static_vals import DV_FILE_TYPE_CHOICES

class IncomingFileTypeSetting(TimeStampedModel):
    """
    Settings that determine whether handling for incoming Dataverse
    files is in place.  Show error message if handling not in place.

    Usage: when Dataverse has a "Map Data" button
    next to a file type that Geoconnect cannot yet handle.
    """
    name = models.CharField(unique=True,\
                    choices=DV_FILE_TYPE_CHOICES,\
                    max_length=255)
    active = models.BooleanField(default=True)

    inactive_display_note = models.TextField(blank=True\
            , help_text=('Displayed on landing page if '
                        'the IncomingFileType is not active'))
    slug = models.SlugField(blank=True, max_length=255)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # create the slug
        if self.name:
            self.slug = slugify(self.name)

        super(IncomingFileTypeSetting, self).save(*args, **kwargs)


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

        self.dataverse_url = self.dataverse_url.lower()

        super(RegisteredDataverse, self).save(*args, **kwargs)


    class Meta:
        ordering = ('name',)
