from fastmcp import FastMCP
from fastmcp.server.apps import AppConfig, ResourceCSP
from fastmcp.tools import ToolResult
from mcp import types
from typing import Optional

mcp = FastMCP("Catalog App Server")

FRONTEND_ORIGIN = (
    "https://mcp-front-test-arfbbch0f8hkgqex.canadacentral-01.azurewebsites.net"
)

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
        if not event_type or not tool_name:
                return f"""<!doctype html>
<html>
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
        <style>
            html, body {{
                height: 100%;
                margin: 0;
                overflow: hidden;
            }}
            iframe {{
                width: 100%;
                height: 100%;
                border: 0;
                display: block;
            }}
        </style>
    </head>
    <body>
        <iframe id=\"app\" src=\"{iframe_src}\"></iframe>
    </body>
</html>"""

        return f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
    <style>
      html, body {{
        height: 100%;
        margin: 0;
        overflow: hidden;
      }}
      iframe {{
        width: 100%;
        height: 100%;
        border: 0;
        display: block;
      }}
    </style>
  </head>
  <body>
    <iframe id=\"app\" src=\"{iframe_src}\"></iframe>

    <script type=\"module\">
      import {{ App }} from "https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps";

      const app = new App({{ name: "Catalog UI Wrapper", version: "1.0.0" }});
      await app.connect();

      const iframe = document.getElementById("app");
      let lastSentAt = 0;

      window.addEventListener("message", async (ev) => {{
        const data = ev.data || {{}};

        if (ev.source !== iframe.contentWindow) return;


        if (data.type === "open_link" && typeof data.url === "string") {{
          const result = await app.openLink({{ url: data.url }});
          if (result?.isError) {{
            await app.sendMessage({{
              role: "user",
              content: [{{ type: "text", text: `No pude abrir el link automáticamente. Aquí está: ${data.url}` }}],
            }});
          }}
          return;
        }}

        if (data.type !== "{event_type}") return;

        const value = data.value;

        const now = Date.now();
        if (now - lastSentAt < 400) return;
        lastSentAt = now;

        const toolResult = await app.callServerTool({{
          name: "{tool_name}",
          arguments: {{ value }}
        }});

        const text = toolResult?.content?.find(c => c.type === "text")?.text
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
    prefers_border=True,
)


@mcp.tool(app=AppConfig(resource_uri=RANGE_EARNINGS_VIEW_URI, prefers_border=True))
def open_range_earnings_ui() -> ToolResult:
    """Abre la UI para seleccionar un rango salarial (earnings)."""
    return ToolResult(
        content=[
            types.TextContent(type="text", text="Abriendo UI de rangos salariales…")
        ]
    )


@mcp.tool(app=AppConfig(resource_uri=BENEFITS_VIEW_URI, prefers_border=True))
def open_benefits_ui() -> ToolResult:
    """Abre la UI para seleccionar el tipo de beneficios (cashback, millas, descuentos, etc)."""
    return ToolResult(
        content=[types.TextContent(type="text", text="Abriendo UI de beneficios…")]
    )


@mcp.tool(app=AppConfig(resource_uri=CARD_DASHBOARD_VIEW_URI, prefers_border=True))
def open_card_dashboard_ui() -> ToolResult:
    """Abre la UI que muestra la lista de tarjetas de crédito."""
    return ToolResult(
        content=[types.TextContent(type="text", text="Abriendo Card Dashboard…")]
    )


@mcp.tool(
    app=AppConfig(resource_uri=IDENTIFICATION_FLOW_VIEW_URI, prefers_border=True)
)
def open_identification_flow_ui() -> ToolResult:
    """Abre la UI del flujo de identificación del usuario."""
    return ToolResult(
        content=[
            types.TextContent(type="text", text="Abriendo Identification Flow…")
        ]
    )


@mcp.tool(
    app=AppConfig(
        resource_uri=RANGE_EARNINGS_VIEW_URI,
        visibility=["app"],
        prefers_border=True,
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
        prefers_border=True,
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
    return _wrapper_html(
        iframe_src=f"{FRONTEND_ORIGIN}/card-dashboard",
        event_type="open_link",
        tool_name="unknown",
    )


@mcp.resource(IDENTIFICATION_FLOW_VIEW_URI, app=_RESOURCE_APP)
def identification_flow_view() -> str:
    return _wrapper_html(iframe_src=f"{FRONTEND_ORIGIN}/identification-flow")

@mcp.tool(app=AppConfig(resource_uri=RANGE_EARNINGS_VIEW_URI, prefers_border=True))
def open_ui() -> ToolResult:
    return open_range_earnings_ui()

if __name__ == "__main__":
    mcp.run()