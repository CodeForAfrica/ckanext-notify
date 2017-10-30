import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import constants
import actions
import auth


class NotifyPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IMapper)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'notify')

    # IActions

    def get_actions(self):
        additional_actions = {
            constants.DATAREQUEST_REGISTER_SLACK: actions.datarequest_register_slack,
            constants.SLACK_CHANNELS_SHOW: actions.slack_channels_show,
            constants.SLACK_CHANNEL_SHOW: actions.slack_channel_show,
            constants.SLACK_CHANNEL_UPDATE: actions.slack_channel_update,
            constants.SLACK_CHANNEL_DELETE: actions.slack_channel_delete,
            constants.DATAREQUEST_REGISTER_EMAIL: actions.datarequest_register_email,
            constants.EMAIL_CHANNELS_SHOW: actions.email_channels_show,
            constants.EMAIL_CHANNEL_SHOW: actions.email_channel_show,
            constants.EMAIL_CHANNEL_UPDATE: actions.email_channel_update,
            constants.EMAIL_CHANNEL_DELETE: actions.email_channel_delete,
        }

        return additional_actions

    # IAuthFunctions

    def get_auth_functions(self):
        auth_functions = {
            constants.MANAGE_NOTIFICATIONS: auth.manage_notifications,
        }

        return auth_functions

    # IRoutes

    def before_map(self, map):

        # Existing Channels
        map.connect('organization_channels', '/organization/channels/{id}',
                    controller='ckanext.notify.controllers.ui_controller:DataRequestsNotifyUI',
                    action='organization_channels', conditions=dict(method=['GET']), ckan_icon='bell')

        # Add Channels
        map.connect('add_channel', '/organization/channels/add/{id}',
                    controller='ckanext.notify.controllers.ui_controller:DataRequestsNotifyUI',
                    action='add_channel', conditions=dict(method=['GET']))

        # Slack channel registration
        map.connect('slack_form', '/organization/channels/slack/{organization_id}',
                    controller='ckanext.notify.controllers.ui_controller:DataRequestsNotifyUI',
                    action='slack_form', conditions=dict(method=['GET', 'POST']))

        # Update Slack Channel
        map.connect('update_slack_form', '/organization/channels/slack/edit/{id}/{organization_id}',
                    controller='ckanext.notify.controllers.ui_controller:DataRequestsNotifyUI',
                    action='update_slack_details', conditions=dict(method=['GET', 'POST']))

        # Delete Slack Channel
        map.connect('delete_slack_form', '/organization/channels/slack/delete/{id}/{organization_id}',
                    controller='ckanext.notify.controllers.ui_controller:DataRequestsNotifyUI',
                    action='delete_slack_details', conditions=dict(method=['POST']))

        # Email channel registration
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
