

class JoinTargetInfoSnippet(object):
    """Convenience class for passing JoinTarget information from WorldMap"""

    def __init__(self, target_layer_name, target_column_name, target_attribute_type, zero_pad_length):

        self.target_layer_name = target_layer_name
        self.target_column_name = target_column_name
        self.target_attribute_type = target_attribute_type
        self.zero_pad_length = zero_pad_length

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
