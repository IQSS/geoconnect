from apps.registered_dataverse.models import IncomingFileTypeSetting



def is_setting_active(setting_slug):
    """
    Check if a setting is active
    """
    filters = dict(slug=setting_slug,
                    active=True)
    if IncomingFileTypeSetting.objects.filter(**filters).count() > 0:
        return True

    return False
