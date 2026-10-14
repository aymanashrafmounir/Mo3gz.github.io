"""Reopen the saved native document and export first-fold review slices."""
import json
from pathlib import Path
from figcraft_mcp import Figcraft

root = Path(__file__).resolve().parents[2]
design = root / "design"
frames = json.loads((design / "screen-manifest.json").read_text())
mcp = Figcraft()
try:
    mcp.tool("open_file", {"path": str(design / "ayman-portfolio-v2.figcraft")})
    document = mcp.tool("inspect_document", {"depth": 0, "allPages": True})
    assert len(document["pages"]) == 4
    assert len(document["styles"]) == 10
    assert document["images"] == 19
    for width in [1440, 390]:
        frame = next(f for f in frames if f["slug"] == "home" and f["width"] == width)
        mcp.command("page.select", {"id": frame["page"]})
        home = mcp.tool("get_node", {"id": frame["id"], "depth": 1})
        assert home["width"] == width
        layer = mcp.tool("create_node", {"type": "slice", "name": "Homepage first fold", "parent": frame["id"], "x": 0, "y": 0, "width": width, "height": 940})
        mcp.tool("export", {"ids": [layer["id"]], "path": str(design / "screens" / ("home-preview-" + str(width) + ".png")), "format": "png"})
    (design / "saved-document-verification.json").write_text(json.dumps({"reopened": True, "document": document, "previewSource": "Native Figcraft slice export from reopened document", "note": "Review slices are transient; the editable document is unchanged."}, indent=2))
    mcp.save_log(design / "review-mcp-calls.json")
    print("Saved document reopened: four pages, ten shared styles, nineteen image resources. Native first-fold previews exported.")
finally:
    mcp.close()
