import logging
import json
import ckan.model as model
import ckan.lib.helpers as helpers
import ckan.plugins as plugins
import ckanext.notify.constants as constants

from ckan.common import request
from ckanext.datarequests.controllers.ui_controller import DataRequestsUI


log = logging.getLogger(__name__)
tk = plugins.toolkit
c = tk.c


def _get_errors_summary(errors):
    errors_summary = {}

    for key, error in errors.items():
        errors_summary[key] = ', '.join(error)

    return errors_summary


class DataRequestsNotifyUI(DataRequestsUI):

    def _get_context(self):
        return {'model': model, 'session': model.Session,
                'user': c.user, 'auth_user_obj': c.userobj}

    def _process_post(self, action, context):
        # If the user has submitted the form, the data request must be created
        if request.POST:
            data_dict = {}
            data_dict['title'] = request.POST.get('title', '')
            data_dict['description'] = request.POST.get('description', '')
            data_dict['organization_id'] = request.POST.get('organization_id', '')

            if action == constants.DATAREQUEST_UPDATE:
                data_dict['id'] = request.POST.get('id', '')

            try:
                result = tk.get_action(action)(context, data_dict)
                if result['id']:
                    # Org members are notified via email when data request is created
                    tk.get_action(constants.DATAREQUEST_SEND_EMAIL_NOTIFICATION)(context, result)
                    print(">>>done")
                    tk.get_action(constants.DATAREQUEST_SEND_SLACK_NOTIFICATION)(context, result)
                tk.redirect_to(helpers.url_for(controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI', action='show', id=result['id']))

            except tk.ValidationError as e:
                log.warn(e)
                print(e)
                # Fill the fields that will display some information in the page
                c.datarequest = {
                    'id': data_dict.get('id', ''),
                    'title': data_dict.get('title', ''),
                    'description': data_dict.get('description', ''),
                    'organization_id': data_dict.get('organization_id', '')
                }
                c.errors = e.error_dict
                c.errors_summary = _get_errors_summary(c.errors)
