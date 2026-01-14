"""
API client for Shopify.
"""

import json
import logging
import os

import httpx
from typing import Literal

logger = logging.getLogger(__name__)


class ShopifyClient:
    """Custom RapidAPI client using httpx."""

    def __init__(self, enable_retries: bool = False):
        """
        Initialize the client with API configuration from the environment file.
        """
        self.shopify_store = os.getenv("SHOPIFY_STORE")
        self.shopify_store_url = f'https://{self.shopify_store}/api/mcp'
        self.api_timeout = int(os.getenv("API_TIMEOUT_IN_SECONDS") or 10)
        self.enable_retries = enable_retries
        self.session = httpx.AsyncClient()

    async def __aenter__(self) -> ShopifyClient:
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        await self.close()

    async def close(self):
        if self.session:
            await self.session.aclose()

    async def _make_request(
        self,
        method: Literal["GET", "POST"],
        params: dict | None = None,
    ) -> dict:
        """
        Make an HTTP request to the Shopify API

        Args:
            method (str): HTTP method (e.g., "GET", "POST").
            params (dict | None): Query parameters.
        Returns:
            dict: JSON response from the API
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        logger.info(f"Making API request with params: {params}")
        async with self.session as client:
            try:
                response = await client.post(
                    self.shopify_store_url,
                    headers=headers,
                    json=params,
                    timeout=self.api_timeout,
                )

                # Read response body before raising for status
                try:
                    response_data = response.json()
                except (ValueError, AttributeError):
                    response_data = response.text

                response.raise_for_status()
                return response_data, response.status_code
            except httpx.HTTPStatusError as e:
                status_code = 500
                message = str(e)
                
                # Try to get error details from response body
                try:
                    error_data = e.response.json()
                    api_message = error_data.get("message", error_data.get("error", error_data.get("detail", str(e))))
                    message = f"{message} | API Error: {api_message}"
                    error_result = {
                        "error": True,
                        "error_message": message,
                        "status_code": status_code,
                        "error_data": error_data
                    }
                except (ValueError, AttributeError):
                    response_text = e.response.text[:500] if hasattr(e.response, 'text') else None
                    message = f"{message} | Response: {response_text}"
                    error_result = {
                        "error": True,
                        "error_message": message,
                        "status_code": status_code,
                    }
                
                logger.error(f"API request failed with status {status_code}: {error_result}")
                return error_result, status_code
            except Exception as e:
                message = str(e)
                error_result = {"error": True, "error_message": message}
                logger.error(f"Exception raised from the API with params: {params}. Error: {error_result}")
                return error_result, status_code
            finally:
                await self.close()

    async def make_request(
        self,
        tool_name: str,
        arguments: dict
    ) -> dict:
        """Request to the Shopify MCP server."""
        logger.info(f"Calling the Shopify MCP server tool: {tool_name} with args: {arguments}")

        params = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        return await self._make_request("POST", params=params)
