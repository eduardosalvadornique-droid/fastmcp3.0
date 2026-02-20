from fastmcp import FastMCP
from fastmcp.server.apps import AppConfig, ResourceCSP
from fastmcp.tools import ToolResult
from mcp import types

mcp = FastMCP("Catalog App Server")

#FRONTEND_ORIGIN = "https://mcp-front-test-arfbbch0f8hkgqex.canadacentral-01.azurewebsites.net"
FRONTEND_ORIGIN = "https://poc-back-ai-front.netlify.app"
VIEW_URI = "ui://catalog/view.html"

@mcp.tool(app=AppConfig(resource_uri=VIEW_URI, prefers_border=True))
def open_ui() -> ToolResult:
    return ToolResult(content=[types.TextContent(type="text", text="Abriendo UI…")])

@mcp.tool(
    app=AppConfig(
        resource_uri=VIEW_URI,
        visibility=["app"],   # tool callable desde la app
        prefers_border=True
    )
)
def build_range_earnings_message(value: str) -> ToolResult:
    messages = {
        "lt_1200": "SOLO COMENTA: Elegiste menos de **S/ 1200**. NOTA: no coloques níngun mensaje adicional ni modifiques nada.",
        "1200_2500": "SOLO COMENTA: Elegiste **S/ 1200 - S/ 2500**. NOTA: no coloques níngun mensaje adicional ni modifiques nada.",
        "2501_5000": "SOLO COMENTA: Elegiste **S/ 2501 - S/ 5000**. NOTA: no coloques níngun mensaje adicional ni modifiques nada.",
        "gt_5000": "SOLO COMENTA: Elegiste más de **S/ 5000**. NOTA: no coloques níngun mensaje adicional ni modifiques nada.",
    }
    text = messages.get(value, f"Recibí tu selección: {value}")

    return ToolResult(content=[types.TextContent(type="text", text=text)])



@mcp.resource(
    VIEW_URI,
    app=AppConfig(
        csp=ResourceCSP(
            resource_domains=["https://unpkg.com", FRONTEND_ORIGIN],
            frame_domains=[FRONTEND_ORIGIN],
            # connect_domains: solo si en el wrapper haces fetch externo (normalmente no)
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
    <iframe id="app" src="{FRONTEND_ORIGIN}/range-earings"></iframe>

    <script type="module">
      import {{ App }} from "https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps";

      const app = new App({{ name: "Catalog UI Wrapper", version: "1.0.0" }});
      await app.connect();

      const iframe = document.getElementById("app");

      let lastSentAt = 0;

      window.addEventListener("message", async (ev) => {{
        // seguridad mínima: solo aceptar mensajes del iframe
        if (ev.source !== iframe.contentWindow) return;

        const data = ev.data || {{}};
        if (data.type !== "range_earnings_selected") return;

        const value = data.value;

        // anti-spam simple (por si cambian rápido)
        const now = Date.now();
        if (now - lastSentAt < 400) return;
        lastSentAt = now;

        // 1) llamar tool del MCP server para construir el mensaje
        const toolResult = await app.callServerTool({{
          name: "build_range_earnings_message",
          arguments: {{ value }}
        }});

        // 2) extraer texto del resultado
        const text = toolResult?.content?.find(c => c.type === "text")?.text
          ?? `Selección: ${{value}}`;;

        // 3) mandar mensaje al chat de ChatGPT
        await app.sendMessage({{
          role: "user",
          content: [{{ type: "text", text }}]
        }});
      }});
    </script>
  </body>
</html>"""

if __name__ == "__main__":
    mcp.run()
