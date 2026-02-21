from fastmcp import FastMCP
from fastmcp.server.apps import AppConfig, ResourceCSP
from fastmcp.tools import ToolResult
from mcp import types
from typing import Optional

mcp = FastMCP("Catalog App Server")

FRONTEND_ORIGIN = "https://mcp-front-test-arfbbch0f8hkgqex.canadacentral-01.azurewebsites.net"

RANGE_EARNINGS_VIEW_URI = "ui://catalog/range-earnings.html"
BENEFITS_VIEW_URI = "ui://catalog/benefits.html"
CARD_DASHBOARD_VIEW_URI = "ui://catalog/card-dashboard.html"
IDENTIFICATION_FLOW_VIEW_URI = "ui://catalog/identification-flow.html"


def _wrapper_html(
    *,
    iframe_src: str,
    event_type: Optional[str] = None,
    tool_name: Optional[str] = None,
) -> str:
    # Evita que "None" se imprima en JS
    event_type_js = event_type or ""
    tool_name_js = tool_name or ""

    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <style>
      html, body {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        background: transparent;
      }}

      /* Fullscreen dentro del webview */
      iframe {{
        position: fixed;
        inset: 0;
        width: 100vw;
        height: 100vh;
        border: 0;
        display: block;
      }}
    </style>
  </head>
  <body>
    <iframe
      id="app"
      src="{iframe_src}"
      allow="clipboard-read; clipboard-write; fullscreen"
    ></iframe>

    <script type="module">
      import {{ App }} from "https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps";

      const app = new App({{ name: "Catalog UI Wrapper", version: "1.0.0" }});
      await app.connect();

      const iframe = document.getElementById("app");
      let lastSentAt = 0;

      window.addEventListener("message", async (ev) => {{
        const data = ev.data || {{}};

        // 1) open_link: siempre disponible
        if (data.type === "open_link" && typeof data.url === "string") {{
          try {{
            const result = await app.openLink({{ url: data.url }});
            if (result?.isError) {{
              await app.sendMessage({{
                role: "user",
                content: [{{ type: "text", text: `No pude abrir el link automáticamente. Aquí está: ${{data.url}}` }}],
              }});
            }}
          }} catch (e) {{
            await app.sendMessage({{
              role: "user",
              content: [{{ type: "text", text: `No pude abrir el link automáticamente. Aquí está: ${{data.url}}` }}],
            }});
          }}
          return;
        }}

        // 2) Desde aquí, solo mensajes del iframe principal
        if (ev.source !== iframe.contentWindow) return;

        const EVENT_TYPE = "{event_type_js}";
        const TOOL_NAME  = "{tool_name_js}";
        if (!EVENT_TYPE || !TOOL_NAME) return;

        if (data.type !== EVENT_TYPE) return;

        const value = data.value;

        const now = Date.now();
        if (now - lastSentAt < 400) return;
        lastSentAt = now;

        const toolResult = await app.callServerTool({{
          name: TOOL_NAME,
          arguments: {{ value }}
        }});

        const text =
          toolResult?.content?.find(c => c.type === "text")?.text
          ?? `Selección: ${{value}}`;

        await app.sendMessage({{
          role: "user",
          content: [{{ type: "text", text }}]
        }});
      }});
    </script>
  </body>
</html>"""


_RESOURCE_APP = AppConfig(
    csp=ResourceCSP(
        resource_domains=["https://unpkg.com", FRONTEND_ORIGIN],
        frame_domains=[FRONTEND_ORIGIN],
    ),
    prefers_border=False,
)


# =========================
# TOOLS "ABRIR UI" (los que el modelo elegirá por keywords)
# =========================

# --- DASHBOARD / CATÁLOGO ---
@mcp.tool(app=AppConfig(resource_uri=CARD_DASHBOARD_VIEW_URI, prefers_border=False, visibility=["app"]))
def catalogo() -> ToolResult:
    """Abre el catálogo de tarjetas (dashboard / listado de tarjetas)."""
    return ToolResult(content=[types.TextContent(type="text", text="Abriendo catálogo de tarjetas…")])


@mcp.tool(app=AppConfig(resource_uri=CARD_DASHBOARD_VIEW_URI, prefers_border=False, visibility=["app"]))
def tarjetas() -> ToolResult:
    """Abre tarjetas (catálogo / dashboard / listado de tarjetas)."""
    return ToolResult(content=[types.TextContent(type="text", text="Abriendo listado de tarjetas…")])


@mcp.tool(app=AppConfig(resource_uri=CARD_DASHBOARD_VIEW_URI, prefers_border=False, visibility=["app"]))
def listado_tarjetas() -> ToolResult:
    """Abre el listado de tarjetas (catálogo / dashboard)."""
    return ToolResult(content=[types.TextContent(type="text", text="Abriendo listado de tarjetas…")])


# --- IDENTIFICACIÓN / DNI / AUTENTICACIÓN ---
@mcp.tool(app=AppConfig(resource_uri=IDENTIFICATION_FLOW_VIEW_URI, prefers_border=False, visibility=["app"]))
def dni() -> ToolResult:
    """Abre el flujo de DNI / identificación del usuario."""
    return ToolResult(content=[types.TextContent(type="text", text="Abriendo flujo de DNI…")])


@mcp.tool(app=AppConfig(resource_uri=IDENTIFICATION_FLOW_VIEW_URI, prefers_border=False, visibility=["app"]))
def autenticacion() -> ToolResult:
    """Abre autenticación / verificación / identificación del usuario."""
    return ToolResult(content=[types.TextContent(type="text", text="Abriendo flujo de autenticación…")])


# --- BENEFICIOS ---
@mcp.tool(app=AppConfig(resource_uri=BENEFITS_VIEW_URI, prefers_border=False, visibility=["app"]))
def beneficios() -> ToolResult:
    """Abre la vista de beneficios (cashback, millas, descuentos, recompensas)."""
    return ToolResult(content=[types.TextContent(type="text", text="Abriendo beneficios…")])


# --- RANGO / RANGO SALARIAL ---
@mcp.tool(app=AppConfig(resource_uri=RANGE_EARNINGS_VIEW_URI, prefers_border=False, visibility=["app"]))
def rango() -> ToolResult:
    """Abre la vista de rango (rango salarial / ingresos)."""
    return ToolResult(content=[types.TextContent(type="text", text="Abriendo rango salarial…")])


@mcp.tool(app=AppConfig(resource_uri=RANGE_EARNINGS_VIEW_URI, prefers_border=False, visibility=["app"]))
def rango_salarial() -> ToolResult:
    """Abre la vista de rango salarial / ingresos."""
    return ToolResult(content=[types.TextContent(type="text", text="Abriendo rango salarial…")])


# (Opcional) Mantener un "open_ui" por defecto -> catálogo
@mcp.tool(app=AppConfig(resource_uri=CARD_DASHBOARD_VIEW_URI, prefers_border=False, visibility=["app"]))
def open_ui() -> ToolResult:
    """Abre la UI principal (catálogo de tarjetas)."""
    return ToolResult(content=[types.TextContent(type="text", text="Abriendo catálogo de tarjetas…")])



# =========================
# TOOLS "BRIDGE" (llamados desde la UI)
# =========================

@mcp.tool(
    app=AppConfig(
        resource_uri=RANGE_EARNINGS_VIEW_URI,
        visibility=["app"],
        prefers_border=False,
    )
)
def build_range_earnings_message(value: str) -> ToolResult:
    print(f"[tool] build_range_earnings_message value={value!r}")
    messages = {
        "lt_1200": "SOLO COMENTA: Elegiste menos de **S/ 1200**. NOTA: no coloques níngun mensaje adicional ni modifiques nada.",
        "1200_2500": "SOLO COMENTA: Elegiste **S/ 1200 - S/ 2500**. NOTA: no coloques níngun mensaje adicional ni modifiques nada.",
        "2501_5000": "SOLO COMENTA: Elegiste **S/ 2501 - S/ 5000**. NOTA: no coloques níngun mensaje adicional ni modifiques nada.",
        "gt_5000": "SOLO COMENTA: Elegiste más de **S/ 5000**. NOTA: no coloques níngun mensaje adicional ni modifiques nada.",
    }
    text = messages.get(value, f"Recibí tu selección: {value}")
    return ToolResult(content=[types.TextContent(type="text", text=text)])


@mcp.tool(
    app=AppConfig(
        resource_uri=BENEFITS_VIEW_URI,
        visibility=["app"],
        prefers_border=False,
    )
)
def build_benefits_message(value: str) -> ToolResult:
    print(f"[tool] build_benefits_message value={value!r}")
    messages = {
        "cb": "SOLO COMENTA: Elegiste **Cashback** como beneficio. NOTA: no coloques níngun mensaje adicional ni modifiques nada.",
        "mv": "SOLO COMENTA: Elegiste **Millas / Viaje** como beneficio. NOTA: no coloques níngun mensaje adicional ni modifiques nada.",
        "dl": "SOLO COMENTA: Elegiste **Descuentos locales** como beneficio. NOTA: no coloques níngun mensaje adicional ni modifiques nada.",
        "rg": "SOLO COMENTA: Elegiste **Recompensas generales** como beneficio. NOTA: no coloques níngun mensaje adicional ni modifiques nada.",
    }
    text = messages.get(value, f"Recibí tu selección: {value}")
    return ToolResult(content=[types.TextContent(type="text", text=text)])



# =========================
# RESOURCES (HTML wrapper)
# =========================

@mcp.resource(RANGE_EARNINGS_VIEW_URI, app=_RESOURCE_APP)
def range_earnings_view() -> str:
    return _wrapper_html(
        iframe_src=f"{FRONTEND_ORIGIN}/range-earings",
        event_type="range_earnings_selected",
        tool_name="build_range_earnings_message",
    )


@mcp.resource(BENEFITS_VIEW_URI, app=_RESOURCE_APP)
def benefits_view() -> str:
    return _wrapper_html(
        iframe_src=f"{FRONTEND_ORIGIN}/benefit-options",
        event_type="benefits_selected",
        tool_name="build_benefits_message",
    )


@mcp.resource(CARD_DASHBOARD_VIEW_URI, app=_RESOURCE_APP)
def card_dashboard_view() -> str:
    # dashboard no necesita event_type/tool_name
    return _wrapper_html(iframe_src=f"{FRONTEND_ORIGIN}/card-dashboard")


@mcp.resource(IDENTIFICATION_FLOW_VIEW_URI, app=_RESOURCE_APP)
def identification_flow_view() -> str:
    return _wrapper_html(iframe_src=f"{FRONTEND_ORIGIN}/identification-flow")


if __name__ == "__main__":
    mcp.run()