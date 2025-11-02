"""
HTTP client for working with API.
"""
import json
import logging
from typing import Optional, Dict, Any
import requests
from requests.exceptions import HTTPError, RequestException
from .config import get_proxy_config

logger = logging.getLogger(__name__)


class HttpClient:
    """HTTP client with proxy support and retry logic."""
    
    def __init__(self, use_proxy: Optional[bool] = None):
        """
        Initialize HTTP client.
        
        Args:
            use_proxy: Whether to use proxy. If None, taken from configuration.
        """
        proxy_config = get_proxy_config()
        self.use_proxy = use_proxy if use_proxy is not None else proxy_config.use_proxy
        self.proxy = self._get_proxy() if self.use_proxy else None
        
    def _get_proxy(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration."""
        proxy_config = get_proxy_config()
        if not proxy_config.proxy_data:
            return None
        
        socks_proxy = f'socks5://{proxy_config.proxy_data}'
        return {'http': socks_proxy, 'https': socks_proxy}
    
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
            url: URL for request
            max_retry: Maximum number of retry attempts
            params: URL parameters
            data: Request body data
            json: JSON data for request body
            headers: HTTP headers
            **kwargs: Additional parameters for requests
            
        Returns:
            Response object
            
        Raises:
            Exception: If all attempts failed
        """
        for attempt in range(max_retry + 1):
            try:
                session = requests.Session()
                
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
                
            except HTTPError as e:
                logger.error(f'HTTP error (attempt {attempt + 1}/{max_retry + 1}): {e}')
                if attempt < max_retry:
                    continue
                raise
                
            except RequestException as e:
                logger.error(f'Request error (attempt {attempt + 1}/{max_retry + 1}): {e}')
                if attempt < max_retry:
                    continue
                raise
                
            except Exception as e:
                logger.error(f'Unknown error (attempt {attempt + 1}/{max_retry + 1}): {e}')
                if attempt < max_retry:
                    continue
                raise
        
        raise Exception(f'All {max_retry + 1} HTTP requests failed')
