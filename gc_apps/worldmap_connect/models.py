from __future__ import absolute_import

from django.db import models

from jsonfield import JSONField
from gc_apps.core.models import TimeStampedModel

from gc_apps.worldmap_connect.jointarget_formatter import JoinTargetFormatter


class JoinTargetInformation(TimeStampedModel):
    """
    Store information retrieved from the WorldMap's JoinTarget API end point.
    This model is used as a "cache" to avoid over calling the API
    """
    name = models.CharField(max_length=255)
    target_info = JSONField()
    is_valid_target_info = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        """
        Check if the JSON in target_info is valid
        """
        if not self.id:
            super(JoinTargetInformation, self).save(*args, **kwargs)

        jt_formatter = JoinTargetFormatter(self.target_info)
        self.is_valid_target_info = jt_formatter.is_valid()

        super(JoinTargetInformation, self).save(*args, **kwargs)

    def get_geocode_types(self):
        jt_formatter = JoinTargetFormatter(self.target_info)
        return jt_formatter.get_join_targets_by_type()

    def get_available_layers_list(self):
        jt_formatter = JoinTargetFormatter(self.target_info)
        # Get all the join targets
        return jt_formatter.get_available_layers_list_by_type(None)
        #return jt_formatter.get_all_target_layers()

    def get_format_info_for_target_layer(self, layer_id):
        """
        Retrieve the WorldMap info related to the
        datatable model JoinTargetFormatType
        """
        jt_formatter = JoinTargetFormatter(self.target_info)

        return jt_formatter.get_format_info_for_target_layer(layer_id)

    def get_formatting_zero_pad_length(self, layer_id):
        """
        Helps with formatting columns that need zero padding
        """
        jt_formatter = JoinTargetFormatter(self.target_info)

        return jt_formatter.get_formatting_zero_pad_length(layer_id)

    def get_available_layers_list_by_type(self, chosen_geocode_type, for_json=False):
        jt_formatter = JoinTargetFormatter(self.target_info)
        # Get all the join targets
        return jt_formatter.get_available_layers_list_by_type(chosen_geocode_type, for_json)

    def get_single_join_target_info(self, target_layer_id):
        """
        Given a target layer id, retrieve the target name
        """
        jt_formatter = JoinTargetFormatter(self.target_info)

        return jt_formatter.get_single_join_target_info(target_layer_id)


    def get_join_targets_by_type(self, chosen_geocode_type):
        jt_formatter = JoinTargetFormatter(self.target_info)
        return jt_formatter.get_join_targets_by_type(chosen_geocode_type)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Join Target information'
        verbose_name_plural = verbose_name

'''
class APIValidationSchema(TimeStampedModel):
    """May be used to evaluate API results such as JoinTargetInformation"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, blank=True)
    json_schema = JSONField(load_kwargs={'object_pairs_hook': OrderedDict})
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # create the slug
        if self.name:
            self.slug = slugify(self.name)

        super(APISchema, self).save(*args, **kwargs)

'''

"""
from gc_apps.gis_basic_file.models import *
for g in GISDataFile.objects.all():
    dir(g)

"""
