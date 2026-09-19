# Customer Support Chatbot

A support chatbot that can fetch product details, fetch user data, and place orders through MCP tools. The backend is FastAPI with the OpenAI SDK configured for DeepSeek by default. The database is SQLite locally and Turso in production. The frontend is Vite and React.

## What is in the repo

- `backend/` - FastAPI app, chat endpoint, OpenAI SDK integration, MCP client
- `mcp_server/` - MCP server with product, user, and order tools
- `shared/` - shared database layer and environment loading
- `frontend/` - Vite and React support page, privacy page, terms page, favicon

## Prerequisites

- Python 3.13
- Node.js 20 or newer
- npm
- A DeepSeek API key or any OpenAI-compatible API key
- Optional: a Turso database for production

## One time setup

1. Create the Python environment and install dependencies from the project root:

   ```bash
   uv venv .venv --python 3.13
   uv pip install --python .venv/bin/python -r requirements.txt
   ```

   If you do not use uv:

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

2. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. Create the environment file:

   ```bash
   cp .env.example .env
   ```

4. Open `.env` and set your LLM key:

   ```bash
   LLM_API_KEY=your-deepseek-api-key
   ```

   The defaults use DeepSeek. To use OpenAI instead, change these values in `.env`:

   ```bash
   LLM_BASE_URL=https://api.openai.com/v1
   LLM_MODEL=gpt-4o-mini
   ```

5. Start the MCP server in one terminal:

   ```bash
   .venv/bin/python -m mcp_server.server
   ```

6. Start the backend in a second terminal:

   ```bash
   .venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
   ```

7. Start the frontend in a third terminal:

   ```bash
   cd frontend
   npm run dev
   ```

8. Open http://localhost:5173

On first startup the backend and MCP server create `support.db` and seed it with two demo users, five products, and two sample orders.

## Environment variables

Backend and MCP server read `.env` from the project root.

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `file:support.db` | Local SQLite file or `libsql://` Turso URL |
| `DATABASE_AUTH_TOKEN` | empty | Turso auth token, required for `libsql://` URLs |
| `LLM_BASE_URL` | `https://api.deepseek.com` | OpenAI-compatible API base URL |
| `LLM_API_KEY` | empty | API key for the LLM provider |
| `LLM_MODEL` | `deepseek-chat` | Model name |
| `MAX_TOOL_STEPS` | `3` | Maximum tool calling rounds per chat turn |
| `MCP_URL` | `http://127.0.0.1:8001/mcp` | URL the backend uses to reach the MCP server |
| `MCP_HOST` | `127.0.0.1` | Host the MCP server binds to |
| `MCP_PORT` | `8001` | Port the MCP server binds to |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma separated origins allowed to call the API |
| `DEFAULT_USER_ID` | `1` | User id used when no `X-User-Id` header is sent |

The frontend reads `frontend/.env` for its proxy target:

| Variable | Default | Purpose |
| --- | --- | --- |
| `VITE_PROXY_TARGET` | `http://127.0.0.1:8000` | Backend URL the Vite dev server proxies `/api` to |

If you run the backend on a different port, create `frontend/.env`:

```bash
cp frontend/.env.example frontend/.env
```

Then set `VITE_PROXY_TARGET` to match the backend port.

## Using the chat

- Ask for product details by name or SKU, for example: "Do you have the KB-101 keyboard in stock?"
- Ask for account details: "Show my recent orders."
- Place an order after confirming items and address: "Order one USB-C Hub 7 in 1 to 48 Market Street, San Francisco, CA 94103."

The demo user is user id 1. To pass a different user, send the `X-User-Id` header with your request:

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -H 'X-User-Id: 2' \
  -d '{"message": "Show my recent orders."}'
```

## Tests

From the project root:

```bash
.venv/bin/python -m pytest backend/tests -q --no-header
```

The tests cover the database layer, the MCP tool functions, the health endpoint, and the assistant tool calling loop. They use a temporary `test_support.db` file and delete it when finished.

## Production build

Build the frontend:

```bash
cd frontend
npm run build
```

The build output is in `frontend/dist`. It includes the favicon, `_redirects` for Netlify, and `vercel.json` for Vercel rewrites so `/privacy` and `/terms` work as direct links.

For the backend, run uvicorn behind your process manager with your production environment variables set:

```bash
.venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Run the MCP server on a private address only:

```bash
.venv/bin/python -m mcp_server.server
```

Keep `MCP_HOST` at `127.0.0.1` and expose only the backend. The MCP server should never be reachable from the public internet.

## Turso setup

Create a Turso database, get its URL and a token, and put them in `.env`:

```bash
turso db create support
turso db show support
turso db tokens create support
```

Then in `.env`:

```bash
DATABASE_URL=libsql://your-database-name.turso.io
DATABASE_AUTH_TOKEN=your-turso-token
```

The schema and seed data are created automatically on startup. The same code path works for `file:support.db`, so local development needs no Turso account.

## Pre-launch checklist

Before going live:

1. Set a real `LLM_API_KEY` and pick the model you want to pay for.
2. Replace the placeholder contact details in the support page and legal pages:
   - `support@example.com`
   - `+1 555 010 0100`
   - `privacy@example.com`
   - `legal@example.com`
3. Connect your custom domain and configure SPA fallback. Netlify and Vercel configs are already included for `/privacy` and `/terms`.
4. Set `CORS_ORIGINS` to your production frontend origin.
5. Point `DATABASE_URL` at Turso and set `DATABASE_AUTH_TOKEN`.
6. Add real user authentication and send the signed-in user id through the `X-User-Id` header instead of relying on `DEFAULT_USER_ID`.
7. Review the privacy policy and terms pages so they match your real data practices and legal jurisdiction.

## Troubleshooting

- Port 8000 already in use: run the backend on another port, then set `VITE_PROXY_TARGET` in `frontend/.env` to match.
- Tool calls fail while plain replies work: the MCP server is not running. Start it with `.venv/bin/python -m mcp_server.server`.
- Chat returns an error event: check that `LLM_API_KEY` is set and that `LLM_BASE_URL` is reachable.
- Run all commands from the project root so the `.env` file and `support.db` are found.
