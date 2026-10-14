"""Verify exported native screen geometry, route coverage and prototype links."""
import collections
import hashlib
import json
import sys
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[2]
design = root / "design"
sys.path.insert(0, str(design / ".tools"))
from create_screens import PAPER, TEXT, MUTED, QUIET, RUST, FOCUS
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

palette = {"Foreground": TEXT, "Secondary": MUTED, "Quiet": QUIET, "Rust": RUST, "Focus": FOCUS}
projects = json.loads((design / "screen-content.json").read_text())["projects"]
palette.update({p["slug"]:p["accent"] for p in projects})
contrast = {name:round((max(luminance(color),luminance(PAPER))+.05)/(min(luminance(color),luminance(PAPER))+.05),2) for name,color in palette.items()}
for name, ratio in contrast.items():
    if ratio < 4.5:
        issues.append({"kind":"contrast", "token":name, "ratio":ratio})
selected = json.loads((design / "selected-media-manifest.json").read_text())["images"]
captures = json.loads((design / "capture-manifest.json").read_text())
approved_assets = [asset for image in selected for asset in [image, *image.get("variants", [])]]
approved_assets.extend(captures)
sources_by_hash = {}
for asset in approved_assets:
    path = (root / asset["path"]).resolve()
    if not path.is_file():
        issues.append({"kind": "missing_manifest_image", "source": str(path)})
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if asset.get("sha256") and digest != asset["sha256"].lower():
        issues.append({"kind": "manifest_image_hash_mismatch", "source": str(path)})
        continue
    sources_by_hash.setdefault(digest, str(path))

active_images = collections.defaultdict(list)
with zipfile.ZipFile(design / "ayman-portfolio-v2.figcraft") as archive:
    document = json.loads(archive.read("document.json"))
    visited = set()

    def visit_image_node(node_id):
        if node_id in visited:
            return
        visited.add(node_id)
        node = document["nodes"][str(node_id)]
        if not node.get("visible", True) or node.get("opacity", 1) <= 0:
            return
        for fill in node.get("fills", []):
            if fill.get("type") == "image" and fill.get("visible", True) and fill.get("opacity", 1) > 0:
                active_images[fill["image"]].append(node_id)
        for child_id in node.get("children", []):
            visit_image_node(child_id)

    for page_id in document["pages"]:
        visit_image_node(page_id)
    for digest, node_ids in active_images.items():
        resource = f"images/{digest}"
        if resource not in archive.namelist():
            issues.append({"kind": "missing_native_image", "image": digest, "nodes": node_ids})
        elif hashlib.sha256(archive.read(resource)).hexdigest() != digest:
            issues.append({"kind": "native_image_hash_mismatch", "image": digest, "nodes": node_ids})
        if digest not in sources_by_hash:
            issues.append({"kind": "unapproved_image_in_use", "image": digest, "nodes": node_ids})

sources = sorted({sources_by_hash[digest] for digest in active_images if digest in sources_by_hash})
if any("masters" in source or "\\web\\" in source for source in sources):
    issues.append({"kind":"rejected_generated_asset_in_use"})
result = {"direction":"A / warm paper and rust", "scope":"Native design verification only; no website/browser QA", "route_frames":sum(coverage.values()), "state_frames":len(screens)-sum(coverage.values()), "routes_by_width":coverage, "layer_types":types, "prototype_actions":len(interactions), "text_contrast_on_paper":contrast, "active_image_sources":sources, "active_image_hashes":sorted(active_images), "issues":issues}
(design / "screen-qa.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
