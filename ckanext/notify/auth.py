import constants
from ckan.plugins import toolkit as toolkit
import ckan.lib.helpers as helpers


def datarequest_register_slack(context, data_dict):
    my_groups = helpers.groups_available()
    print('Data', data_dict)
    print('My Groups', my_groups)
    return {'success': False}
