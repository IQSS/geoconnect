"""
- Maintenance mode flag
  - Core code from Senko Rasic <senko.rasic@goodcode.io>
  - https://goodcode.io/articles/django-singleton-models/
"""
from django.db import models
from model_utils.models import TimeStampedModel

class MaintenanceMode(TimeStampedModel):
    """Put the entire app into maintance mode
      This is a system-wide user-editable settings.
    """
    name = models.CharField(max_length=255,
                            default='Maintenance Mode')

    is_active = models.BooleanField(default=False)

    message = models.TextField(\
                    blank=True,
                    help_text=('Message to Display on Page.'
                               '  When available, displayed instead of a template.'))

    template_name = models.CharField(\
                        max_length=255,
                        default='content_pages/maintenance_message.html',
                        help_text=('Template with HTML snippet to'
                                   ' display.  Note: This'
                                   ' field is ignored if a "message"'
                                   ' is available.'))

    end_datetime = models.DateTimeField(\
                    blank=True,
                    null=True,
                    help_text=('End datetime to display within the template.'
                               ' Important: Maintenance mode NEEDS TO BE'
                               ' TURNED OFF *manually*.  This date/time is for'
                               ' display purposes only.'))

    def save(self, *args, **kwargs):
        """
        Save object to the database. Removes all other entries if there
        are any.
        """
        self.__class__.objects.exclude(id=self.id).delete()
        super(MaintenanceMode, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Maintenance Mode'
        db_table = 'content_pages'

    @classmethod
    def load(cls):
        """
        Load object from the database. Failing that, create a new empty
        (default) instance of the object and return it (without saving it
        to the database).
        """
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()
