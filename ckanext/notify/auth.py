import constants
from ckan.plugins import toolkit as toolkit
import ckan.lib.helpers as helpers


def datarequest_register_slack(context, data_dict):
    my_groups = helpers.groups_available()
    print('Data', data_dict)
    print('My Groups', my_groups)
    return {'success': False}


def datarequest_register_email(context, data_dict):
    my_organizations = helpers.organizations_available()
    can_manage = [org['name'] for org in my_organizations]
    if data_dict['organization_id'] in can_manage:
        return {'success': True}
    else:
        return {'success': False, 'msg': 'You do not have permission to register email for this organization'}
