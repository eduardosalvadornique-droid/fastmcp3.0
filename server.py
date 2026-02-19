from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.apps import AppConfig, ResourceCSP
from fastmcp.tools import ToolResult
from mcp import types

mcp = FastMCP("Catalog App Server")

UI_DIR = Path("ui")
BASE_URI = "ui://sum-app"
VIEW_URI = f"{BASE_URI}/index.html"

# Config compartida para UI (puedes ajustar CSP si lo necesitas)
UI_APP_CONFIG = AppConfig(
    domain="https://sum-app.local",
    # Si NO usas CDN (unpkg) ya no lo necesitas.
    # Déjalo vacío o quítalo por completo.
    csp=ResourceCSP(
        resource_domains=["https://unpkg.com"]
    ),
    prefers_border=True
)

# TOOL PRINCIPAL: esto es lo que "abre" la UI dentro de ChatGPT
@mcp.tool(app=AppConfig(resource_uri=VIEW_URI, prefers_border=True))
def open_catalog() -> ToolResult:
    return ToolResult(
        content=[
            types.TextContent(type="text", text="Mostrando catálogo embebido…")
        ]
    )

# 1) RECURSO: index.html (producto del build)
@mcp.resource(VIEW_URI, app=UI_APP_CONFIG)
def view() -> str:
    html = (UI_DIR / "index.html").read_text(encoding="utf-8")

    # Para que <img src="tarjetas_ntt-01.png"> resuelva a ui://sum-app/tarjetas_ntt-01.png
    if "<base" not in html:
        html = html.replace("<head>", f'<head><base href="{BASE_URI}/">', 1)

    return html

# 2) RECURSOS: imágenes (como son pocas, explícitas es lo más simple y robusto)
def _png(name: str) -> bytes:
    return (UI_DIR / name).read_bytes()

@mcp.resource(f"{BASE_URI}/tarjetas_ntt-01.png", app=UI_APP_CONFIG)
def img_01() -> bytes: return _png("tarjetas_ntt-01.png")

@mcp.resource(f"{BASE_URI}/tarjetas_ntt-02.png", app=UI_APP_CONFIG)
def img_02() -> bytes: return _png("tarjetas_ntt-02.png")

@mcp.resource(f"{BASE_URI}/tarjetas_ntt-03.png", app=UI_APP_CONFIG)
def img_03() -> bytes: return _png("tarjetas_ntt-03.png")

@mcp.resource(f"{BASE_URI}/tarjetas_ntt-04.png", app=UI_APP_CONFIG)
def img_04() -> bytes: return _png("tarjetas_ntt-04.png")

@mcp.resource(f"{BASE_URI}/tarjetas_ntt-05.png", app=UI_APP_CONFIG)
def img_05() -> bytes: return _png("tarjetas_ntt-05.png")

# SVG
@mcp.resource(f"{BASE_URI}/vite.svg", app=UI_APP_CONFIG)
def vite_svg() -> bytes:
    return (UI_DIR / "vite.svg").read_bytes()

if __name__ == "__main__":
    mcp.run()
