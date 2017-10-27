import ckan.lib.helpers as helpers


def manage_notifications(context, data_dict):
    my_organizations = helpers.organizations_available()
    can_manage = [org['name'] for org in my_organizations]
    if data_dict['organization_id'] in can_manage:
        return {'success': True}
    else:
        return {'success': False, 'msg': 'You do not have permission to register slack for this organization'}
