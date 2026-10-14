"""Show the selected portfolio in an already-running, control-enabled Figcraft app.

Uses attached MCP only. Never launches a GUI or changes application content.
"""
import base64
import json
import sys
from pathlib import Path
from figcraft_mcp import Figcraft

root = Path(__file__).resolve().parents[2]
design = root / "design"
native = design / "ayman-portfolio-v2.figcraft"
frames = json.loads((design / "screen-manifest.json").read_text())
home = next(f for f in frames if f["slug"] == "home" and f["width"] == 1440)
mcp = Figcraft(attach_port=47800)
try:
    current = mcp.tool("inspect_document", {"depth": 0, "allPages": True})
    if current.get("path") != str(native):
        mcp.tool("open_file", {"path": str(native)})
    if "--close-session-recovery" in sys.argv:
        ui = mcp.tool("inspect_ui")
        files = ui.get("windows", [{}])[0].get("files", [])
        # This explicit maintenance option is only for this task's recovered,
        # unsaved partial refinement tab. The saved final document stays open.
        if files == ["Ayman Portfolio V2", "Ayman Portfolio V2"]:
            mcp.command("file.close", {"index": 0, "force": True})
    mcp.command("page.select", {"id": home["page"]})
    mcp.tool("select", {"ids": [home["id"]]})
    mcp.command("view.zoomAt", {"x": 0, "y": 0, "width": 1440, "height": 1050})
    ui = mcp.tool("inspect_ui")
    (design / "attached-ui.json").write_text(json.dumps(ui, indent=2))
    print(json.dumps(ui)[:6500])
    screenshot = mcp.tool("screenshot", {"window": True, "maxSize": 1800})
    for content in screenshot.get("content", []):
        if content.get("type") == "image":
            (design / "screens" / "figcraft-app.png").write_bytes(base64.b64decode(content["data"]))
    mcp.save_log(design / "attached-mcp-calls.json")
    print("Approved portfolio opened and framed through attached MCP.")
finally:
    mcp.close()
