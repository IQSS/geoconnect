"""
Delete stale geoconnect objects and related files (including S3)
"""
import boto3

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail

from gc_apps.gis_shapefiles.models import ShapefileInfo,\
                                          WorldMapShapefileLayerInfo
from gc_apps.gis_tabular.models import TabularFileInfo,\
                                       WorldMapJoinLayerInfo,\
                                       WorldMapLatLngInfo
from gc_apps.geo_utils.msg_util import msg, msgt

DV_DATA_OBJECTS_TO_CHECK = [ShapefileInfo,
                            TabularFileInfo]
MAP_INFO_OBJECTS_TO_CHECK = [WorldMapShapefileLayerInfo,
                             WorldMapJoinLayerInfo, WorldMapLatLngInfo]

class StaleDataRemover(object):
    """
    Delete old files and related geoconnect objects.
    This includes removing files stored on S3.

    Note: "really_delete" must be True for actual deletion to happen
    """
    def __init__(self, really_delete=False, **kwargs):
        self.num_objects_checked = 0
        self.num_objects_removed = 0
        self.message_lines = []

        assert really_delete in (True, False),\
            'really_delete must be True or False'
        self.really_delete = really_delete


    def using_s3_file_storage(self):
        """Is S3 being used for file storage?"""
        if settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto3.S3Boto3Storage':
            return True

        return False

    def add_message_title_line(self, mline, prepend=False):
        """Add message title line"""
        if not mline:
            return

        self.add_message_line('=' * 40, prepend)
        self.add_message_line(mline)
        self.add_message_line('=' * 40, prepend)


    def add_message_line(self, mline, prepend=False):
        """Add message line"""
        if not mline:
            return

        msg(mline)
        if prepend:
            self.message_lines.insert(0, mline)
        else:
            self.message_lines.append(mline)


    def check_for_stale_objects(self, model_class, stale_age_in_seconds):
        """
        Retrieve a class of objects (e.g. WorldMapLatLngInfo) and count what's happening
        """
        current_time = timezone.now()

        for obj_info in model_class.objects.all():
            self.num_objects_checked += 1
            if self.remove_if_stale(obj_info, stale_age_in_seconds, current_time):
                self.num_objects_removed += 1


    def remove_stale_data(self, stale_age_in_seconds=None):
        """Main method called for running stale data removal process"""
        if stale_age_in_seconds is None:
            stale_age_in_seconds = settings.STALE_DATA_SECONDS_TO_EXPIRATION

        assert isinstance(stale_age_in_seconds, int),\
            'stale_age_in_seconds must be an int'

        msgt(("Remove stale WorldMap data"
              "\n(older than %s seconds)") % stale_age_in_seconds)

        # Reset object counters
        self.num_objects_checked = 0
        self.num_objects_removed = 0

        # Remove Geoconnect objects
        self.remove_geoconnect_objects(stale_age_in_seconds)
        self.remove_s3_data(stale_age_in_seconds)

        self.add_message_title_line('Final counts')
        self.add_message_line("# of objects Checked: %s" % self.num_objects_checked)
        self.add_message_line("# of objects Removed: %s" % self.num_objects_removed)


    def get_existing_file_names_for_s3_check(self):
        """Retrieve legit file names for S3 check
        - Called by "remove_s3_data()"
        """

        ok_names = [obj.dv_file.name\
                    for obj in ShapefileInfo.objects.only('dv_file')\
                    if obj.dv_file and obj.dv_file.name]

        for obj in TabularFileInfo.objects.only('dv_file', 'dv_join_file'):
            if obj.dv_file and obj.dv_file.name:
                ok_names.append(obj.dv_file.name)
            if obj.dv_join_file and obj.dv_join_file.name:
                ok_names.append(obj.dv_join_file.name)

        return ok_names


    def remove_s3_data(self, stale_age_in_seconds):
        """Check for old S3 objects that no longer have
        associated Geoconnect objects.
        Assumes that "remove_geoconnect_objects()" has already been run."""

        if self.using_s3_file_storage() is False:
            self.add_message_title_line('Note: Skip S3 check (not using S3)')
            # S3 not in use, don't check
            return

        # ------------------------
        # Get the names of legitimate files
        # ------------------------
        ok_names = self.get_existing_file_names_for_s3_check()

        #msgt(ok_names)
        # ------------------------
        # load the S3 resource
        # ------------------------
        s3_resource = boto3.resource(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        # ------------------------
        # Check the files in the bucket
        # ------------------------
        bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

        self.add_message_title_line('Check S3 files')
        for obj in bucket.objects.all():
            self.num_objects_checked += 1

            self.add_message_line('  > Checking %s' % obj.key)
            if obj.key in ok_names:
                self.add_message_line('    > File ok to stay')
                continue
            else:
                if self.really_delete:
                    self.add_message_line('    > Try to delete')
                    info_object.delete()
                    self.add_message_line('    > Deleted!')
                    self.num_objects_removed += 1
                else:
                    self.add_message_line('    > Expired (test, not really deleting)')


    def remove_geoconnect_objects(self, stale_age_in_seconds):
        """Iterate through Model classes and delete stale objects.
        Related FileField objects will also be removed"""

        objects_to_check = MAP_INFO_OBJECTS_TO_CHECK + DV_DATA_OBJECTS_TO_CHECK

        cnt = 0
        for model_type in objects_to_check:
            cnt += 1
            self.add_message_title_line(\
                '(%s) checking: %s' % (cnt, model_type.__name__))
            self.check_for_stale_objects(model_type, stale_age_in_seconds)



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
            current_time = timezone.now()

        self.add_message_line('  > Checking: %s, id: %s' % (info_object, info_object.id))

        # Pull the modification time
        #
        mod_time = info_object.modified

        #if hasattr(mod_time, 'tzinfo'):    # setting timezone info to None
        #    mod_time = mod_time.replace(tzinfo=None)

        # Is this object beyond its time limit?
        #
        time_diff = (current_time - mod_time).total_seconds()
        if time_diff > stale_age_in_seconds:
            # Yes! delete it
            if self.really_delete:
                self.add_message_line('    > Try to delete')
                info_object.delete()
                self.add_message_line('    > Deleted!')
                return True
            else:
                self.add_message_line('    > Expired (test, not really deleting)')
                return False
        else:
            self.add_message_line('    > OK, not expired')
            return False

    def send_email_notice(self):
        """Send email notice to settings.ADMINS"""
        msgt('Send email notice!')

        subject = 'GeoConnect: Clear stale data (%s)' % timezone.now()

        self.add_message_title_line('This is an email notice from Geoconnect',\
                prepend=True)
        self.add_message_title_line('(end of message)')

        if len(settings.ADMINS) == 0:
            msg('No one to email! (no one in settings.ADMINS)')
            return

        to_addresses = [x[1] for x in settings.ADMINS]
        if len(settings.ADMINS) == 0:
            msg('No one to email! (no one in settings.ADMINS)')
            return

        #email_msg = render_to_string('task_scripts/prune_scratch_directories_email.txt', d)
        #msg(subject)
        #msg(email_msg)
        from_email = to_addresses[0]
        email_msg = '\n'.join(self.message_lines)

        send_mail(subject, email_msg,
                  from_email, to_addresses,
                  fail_silently=False)

        msg('email sent to: %s' % to_addresses)
"""
s3_resource = boto3.resource(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

def show_or_delete_from_bucket(bucket_name, delete_it=False)

    bucket = s3_resource.Bucket(bucket_name)

    for obj in bucket.objects.all():
        print obj
        if delete_it is True:
            obj.delete()
"""

if __name__ == '__main__':
    stale_data_remover = StaleDataRemover()
    stale_data_remover.remove_stale_data()

    #show_or_delete_from_bucket(settings.AWS_STORAGE_BUCKET_NAME)
    #show_or_delete_from_bucket(settings.AWS_STORAGE_BUCKET_NAME, delete_it=True)
    #show_or_delete_from_bucket(settings.AWS_STORAGE_BUCKET_NAME)
