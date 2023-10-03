from msal import ConfidentialClientApplication

client_id = '68e11217-f842-4df4-8720-75a08c58f491'
client_secret = ''
tenant_id = '9add987e-b316-43b4-8750-4007763832b0'

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
        return token
