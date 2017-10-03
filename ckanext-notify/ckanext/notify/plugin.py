import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import constants
import actions


class NotifyPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'notify')

    def get_actions(self):
        additional_actions = {
            constants.DATAREQUEST_CREATE: actions.datarequest_create,
            constants.DATAREQUEST_SHOW: actions.datarequest_show,
            constants.DATAREQUEST_UPDATE: actions.datarequest_update,
            constants.DATAREQUEST_INDEX: actions.datarequest_index,
            constants.DATAREQUEST_DELETE: actions.datarequest_delete,
            constants.DATAREQUEST_CLOSE: actions.datarequest_close,
            constants.DATAREQUEST_SEND_EMAIL_NOTIFICATION: actions.datarequest_email_notification,
            constants.DATAREQUEST_SEND_SLACK_NOTIFICATION: actions.datarequest_send_slack_notification,
        }

        if self.comments_enabled:
            additional_actions[constants.DATAREQUEST_COMMENT] = actions.datarequest_comment
            additional_actions[constants.DATAREQUEST_COMMENT_LIST] = actions.datarequest_comment_list
            additional_actions[constants.DATAREQUEST_COMMENT_SHOW] = actions.datarequest_comment_show
            additional_actions[constants.DATAREQUEST_COMMENT_UPDATE] = actions.datarequest_comment_update
            additional_actions[constants.DATAREQUEST_COMMENT_DELETE] = actions.datarequest_comment_delete

        return additional_actions
