import constants
import ckan.plugins.toolkit as tk
import ckanext.datarequests.db as db


def validate_slack_form(context, request_data):

    errors = {}

    # Check webhook_url
    if len(request_data['webhook']) > constants.WEBHOOK_MAX_LENGTH:
        errors[tk._('Webhook URL')] = [tk._('Webhook URL must be a maximum of %d characters long') % constants.WEBHOOK_MAX_LENGTH]

    if not request_data['webhook']:
        errors[tk._('Webhook URL')] = [tk._('Webhook URL cannot be empty')]

    # Check channel
    if len(request_data['channel']) > constants.CHANNEL_MAX_LENGTH:
        errors[tk._('Channel')] = [tk._('Channel must be a maximum of %d characters long') % constants.CHANNEL_MAX_LENGTH]

    if not request_data['channel']:
        errors[tk._('Channel')] = [tk._('Channel cannot be empty')]

    if len(errors) > 0:
        raise tk.ValidationError(errors)
