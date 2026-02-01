from mcp.server import FastMCP

mcp = FastMCP("ambientdata-mcp")


@mcp.tool()
def demo_tool(name: str) -> str:
    """A demo tool that greets the user by name."""
    return f"Hello, {name}!"


def main() -> None:
    mcp.run()
