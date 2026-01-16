"""
This file initializes the FastMCP server, sets up authentication, logging,
and registers the custom Shopify MCP tools for searching products and
performing the cart operations.
"""

import logging, json


from dotenv import load_dotenv
from fastmcp import Context, FastMCP, settings
from typing import Any, Dict, Optional, Union, List
from starlette.responses import JSONResponse
    

from mcp_server.client import ShopifyClient
from mcp_server.utils import setup_logging, get_cart_html, get_products_html
from mcp_ui_server import create_ui_resource
from mcp_ui_server.core import UIResource
from mcp_ui_server.exceptions import InvalidURIError

# Load environment variables from .env file
load_dotenv()

setup_logging()

logger = logging.getLogger(__name__)

settings.json_response = True
mcp = FastMCP(
    "Shopify Storefront",
    on_duplicate_tools="error",
    instructions="This server provides Shopify tools.",
    auth=None
)

logger.info(f"MCP server started!")

@mcp.tool(
    annotations={
        "title": "Search Products on Shopify Store.",
        "readOnlyHint": True,
        "openWorldHint": False,
        "openWorldHint": False
    }
)
async def search_products(query: str, ctx: Context) -> Union[List[Union[UIResource, List[Dict[str, Any]]]], Dict[str, Any]]:
    """Search for Shopify store products by product name or category."""    
    tool_name = "search_shop_catalog"
    arguments = {
        "query": query,
        "context": ""
    }
    result = {}
    status_code = 200
    async with ShopifyClient() as api_client:
        result, status_code = await api_client.make_request(tool_name, arguments)
    
    if "error" in result:
        logger.error(f"Error in search_products: {result.get("error_message", "Error fetching products.")}")
        return result
    
    products = json.loads(result['result']['content'][0]['text'])
    #print(f"search_products response: {products['products']} - code: {status_code}")

    if not products['products']:
        return { "search_result": [] }

    try:
        interactive_form = create_ui_resource({
            "uri": f"ui://Shopify/products/",
            "content": {
                "type": "rawHtml",
                "htmlString": get_products_html(products['products'])
            },
            "encoding": "text"
        })
    except InvalidURIError as e:
        print(f"Failed to create UI resource: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

    return [interactive_form, products['products']]


@mcp.tool(
    annotations={
        "title": "Fetch Hotels",
        "readOnlyHint": True,
        "openWorldHint": False,
        "openWorldHint": False
    }
)
async def get_product_details_by_id(product_id: str, ctx: Context) -> Dict[str, Any]:
    """Get Shopify store product's details by product ID."""    
    tool_name = "get_product_details"
    arguments = {
        "product_id": product_id,
        "context": ""
    }
    result = {}
    status_code = 200
    async with ShopifyClient() as api_client:
        result, status_code = await api_client.make_request(tool_name, arguments)
    
    if "error" in result:
        logger.error(f"Error in get_product_by_id: {result.get("error_message", "Error fetching product by ID.")}")
        return result
    
    products = json.loads(result['result']['content'][0]['text'])
    #print(f"get_product_details_by_id response: {products['product']} - code: {status_code}")

    return { "search_results": products['product'] }


@mcp.tool(
    annotations={
        "title": "Create Cart",
        "readOnlyHint": False,
        "openWorldHint": False,
        "openWorldHint": False
    }
)
async def add_to_cart(product_variant_id: str, ctx: Context, cart_id: Optional[str] = None, quantity: int = 1) -> Union[List[Union[UIResource, Dict[str, Any]]], Dict[str, Any]]:
    """Add the product variant to the cart by creating a new Shopify store cart."""    
    tool_name = "update_cart"
    arguments = {
        "add_items": [
            {
                "product_variant_id": product_variant_id,
                "quantity": quantity
            }
        ]
    }
    result = {}
    status_code = 200
    async with ShopifyClient() as api_client:
        result, status_code = await api_client.make_request(tool_name, arguments)
    
    if "error" in result:
        logger.error(f"Error in create_cart: {result.get("error_message", "Error creating the cart.")}")
        return result
    
    products = json.loads(result['result']['content'][0]['text'])
    cart = products.get("cart")
    #print(f"create_cart response: {cart} - code: {status_code}")

    if cart:
        try:
            interactive_form = create_ui_resource({
                "uri": f"ui://Shopify/cart/",
                "content": {
                    "type": "rawHtml",
                    "htmlString": get_cart_html(cart)
                },
                "encoding": "text"
            })
        except InvalidURIError as e:
            print(f"Failed to create UI resource: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        return [interactive_form, cart]
    else:
        return { "cart": cart, "error": "Cart creation failed" }


@mcp.tool(
    annotations={
        "title": "Get Cart",
        "readOnlyHint": True,
        "openWorldHint": False,
        "openWorldHint": False
    }
)
async def get_cart(cart_id: str, ctx: Context) -> Union[List[Union[UIResource, Dict[str, Any]]], Dict[str, Any]]:
    """Retrieve the Shopify store cart for the current session."""    
    tool_name = "get_cart"
    arguments = {
        "cart_id": cart_id
    }
    result = {}
    status_code = 200
    async with ShopifyClient() as api_client:
        result, status_code = await api_client.make_request(tool_name, arguments)
    
    if "error" in result:
        logger.error(f"Error in get_cart: {result.get("error_message", "Error getting the cart.")}")
        return result
    
    products = json.loads(result['result']['content'][0]['text'])
    cart = products.get("cart")
    #print(f"get_cart response: {cart} - code: {status_code}")

    if cart:
        try:
            interactive_form = create_ui_resource({
                "uri": f"ui://Shopify/cart/",
                "content": {
                    "type": "rawHtml",
                    "htmlString": get_cart_html(cart)
                },
                "encoding": "text"
            })
        except InvalidURIError as e:
            print(f"Failed to create UI resource: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        return [interactive_form, cart]
    else:
        return { "cart": cart, "error": "No active cart found." }


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """
    Check the health of the server.
    """
    return JSONResponse(status_code=200, content={"status": "healthy", "service": "Shopify-storefront-mcp-server"})


def run_server():
    logger.info("Starting MCP development server.")
    mcp.run(transport="http", port=9300)


# Create ASGI application
app = mcp.http_app(transport="http")
