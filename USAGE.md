# RockAuto API & MCP Server Usage Guide

This project provides both a traditional REST API and an MCP (Model Context Protocol) server for accessing RockAuto catalog data.

## Understanding the Architecture

### FastMCP vs Regular API
- **FastAPI Server (`start.py`)**: Traditional REST API with OpenAPI docs
- **MCP Server (`mcp_server.py`)**: Model Context Protocol server for AI agents/clients
- **Combined Server (`combined_server.py`)**: Simplified approach running just the FastAPI server

## Running the Servers

### Option 1: Separate Servers (Recommended)

**Terminal 1 - FastAPI Server:**
```bash
python start.py
```
- Serves REST API at: http://localhost:8000
- API docs at: http://localhost:8000/docs

**Terminal 2 - MCP Server (for AI clients):**
```bash
python mcp_server.py
```
- Runs on stdio for MCP clients (Claude Desktop, etc.)

**Terminal 2 Alternative - MCP Server (for HTTP testing):**
```bash
python mcp_server.py --http
```
- Serves MCP over HTTP at: http://localhost:8002/mcp/
- Can test with web clients (requires SSE headers)

### Option 2: Combined Server (Simplified)

```bash
python combined_server.py
```
- Serves only the REST API at: http://localhost:8000
- For MCP functionality, still run `mcp_server.py` separately

## Testing the Setup

### Test the REST API:
```bash
curl http://localhost:8000/makes
```

### Test MCP Server (if running with --http):
```bash
curl -H "Accept: text/event-stream" http://localhost:8002/mcp/
```
(Note: This will show an error about missing session ID, which is expected)

### Available Endpoints

#### REST API Endpoints:
- `GET /makes` - List all vehicle makes
- `GET /years` - Get years for a make
- `GET /models` - Get models for make/year
- `GET /engines` - Get engines for make/year/model
- `GET /categories` - Get part categories
- `GET /sub_categories` - Get subcategories
- `GET /parts` - Get parts for specific vehicle/category
- `GET /search` - Flexible search
- `GET /closeouts/{carcode}` - Closeout deals
- `GET /vehicle_info` - Vehicle details

#### MCP Tools (when using MCP server):
The MCP server automatically converts all FastAPI endpoints to MCP tools that can be used by AI agents.

## For MCP Integration

### With Claude Desktop
Add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "rockauto": {
      "command": "python",
      "args": ["/path/to/your/mcp_server.py"],
      "cwd": "/path/to/rockauto-api-open"
    }
  }
}
```

### With FastMCP Client
```python
from fastmcp import Client

async with Client("python mcp_server.py") as client:
    tools = await client.list_tools()
    result = await client.call_tool("get_makes_makes_get", {})
```

## Key Points

1. **FastMCP doesn't serve both protocols simultaneously** - it converts your FastAPI app to MCP format
2. **Use separate processes** for REST API and MCP if you need both
3. **MCP is for AI agents**, REST API is for traditional web/mobile clients
4. **The `--http` flag** on MCP server is mainly for testing; real MCP clients use stdio

## Troubleshooting

- If MCP server doesn't work, ensure all dependencies are installed: `pip install fastmcp`
- If you see "tool not found" errors, the MCP conversion might have issues with complex endpoints
- For production, consider using separate deployment strategies for each protocol

## ✅ MCP Integration Status: WORKING!

**Good News:** The MCP integration is functional! Here's what we confirmed:

### ✅ What's Working:
- **MCP tools are available** in AI agent toolsets
- **Part number search works perfectly**: `mcp_test-rockauto_search_part_by_number_part_number(partnum="12345")`
- **Direct function calls work**: Both `get_makes()` and `search_parts()` return complete data
- **FastAPI endpoints work**: HTTP requests to `/makes` return all 268 makes including Honda
- **FastMCP integration is correct**: FastAPI → MCP conversion is successful

### ⚠️ Known Issue:
- **Mechanize SSL compatibility**: Some MCP tools fail with `HTTPSConnection.__init__() got an unexpected keyword argument 'key_file'`
- **Root cause**: The mechanize library has SSL/TLS compatibility issues with current Python/SSL setup
- **Impact**: Affects web scraping endpoints, but not all MCP functionality

### 🎯 Honda Confirmed Available:
- **268 total makes** in RockAuto catalog
- **Honda is present**: `{'make': 'HONDA', 'link': 'https://www.rockauto.com/en/catalog/honda'}`
- **Accessible via**: Direct API calls, search functions, and working MCP tools

### 🔧 Fixes Applied:
- Replaced mechanize with requests in `get_makes()` function
- Fixed BeautifulSoup syntax and SSL issues
- Updated search function to use requests for makes retrieval

### 🚀 For AI Agents:
The MCP tools that work (like part number search) provide rich, structured data perfect for AI agents to help users find Honda parts and other vehicle components.
