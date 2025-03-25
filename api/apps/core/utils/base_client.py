import logging
import requests
from typing import Type, Optional, Dict, Any, TypeVar
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryCallState,
)
from pydantic import BaseModel, ValidationError

# Configure base logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

T = TypeVar("T", bound=BaseModel)


class BaseAPIError(Exception):
    """Base exception for all API services"""

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception


class RateLimitError(BaseAPIError):
    """Base class for rate limiting errors"""


class NetworkError(BaseAPIError):
    """Base class for network-related errors"""


class ServiceUnavailableError(BaseAPIError):
    """Base class for service unavailable errors"""


class InvalidResponseError(BaseAPIError):
    """Base class for response validation errors"""


class BaseService:
    """
    Base service class for API clients with common error handling and retry logic

    Features:
    - Automatic retries with exponential backoff
    - Response validation with Pydantic
    - Custom exception hierarchy
    - Configurable logging
    - Rate limiting detection
    - Network error handling
    """

    # Configuration defaults
    DEFAULT_RETRY_ATTEMPTS = 3
    DEFAULT_TIMEOUT = 10
    DEFAULT_BASE_URL = ""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
        timeout: int = DEFAULT_TIMEOUT,
        logger_name: str = __name__,
    ):
        self.base_url = base_url.rstrip("/") + "/"
        self.retry_attempts = retry_attempts
        self.timeout = timeout
        self.logger = logging.getLogger(logger_name)
        self.session = requests.Session()

    def _get_retry_policy(self):
        """Override this to customize retry policy for specific services"""
        return retry(
            stop=stop_after_attempt(self.retry_attempts),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=(
                retry_if_exception_type((requests.Timeout, requests.ConnectionError))
                | retry_if_exception_type(ServiceUnavailableError)
            ),
            before_sleep=self._log_retry_attempt,
        )

    def _log_retry_attempt(self, retry_state: RetryCallState):
        """Log retry attempts with service-specific context"""
        self.logger.warning(
            f"Retrying {retry_state.fn.__name__} "
            f"(attempt {retry_state.attempt_number}/{self.retry_attempts}): "
            f"{str(retry_state.outcome.exception())}"
        )

    def _get_headers(self) -> Dict[str, str]:
        """Override to add service-specific headers"""
        return {"Content-Type": "application/json"}

    def _validate_response(self, response_data: Dict[str, Any], model: Type[T]) -> T:
        """Validate response against a Pydantic model"""
        try:
            return model(**response_data)
        except ValidationError as e:
            self.logger.error(f"Response validation failed: {str(e)}")
            raise InvalidResponseError(f"Invalid response format: {str(e)}") from e

    def _handle_error_response(self, response: requests.Response):
        """Handle HTTP error responses with service-specific logic"""
        if response.status_code == 429:
            raise RateLimitError(f"Rate limit exceeded: {response.text}")

        error_msg = f"HTTP {response.status_code} Error: {response.text}"

        if 400 <= response.status_code < 500:
            self.logger.error(f"Client error: {error_msg}")
            raise BaseAPIError(error_msg)

        if response.status_code >= 500:
            self.logger.error(f"Server error: {error_msg}")
            raise ServiceUnavailableError(error_msg)

    @_get_retry_policy()
    def _make_request(
        self,
        method: str,
        endpoint: str,
        response_model: Type[T],
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> T:
        """
        Core request handling method with retry logic

        :param method: HTTP method (GET, POST, etc.)
        :param endpoint: API endpoint path
        :param response_model: Pydantic model for response validation
        :param params: Query parameters
        :param data: Request body
        :return: Validated response
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        params = {k: v for k, v in params.items() if v is not None} if params else {}

        try:
            self.logger.info(f"Making {method} request to {url}")
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=self.timeout,
            )

            if not response.ok:
                self._handle_error_response(response)

            return self._validate_response(response.json(), response_model)

        except (requests.Timeout, requests.ConnectionError) as e:
            self.logger.error(f"Network error: {str(e)}")
            raise NetworkError("Network connection failed") from e

        except ValidationError as e:
            self.logger.error(f"Validation error: {str(e)}")
            raise InvalidResponseError("Response validation failed") from e

        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise BaseAPIError("Unexpected API error occurred") from e

    def _get(
        self, endpoint: str, response_model: Type[T], params: Optional[Dict] = None
    ) -> T:
        return self._make_request("GET", endpoint, response_model, params=params)

    def _post(
        self, endpoint: str, response_model: Type[T], data: Optional[Dict] = None
    ) -> T:
        return self._make_request("POST", endpoint, response_model, data=data)
