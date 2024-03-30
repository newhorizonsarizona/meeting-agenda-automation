import os
import httpx
from loguru import logger
from msal import ConfidentialClientApplication
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient, GraphRequestAdapter
from msgraph_core import GraphClientFactory
from kiota_authentication_azure.azure_identity_authentication_provider import (
    AzureIdentityAuthenticationProvider,
)

from o365.util.constants import Constants

tenant_id = Constants.TENANT_ID
client_id = Constants.CLIENT_ID
client_secret = os.environ["CLIENT_SECRET"]
user_auth_code = os.environ.get("USER_AUTH_CODE")


class AuthHelper:
    """Helper for authorization"""

    @staticmethod
    def acquire_token():
        """
        Acquire token via MSAL
        """
        authority_url = f"https://login.microsoftonline.com/{tenant_id}"
        app = ConfidentialClientApplication(
            authority=authority_url,
            client_id=client_id,
            client_credential=client_secret,
        )
        token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if token and token["access_token"] is not None:
            return token["access_token"]

    @staticmethod
    def acquire_token_auth_code():
        """
        Acquire token on behalf of user via MSAL
        """
        authority_url = f"https://login.microsoftonline.com/{tenant_id}"
        app = ConfidentialClientApplication(
            authority=authority_url,
            client_id=client_id,
            client_credential=client_secret,
        )
        token = app.acquire_token_by_authorization_code(
            user_auth_code,
            scopes=["user.read"],
            redirect_uri="https://weeklymeetingagenda.azurewebsites.net/",
        )
        if token:
            if token.get("access_token") is not None:
                return token["access_token"]
            else:
                logger.error(f"Invalid token: {token}")

    @staticmethod
    def client_service_credential():
        """
        Get the client service credential
        """
        credential = ClientSecretCredential(
            tenant_id,
            client_id,
            client_secret,
        )
        return credential

    @staticmethod
    def graph_service_client():
        """
        Get the graph service client
        """
        credential: ClientSecretCredential = AuthHelper.client_service_credential()
        scopes = ["https://graph.microsoft.com/.default"]
        graph_client = GraphServiceClient(credentials=credential, scopes=scopes)
        return graph_client

    @staticmethod
    def graph_service_client_with_adapter():
        """
        Get the graph service client
        """
        credential: ClientSecretCredential = AuthHelper.client_service_credential()
        auth_provider = AzureIdentityAuthenticationProvider(credential)
        timeout = httpx.Timeout(connect=90, read=180, write=120, pool=None)
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=50, keepalive_expiry=30)
        http_client = GraphClientFactory.create_with_default_middleware(
            client=httpx.AsyncClient(timeout=timeout, limits=limits)
        )
        request_adapter = GraphRequestAdapter(auth_provider, http_client)
        graph_client = GraphServiceClient(request_adapter=request_adapter)
        return graph_client
