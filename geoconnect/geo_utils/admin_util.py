


def make_changelist_updates(model_admin_instance, attr_name, additional_fields, add_to_end_of_list=False):
    if model_admin_instance is None:
        return 
        
    if attr_name is None or not type(additional_fields) is list:
        return
    
    current_fields = getattr(model_admin_instance, attr_name)
    if current_fields is None:
        return
    if type(current_fields) is tuple:           
        current_fields = list(current_fields)
        
    if not set(additional_fields).issubset(set(current_fields)):
        # list_filter_items = ['name', 'zipfile_checked'] + list_filter_items
        if add_to_end_of_list:
            setattr(model_admin_instance, attr_name, current_fields + additional_fields )
        else:
            setattr(model_admin_instance, attr_name, additional_fields + current_fields)