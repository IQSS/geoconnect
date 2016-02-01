"""
Helper class to format JSON in the JoinTargetInformation model's "target_info" field

- In terms of UI, this data is used for:
    1. Creating a list of Geospatial Identifiers
        - e.g. Census Tract, Zip code
    2. Creating a list of Names/Years based on the chosen Geospatial Identifiers
        - e.g. If Cenus Tract is chosen, list might be:
            "US Census 2010", "US Census 2000", "US Census 1990", etc.
    3. Based on the chosen JoinTarget, prep data for WorldMap datatables API
        - The Upload and Join API
        - Parms: name of target layer, name of target layer column
"""

class JoinTargetFormatter(object):
    """
    Helper class to format JSON in the JoinTargetInformation model's "target_info" field
        Sample target info data:
        {
          "data": [
            {
              "layer": "geonode:massachusetts_census_nhu",
              "geocode_type": "US Census Tract",
              "geocode_type_slug": "us-census-tract",
              "attribute": {
                "attribute": "TRACTCE",
                "type": "xsd:string"
              },
              "year": 2010,
              "type": null,
              "id": 3
            }
          ],
          "success": true
        }
    """
    def __init__(self, target_info):
        self.target_info = target_info

        self.err_found = False
        self.err_message = None

        self.initial_check()

    def is_valid(self):
        return self.err_found

    def add_error(self, msg):
        """
        Error detected, store a messsage in the class
        """
        self.err_found = True
        self.err_message = msg

    def initial_check(self):
        """
        Make sure that 'target_info' has the expected data
        """
        if self.target_info is None:
            self.add_error("target_info should not be None")
            return False

        # Is this a dict?  (e.g. not a list or blank, etc)
        print 'target_info', self.target_info
        if not hasattr(self.target_info, 'has_key'):
            self.add_error("target_info is not a dict")
            return False

        # Is there a 'success' attribute?
        if not 'success' in self.target_info:
            self.add_error("target_info does not have a 'success' attribute")
            return False

        # Is success True?
        if not self.target_info['success'] is True:
            self.add_error("target_info does not have a 'success' marked as True")
            return False

        # Is there a data attribute?
        if not 'data' in self.target_info:
            self.add_error("target_info does not have a 'data' attribute")
            return False

        # Does the data attribute contain any elements?
        if len(self.target_info['data']) == 0:
            self.add_error("There are no JoinTargets available.")
            return False

        return True


    @staticmethod
    def get_formatted_name(geocode_type, year=None, title=None):
        if geocode_type is None:
            return None

        if year and title:
            return "{0} ({1}) {2}".format(geocode_type, year, title)

        if year:
            return "{0} ({1})".format(geocode_type, year)

        if title:
            return "{0} - {1}".format(geocode_type, title)

        return "{0}".format(geocode_type)


    def get_target_layer_name_column(self, target_layer_id):
        """
        return (target layer name, target layer column)
        """

        if target_layer_id is None:
            return None

        for info in self.target_info['data']:
            if 'id' in info and target_layer_id == info['id']:
                return (info['layer'], info['attribute']['attribute'])

        return (None, None)

    def get_geocode_types(self):
        """
        Create a list tuples for available Geospatial Identifiers
            - Tuple Format: (name, slug)
            - e.g. [("Census Tract", "census-tract'"), ("Zip code", "zip-code")]
        """
        if self.err_found:
            return None

        gtypes = []
        type_dict = {}
        for info in self.target_info['data']:
            # Have we already added this type to the list?
            if not info['geocode_type_slug'] in type_dict:
                # Nope, add it
                gtypes.append((info['geocode_type'], info['geocode_type_slug']))
                type_dict.update({ info['geocode_type_slug']: 1 })
        return gtypes

    def get_all_join_targets(self):
        if self.err_found:
            return None

        join_targets = []
        for info in self.target_info['data']:
            info_line = JoinTargetFormatter.get_formatted_name(
                        info['geocode_type'],
                        info['year'],
                        info['title'])
            join_targets.append((info['id'], info_line))
        return join_targets

    def get_join_targets_by_type(self, chosen_geocode_type=None):
        """
        Creating a list of tuples of Names/Years based on the chosen Geospatial Identifier
            - Tuple Format:
                [(join target name, join_target_id),]

                join_target_name = name (year)
                join_target_id = JoinTarget id on the WorldMap system
                    - Used in the Geoconnect form

            - e.g. If Cenus Tract is chosen, list might be:
                [("US Census 2010", 7), ("US Census 2000", 3), etc.]

        Note: if chosen_geocode_type is None, all identifiers will be retrieved
        """
        if self.err_found:
            return None

        join_targets = []
        for info in self.target_info['data']:

            gtype_slug = info['geocode_type_slug']
            if chosen_geocode_type == gtype_slug or\
                chosen_geocode_type is None:
                info_line = JoinTargetFormatter.get_formatted_name(
                            info['geocode_type'])
                            #info['year'])
                gtype_tuple = (info['geocode_type_slug'], info_line)
                if not gtype_tuple in join_targets:
                    join_targets.append(gtype_tuple)
        return join_targets

"""
python manage.py shell
from apps.worldmap_connect.utils import get_latest_jointarget_information
from apps.worldmap_connect.jointarget_formatter import JoinTargetFormatter

jt = get_latest_jointarget_information()
formatter = JoinTargetFormatter(jt.target_info)
gtypes = formatter.get_geocode_types()
print gtypes
print '-- targets for each type --'
cnt = 0
for g in gtypes:
    cnt +=1
    print '({0}) {1}'.format(cnt, formatter.get_join_targets_by_type(g))

cnt = 0
print '\n-- all targets --'
for item in formatter.get_join_targets_by_type(g):
    cnt +=1
    print '({0}) {1}'.format(cnt, item)

"""
