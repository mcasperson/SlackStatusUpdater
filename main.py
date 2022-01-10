import logging
import argparse
from slack_sdk import WebClient

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Create an incident channel and post updates to it.')
parser.add_argument('--slackApiToken',
                    dest='slack_api_token',
                    action='store',
                    help='The Slack API token',
                    required=True)
parser.add_argument('--slackChannelName',
                    dest='slack_channel_name',
                    action='store',
                    help='The Slack channel name',
                    required=True)
parser.add_argument('--slackUsers',
                    dest='slack_users',
                    action='store',
                    help='A comma seperated list of users to invite to the channel',
                    required=True)
parser.add_argument('--incidentStatus',
                    dest='incident_status',
                    action='store',
                    help='The status of the incident',
                    required=True)
parser.add_argument('--estimatedTimeToResolution',
                    dest='estimated_time_to_resolution',
                    action='store',
                    help='The estimated time before the incident is resolved',
                    required=True)
parser.add_argument('--updater',
                    dest='updater',
                    action='store',
                    help='The user posting the update message',
                    required=True)
parser.add_argument('--customMessage',
                    dest='custom_message',
                    action='store',
                    help='An optional custom message',
                    required=False)
args = parser.parse_args()


def create_slack_channel(client, channel_name):
    channel = client.conversations_create(name=channel_name)
    return channel


def find_slack_channel(client, channel_name):
    channels = client.conversations_list()
    for channel in channels.data['channels']:
        if channel['name'] == channel_name:
            return channel['id']

    return None


def join_channel(client, channel_id):
    client.conversations_join(channel=channel_id)


def invite_users(client, channel_id):
    for email in args.slack_users.split(","):
        user = client.users_lookupByEmail(email=email.strip())
        user_id = user.data["user"]["id"]
        members = client.conversations_members(channel=channel_id)
        if user_id not in members.data["members"]:
            client.conversations_invite(channel=channel_id, users=user_id)


def post_update_message(client, channel_id):
    text = "===== STATUS UPDATE =====" \
           + "\nStatus: " + args.incident_status \
           + "\nEstimated Resolution: " + args.estimated_time_to_resolution \
           + "\nUpdater: " + args.updater
    if len(args.custom_message) != 0:
        text = text + "\nMessage: " + args.custom_message
    client.chat_postMessage(channel=channel_id, text=text)


def post_status_message():
    client = WebClient(token=args.slack_api_token)
    channel_id = find_slack_channel(client, args.slack_channel_name)
    if channel_id is None:
        channel_id = create_slack_channel(client, args.slack_channel_name)
    join_channel(client, channel_id)
    invite_users(client, channel_id)
    post_update_message(client, channel_id)


post_status_message()
