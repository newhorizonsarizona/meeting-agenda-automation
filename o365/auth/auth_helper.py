import os
from msal import ConfidentialClientApplication
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient

tenant_id = '9add987e-b316-43b4-8750-4007763832b0'
client_id = '68e11217-f842-4df4-8720-75a08c58f491'
client_secret = os.environ['CLIENT_SECRET']

class AuthHelper:
    """Helper for authorization"""
            
    @staticmethod    
    def acquire_token():
        """
        Acquire token via MSAL
        """
        authority_url = f'https://login.microsoftonline.com/{tenant_id}'
        app = ConfidentialClientApplication(
            authority=authority_url,
            client_id=client_id,
            client_credential=client_secret
        )
        token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if token and token['access_token'] is not None:
            return token['access_token']
    
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
        credential : ClientSecretCredential = AuthHelper.client_service_credential()
        scopes = ['https://graph.microsoft.com/.default']
        graph_client = GraphServiceClient(credentials=credential, scopes=scopes)
        return graph_client