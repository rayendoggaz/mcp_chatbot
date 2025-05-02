from mcp.server.fastmcp import FastMCP
from article_tools import register_tools as register_article_tools
from client_tools import register_tools as register_client_tools
from sales_order_tools import register_tools as register_sales_order_tools

mcp = FastMCP("churnandburn")

# Register tools from each module
register_article_tools(mcp)
register_client_tools(mcp)
register_sales_order_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")