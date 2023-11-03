import httpx

from auth.auth_helper import AuthHelper

class GraphHelper:
    """This class is a helper for making GraphQL API calls via http"""
    
    access_token = None
    url = 'https://graph.microsoft.com/v1.0/'
    headers = None
    timeout = 60

    def __init__(self) -> None:
        """initialize the http helper"""
        self.access_token = AuthHelper.acquire_token()
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
        }

    def get_request(self, path: str, headers: dict):
        """Make a GET request to the provided url, passing the access token in a header"""
        request_url = f'{self.url}/{path}'
        self.headers.update(headers)
        graph_response = httpx.get(url=request_url, headers=self.headers, timeout=self.timeout)

        if graph_response.status_code == 200:
            # Print the results in a JSON format
            #print(graph_response.json())
            return graph_response.json()
        else:
            print(f'Error {graph_response.status_code} - {graph_response.text}')


    def post_request(self, path: str, data: str, headers: dict):
        """Make a POST request to the provided url, passing the access token in a header"""
        request_url = f'{self.url}/{path}'
        self.headers.update(headers)
        graph_response = httpx.post(url=request_url, data=data, headers=self.headers, timeout=self.timeout)

        if graph_response.status_code == 200:
            # Print the results in a JSON format
            #print(graph_response.json())
            return graph_response.json()
        else:
            print(f'Error {graph_response.status_code} - {graph_response.text}')
