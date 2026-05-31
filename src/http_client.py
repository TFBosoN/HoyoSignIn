"""
HTTP client for working with API.
"""
import json
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


class HttpClient:
    """HTTP client with optional proxy support and retry logic."""

    def __init__(self, proxy: Optional[Dict[str, str]] = None):
        """
        Args:
            proxy: requests-compatible proxy dict, e.g.
                   {'http': 'socks5://host:port', 'https': 'socks5://host:port'}
                   Pass None to make direct connections.
        """
        self.proxy = proxy

    @staticmethod
    def to_python(json_str: str) -> Any:
        """Parse JSON string to Python object."""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise

    @staticmethod
    def to_json(obj: Any) -> str:
        """Convert Python object to JSON string."""
        return json.dumps(obj, indent=4, ensure_ascii=False)

    def request(
        self,
        method: str,
        url: str,
        max_retry: int = 3,
        params: Optional[Dict] = None,
        data: Optional[Any] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Execute HTTP request with retries.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            max_retry: Maximum retry attempts
            params: URL query parameters
            data: Raw request body
            json: JSON body (sets Content-Type automatically)
            headers: HTTP headers
            **kwargs: Additional arguments forwarded to requests

        Returns:
            Response object

        Raises:
            Exception: When all attempts fail
        """
        for attempt in range(max_retry + 1):
            try:
                with requests.Session() as session:
                    if self.proxy:
                        session.proxies = self.proxy
                    response = session.request(
                        method=method,
                        url=url,
                        params=params,
                        data=data,
                        json=json,
                        headers=headers,
                        timeout=30,
                        **kwargs
                    )
                    response.raise_for_status()
                    return response

            except Exception as e:
                logger.error(f'Request error (attempt {attempt + 1}/{max_retry + 1}): {e}')
                if attempt < max_retry:
                    continue
                raise
