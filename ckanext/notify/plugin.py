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
            constants.DATAREQUEST_REGISTER_EMAIL: actions.datarequest_register_email,
            constants.EMAIL_CHANNELS_SHOW: actions.email_channels_show,
            constants.EMAIL_CHANNEL_SHOW: actions.email_channel_show,
            constants.EMAIL_CHANNEL_UPDATE: actions.email_channel_update,
            constants.EMAIL_CHANNEL_DELETE: actions.email_channel_delete,
            constants.DATAREQUEST_SEND_EMAIL_NOTIFICATION: actions.datarequest_email_notification,
            constants.DATAREQUEST_SEND_SLACK_NOTIFICATION: actions.datarequest_send_slack_notification,
        }

        return additional_actions

    # IAuthFunctions

    def get_auth_functions(self):
        auth_functions = {
            constants.DATAREQUEST_REGISTER_SLACK: auth.datarequest_register_slack,
            constants.DATAREQUEST_REGISTER_EMAIL: auth.datarequest_register_email,
        }

        return auth_functions

    # IRoutes

    def before_map(self, map):

        # Channels that an organization can subscribe to be notified with
        map.connect('organization_channels', '/organization/channels/{id}',
                    controller='ckanext.notify.controllers.ui_controller:DataRequestsNotifyUI',
                    action='organization_channels', conditions=dict(method=['GET']), ckan_icon='bell')

        # Slack channel registration
        map.connect('slack_form', '/organization/channels/slack/{organization_id}',
                    controller='ckanext.notify.controllers.ui_controller:DataRequestsNotifyUI',
                    action='slack_form', conditions=dict(method=['GET', 'POST']))

        # Organization email registration
        map.connect('email_form', '/organization/channels/email/{organization_id}',
                    controller='ckanext.notify.controllers.ui_controller:DataRequestsNotifyUI',
                    action='email_form', conditions=dict(method=['GET', 'POST']))

        # Update Email Channel
        map.connect('update_email_form', '/organization/channels/email/edit/{id}/{organization_id}',
                    controller='ckanext.notify.controllers.ui_controller:DataRequestsNotifyUI',
                    action='update_email_details', conditions=dict(method=['GET', 'POST']))

        # Delete Email Channel
        map.connect('delete_email_form', '/organization/channels/email/delete/{id}/{organization_id}',
                    controller='ckanext.notify.controllers.ui_controller:DataRequestsNotifyUI',
                    action='delete_email_details', conditions=dict(method=['POST']))

        return map
