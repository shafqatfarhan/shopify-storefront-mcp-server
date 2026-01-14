# Shopify Storefront MCP Server

This is an MCP server to interact with [Shopify](https://shopify.dev/docs/api/storefront/latest) APIs via MCP tools.

## Requirements

- Python >=3.14
**This project requires Python 3.14 or newer.**

## Getting Started

Follow these steps to set up and run the Shopify MCP server.

### 1. Install Dependencies

It is recommended to use a [virtual environment](https://docs.python.org/3/tutorial/venv.html).

Install `uv` from https://docs.astral.sh/uv/getting-started/installation/

```bash
uv python install 3.14
uv python pin 3.14
uv pip install -r requirements.txt
source ./.venv/bin/activate
uv sync
uv run server.py 
```

### 2. Configure Environment Variables

**Configuration uses a `.env` file (which should not be checked in to version control; see `.gitignore`).**

1. Locate the `.example.env` file in the repository.
2. Copy its contents to a new file named `.env`:
   ```bash
   cp .example.env .env
   ```
3. Open `.env` in a text editor and set the flag values (`SHOPIFY_STORE` and optionally `API_TIMEOUT_IN_SECONDS`) to reflect your Shopify store URL and settings.

**Example:**
```
SHOPIFY_STORE=<store_name>.myshopify.com
API_TIMEOUT_IN_SECONDS=10
```

### 3. Start the Server (Development)

Run the server:

```bash
uv run server.py

or

fastmcp run server.py --transport http --port 9300 --host "0.0.0.0"
```

The server will start and expose the MCP API endpoints.
### 4. Starting the Production Server

To run the server in a production setting, use the `uvicorn` command below. This ensures optimal performance and reliability:

```bash
uvicorn server:app --port 9300 --host "0.0.0.0" --timeout-graceful-shutdown 10 --limit-concurrency 100 --lifespan "on" --ws "websockets-sansio"
```

This command starts the FastMCP HTTP server on port 9000, configured for concurrency and graceful shutdowns.

### 5. Running the Server in Docker (Containerized Deployment)

You can containerize and run this server using Docker for portable and consistent deployments.

#### **a. Build the Docker Image**

```bash
docker build -t fastmcp-app .
```

#### **b. Run the Docker Container**

Replace `<store_name>` with your actual Shopify store name:

```bash
docker run -d \
  --name fastmcp \
  -p 9300:9300 \
  -e SHOPIFY_STORE="<store_name>.myshopify.com" \
  fastmcp-app
```

- The server will now be accessible on port **9300** of your host machine.

#### **c. Stop the Container**

```bash
docker stop fastmcp
```

#### **d. View Container Logs**

```bash
docker logs -f fastmcp
```

#### **e. Rebuild After Code Changes**

If you've made changes to the code and want to rebuild/restart:

```bash
docker stop fastmcp
docker rm fastmcp
docker build -t fastmcp-app .
docker run -d \
  --name fastmcp \
  -p 9300:9300 \
  -e SHOPIFY_STORE="<store_name>.myshopify.com" \
  fastmcp-app
```


## Features

- **Search Products**: Query using the Shopify search API.
- **Add to Cart**: Add product(s) to the cart.
- **View Cart**: View currently active cart items.
- **Checkout**: Generates the checkout URL.


## License

See [LICENSE](./LICENSE) for license terms.
