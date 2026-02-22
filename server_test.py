from fastmcp import FastMCP
from fastmcp.server.apps import AppConfig, ResourceCSP, ResourcePermissions
from fastmcp.tools import ToolResult
from mcp import types
from dataclasses import dataclass
from typing import Optional
import random

mcp = FastMCP("Catalog App Server")

FRONTEND_ORIGIN = (
    "https://mcp-front-test-arfbbch0f8hkgqex.canadacentral-01.azurewebsites.net"
)

RANGE_EARNINGS_VIEW_URI = "ui://catalog/range-earnings.html"
BENEFITS_VIEW_URI = "ui://catalog/benefits.html"
CARD_DASHBOARD_VIEW_URI = "ui://catalog/card-dashboard.html"
IDENTIFICATION_FLOW_VIEW_URI = "ui://catalog/identification-flow.html"
_card_dashboard_count: Optional[int] = None


@dataclass
class ToolInfo:
    label: str
    mensaje_fijo: str


class ToolInfoStore:
    def __init__(self) -> None:
        self._data: dict[str, ToolInfo] = {}

    def save(self, tool_name: str, label: str) -> ToolInfo:
        tool_info = ToolInfo(
            label=label,
            mensaje_fijo=f"{tool_name}_{random.randint(1, 5)}",
        )
        self._data[tool_name] = tool_info
        return tool_info

    def summary_text(self) -> str:
        return " | ".join(
            f"{tool_name}: label={tool_info.label}; mensaje_fijo={tool_info.mensaje_fijo}"
            for tool_name, tool_info in self._data.items()
        )


_tool_info_store = ToolInfoStore()


def _wrapper_html(
        *,
        iframe_src: str,
        event_type: Optional[str] = None,
        tool_name: Optional[str] = None,
        iframe_height: str = "460px",
) -> str:
        
        return f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
    <style>
      html, body {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: auto;
        overflow: hidden;
        background: transparent;
      }}

      #iframe-container {{
        width: 100%;
        height: {iframe_height};
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
    <div id="iframe-container">
      <iframe
        id="app"
        src="{iframe_src}"
        allow="camera; microphone; clipboard-read; clipboard-write; fullscreen"
        referrerpolicy="strict-origin-when-cross-origin"
      ></iframe>
    </div>

    <script type=\"module\">
      import {{ App }} from "https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps";

      const app = new App({{ name: "Catalog UI Wrapper", version: "1.0.0" }});
      await app.connect();

      const iframe = document.getElementById("app");
      let lastSentAt = 0;

      window.addEventListener("message", async (ev) => {{
        const data = ev.data || {{}};
        const expectedOrigin = new URL("{iframe_src}").origin;

        if (ev.origin !== expectedOrigin) return;

        if (data.type === "open_link" && typeof data.url === "string") {{
          const result = await app.openLink({{ url: data.url }});
          if (result?.isError) {{
            await app.sendMessage({{
              role: "user",
              content: [{{ type: "text", text: `No pude abrir el link automáticamente. Aquí está: ${{data.url}}` }}],
            }});
          }}
          return;
        }}

        if (ev.source !== iframe.contentWindow) return;

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
        const structured = toolResult?.structuredContent ?? toolResult?.structured_content ?? null;
        const nextUiUri = structured?.next_ui_uri;

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
    permissions=ResourcePermissions(
        camera={},
        microphone={},
    ),
    prefers_border=False,
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


@mcp.tool(app=AppConfig(resource_uri=CARD_DASHBOARD_VIEW_URI, prefers_border=False))
def open_card_dashboard_ui() -> ToolResult:
    """Abre la UI que muestra la lista de tarjetas de crédito."""
    return ToolResult(
        content=[types.TextContent(type="text", text="Abriendo Card Dashboard…")]
    )


@mcp.tool(
    app=AppConfig(resource_uri=CARD_DASHBOARD_VIEW_URI, prefers_border=False)
)
def open_card_dashboard_ui_with_count(count: Optional[int] = None) -> ToolResult:
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
        "lt_1200": "El usuario eligió menos de S/ 1200.",
        "1200_2500": "El usuario eligió S/ 1200 - S/ 2500.",
        "2501_5000": "El usuario eligió S/ 2501 - S/ 5000.",
        "gt_5000": "El usuario eligió más de S/ 5000.",
    }
    label = messages.get(value, f"Recibí : {value}")
    _tool_info_store.save("build_range_earnings_message", label)
    text = (
        f"PRIMERO: muestra este mensaje al usuario: {label}. "
        "DESPUÉS: llama inmediatamente a la tool `open_benefits_ui`. "
        "No expliques tu razonamiento."
    )
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
        "cb": "El usuario eligió Cashback.",
        "mv": "El usuario eligió Millas / Viaje.",
        "dl": "El usuario eligió Descuentos locales.",
        "rg": "El usuario eligió Recompensas generales.",
    }
    label = messages.get(value, f"Recibí: {value}")
    _tool_info_store.save("build_benefits_message", label)
    text = (
        f"PRIMERO: muestra este mensaje al usuario: {label}. "
        "DESPUÉS: llama inmediatamente a la tool `open_identification_flow_ui`. "
        "No expliques tu razonamiento."
    )
    return ToolResult(content=[types.TextContent(type="text", text=text)])


@mcp.tool(
    app=AppConfig(
        resource_uri=IDENTIFICATION_FLOW_VIEW_URI,
        visibility=["app"],
        prefers_border=True,
    )
)
def build_identification_message(value: str) -> ToolResult:
    print(f"[tool] build_identification_message value={value!r}")
    label = f"Te hemos evaluado con tu DNI {value}"
    _tool_info_store.save("build_identification_message", label)
    summary = _tool_info_store.summary_text()
    user_message = f"{label} y a continuación te mostraremos tus tarjetas disponibles. RESUMEN TOOLS: {summary}."
    text = (
        "PRIMERO: copia y pega completo, sin recortar ni resumir, el texto entre [INICIO] y [FIN]. "
        f"[INICIO]{user_message}[FIN]. "
        "DESPUÉS: llama inmediatamente a la tool `open_card_dashboard_ui_with_count`. "
        "No expliques tu razonamiento."
    )
    return ToolResult(content=[types.TextContent(type="text", text=text)])


@mcp.resource(RANGE_EARNINGS_VIEW_URI, app=_RESOURCE_APP)
def range_earnings_view() -> str:
    return _wrapper_html(
        iframe_src=f"{FRONTEND_ORIGIN}/range-earings",
        event_type="range_earnings_selected",
        tool_name="build_range_earnings_message",
        iframe_height="280px",
    )


@mcp.resource(BENEFITS_VIEW_URI, app=_RESOURCE_APP)
def benefits_view() -> str:
    return _wrapper_html(
        iframe_src=f"{FRONTEND_ORIGIN}/benefit-options",
        event_type="benefits_selected",
        tool_name="build_benefits_message",
        iframe_height="280px",
    )


@mcp.resource(CARD_DASHBOARD_VIEW_URI, app=_RESOURCE_APP)
def card_dashboard_view() -> str:
    count = random.randint(1, 5)
    iframe_src = f"{FRONTEND_ORIGIN}/card-dashboard?count={count}"

    return _wrapper_html(
        iframe_src=iframe_src,
        event_type="open_link",
        tool_name="unknown",
        iframe_height="420px",
    )

@mcp.resource(IDENTIFICATION_FLOW_VIEW_URI, app=_RESOURCE_APP)
def identification_flow_view() -> str:
    return _wrapper_html(
        iframe_src=f"{FRONTEND_ORIGIN}/identification-flow",
        event_type="identification_send_data",
        tool_name="build_identification_message",
        iframe_height="280px",
    )

@mcp.tool(app=AppConfig(resource_uri=RANGE_EARNINGS_VIEW_URI, prefers_border=True))
def open_ui() -> ToolResult:
    return open_range_earnings_ui()

if __name__ == "__main__":
    mcp.run()
