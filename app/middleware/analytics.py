import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track analytics for requests.
    Extracts user agent, IP, referrer, etc. for analytics.
    """

    async def dispatch(self, request: Request, call_next):
        # Extract analytics data from the request
        analytics_data = self._extract_request_data(request)

        # Store analytics data in request state for use by endpoints
        request.state.analytics_data = analytics_data

        # Process the request
        response = await call_next(request)

        # Log analytics for successful responses (2xx or redirects)
        if 200 <= response.status_code < 400:
            logger.info(
                f"Request: {request.method} {request.url} "
                f"Status: {response.status_code} "
                f"User-Agent: {analytics_data.get('user_agent', 'Unknown')[:50]}"
            )

        return response

    def _extract_request_data(self, request: Request) -> dict:
        """
        Extract analytics data from the request.
        """
        # Get IP address (handle X-Forwarded-For for proxies)
        client_ip = self._get_client_ip(request)

        # Get user agent
        user_agent = request.headers.get("user-agent", "")

        # Get referrer
        referrer = request.headers.get(
            "referer", ""
        )  # Note: referrer is misspelled in HTTP spec

        return {
            "ip_address": client_ip,
            "user_agent": user_agent,
            "referrer": referrer,
            "method": request.method,
            "path": str(request.url.path),
        }

    def _get_client_ip(self, request: Request) -> str:
        """
        Get the client's real IP address, handling proxies.
        """
        # Check for forwarded headers (common in proxy/load balancer setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, first one is usually the original client
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            # Fall back to direct connection IP
            client_ip = request.client.host if request.client else "unknown"

        return client_ip


def get_request_analytics_data(request: Request) -> dict:
    """
    Helper function to get analytics data from request state.
    """
    return getattr(request.state, "analytics_data", {})
