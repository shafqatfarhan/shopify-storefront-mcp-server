"""
Utility functions for the shopify-mcp application.
"""

import os
import sys
from logging.config import dictConfig
from pathlib import Path


def setup_logging() -> None:
    """
    Set up logging configuration.
    """
    log_level = os.getenv("FASTMCP_LOG_LEVEL", "INFO")
    handlers = ['console']
    standard_format = (
        '%(asctime)s %(levelname)s %(process)d '
        '[%(name)s] %(filename)s:%(lineno)d - %(message)s'
    )
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': standard_format,
            },
            'raw': {'format': '%(message)s'},
        },
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': sys.stdout,
            },
        },
        'loggers': {
            "uvicorn.access": {
                "level": "WARNING",
                "handlers": handlers,
                "propagate": False
            },
            "uvicorn.error": {
                "level": log_level,
                "handlers": handlers,
                "propagate": True
            },
            "fastmcp": {
                "level": log_level,
                "handlers": handlers,
                "propagate": False,
            },
            "mcp.server": {
                "level": log_level,
                "handlers": handlers,
                "propagate": True,
            },
            '': {
                'handlers': handlers,
                'level': log_level,
                'propagate': False
            },
        }
    })


def render_product_card(p, i):
    return f"""
        <div class="compact-product-card">
            <img
            src={p['image_url']}
            alt={p['title']}
            class="compact-product-image"
            />
        
            <div class="compact-product-info">
            <p class="compact-product-title">{p['title']}</p>
            <p class="compact-product-price">${p.get('variants')[0]['price']}</p>
            </div>
        
            <button class="compact-quick-add" onclick="addToCart('{p.get('variants')[0]['variant_id']}')">
            Quick Add
            </button>
        </div>
        <br />
        <br />
    """


def get_products_html(products) -> str:
    cards_html = "".join(
        render_product_card(p, i) for i, p in enumerate(products)
    )

    return f"""<!doctype html>
        <html>
            <head>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width,initial-scale=1"/>
                <title>Products</title>
                <style>
                    .compact-product-card {{
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        width: 180px;
                        background: #fff;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 0.5rem;
                        font-family: 'DM Sans', sans-serif;
                        font-size: 14px;
                        gap: 0.5rem;
                        transition: transform 0.2s ease;
                        cursor: pointer;
                    }}
                    
                    .compact-product-card:hover {{
                        transform: translateY(-3px);
                    }}
                    
                    .compact-product-image {{
                        width: 100%;
                        aspect-ratio: 1/1;
                        object-fit: cover;
                        border-radius: 6px;
                    }}
                    
                    .compact-product-info {{
                        text-align: center;
                        display: flex;
                        flex-direction: column;
                        gap: 0.25rem;
                    }}
                    
                    .compact-product-title {{
                        font-weight: 500;
                        color: #333;
                        margin: 0;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }}
                    
                    .compact-product-price {{
                        font-weight: 600;
                        color: #111;
                        margin: 0;
                    }}
                    
                    .compact-quick-add {{
                        background: #000;
                        color: #fff;
                        border: none;
                        border-radius: 6px;
                        padding: 0.4rem 0.6rem;
                        font-weight: 600;
                        font-size: 0.85rem;
                        text-transform: uppercase;
                        cursor: pointer;
                        transition: background 0.2s ease, color 0.2s ease;
                    }}
                    .compact-quick-add:hover {{
                        background: #fff;
                        color: #000;
                        border: 1px solid #000;
                    }}
                </style>
            </head>
            <body>
                <div class="wrap">
                    {cards_html}
                </div>

                <script>
                    const ro = new ResizeObserver(es => {{
                        for (const e of es) {{
                            parent.postMessage(
                                {{ type: "ui-size-change", payload: {{ height: e.contentRect.height }} }},
                                "*"
                            );
                        }}
                    }});
                    ro.observe(document.documentElement);

                    function addToCart(product_id) {{
                        window.parent.postMessage({{
                            type: "tool",
                            payload: {{ 
                                toolName: "create_cart",
                                params: {{ "product_variant_id": product_id }}
                            }}
                        }}, "*");
                    }}
                </script>
            </body>
        </html>
    """


def get_cart_items_html(item, i) -> str:    
    return f"""
        <div class="cart-item">
            <div class="cart-item-info">
                <div class="cart-item-title">{item.get('merchandise', {}).get('product', {}).get('title', "Baby product")}</div>
                <div class="cart-item-meta">
                    Qtantity: {item['quantity']} · ${item.get('cost', {}).get('total_amount', {}).get('amount', 0.0)}
                </div>
            </div>
        </div>
        """


def get_cart_html(cart) -> str:
    cart_items_html = "".join(
        get_cart_items_html(p, i) for i, p in enumerate(cart.get('lines', []))
    )

    return f"""<!doctype html>
        <html>
        <head>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width,initial-scale=1"/>
            <title>Cart</title>

            <style>
                body {{
                    font-family: 'DM Sans', sans-serif;
                    background: #fafafa;
                    margin: 0;
                    padding: 1rem;
                }}

                .wrap {{
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }}

                .success {{
                    background: #e8f7ee;
                    color: #0f5132;
                    border: 1px solid #badbcc;
                    padding: 0.75rem;
                    border-radius: 6px;
                    font-weight: 600;
                    text-align: center;
                }}

                .cart-item {{
                    display: flex;
                    gap: 0.75rem;
                    align-items: center;
                    background: #fff;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 0.5rem;
                }}

                .cart-item img {{
                    width: 64px;
                    height: 64px;
                    object-fit: cover;
                    border-radius: 6px;
                }}

                .cart-item-info {{
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    gap: 0.25rem;
                }}

                .cart-item-title {{
                    font-weight: 600;
                    font-size: 0.9rem;
                }}

                .cart-item-meta {{
                    font-size: 0.8rem;
                    color: #555;
                }}

                .cart-summary {{
                    background: #fff;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 0.75rem;
                    display: flex;
                    flex-direction: column;
                    gap: 0.4rem;
                }}

                .cart-summary-row {{
                    display: flex;
                    justify-content: space-between;
                    font-size: 0.9rem;
                }}

                .cart-summary-total {{
                    font-weight: 700;
                    font-size: 1rem;
                }}

                .checkout-btn {{
                    margin-top: 0.5rem;
                    background: #000;
                    color: #fff;
                    border: none;
                    border-radius: 6px;
                    padding: 0.6rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    cursor: pointer;
                }}

                .checkout-btn:hover {{
                    background: #222;
                }}
            </style>
        </head>

        <body>
            <div class="wrap">
                <div class="success">
                    ✅ Item added to your cart
                </div>

                <!-- Cart items -->
                {cart_items_html}

                <!-- Summary -->
                <div class="cart-summary">
                    <div class="cart-summary-row">
                        <span>Subtotal</span>
                        <span>${cart.get('cost', {}).get('subtotal_amount',{}).get('amount', 0.0)}</span>
                    </div>
                    <div class="cart-summary-row cart-summary-total">
                        <span>Total</span>
                        <span>${cart.get('cost', {}).get('total_amount',{}).get('amount', 0.0)}</span>
                    </div>

                    <button
                        class="checkout-btn"
                        onclick="openCheckoutPage('{cart.get('checkout_url')}')"
                    >
                        Checkout
                    </button>
                </div>
            </div>

            <script>
                const ro = new ResizeObserver(es => {{
                    for (const e of es) {{
                        parent.postMessage(
                            {{ type: "ui-size-change", payload: {{ height: e.contentRect.height }} }},
                            "*"
                        );
                    }}
                }});
                ro.observe(document.documentElement);

                function openCheckoutPage(checkout_url) {{
                        window.parent.postMessage({{
                            type: "link",
                            payload: {{ 
                                url: checkout_url
                            }}
                        }}, "*");
                    }}
            </script>
        </body>
        </html>
        """
