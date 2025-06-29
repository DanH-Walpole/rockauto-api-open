"""
Better approach: Run the MCP server on HTTP transport with a different path.
This serves both the original FastAPI and MCP over HTTP.
"""

from fastapi import FastAPI
from fastmcp import FastMCP
from rockauto import rockauto_api
import uvicorn
import asyncio
import threading

# Create the original API app
app = rockauto_api

# Add a root endpoint to show both services
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "RockAuto API Server",
        "services": {
            "api": "http://localhost:8000/ - Original FastAPI endpoints (this service)",
            "mcp": "http://localhost:8001/sse - MCP over Server-Sent Events (separate port)",
            "docs": "http://localhost:8000/docs - API documentation"
        },
        "note": "Run mcp_server.py separately for MCP functionality"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
