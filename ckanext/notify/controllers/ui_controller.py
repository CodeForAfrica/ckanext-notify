import logging
import ckan.model as model
import ckan.lib.base as base
import ckan.plugins as plugins
import ckan.lib.helpers as helpers
import ckanext.notify.constants as constants

from ckan.common import request

log = logging.getLogger(__name__)
toolkit = plugins.toolkit
c = toolkit.c


def _get_errors_summary(errors):
    errors_summary = {}

    for key, error in errors.items():
        errors_summary[key] = ', '.join(error)

    return errors_summary


class DataRequestsNotifyUI(base.BaseController):

    def _get_context(self):
        return {'model': model, 'session': model.Session,
                'user': c.user, 'auth_user_obj': c.userobj}

    def organization_channels(self, id):
        context = self._get_context()
        c.group_dict = toolkit.get_action('organization_show')(context, {'id': id})
        slack_channels = toolkit.get_action(constants.SLACK_CHANNELS_SHOW)(context, {'organization_id': id})
        return toolkit.render('notify/channels.html', extra_vars={'channels': slack_channels})

    def slack_form(self, organization_id):
        context = self._get_context()

        # Basic initialization
        c.slack_data = {
            'organization_id': organization_id
        }
        c.errors = {}
        c.errors_summary = {}

        try:
            toolkit.check_access(constants.DATAREQUEST_REGISTER_SLACK, context, {'organization_id': organization_id})
            self.post_slack_form(constants.DATAREQUEST_REGISTER_SLACK, context)

            c.group_dict = toolkit.get_action('organization_show')(context, {'id': organization_id})
            required_vars = {'data': c.slack_data, 'errors': c.errors, 'errors_summary': c.errors_summary}
            return toolkit.render('notify/register_slack.html', extra_vars=required_vars)

        except toolkit.NotAuthorized as e:
            log.warning(e)
            toolkit.abort(403, toolkit._('Unauthorized to register slack details for this organization'))

    def post_slack_form(self, action, context, **kwargs):
        if request.POST:
            data_dict = dict()
            data_dict['webhook'] = request.POST.get('webhook', '')
            data_dict['channel'] = request.POST.get('channel', '').lower()
            data_dict['organization_id'] = request.POST.get('organization_id', '')

            try:
                toolkit.get_action(action)(context, data_dict)
                helpers.flash_success(toolkit._('You have successfully added your slack notification channel'))
                toolkit.redirect_to('organization_channels', id=data_dict['organization_id'])
            except toolkit.ValidationError as e:
                log.warning(e)
                # Fill the fields that will display some information in the page
                c.slack_data = {
                    'organization_id': data_dict.get('organization_id', ''),
                    'webhook': data_dict.get('webhook', ''),
                    'channel': data_dict.get('channel', '')
                }
                c.errors = e.error_dict
                c.errors_summary = _get_errors_summary(c.errors)

