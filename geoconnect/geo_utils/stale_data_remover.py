from __future__ import print_function
from datetime import datetime

from apps.gis_shapefiles.models import ShapefileInfo
from apps.gis_tabular.models import TabularFileInfo
from apps.gis_tabular.models import WorldMapLatLngInfo, WorldMapJoinLayerInfo
from apps.worldmap_connect.models import WorldMapLayerInfo
from django.core.mail import send_mail
#from django.template.loader import render_to_string
from django.conf import settings

from msg_util import msg, msgt


DEFAULT_STALE_THREE_HOURS = 3 * 60 * 60 # 3 hours, in seconds
STALE_AGE_TWO_DAYS = 2 * 24 * 60 * 60 # 48 hours, in seconds
DEFAULT_STALE_AGE = DEFAULT_STALE_THREE_HOURS


class StaleDataRemover(object):
    """Convenience class for removing old objects"""

    def __init__(self):
        self.num_objects_checked = 0
        self.num_objects_removed = 0
        self.message_lines = []

    def add_message_line(self, mline, prepend=False):
        if mline:
            msg(mline)
            if prepend:
                self.message_lines.insert(0, mline)
            else:
                self.message_lines.append(mline)

    def check_for_stale_objects(self, MODEL_CLASS, stale_age_in_seconds):
        """
        Retrieve a class of objects (e.g. WorldMapLatLngInfo) and count what's happening
        """
        current_time = datetime.now()
        self.num_objects_checked = 0
        self.num_objects_removed = 0

        for obj_info in MODEL_CLASS.objects.all():
            self.num_objects_checked += 1
            if self.remove_if_stale(obj_info, stale_age_in_seconds, current_time):
                self.num_objects_removed += 1


    def remove_stale_worldmap_data(self, stale_age_in_seconds=DEFAULT_STALE_AGE):
        """
        Remove old map data...There are the objects storing WorldMap links
        """
        msgt("Remove stale WorldMap data")

        for CLASS_TYPE in (WorldMapLatLngInfo, WorldMapJoinLayerInfo, WorldMapLayerInfo):
            self.add_message_line('checking: %s' % CLASS_TYPE.__name__)
            self.check_for_stale_objects(CLASS_TYPE, stale_age_in_seconds)

        self.add_message_line("# of WorldMap objects Checked: %s" % self.num_objects_checked)
        self.add_message_line("# of WorldMap objects Removed: %s" % self.num_objects_removed)


    def remove_stale_dataverse_data(self, stale_age_in_seconds=STALE_AGE_TWO_DAYS):
        """
        Here we're removing the metadata and files from dataverse
        """
        msgt("Remove stale Dataverse data")

        for CLASS_TYPE in (TabularFileInfo, ShapefileInfo):
            self.add_message_line('checking: %s' % CLASS_TYPE.__name__)
            self.check_for_stale_objects(CLASS_TYPE, stale_age_in_seconds)

        self.add_message_line("# of Dataverse objects Checked: %s" % self.num_objects_checked)
        self.add_message_line("# of Dataverse objects Removed: %s" % self.num_objects_removed)


    def remove_if_stale(self, info_object, stale_age_in_seconds, current_time=None):
        """
        If the object has a "modified" timestamp
        older than "stale_age_in_seconds", then delete it
        """
        assert hasattr(info_object, 'modified'),\
            'The info_object must have "modified" date'

        # Get the current time, if not already given
        #
        if not current_time:
            current_time = datetime.now()

        # Pull the modification time, setting timezone info to None
        #
        mod_time = info_object.modified
        if hasattr(mod_time, 'tzinfo'):
            mod_time = mod_time.replace(tzinfo=None)

        # Is this object beyond its time limit?
        #
        time_diff = (current_time - mod_time).total_seconds()
        if time_diff > stale_age_in_seconds:
            # Yes! delete it
            msg('   > Removing: %s' % info_object)
            info_object.delete()
            return True
        else:
            return False

    def send_email_notice(self):
        msgt('Send email notice!')

        subject = 'GeoConnect: Clear stale data (%s)' % datetime.now()

        self.add_message_line('This is an email notice from Geoconnect',\
                prepend=True)
                
        if len(settings.ADMINS)==0:
            msg('No one to email! (no one in settings.ADMINS)')
            return

        to_addresses = map(lambda x: x[1], settings.ADMINS)
        if len(settings.ADMINS)==0:
            msg('No one to email! (no one in settings.ADMINS)')
            return

        #email_msg = render_to_string('task_scripts/prune_scratch_directories_email.txt', d)
        #msg(subject)
        #msg(email_msg)
        from_email = to_addresses[0]
        email_msg = '\n'.join(self.message_lines)

        send_mail(subject, email_msg, from_email, to_addresses, fail_silently=False)

        msg('email sent to: %s' % to_addresses)


"""
from geo_utils.stale_data_remover import StaleDataRemover
sdr = StaleDataRemover()
sdr.remove_stale_worldmap_data()
sdr.send_email_notice()
#sdr.remove_stale_dataverse_data()
"""
