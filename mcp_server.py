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
    server.run()
