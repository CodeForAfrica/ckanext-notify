import ckan.logic as logic
import ckan.model as model
import ckan.lib.base as base
import ckan.plugins as plugins
import ckan.lib.mailer as mailer
import constants
import validator
import datetime
import requests
import db


from ckan.common import _, config
from socket import error as socket_error

tk = plugins.toolkit
c = tk.c

ValidationError = logic.ValidationError


def _dictize_slack_details(slack_details):

    # Convert the slack details into a dict
    data_dict = {
        'id': slack_details.id,
        'webhook_url': slack_details.webhook_url,
        'slack_channel': slack_details.slack_channel,
        'organization_id': slack_details.organization_id
    }

    return data_dict


def _undictize_slack_basic(slack_details, data_dict):
    slack_details.webhook_url = data_dict['webhook_url']
    slack_details.slack_channel = data_dict['slack_channel']
    slack_details.organization_id = data_dict['organization_id']


def datarequest_register_slack(context, data_dict):
    '''
    Action to register a slack channel. The function checks the access rights
    of the user before creating the slack channel. If the user is not allowed
    a NotAuthorized exception will be risen.

    In addition, you should note that the parameters will be checked and an
    exception (ValidationError) will be risen if some of these parameters are
    not valid.

    :param context: the context of the request
    :type data_dict: dict

    :param data_dict: Contains the following:
    webhook_url: The webhook_url of the slack organization
    slack_channel: The slack_channel via which notifications are to be received
    organization_id: The ID of the organization
    :type data_dict: dict

    :returns: A dict with the slack details (id, webhook_url, channel
        organization_id)
    :rtype: dict
    '''

    model = context['model']
    session = context['session']

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_REGISTER_SLACK, context, data_dict)

    # Validate data
    validator.validate_slack_form(context, data_dict)

    # Store the data
    slack_details = db.Org_Slack_Details()
    _undictize_slack_basic(slack_details, data_dict)

    session.add(slack_details)
    session.commit()

    return _dictize_slack_details(slack_details)


def slack_channels_show(context, data_dict):
    '''
    Action to retrieve the slack notification channels. The only required
    parameter is the name of the organization passed as id. A NotFound
    exception will be risen if the organization id is not found.

    Access rights will be checked before returning the information and an
    exception will be risen (NotAuthorized) if the user is not authorized.

    :param context: the context of the request
    :type data_dict: dict

    :param data_dict: Contains the following
    organization_id: The ID of the organization
    :type data_dict: dict

    :returns: A list of the slack notification details(id,
        organization_id, webhook_url, slack_channel)
    :rtype: list
    '''

    model = context['model']
    organization_id = data_dict.get('organization_id', '')

    if not organization_id:
        raise tk.ValidationError(tk._('Organization ID has not been included'))

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_REGISTER_SLACK, context, data_dict)

    # Get the available slack channels
    result = db.Org_Slack_Details.get(organization_id=organization_id)
    if result:
        slack_channels = [_dictize_slack_details(channel) for channel in result]
    else:
        slack_channels = {}

    return slack_channels


def slack_channel_show(context, data_dict):
    '''
    Action to retrieve the information of a slack notification channel.
    The only required parameter is the id of the channel. A NotFound
    exception will be risen if the given id is not found.

    Access rights will be checked before returning the information and an
    exception will be risen (NotAuthorized) if the user is not authorized.

    :param context: the context of the request
    :type data_dict: dict

    :param data_dict: Contains the following
    id: The id of the slack notification channel to be shown
    :type data_dict: dict

    :returns: A dict with the data request (id, user_id, title, description,
        organization_id, open_time, accepted_dataset, close_time, closed)
    :rtype: dict
    '''

    model = context['model']
    id = data_dict.get('id', '')

    if not id:
        raise tk.ValidationError(tk._('Channel ID has not been included'))

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_REGISTER_SLACK, context, data_dict)

    # Get the data request
    result = db.Org_Slack_Details.get(id=id)
    if not result:
        raise tk.ObjectNotFound(tk._('Channel {0} not found in the data base'.format(id)))

    slack_data = result[0]
    data_dict = _dictize_slack_details(slack_data)

    return data_dict


def slack_channel_update(context, data_dict):
    '''
    Action to update a slack channel. The only required parameter is the id
    of the channel. The function checks the access rights of the user before
    updating the slack channel. If the user is not allowed a NotAuthorized
    exception will be risen.

    In addition, you should note that the parameters will be checked and an
    exception (ValidationError) will be risen if some of these parameters are
    invalid.

    :param context: the context of the request
    :type data_dict: dict

    :param data_dict: Contains the following:
    id: The ID of the slack channel to be updated
    webhook_url: The webhook_url of the slack organization
    slack_channel: The slack_channel
    organization_id: The ID of the organization whose channel is to be updated
    :type data_dict: dict

    :returns: A dict with the data request (id, webhook_url, slack_channel,
        organization_id)
    :rtype: dict
    '''

    model = context['model']
    session = context['session']
    id = data_dict.get('id', '')

    if not id:
        raise tk.ValidationError(tk._('Slack Channel ID has not been included'))

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_REGISTER_SLACK, context, data_dict)

    # Get the initial data
    result = db.Org_Slack_Details.get(id=id)
    if not result:
        raise tk.ObjectNotFound(tk._('Channel {0} not found in the database'.format(id)))
    slack_details = result[0]

    # Avoid the validator to return an error when the user does not change the title
    # context['avoid_existing_title_check'] = data_req.title == data_dict['title']

    # Validate data
    validator.validate_slack_form(context, data_dict)

    # Set the data provided by the user in the data_red
    _undictize_slack_basic(slack_details, data_dict)

    session.add(slack_details)
    session.commit()

    return _dictize_slack_details(slack_details)


def slack_channel_delete(context, data_dict):
    '''
    Action to delete a slack channel. The function checks the access rights
    of the user before deleting the data request. If the user is not allowed
    a NotAuthorized exception will be risen.

    :param context: the context of the request
    :type data_dict: dict

    :param data_dict: Contains the following
    id: The id of the slack notification channel to delete
    :type data_dict: dict
    '''

    model = context['model']
    session = context['session']
    id = data_dict.get('id', '')

    # Check id
    if not id:
        raise tk.ValidationError(tk._('Slack Channel ID has not been included'))

    # Init the data base
    db.init_db(model)

    # Check access
    tk.check_access(constants.DATAREQUEST_REGISTER_SLACK, context, data_dict)

    # Get the slack channel
    result = db.Org_Slack_Details.get(id=id)
    if not result:
        raise tk.ObjectNotFound(tk._('Channel {0} not found in the database'.format(id)))

    slack_details = result[0]
    session.delete(slack_details)
    session.commit()


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
