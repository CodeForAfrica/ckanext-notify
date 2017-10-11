import ckan.plugins as plugins
import constants
import actions
import auth

toolkit = plugins.toolkit


class NotifyPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'notify')

    # IActions

    def get_actions(self):
        additional_actions = {
            constants.DATAREQUEST_REGISTER_SLACK: actions.datarequest_register_slack,
            constants.DATAREQUEST_SEND_EMAIL_NOTIFICATION: actions.datarequest_email_notification,
            constants.DATAREQUEST_SEND_SLACK_NOTIFICATION: actions.datarequest_send_slack_notification,
        }

        return additional_actions

    # IAuthFunctions

    def get_auth_functions(self):
        auth_functions = {
            constants.DATAREQUEST_REGISTER_SLACK: auth.datarequest_register_slack,
        }

        return auth_functions

    # IRoutes

    def before_map(self, map):

        # Channels that an organization can subscribe to be notified with
        map.connect('organization_channels', '/organization/channels/{id}',
                    controller='ckanext.notify.controllers.ui_controller:DataRequestsNotifyUI',
                    action='organization_channels', conditions=dict(method=['GET']), ckan_icon='bell')

        # Slack channel registration
        map.connect('slack_form', '/organization/channels/slack/{id}',
                    controller='ckanext.notify.controllers.ui_controller:DataRequestsNotifyUI',
                    action='slack_form', conditions=dict(method=['GET', 'POST']))

        return map
