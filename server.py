"""
Entry point for the Shopify storefront MCP server.

This module initializes and starts the FastMCP server, providing
API tools and endpoints to interact with Shopify's APIs.
"""

from mcp_server import app, run_server 

if __name__ == "__main__":
    run_server()
