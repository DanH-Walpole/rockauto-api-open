#!/usr/bin/env python3
"""
Alternative MCP server that bypasses SSL issues by using a simpler HTTP approach
"""
import os
import sys
import ssl
import urllib3

# Disable SSL warnings and verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# Set environment variables to disable SSL verification
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['HTTPX_SSL_VERIFY'] = 'false'

from fastmcp import FastMCP
from rockauto import rockauto_api

INSTRUCTIONS = (
    "Use the available tools to help users find vehicle parts in the RockAuto catalog. "
    "Navigate makes, years, engines, categories, subcategories and part numbers."
)

server = FastMCP.from_fastapi(
    rockauto_api,
    name="RockAuto MCP",
    instructions=INSTRUCTIONS,
)

# Remove the root endpoint so the toolset stays small
try:
    server.remove_tool("root")
except Exception:
    pass

if __name__ == "__main__":
    # Run MCP server on HTTP for web access and testing
    # For Claude Desktop or other MCP clients, use: server.run() for stdio
    # For web/HTTP testing: server.run(transport="http", port=8002)
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        print("Starting MCP server on HTTP at http://localhost:8002/mcp/")
        server.run(transport="http", host="0.0.0.0", port=8002)
    else:
        print("Starting MCP server on stdio (for MCP clients)")
        print("Use --http flag to run on HTTP at port 8002")
        server.run()
