from abc import ABC
from typing import Optional

from web3.providers import HTTPProvider
from requests import Session
from requests.adapters import HTTPAdapter


class Connection(ABC):

    def __init__(self, node_url: str, request_timeout: int = 5):
        self.auth_token = None
        self.ca_cert_path = None
        self.node_url = node_url
        self.request_timeout = request_timeout

        self.session = Session()
        self.adapter = HTTPAdapter()
        
        self.session.mount('http://', self.adapter)
        self.session.mount('https://', self.adapter)

        self.session.verify = False

    def with_tls(self, ca_cert_path: Optional[str] = None) -> 'Connection':
        if not self.node_url.startswith('https://'):
            raise ValueError(
                f"Cannot enable TLS on non-https url '{self.node_url}'")
        
        self.ca_cert_path = ca_cert_path
        self.session.verify = ca_cert_path if ca_cert_path is not None else True
        
        return self

    def with_authentication(self, username:str, password:str) -> 'Connection':
        try:
            response = self.session.post(
                f"{self.node_url.rstrip('/')}/login",
                json={
                    "username": username,
                    "password": password
                },
                timeout=self.request_timeout
            )
            response.raise_for_status()
            token_data = response.json()
            token_value = token_data.get("token")
 
            if not token_value:
                raise ValueError("No token received from login response")
            
            self.auth_token = token_value
            self.session.headers.update({"Authorization": f"Bearer {token_value}"})

            return self
        except Exception as e:
            raise ConnectionError(
                f"Authentication failed for user '{username}' at {self.node_url}: {str(e)}"
            )

    def get_provider(self) -> HTTPProvider:
        return HTTPProvider(
            self.node_url,
            session=self.session,
            request_kwargs={'timeout': self.request_timeout}
        )
