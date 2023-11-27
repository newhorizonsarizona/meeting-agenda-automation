from msgraph import GraphServiceClient
from msgraph.generated.models.chat_message import ChatMessage
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.chat_message_attachment import ChatMessageAttachment
from kiota_abstractions.api_error import APIError


class TeamsHelper:
    """This is a helper for MS Teams"""

    @staticmethod
    # GET /teams/{team-id}/channels
    async def get_channels(graph_client: GraphServiceClient, team_id: str):
        """Gets all the channels for a team/group"""
        try:
            print(f"Getting all the channels for {team_id}")
            channels = await graph_client.teams.by_team_id(team_id).channels.get()
            return channels
        except APIError as e:
            print(f"Error: {e.error.message}")
        return None

    @staticmethod
    # GET /teams/{team-id}/channels/{channel-id}/messages
    async def post_message(
        graph_client: GraphServiceClient,
        team_id: str,
        channel_id: str,
        message: str,
        subject: str = None,
        attachment_url: str = None,
        content_type: str = "application/vnd.ms-excel",
    ):
        """Post a message to a teams channel and add an attachment"""
        print(f"Posting a message for team {team_id} to channel {channel_id}")
        try:
            chat_message = ChatMessage(
                body=ItemBody(
                    content=message,
                )
            )
            if subject is not None:
                chat_message.subject = subject
            if attachment_url is not None:
                chat_message.attachments = [
                    ChatMessageAttachment(
                        content_type=content_type,
                        content_url=attachment_url,
                    )
                ]
            request_body = chat_message
            print("Posting message")
            send_message_result = (
                await graph_client.teams.by_team_id(team_id)
                .channels.by_channel_id(channel_id)
                .messages.post(request_body)
            )
            print(send_message_result)
            return send_message_result
        except APIError as e:
            print(f"Error: {e.error.message}")
        return None
