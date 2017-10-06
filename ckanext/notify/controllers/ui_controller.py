import logging
import json
import functools
import ckan.model as model
import ckan.lib.base as base
import ckan.lib.helpers as helpers
import ckan.plugins as plugins
import ckanext.notify.constants as constants

from urllib import urlencode
from ckan.common import request

log = logging.getLogger(__name__)
tk = plugins.toolkit
c = tk.c


class DataRequestsNotifyUI(base.BaseController):

    def _get_context(self):
        return {'model': model, 'session': model.Session,
                'user': c.user, 'auth_user_obj': c.userobj}

    def organization_channels(self, id):
        context = self._get_context()
        c.group_dict = tk.get_action('organization_show')(context, {'id': id})
        c.group_dict['channels'] = ['slack', 'email']
        return tk.render('organization/channels.html', extra_vars=None)

    def slack_form(self, id):
        context = self._get_context()
        c.group_dict = tk.get_action('organization_show')(context, {'id': id})
        return tk.render('organization/slack_form.html', extra_vars=None)

    def post_slack_form(self):
        context = self._get_context()
        action = constants.DATAREQUEST_REGISTER_SLACK
        if request.POST:
            data_dict = dict()
            data_dict['webhook'] = request.POST.get('webhook', '')
            data_dict['channel'] = request.POST.get('channel', '')

            try:
                result = tk.get_action(action)(context, data_dict)
                print('Result', result)
            except tk.ValidationError as e:
                log.warn(e)
                # Fill the fields that will display some information in the page
                c.datarequest_notify = {
                    'id': data_dict.get('id', ''),
                    'webhook': data_dict.get('webhook', ''),
                    'chnnel': data_dict.get('channel', '')
                }
