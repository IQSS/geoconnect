

class SingleJoinTargetInfo(object):
    """Convenience class for passing JoinTarget information from WorldMap"""

    def __init__(self, target_info):
        """target_info is JSON information"""
        assert target_info is not None, "target_info cannot be None"

        # Add JSON Schema evaluation here!
        self.target_info = target_info

        self.target_id = target_info['id']
        self.target_layer_name = target_info['layer']
        self.target_column_name = target_info['attribute']['attribute']
        self.target_attribute_type = target_info['attribute']['type']
        self.zero_pad_length = self.get_zero_pad_length()


    def get_zero_pad_length(self):
        """
        Used to format join columns before sending them over to WorldMap.

        If this Target layer expects zero padding, return the
        length of the expected field.

        If no zero padding needed, return None
        """
        expected_format = self.target_info['expected_format']

        if expected_format.get('is_zero_padded') is True\
            and expected_format.get('expected_zero_padded_length', -1) > 0:
            return expected_format['expected_zero_padded_length']

        return None


    def show(self):
        """for debug"""
        for k, v in self.__dict__.items():
            print '%s: [%s]' % (k, v)

    def is_target_column_string(self):
        """
        Is the attribute type from the WorldMap API a string?  (usually "xsd:string")

        Example:
            {...
                , "attribute": {
                    "attribute": "CT_ID_10",
                    "type": "xsd:string"
                },
            ...}
        """
        if self.target_attribute_type is None:
            return False

        return self.target_attribute_type.lower().endswith(':string')


    def requires_zero_padding(self):
        """Does this column require zero-padding?"""

        if self.zero_pad_length is None or self.zero_pad_length < 1:
            return False

        return True

    def does_join_column_potentially_need_formatting(self):
        """Based on the target info, does the join column potentially need formatting?"""


        if self.requires_zero_padding() or self.is_target_column_string():
            return True

        return False

"""
--------------
EXAMPLE DATA:
--------------

    {
      "layer": "geonode:fire_districts_2014_boston_ccw",
      "name": "Fire Districts, Boston",
      "geocode_type_slug": "boston-administrative-geography",
      "geocode_type": "Boston, Administrative Geography",
      "attribute": {
        "attribute": "DISTRICT",
        "type": "xsd:double"
      },
      "abstract": "Fire Districts Boston. Provided by the Boston Area Research Initiative (BARI)\n\nhttps&#58;//www.northeastern.edu/csshresearch/bostonarearesearchinitiative/",
      "title": "Fire Districts 2014, Boston (BARI)",
      "expected_format": {
        "expected_zero_padded_length": -1,
        "is_zero_padded": false,
        "description": "Boston, Administrative Geography, Fire District ID.",
        "name": "Boston Fire District ID (integer)"
      },
      "year": 2015,
      "id": 13
    }

--------------
JSON SCHEMA
--------------
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "layer": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "geocode_type_slug": {
      "type": "string"
    },
    "geocode_type": {
      "type": "string"
    },
    "attribute": {
      "type": "object",
      "properties": {
        "attribute": {
          "type": "string"
        },
        "type": {
          "type": "string"
        }
      },
      "required": [
        "attribute",
        "type"
      ]
    },
    "abstract": {
      "type": "string"
    },
    "title": {
      "type": "string"
    },
    "expected_format": {
      "type": "object",
      "properties": {
        "expected_zero_padded_length": {
          "type": "integer"
        },
        "is_zero_padded": {
          "type": "boolean"
        },
        "description": {
          "type": "string"
        },
        "name": {
          "type": "string"
        }
      },
      "required": [
        "expected_zero_padded_length",
        "is_zero_padded",
        "description",
        "name"
      ]
    },
    "year": {
      "type": "integer"
    },
    "id": {
      "type": "integer"
    }
  },
  "required": [
    "layer",
    "name",
    "geocode_type_slug",
    "geocode_type",
    "attribute",
    "abstract",
    "title",
    "expected_format",
    "year",
    "id"
  ]
}
"""
