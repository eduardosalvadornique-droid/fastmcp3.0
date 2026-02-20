from fastmcp import FastMCP
from fastmcp.server.apps import AppConfig, ResourceCSP
from fastmcp.tools import ToolResult
from mcp import types

mcp = FastMCP("Catalog App Server")

FRONTEND_ORIGIN = "https://mcp-front-test-arfbbch0f8hkgqex.canadacentral-01.azurewebsites.net"
VIEW_URI = "ui://catalog/view.html"

@mcp.tool(app=AppConfig(resource_uri=VIEW_URI, prefers_border=True))
def open_ui() -> ToolResult:
    return ToolResult(content=[types.TextContent(type="text", text="Abriendo UI…")])

@mcp.resource(
    VIEW_URI,
    app=AppConfig(
        csp=ResourceCSP(
            # por si tu HTML del "wrapper" carga imágenes/css/etc (normalmente no mucho)
            resource_domains=[FRONTEND_ORIGIN],
            # CLAVE: permitir iframes anidados
            frame_domains=[FRONTEND_ORIGIN],
            # solo si dentro del wrapper haces fetch (no necesario en este wrapper)
            # connect_domains=[FRONTEND_ORIGIN],
        ),
        prefers_border=True,
    ),
)
def view() -> str:
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <style>
      html, body {{ height: 100%; margin: 0; }}
      iframe {{ width: 100%; height: 100%; border: 0; }}
    </style>
  </head>
  <body>
    <iframe src="{FRONTEND_ORIGIN}/" allow="clipboard-read; clipboard-write"></iframe>
  </body>
</html>"""

if __name__ == "__main__":
    mcp.run()