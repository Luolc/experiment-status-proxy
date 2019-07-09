import unittest

import os
import json
import slacker

TOKEN = os.environ['SLACK_TOKEN']
CHANNEL = os.environ['SLACK_CHANNEL']


def send_completed_msg(status):
    message_builder = slacker.CompleteMessageBuilder(status['expr_name'])

    message_builder.set_start_time(status['start_at'])
    message_builder.set_end_time(status['end_at'])
    blocks = message_builder.create_message(status['message'])

    sender = slacker.Sender(TOKEN, CHANNEL)
    response = sender.send(blocks)
    assert response['ok'], 'Sending failed'


def send():
    path = 'status-payload'
    filenames = os.listdir(path)
    num_files = len(filenames)

    if num_files < 2:
        print('No status to send, bye.')
    assert num_files == 2, 'Invalid file number: {}'.format(num_files)

    filename = next(name for name in filenames if name != 'README.md')
    assert filename.endswith('.json'), 'Require JSON status file'

    with open(os.path.join(path, filename), 'r') as f:
        status = json.load(f)

    send_fn = {
        'completed': send_completed_msg,
    }
    assert status['type'] in send_fn, 'Invalid status type: {}'.format(
        status['type'])
    send_fn[status['type']](status)


class SlackSendTest(unittest.TestCase):
    def testSendStatus(self):
        branch = os.environ.get('TRAVIS_BRANCH', '<local>')
        if branch != 'master':
            send()
