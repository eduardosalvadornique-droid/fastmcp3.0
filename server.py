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
CARD_DASHBOARD_VIEW_READONLY_URI = "ui://catalog/card-dashboard-readonly.html"
IDENTIFICATION_FLOW_VIEW_URI = "ui://catalog/identification-flow.html"

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
      let eventHandled = false;
      let eventInFlight = false;

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
        if (eventHandled || eventInFlight) return;

        const value = data.value;

        const now = Date.now();
        if (now - lastSentAt < 400) return;
        lastSentAt = now;
        eventInFlight = true;
        try {{
          const toolResult = await app.callServerTool({{
            name: "{tool_name}",
            arguments: {{ value }}
          }});

          const text = toolResult?.content?.find(c => c.type === "text")?.text
            ?? `Selección: ${{value}}`;
          const structured = toolResult?.structuredContent ?? toolResult?.structured_content ?? null;
          const nextToolName = structured?.next_tool_name ?? null;
          const nextToolArguments = structured?.next_tool_arguments ?? {{}};

          await app.sendMessage({{
            role: "user",
            content: [{{ type: "text", text }}]
          }});

          if (typeof nextToolName === "string" && nextToolName.length > 0) {{
            try {{
              await app.callServerTool({{
                name: nextToolName,
                arguments: nextToolArguments
              }});
            }} catch (err) {{
              await app.sendMessage({{
                role: "user",
                content: [{{ type: "text", text: `No pude abrir la siguiente pantalla automáticamente (${{nextToolName}}).` }}]
              }});
            }}
          }}

          eventHandled = true;
        }} finally {{
          eventInFlight = false;
        }}
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


@mcp.tool(
    app=AppConfig(
        resource_uri=RANGE_EARNINGS_VIEW_URI,
        prefers_border=True,
    )
)
def open_range_earnings_ui() -> ToolResult:
    """Abre la UI para seleccionar un rango salarial (earnings).
    Usar cuando el usuario quiera iniciar solicitud de tarjeta.
    """
    return ToolResult(
        content=[
            types.TextContent(type="text", text="Abriendo UI de rangos salariales…")
        ]
    )


@mcp.tool(
    app=AppConfig(
        resource_uri=RANGE_EARNINGS_VIEW_URI,
        prefers_border=True,
    )
)
def start_card_application_flow() -> ToolResult:
    """Usar cuando la intención sea obtener/conseguir/aplicar a una tarjeta.
    Esta tool SIEMPRE inicia el flujo en rango salarial.
    """
    return ToolResult(
        content=[
            types.TextContent(
                type="text",
                text="Iniciando flujo de solicitud de tarjeta desde rango salarial…",
            )
        ]
    )


@mcp.tool(
    app=AppConfig(
        resource_uri=BENEFITS_VIEW_URI,
        prefers_border=True,
    )
)
def open_benefits_ui() -> ToolResult:
    """Abre la UI para seleccionar el tipo de beneficios (cashback, millas, descuentos, etc)."""
    return ToolResult(
        content=[types.TextContent(type="text", text="Abriendo UI de beneficios…")]
    )


@mcp.tool(
    app=AppConfig(
        resource_uri=CARD_DASHBOARD_VIEW_URI,
        prefers_border=False,
    )
)
def open_card_dashboard_ui() -> ToolResult:
    """Tool genérica de tarjetas.
    Preferencia de uso:
    - Si el usuario solo quiere ver/explorar tarjetas, usar `open_card_dashboard_ui_readonly`.
    - Si vienes del flujo evaluado/final, usar `open_card_dashboard_ui_with_count`.
    """
    return ToolResult(
        content=[types.TextContent(type="text", text="Abriendo Card Dashboard…")]
    )


@mcp.tool(
    app=AppConfig(
        resource_uri=CARD_DASHBOARD_VIEW_READONLY_URI,
        prefers_border=False,
    )
)
def open_card_dashboard_ui_readonly() -> ToolResult:
    """Usar cuando la intención sea ver/explorar tarjetas sin aplicar.
    Ejemplos: "ver tarjetas", "mostrar tarjetas", "qué tarjetas hay".
    Esta vista oculta el botón de aplicar.
    """
    return ToolResult(
        content=[types.TextContent(type="text", text="Abriendo Card Dashboard (solo vista)…")]
    )


@mcp.tool(
    app=AppConfig(
        resource_uri=CARD_DASHBOARD_VIEW_URI,
        prefers_border=False,
    )
)
def open_card_dashboard_ui_with_count(count: Optional[int] = None) -> ToolResult:
    """Usar al final del flujo evaluado/personalizado de identificación.
    No usar para intención genérica de explorar tarjetas.
    """
    return ToolResult(
        content=[types.TextContent(type="text", text="Abriendo Card Dashboard…")]
    )


@mcp.tool(
    app=AppConfig(
        resource_uri=IDENTIFICATION_FLOW_VIEW_URI,
        prefers_border=True,
    )
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
        resource_uri=BENEFITS_VIEW_URI,
        prefers_border=True,
    )
)
def on_range_selected(value: str) -> ToolResult:
    print(f"[tool] on_range_selected value={value!r}")
    messages = {
        "lt_1200": "El usuario eligió menos de S/ 1200.",
        "1200_2500": "El usuario eligió S/ 1200 - S/ 2500.",
        "2501_5000": "El usuario eligió S/ 2501 - S/ 5000.",
        "gt_5000": "El usuario eligió más de S/ 5000.",
    }
    label = messages.get(value, f"Recibí : {value}")
    _tool_info_store.save("on_range_selected", label)
    text = label
    return ToolResult(
        content=[types.TextContent(type="text", text=text)],
        structured_content={
            "next_tool_name": "open_benefits_ui",
            "next_tool_arguments": {},
        },
    )


@mcp.tool(
    app=AppConfig(
        resource_uri=IDENTIFICATION_FLOW_VIEW_URI,
        prefers_border=True,
    )
)
def on_benefit_selected(value: str) -> ToolResult:
    print(f"[tool] on_benefit_selected value={value!r}")
    messages = {
        "cb": "El usuario eligió Cashback.",
        "mv": "El usuario eligió Millas / Viaje.",
        "dl": "El usuario eligió Descuentos locales.",
        "rg": "El usuario eligió Recompensas generales.",
    }
    label = messages.get(value, f"Recibí: {value}")
    _tool_info_store.save("on_benefit_selected", label)
    text = label
    return ToolResult(
        content=[types.TextContent(type="text", text=text)],
        structured_content={
            "next_tool_name": "open_identification_flow_ui",
            "next_tool_arguments": {},
        },
    )


@mcp.tool(
    app=AppConfig(
        resource_uri=CARD_DASHBOARD_VIEW_URI,
        prefers_border=False,
    )
)
def on_identification_submitted(value: str) -> ToolResult:
    print(f"[tool] on_identification_submitted value={value!r}")
    label = f"Te hemos evaluado con tu DNI {value}"
    _tool_info_store.save("on_identification_submitted", label)
    summary = _tool_info_store.summary_text()
    user_message = f"{label} y a continuación te mostraremos tus tarjetas disponibles. RESUMEN TOOLS: {summary}."
    return ToolResult(content=[types.TextContent(type="text", text=user_message)])


@mcp.resource(RANGE_EARNINGS_VIEW_URI, app=_RESOURCE_APP)
def range_earnings_view() -> str:
    return _wrapper_html(
        iframe_src=f"{FRONTEND_ORIGIN}/range-earings",
        event_type="range_earnings_selected",
        tool_name="on_range_selected",
        iframe_height="280px",
    )


@mcp.resource(BENEFITS_VIEW_URI, app=_RESOURCE_APP)
def benefits_view() -> str:
    return _wrapper_html(
        iframe_src=f"{FRONTEND_ORIGIN}/benefit-options",
        event_type="benefits_selected",
        tool_name="on_benefit_selected",
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


@mcp.resource(CARD_DASHBOARD_VIEW_READONLY_URI, app=_RESOURCE_APP)
def card_dashboard_readonly_view() -> str:
    iframe_src = f"{FRONTEND_ORIGIN}/card-dashboard?hideApplyButton=true"

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
        tool_name="on_identification_submitted",
        iframe_height="280px",
    )

if __name__ == "__main__":
    mcp.run()
