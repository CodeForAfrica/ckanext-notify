import constants
import ckan.plugins.toolkit as toolkit
import ckanext.datarequests.db as db
import re

_space_or_period = re.compile(r'\.|\s|#')
_slack_webhook = re.compile(r'^https://hooks\.slack\.com/services/T\w+/B\w+/\w+')


def validate_slack_form(context, request_data):

    errors = {}

    # Check webhook_url
    if len(request_data['webhook']) > constants.WEBHOOK_MAX_LENGTH:
        errors[toolkit._('Webhook URL')] =\
            [toolkit._('Webhook URL must be a maximum of %d characters long') % constants.WEBHOOK_MAX_LENGTH]

    if not _slack_webhook.match(request_data['webhook']):
        errors[toolkit._('Webhook URL')] = [toolkit._('Webhook URL is not in the correct format')]

    if not request_data['webhook']:
        errors[toolkit._('Webhook URL')] = [toolkit._('Webhook URL cannot be empty')]

    # Check channel
    if len(request_data['channel']) > constants.CHANNEL_MAX_LENGTH:
        errors[toolkit._('Channel')] =\
            [toolkit._('Channel must be a maximum of %d characters long') % constants.CHANNEL_MAX_LENGTH]

    if _space_or_period.search(request_data['channel']):
        errors[toolkit._('Channel')] = [toolkit._('Channel must be lowercase, without hash, space or periods')]

    if not request_data['channel']:
        errors[toolkit._('Channel')] = [toolkit._('Channel cannot be empty')]

    if len(errors) > 0:
        raise toolkit.ValidationError(errors)


def validate_email_form(context, request_data):
    errors = {}

    if len(request_data['email']) is 0:
        errors[toolkit._('Email')] = [toolkit._('Email cannot be empty')]
