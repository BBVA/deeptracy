"""
Detailed documentation of Slack Incoming Webhooks:
https://api.slack.com/incoming-webhooks
"""

import json
import requests
import logging

log = logging.getLogger(__name__)


def notify(webhook_url: str, text):

    slack_data = {'text': text}

    log.info('notify to SLACK -> {}'.format(text))

    response = requests.post(
        webhook_url,
        data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )
