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

    def add_channel(self, id):
        context = self._get_context()
        c.group_dict = toolkit.get_action('organization_show')(context, {'id': id})
        return toolkit.render('notify/add_channel.html')

    def slack_form(self, organization_id):
        context = self._get_context()

        # Basic initialization
        c.slack_data = {
            'organization_id': organization_id
        }
        c.errors = {}
        c.errors_summary = {}
        new_form = True

        try:
            toolkit.check_access(constants.DATAREQUEST_REGISTER_SLACK, context, {'organization_id': organization_id})
            self.post_slack_form(constants.DATAREQUEST_REGISTER_SLACK, context)

            c.group_dict = toolkit.get_action('organization_show')(context, {'id': organization_id})
            required_vars = \
                {'data': c.slack_data, 'errors': c.errors, 'errors_summary': c.errors_summary, 'new_form': new_form}
            return toolkit.render('notify/register_slack.html', extra_vars=required_vars)

        except toolkit.NotAuthorized as e:
            log.warning(e)
            toolkit.abort(403, toolkit._('Unauthorized to register slack details for this organization'))

    def post_slack_form(self, action, context, **kwargs):
        if request.POST:
            data_dict = dict()
            data_dict['webhook_url'] = request.POST.get('webhook_url', '')
            data_dict['slack_channel'] = request.POST.get('slack_channel', '').lower()
            data_dict['organization_id'] = request.POST.get('organization_id', '')

            if action == constants.SLACK_CHANNEL_UPDATE:
                data_dict['id'] = kwargs['id']

            try:
                toolkit.get_action(action)(context, data_dict)
                if action == constants.DATAREQUEST_REGISTER_SLACK:
                    helpers.flash_success(toolkit._('You have successfully added a slack notification channel'))
                else:
                    helpers.flash_success(toolkit._('You have successfully updated a slack notification channel'))

                toolkit.redirect_to('organization_channels', id=data_dict['organization_id'])
            except toolkit.ValidationError as e:
                log.warning(e)
                # Fill the fields that will display some information in the page
                c.slack_data = {
                    'organization_id': data_dict.get('organization_id', ''),
                    'webhook_url': data_dict.get('webhook_url', ''),
                    'slack_channel': data_dict.get('slack_channel', '')
                }
                c.errors = e.error_dict
                c.errors_summary = _get_errors_summary(c.errors)

    def update_slack_details(self, id, organization_id):
        data_dict = {'id': id, 'organization_id': organization_id}
        context = self._get_context()

        # Basic initialization
        c.slack_data = {}
        c.errors = {}
        c.errors_summary = {}
        new_form = False

        try:
            toolkit.check_access(constants.DATAREQUEST_REGISTER_SLACK, context, data_dict)
            c.slack_data = toolkit.get_action(constants.SLACK_CHANNEL_SHOW)(context, data_dict)

            self.post_slack_form(constants.SLACK_CHANNEL_UPDATE, context, id=id)

            c.group_dict = toolkit.get_action('organization_show')(context, {'id': organization_id})
            required_vars = \
                {'data': c.slack_data, 'errors': c.errors, 'errors_summary': c.errors_summary, 'new_form': new_form}
            return toolkit.render('notify/register_slack.html', extra_vars=required_vars)
        except toolkit.ObjectNotFound as e:
            log.warning(e)
            toolkit.abort(404, toolkit._('Slack detail {0} not found').format(id))
        except toolkit.NotAuthorized as e:
            log.warning(e)
            toolkit.abort(403, toolkit._('You are not authorized to update the channel {0}').format(id))

    def delete_slack_details(self, id, organization_id):
        data_dict = {'id': id, 'organization_id': organization_id}
        context = self._get_context()

        try:
            toolkit.check_access(constants.DATAREQUEST_REGISTER_SLACK, context, data_dict)
            toolkit.get_action(constants.SLACK_CHANNEL_DELETE)(context, data_dict)
            helpers.flash_notice(toolkit._('A slack notification channel has been deleted'))
            toolkit.redirect_to('organization_channels', id=organization_id)
        except toolkit.ObjectNotFound as e:
            log.warning(e)
            toolkit.abort(404, toolkit._('Slack detail {0} not found').format(id))
        except toolkit.NotAuthorized as e:
            log.warning(e)
            toolkit.abort(403, toolkit._('You are not authorized to delete the channel {0}').format(id))

    def email_form(self, id):
        context = self._get_context()

        # Basic initialization
        c.email_data = {}
        c.errors = {}
        c.errors_summary = {}

        # Check access
        try:
            # toolkit.check_access(constants.DATAREQUEST_REGISTER_EMAIL, context, {'org_id': id})
            self.post_email_form(id, constants.DATAREQUEST_REGISTER_EMAIL, context)

            c.group_dict = toolkit.get_action('organization_show')(context, {'id': id})
            required_vars = {'data': c.email_data, 'errors': c.errors, 'error_summary': c.errors_summary}
            return toolkit.render('notify/register_email.html', extra_vars=required_vars)

        except toolkit.NotAuthorized as e:
            log.warning(e)
            toolkit.abort(403, toolkit._('Unauthorized to register email details for this organization'))

    def post_email_form(self, id, action, context):
        if request.POST:
            data_dict = dict()
            data_dict['email'] = request.POST.get('email', '')
            data_dict['id'] = id

            try:
                toolkit.get_action(action)(context, data_dict)
                helpers.flash_success(toolkit._('You have successfully added your email notification channel'))
                toolkit.redirect_to('organization_channels', id=id)
            except toolkit.ValidationError as e:
                log.warning(e)
                # Fill the fields that will display some information in the page
                c.slack_data = {
                    'id': data_dict.get('id', ''),
                    'email': data_dict.get('email', '')
                }
                c.errors = e.error_dict
                c.errors_summary = _get_errors_summary(c.errors)
