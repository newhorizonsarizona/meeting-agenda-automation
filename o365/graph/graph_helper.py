import os
import httpx
import requests

from o365.auth.auth_helper import AuthHelper
from o365.exception.agenda_exception import AgendaException
from o365.util.constants import Constants


class GraphHelper:
    """This class is a helper for making GraphQL API calls via http"""

    access_token = None
    obo_access_token = None
    url = "https://graph.microsoft.com/v1.0/"
    headers = None
    timeout = 60
    
    def __init__(self, obo_token: bool = False) -> None:
        """initialize the http helper"""
        self.access_token = AuthHelper.acquire_token()
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        if not obo_token:
            return
        self.obo_access_token = AuthHelper.acquire_token_auth_code()
        self.headers.update({"Authorization": f"Bearer {self.obo_access_token}"})

    def get_request(self, path: str, headers: dict):
        """Make a GET request to the provided graph api path, passing the access token in a header"""
        request_url = f"{self.url}/{path}"
        self.headers.update(headers)
        graph_response = httpx.get(
            url=request_url, headers=self.headers, timeout=self.timeout
        )

        if graph_response.status_code == 200:
            # Print the results in a JSON format
            # print(graph_response.json())
            return graph_response.json()
        else:
            raise AgendaException(
                f"Error {graph_response.status_code} - {graph_response.text}"
            )
        return None

    def _post(self, request_url: str, data: str, headers: dict = {}):
        """Make a POST request to the provided url, passing the access token in a header"""
        self.headers.update(headers)
        graph_response = httpx.post(
            url=request_url, data=data, headers=self.headers, timeout=self.timeout
        )

        if graph_response.status_code == 200:
            # Print the results in a JSON format
            # print(graph_response.json())
            return graph_response.json()
        else:
            raise AgendaException(
                f"Error {graph_response.status_code} - {graph_response.text}"
            )
        return None


    def post_request(self, path: str, data: str, headers: dict):
        """Make a POST request to the provided graph api path, passing the access token in a header"""
        request_url = f"{self.url}/{path}"
        self.headers.update(headers)
        return self._post(request_url, data, headers)
    
    def patch_request(self, path: str, data: str, headers: dict):
        """Make a PATCH request to the provided graph api path, passing the access token in a header"""
        request_url = f"{self.url}/{path}"
        self.headers.update(headers)
        graph_response = requests.patch(
            request_url, data=data, headers=self.headers, timeout=self.timeout
        )

        if graph_response.status_code == 200:
            # Print the results in a JSON format
            # print(graph_response.json())
            return graph_response.json()
        else:
            raise AgendaException(
                f"Error {graph_response.status_code} - {graph_response.text}"
            )
        return None
