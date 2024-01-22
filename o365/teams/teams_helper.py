import asyncio
import datetime
from logging import error
import time

from msgraph import GraphServiceClient
from msgraph.generated.teams.item.channels.channels_request_builder import (
    ChannelsRequestBuilder,
)
from msgraph.generated.models.chat_message import ChatMessage
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.chat_message_attachment import ChatMessageAttachment
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.chat_message_mention import ChatMessageMention
from msgraph.generated.models.chat_message_from_identity_set import (
    ChatMessageFromIdentitySet,
)
from msgraph.generated.models.chat_message_mentioned_identity_set import (
    ChatMessageMentionedIdentitySet,
)
from msgraph.generated.models.share_point_identity_set import SharePointIdentitySet
from msgraph.generated.models.identity import Identity
from kiota_abstractions.api_error import APIError

from o365.teams.weekly_meeting_message import WeeklyMeetingMessage


class TeamsHelper:
    """This is a helper for MS Teams"""

    @staticmethod
    # GET /teams/{team-id}/channels?$startswith(displayName,'a')
    async def get_channels(graph_client: GraphServiceClient, team_id: str, display_name: str = None):
        """Gets all the channels for a team/group"""
        try:
            print(f"Getting all the channels for {team_id}")
            request_configuration = None
            if display_name is not None:
                query_params = ChannelsRequestBuilder.ChannelsRequestBuilderGetQueryParameters(
                    filter=f"startswith(displayName,'{display_name}')",
                )

                request_configuration = ChannelsRequestBuilder.ChannelsRequestBuilderGetRequestConfiguration(
                    query_parameters=query_params,
                )

            channels = await graph_client.teams.by_team_id(team_id).channels.get(
                request_configuration=request_configuration
            )
            return channels
        except APIError as e:
            print(f"Error: {e.error.message}")
        return None

    @staticmethod
    def generate_chat_message(meeting_message: WeeklyMeetingMessage) -> ChatMessage:
        if meeting_message is None:
            return None
        chat_message = ChatMessage(
            created_date_time=datetime.date.today(),
            from_=ChatMessageFromIdentitySet(
                user=Identity(
                    id="019a5991-0ce0-43a4-a5c4-e54932c6ed5f",
                    display_name="nhtm-laptop-user",
                    additional_data={
                        "user_identity_type": "aadUser",
                    },
                ),
            ),
            body=ItemBody(
                content_type=BodyType.Html,
                content=meeting_message.message,
            ),
        )
        chat_message_mentions = []
        mention_users = meeting_message.speaker_users + [meeting_message.topics_master_user]

        if meeting_message.subject is not None:
            chat_message.subject = meeting_message.subject
        mention_id = 0
        for mention_user in mention_users:
            chat_message_mentions.append(
                ChatMessageMention(
                    id=mention_id,
                    mention_text=mention_user["displayName"],
                    mentioned=ChatMessageMentionedIdentitySet(
                        user=Identity(
                            display_name=mention_user["displayName"],
                            id=mention_user["id"],
                            additional_data={
                                "user_identity_type": "aadUser",
                            },
                        ),
                    ),
                )
            )
            mention_id += 1

        if meeting_message.meeting_agenda_item is not None:
            chat_message.attachments = [
                ChatMessageAttachment(
                    content_type=meeting_message.attachment_content_type,
                    content_url=meeting_message.meeting_agenda_item["webUrl"],
                )
            ]

        chat_message.mentions = chat_message_mentions
        return chat_message

    @staticmethod
    def generate_chat_message_dict(meeting_message: WeeklyMeetingMessage) -> dict:
        if meeting_message is None:
            return None
        chat_message: dict = {"subject": meeting_message.subject}
        chat_message["body"] = {
            "contentType": "html",
            "content": f"{meeting_message.message}",
        }
        created_date_time = datetime.date.today() + datetime.timedelta(minutes=10)
        chat_message["created_date"] = created_date_time = created_date_time.strftime("%Y-%m-%dT%H:%M:%S")
        # chat_message["from"] = {
        #         "user": {
        #             "id": "019a5991-0ce0-43a4-a5c4-e54932c6ed5f",
        #             "displayName": "nhtm-laptop-user",
        #             "userIdentityType": "aadUser"
        #         }
        # }
        # chat_message["attachments"] = [
        #     {
        #         "id": meeting_message.meeting_agenda_item["id"],
        #         "contentType": meeting_message.attachment_content_type,
        #         "contentUrl": meeting_message.meeting_agenda_item["webUrl"],
        #     }
        # ]
        chat_message_mentions = []
        mention_users = meeting_message.speaker_users + [meeting_message.topics_master_user]
        mention_id = 0
        for mention_user in mention_users:
            chat_message_mentions.append(
                {
                    "id": mention_id,
                    "mentionText": mention_user["displayName"],
                    "mentioned": {
                        "user": {
                            "displayName": mention_user["displayName"],
                            "id": mention_user["id"],
                            "userIdentityType": "aadUser",
                        },
                    },
                }
            )
            mention_id += 1
        chat_message["mentions"] = chat_message_mentions

        return chat_message

    @staticmethod
    # GET /teams/{team-id}/channels/{channel-id}/messages
    async def post_message(
        graph_client: GraphServiceClient,
        team_id: str,
        channel_id: str,
        meeting_message: WeeklyMeetingMessage,
    ):
        """Post a message to a teams channel and add an attachment"""
        print(f"Posting a message for team {team_id} to channel {channel_id}")
        try:
            chat_message = TeamsHelper.generate_chat_message(meeting_message)
            print("Posting message")
            send_message_result = (
                await graph_client.teams.by_team_id(team_id)
                .channels.by_channel_id(channel_id)
                .messages.post(chat_message)
            )
            print(send_message_result)
            return send_message_result
        except APIError as e:
            print(f"Error: {e.error.message}")
        return None

    @staticmethod
    # GET /teams/{team-id}/channels
    def get_teams_channel(graph_client, team_id, channel_name):
        """Get the teams channel"""
        retry_count = 0
        channel_item = None
        while retry_count < 5:
            try:
                print(f"Getting the channel {channel_name} for team: {team_id}")
                channels = asyncio.run(TeamsHelper.get_channels(graph_client, team_id, channel_name))
                print(channels)
                if channels and channels.value:
                    if len(channels.value) > 0:
                        return channels.value[0]
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
            except Exception as ex:
                print(ex)

        return channel_item

    @staticmethod
    # GET /teams/{team-id}/channels/{channel-id}/messages
    def post_message_to_channel(graph_client, team_id, channel_id, meeting_message: WeeklyMeetingMessage):
        """Post the message to a teams channel"""
        retry_count = 0
        message_item = None
        while retry_count < 5:
            try:
                print(f"Posting message to channel {channel_id} for team: {team_id}")
                message_response = asyncio.run(
                    TeamsHelper.post_message(graph_client, team_id, channel_id, meeting_message)
                )
                if message_response:
                    return message_response
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)

        return message_item
