from fastmcp import FastMCP
from fastmcp.server.apps import AppConfig, ResourceCSP
from fastmcp.tools import ToolResult
from mcp import types

mcp = FastMCP("Sum App Server")

VIEW_URI = "ui://sum-app/view.html"


# TOOL PRINCIPAL
@mcp.tool(
    app=AppConfig(
        resource_uri=VIEW_URI,
        prefers_border=True  # Hace que el host renderice con borde visual
    )
)
def sumar(a: float, b: float) -> ToolResult:
    """Suma dos números y devuelve el resultado."""
    resultado = a + b

    return ToolResult(
        content=[
            types.TextContent(
                type="text",
                text=str(resultado)
            )
        ]
    )


# RECURSO UI
@mcp.resource(
    VIEW_URI,
    app=AppConfig(
        domain="https://sum-app.local",
        csp=ResourceCSP(
            resource_domains=["https://unpkg.com"]
        ),
        prefers_border=True
    )
)
def view() -> str:
    with open("ui/sum.html", "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    mcp.run()
