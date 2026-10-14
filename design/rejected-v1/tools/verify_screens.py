"""Verify exported native screen geometry, route coverage and prototype links."""
import collections
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
design = root / "design"
screens = json.loads((design / "screen-inspection.json").read_text())
issues, types, ids, interactions = [], collections.Counter(), {}, []

def visit(node, frame):
    ids[node["id"]] = (node, frame)
    types[node["type"]] += 1
    children = node.get("children", [])
    for child in children:
        if node["id"] == frame["id"]:
            b, p = child["absoluteBounds"], node["absoluteBounds"]
            margin = 80 if frame["width"] >= 1200 else 40 if frame["width"] >= 700 else 24
            if b["x"] < p["x"] + margin - 1 or b["x"] + b["width"] > p["x"] + p["width"] - margin + 1:
                issues.append({"kind":"content_outside_margin", "screen":[frame["slug"],frame["width"]], "node":child["name"]})
        if child["type"] == "TEXT":
            b, p = child["absoluteBounds"], node["absoluteBounds"]
            if b["x"] < p["x"] - 1 or b["y"] < p["y"] - 1 or b["x"] + b["width"] > p["x"] + p["width"] + 1 or b["y"] + b["height"] > p["y"] + p["height"] + 1:
                issues.append({"kind": "text_outside_parent", "screen": [frame["slug"], frame["width"]], "id": child["id"], "text": child.get("characters"), "parent": node["name"]})
        visit(child, frame)
    texts = [child for child in children if child["type"] == "TEXT"]
    for i, first in enumerate(texts):
        a = first["absoluteBounds"]
        for second in texts[i+1:]:
            b = second["absoluteBounds"]
            overlap_x = min(a["x"]+a["width"], b["x"]+b["width"]) - max(a["x"], b["x"])
            overlap_y = min(a["y"]+a["height"], b["y"]+b["height"]) - max(a["y"], b["y"])
            if overlap_x > 1 and overlap_y > 1:
                issues.append({"kind": "text_overlap", "screen": [frame["slug"], frame["width"]], "texts": [first.get("characters"), second.get("characters")], "overlap": [overlap_x, overlap_y]})
    for interaction in node.get("interactions", []):
        for action in interaction.get("actions", []):
            interactions.append((node["id"], frame, action))

for screen in screens:
    visit(screen["node"], screen["frame"])
for source, frame, action in interactions:
    if action.get("type") in ["navigate", "scrollTo"]:
        target = ids.get(action.get("dest"))
        if not target or target[1]["width"] != frame["width"]:
            issues.append({"kind": "invalid_prototype_destination", "source": source, "action": action})
coverage = collections.Counter(screen["frame"]["width"] for screen in screens if screen["frame"]["kind"] == "route")
for width in [1440, 768, 390]:
    if coverage[width] != 19:
        issues.append({"kind": "coverage", "width": width, "routes": coverage[width]})

def luminance(value):
    parts = [int(value[i:i+2], 16) / 255 for i in [1, 3, 5]]
    return sum((v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4) * c for v, c in zip(parts, [.2126, .7152, .0722]))

palette = {"Foreground":"#E8EEF4", "Secondary":"#A7B5C6", "Quiet":"#7E93AA", "Signal blue":"#5D9EFF", "Cyan":"#67D8E4"}
projects = json.loads((design / "screen-content.json").read_text())["projects"]
palette.update({p["slug"]:p["accent"] for p in projects})
contrast = {name:round((max(luminance(color),luminance("#10151D"))+.05)/(min(luminance(color),luminance("#10151D"))+.05),2) for name,color in palette.items()}
for name, ratio in contrast.items():
    if ratio < 4.5:
        issues.append({"kind":"contrast", "token":name, "ratio":ratio})
result = {"scope":"Native design verification only; no website/browser QA", "route_frames":sum(coverage.values()), "state_frames":len(screens)-sum(coverage.values()), "routes_by_width":coverage, "layer_types":types, "prototype_actions":len(interactions), "text_contrast_on_ink":contrast, "issues":issues}
(design / "screen-qa.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
