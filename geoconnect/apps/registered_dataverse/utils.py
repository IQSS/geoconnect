from apps.registered_dataverse.models import IncomingFileTypeSetting



def is_setting_active(setting_slug):
    """
    Check if a setting is active
    """
    if IncomingFileTypeSetting.objects.filter(slug=setting_slug).count() > 0:
        return True

    return False
