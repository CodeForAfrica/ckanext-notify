import ckan.plugins as plugins
import ckan.logic as logic
import constants
import validator
import db

toolkit = plugins.toolkit
c = toolkit.c

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


def _dictize_email_details(email_details):

    # Convert the slack details into a dict
    data_dict = {
        'id': email_details.id,
        'email': email_details.email,
        'organization_id': email_details.organization_id
    }

    return data_dict


def _undictize_email_basic(email_details, data_dict):
    email_details.email = data_dict['email']
    email_details.organization_id = data_dict['organization_id']


def datarequest_register_slack(context, data_dict):
    '''
    Action to register a slack channel. The function checks the access rights
    of the user before creating the slack channel. If the user is not allowed
    a NotAuthorized exception will be risen.
    In addition, you should note that the parameters will be checked and an
    exception (ValidationError) will be risen if some of these parameters are
    not valid.
    :param context: the context of the request
    :type context: dict
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
    toolkit.check_access(constants.MANAGE_NOTIFICATIONS, context, data_dict)

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
    :type context: dict
    :param data_dict: Contains the following
    organization_id: The ID of the organization
    :type data_dict: dict
    :returns: A list of the slack notification details(id,
        organization_id, webhook_url, slack_channel)
    :rtype: list
    '''

    model = context['model']
    organization_id = data_dict.get('organization_id')
    success = data_dict.get('success', False)

    if not organization_id and not success:
        raise toolkit.ValidationError(toolkit._('Organization ID has not been included'))

    # Init the data base
    db.init_db(model)

    # Check access
    if not success:
        toolkit.check_access(constants.MANAGE_NOTIFICATIONS, context, data_dict)

    # Get the available slack channels
    result = db.Org_Slack_Details.get(organization_id=organization_id)
    if result:
        slack_channels = [_dictize_slack_details(channel) for channel in result]
    else:
        slack_channels = []

    return slack_channels


def slack_channel_show(context, data_dict):
    '''
    Action to retrieve the information of a slack notification channel.
    The only required parameter is the id of the channel. A NotFound
    exception will be risen if the given id is not found.
    Access rights will be checked before returning the information and an
    exception will be risen (NotAuthorized) if the user is not authorized.
    :param context: the context of the request
    :type context: dict
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
        raise toolkit.ValidationError(toolkit._('Channel ID has not been included'))

    # Init the data base
    db.init_db(model)

    # Check access
    toolkit.check_access(constants.MANAGE_NOTIFICATIONS, context, data_dict)

    # Get the data request
    result = db.Org_Slack_Details.get(id=id)
    if not result:
        raise toolkit.ObjectNotFound(toolkit._('Channel {0} not found in the data base').format(id))

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
        raise toolkit.ValidationError(toolkit._('Slack Channel ID has not been included'))

    # Init the data base
    db.init_db(model)

    # Check access
    toolkit.check_access(constants.MANAGE_NOTIFICATIONS, context, data_dict)

    # Get the initial data
    result = db.Org_Slack_Details.get(id=id)
    if not result:
        raise toolkit.ObjectNotFound(toolkit._('Channel {0} not found in the database').format(id))
    slack_details = result[0]

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
        raise toolkit.ValidationError(toolkit._('Slack Channel ID has not been included'))

    # Init the data base
    db.init_db(model)

    # Check access
    toolkit.check_access(constants.MANAGE_NOTIFICATIONS, context, data_dict)

    # Get the slack channel
    result = db.Org_Slack_Details.get(id=id)
    if not result:
        raise toolkit.ObjectNotFound(toolkit._('Channel {0} not found in the database').format(id))

    slack_details = result[0]
    session.delete(slack_details)
    session.commit()


def datarequest_register_email(context, data_dict):
    '''
    Action to register the organization email address used for notifications.
    The function checks the access rights of the user before creating the
    data request. If the user is not allowed a NotAuthorized exception will be risen.
    In addition, you should note that the parameters will be checked and an
    exception (ValidationError) will be risen if some of these parameters are
    not valid.
    :param title: The title of the data request
    :type title: string
    :param description: A brief description for your data request
    :type description: string
    :param organiztion_id: The ID of the organization you want to asign the
        data request (optional).
    :type organization_id: string
    :returns: A dict with the data request (id, user_id, title, description,
        organization_id, open_time, accepted_dataset, close_time, closed)
    :rtype: dict
    '''

    model = context['model']
    session = context['session']

    # Init the data base
    db.init_db(model)

    # Check access
    toolkit.check_access(constants.MANAGE_NOTIFICATIONS, context, data_dict)

    # Validate data
    validator.validate_email_form(context, data_dict)

    # Store the data
    email_details = db.Org_Email_Details()
    _undictize_email_basic(email_details, data_dict)

    session.add(email_details)
    session.commit()

    return _dictize_email_details(email_details)


def email_channel_show(context, data_dict):
    '''
    Action to retrieve the information of an email notification channel.
    The only required parameter is the id of the channel. A NotFound
    exception will be risen if the given id is not found.
    Access rights will be checked before returning the information and an
    exception will be risen (NotAuthorized) if the user is not authorized.
    :param context: the context of the request
    :type data_dict: dict
    :param data_dict: Contains the following
    id: The id of the email notification channel to be shown
    :type data_dict: dict
    :returns: A dict with the data request (id, user_id, title, description,
        organization_id, open_time, accepted_dataset, close_time, closed)
    :rtype: dict
    '''

    model = context['model']
    id = data_dict.get('id', '')

    if not id:
        raise toolkit.ValidationError(toolkit._('Email ID has not been included'))

    # Init the data base
    db.init_db(model)

    # Check access
    toolkit.check_access(constants.MANAGE_NOTIFICATIONS, context, data_dict)

    # Get the data request
    result = db.Org_Email_Details.get(id=id)
    if not result:
        raise toolkit.ObjectNotFound(toolkit._('Email {0} not found in the data base'.format(id)))

    email_data = result[0]
    data_dict = _dictize_email_details(email_data)

    return data_dict


def email_channels_show(context, data_dict):
    '''
    Action to retrieve the email notification channels. The only required
    parameter is the name of the organization passed in as an id. A NotFound
    exception will be risen if the organization id is not found.
    Access rights will be checked before returning the information and an
    exception will be risen (NotAuthorized) if the user is not authorized.
    :param context: the context of the request
    :type data_dict: dict
    :param data_dict: Contains the following
    organization_id: The ID of the organization
    :type data_dict: dict
    :returns: A list of the email notification details(id,
        organization_id, email)
    :rtype: list
    '''

    model = context['model']
    organization_id = data_dict.get('organization_id', '')

    if not organization_id:
        raise toolkit.ValidationError(toolkit._('Organization ID has not been included'))

    # Init the data base
    db.init_db(model)

    # Check access
    toolkit.check_access(constants.MANAGE_NOTIFICATIONS, context, data_dict)

    # Get the available slack channels
    result = db.Org_Email_Details.get(organization_id=organization_id)
    if result:
        email_channels = [_dictize_email_details(channel) for channel in result]
    else:
        email_channels = []

    return email_channels


def email_channel_update(context, data_dict):
    '''
    Action to update an email notification channel. The only required parameter is the id
    of the channel. The function checks the access rights of the user before
    updating the email notification channel. If the user is not allowed a NotAuthorized
    exception will be risen.
    In addition, you should note that the parameters will be checked and an
    exception (ValidationError) will be risen if some of these parameters are
    invalid.
    :param context: the context of the request
    :type data_dict: dict
    :param data_dict: Contains the following:
    id: The ID of the email notification channel to be updated
    email: The email address of the organization
    organization_id: The ID of the organization whose channel is to be updated
    :type data_dict: dict
    :returns: A dict with the data request (id, email,
        organization_id)
    :rtype: dict
    '''

    model = context['model']
    session = context['session']
    id = data_dict.get('id', '')

    if not id:
        raise toolkit.ValidationError(toolkit._('Email Notification ID has not been included'))

    # Init the data base
    db.init_db(model)

    # Check access
    toolkit.check_access(constants.MANAGE_NOTIFICATIONS, context, data_dict)

    # Get the initial data
    result = db.Org_Email_Details.get(id=id)
    if not result:
        raise toolkit.ObjectNotFound(toolkit._('Email {0} not found in the database'.format(id)))
    email_data = result[0]

    # Validate data
    validator.validate_email_form(context, data_dict)

    # Set the data provided by the user in the data_dict
    _undictize_email_basic(email_data, data_dict)

    session.add(email_data)
    session.commit()

    return _dictize_email_details(email_data)


def email_channel_delete(context, data_dict):
    '''
    Action to delete an email notification channel. The function checks the access rights
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
        raise toolkit.ValidationError(toolkit._('Email ID has not been included'))

    # Init the data base
    db.init_db(model)

    # Check access
    toolkit.check_access(constants.MANAGE_NOTIFICATIONS, context, data_dict)

    # Get the slack channel
    result = db.Org_Email_Details.get(id=id)
    if not result:
        raise toolkit.ObjectNotFound(toolkit._('Email {0} not found in the database'.format(id)))

    email_data = result[0]
    session.delete(email_data)
    session.commit()
