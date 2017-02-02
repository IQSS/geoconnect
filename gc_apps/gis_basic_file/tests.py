from django.test import TestCase

"""
from django.core.files.storage import default_storage

file = default_storage.open('storage_test', 'w')
file.write('storage contents')
file.close()

default_storage.exists('storage_test')
file = default_storage.open('storage_test', 'r')
file.read()
file.close()

default_storage.delete('storage_test')
default_storage.exists('storage_test')
"""

"""
import settings
print settings.GISFILE_SCRATCH_WORK_DIRECTORY

# make some directories
from gc_apps.gis_shapefiles.models import GISDataFile
for g in GISDataFile.objects.all():
    g.get_scratch_work_directory()

# delete them
for g in GISDataFile.objects.all():
    g.delete_scratch_work_directory()

# make some directories
for g in GISDataFile.objects.all():
        g.get_scratch_work_directory()

# delete them
from gc_apps.gis_basic_file.scratch_directory_services import *
ScratchDirectoryHelper.clear_scratch_directories()


"""
