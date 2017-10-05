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
from ckanext.datarequests.controllers.ui_controller import DataRequestsUI


log = logging.getLogger(__name__)
tk = plugins.toolkit
c = tk.c


def _get_errors_summary(errors):
    errors_summary = {}

    for key, error in errors.items():
        errors_summary[key] = ', '.join(error)

    return errors_summary


def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
            for k, v in params]


def url_with_params(url, params):
    params = _encode_params(params)
    return url + u'?' + urlencode(params)


def org_datarequest_url(params, id):
    url = helpers.url_for(controller='ckanext.datarequests.controllers.ui_controller:DataRequestsUI',
                          action='organization_datarequests', id=id)
    return url_with_params(url, params)


class DataRequestsNotifyUI(base.BaseController):

    def _get_context(self):
        return {'model': model, 'session': model.Session,
                'user': c.user, 'auth_user_obj': c.userobj}

    def _show_index(self, user_id, organization_id, include_organization_facet, url_func, file_to_render):

        def pager_url(state=None, sort=None, q=None, page=None):
            params = list()

            if q:
                params.append(('q', q))

            if state is not None:
                params.append(('state', state))

            params.append(('sort', sort))
            params.append(('page', page))

            return url_func(params)

        try:
            context = self._get_context()
            page = int(request.GET.get('page', 1))
            limit = constants.DATAREQUESTS_PER_PAGE
            offset = (page - 1) * constants.DATAREQUESTS_PER_PAGE
            data_dict = {'offset': offset, 'limit': limit}

            state = request.GET.get('state', None)
            if state:
                data_dict['closed'] = True if state == 'closed' else False

            q = request.GET.get('q', '')
            if q:
                data_dict['q'] = q

            if organization_id:
                data_dict['organization_id'] = organization_id

            if user_id:
                data_dict['user_id'] = user_id

            sort = request.GET.get('sort', 'desc')
            sort = sort if sort in ['asc', 'desc'] else 'desc'
            if sort is not None:
                data_dict['sort'] = sort

            tk.check_access(constants.DATAREQUEST_INDEX, context, data_dict)
            datarequests_list = tk.get_action(constants.DATAREQUEST_INDEX)(context, data_dict)

            c.filters = [(tk._('Newest'), 'desc'), (tk._('Oldest'), 'asc')]
            c.sort = sort
            c.q = q
            c.organization = organization_id
            c.state = state
            c.datarequest_count = datarequests_list['count']
            c.datarequests = datarequests_list['result']
            c.search_facets = datarequests_list['facets']
            c.page = helpers.Page(
                collection=datarequests_list['result'],
                page=page,
                url=functools.partial(pager_url, state, sort),
                item_count=datarequests_list['count'],
                items_per_page=limit
            )
            c.facet_titles = {
                'state': tk._('State'),
            }

            # Organization facet cannot be shown when the user is viewing an org
            if include_organization_facet is True:
                c.facet_titles['organization'] = tk._('Organizations')

            return tk.render(file_to_render)
        except ValueError as e:
            # This exception should only occur if the page value is not valid
            log.warn(e)
            tk.abort(400, tk._('"page" parameter must be an integer'))
        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('Unauthorized to list Data Requests'))

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

    def organization_channels(self, id):
        context = self._get_context()
        c.group_dict = tk.get_action('organization_show')(context, {'id': id})
        url_func = functools.partial(org_datarequest_url, id=id)
        return self._show_index(None, id, False, url_func, 'organization/channels.html')

    # def organization_slack(self):
    #     return tk.render('organization/slack.html')
