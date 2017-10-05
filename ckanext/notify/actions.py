import ckan.logic as logic
import ckan.model as model
import ckan.lib.base as base
import ckan.lib.mailer as mailer
import requests

from ckan.common import _, config
from socket import error as socket_error

ValidationError = logic.ValidationError


def send_slack_message(slack_data):
    response = requests.post(
        config.get('slack.webhook_url'), data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


def datarequest_email_notification(context, data_dict):
    '''
    Action to send email notification to organization members when a new
    data request is created.

    :param id: The id of the data request
    :type id: string
    :param title: The title of the data request
    :type title: string
    :param description: A brief description for your data request
    :type description: string
    :param organization_users: The organization members who will be notified when a data request
    :type organization_users: dictionary
    '''
    try:
        datarequest_url = config.get('ckan.site_url') + '/datarequest/' + data_dict['id']
        users = data_dict['organization']['users']
        extra_vars = {
            'site_title': config.get('ckan.site_title'),
            'site_url': config.get('ckan.site_url'),
            'datarequest_title': data_dict['title'],
            'datarequest_description': data_dict['description'],
            'datarequest_url': datarequest_url,
        }
        subject = base.render_jinja2('emails/notify_user_subject.txt',
                                     extra_vars)

        for user in users:
            # Retrieve user data
            user_data = model.User.get(user['id'])
            extra_vars['user_fullname'] = user_data.fullname
            body = base.render_jinja2('emails/notify_user_body.txt',
                                      extra_vars)
            mailer.mail_user(user_data, subject, body)
    except(socket_error, mailer.MailerException) as error:
        # Email could not be sent
        msg = _('Error sending the notification email, {0}').format(error)
        raise ValidationError({'message': msg}, error_summary=msg)


def datarequest_send_slack_notification(context, data_dict):
    datarequest_url = config.get('ckan.site_url') + '/datarequest/' + data_dict['id']
    extra_vars = {
        'site_title': config.get('ckan.site_title'),
        'site_url': config.get('ckan.site_url'),
        'datarequest_title': data_dict['title'],
        'datarequest_description': data_dict['description'],
        'datarequest_url': datarequest_url,
    }
    slack_data = {'text': base.render_jinja2('slack/slack_notify_request_body.txt',
                  extra_vars),
                  'username': config.get('slack.username'),
                  'channel': config.get('slack.channel')
                  }
    send_slack_message(slack_data)
