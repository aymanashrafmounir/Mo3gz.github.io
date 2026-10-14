"""Generate licensed web subsets; regular site builds only copy the results."""

import hashlib
import json
import subprocess
from pathlib import Path

from fontTools import subset
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "design/assets/fonts"
WEB = SOURCE / "web"
CACHE = ROOT / "output/font-subsets"
WEIGHTS = ["Regular", "Medium", "SemiBold", "Bold"]
UNICODES = (
    list(range(0x20, 0x7F))
    + list(range(0xA0, 0x100))
    + list(range(0x2000, 0x2070))
    + list(range(0x20A0, 0x20D0))
    + list(range(0x2190, 0x2200))
    + [0x2212, 0x2713]
)
for source_path in sorted((ROOT / "src").rglob("*")):
    if source_path.suffix in {".astro", ".ts"}:
        UNICODES.extend(map(ord, source_path.read_text(encoding="utf8")))
UNICODES.extend(map(ord, (ROOT / "design/screen-content.json").read_text(encoding="utf8")))
WEB.mkdir(exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)
OPTIONS = subset.Options()
OPTIONS.layout_features = ["*"]
OPTIONS.glyph_names = True
OPTIONS.notdef_outline = True
OPTIONS.name_IDs = ["*"]
OPTIONS.name_legacy = True
OPTIONS.name_languages = ["*"]
records = []

for weight in WEIGHTS:
    source_path = SOURCE / f"MonaSans-{weight}.ttf"
    original = TTFont(source_path, recalcTimestamp=False)
    web_font = TTFont(source_path, recalcTimestamp=False)
    subsetter = subset.Subsetter(options=OPTIONS)
    subsetter.populate(unicodes=UNICODES)
    subsetter.subset(web_font)
    # OFL reserves "Mona"; give the modified subset its own family identity.
    names = {
        1: "Ayman Sans Web", 2: weight,
        3: f"AymanSansWeb-{weight}-Subset1", 4: f"Ayman Sans Web {weight}",
        6: f"AymanSansWeb-{weight}", 16: "Ayman Sans Web",
        17: weight, 18: f"Ayman Sans Web {weight}",
        21: "Ayman Sans Web", 22: weight,
    }
    for entry in list(web_font["name"].names):
        if entry.nameID in names:
            web_font["name"].setName(names[entry.nameID], entry.nameID,
                                     entry.platformID, entry.platEncID, entry.langID)
    subset_path = CACHE / f"AymanSansWeb-{weight}.ttf"
    web_font.save(subset_path)
    output_path = WEB / f"AymanSansWeb-{weight}.woff2"
    subprocess.run(["node", str(ROOT / "node_modules/wawoff2/bin/woff2_compress.js"),
                    str(subset_path), str(output_path)], check=True, cwd=ROOT)
    roundtrip_path = CACHE / f"AymanSansWeb-{weight}-roundtrip.ttf"
    subprocess.run(["node", str(ROOT / "node_modules/wawoff2/bin/woff2_decompress.js"),
                    str(output_path), str(roundtrip_path)], check=True, cwd=ROOT)
    restored = TTFont(roundtrip_path)
    original_glyphs = original.getGlyphSet()
    restored_glyphs = restored.getGlyphSet()
    for glyph_name in restored.getGlyphOrder():
        left, right = RecordingPen(), RecordingPen()
        original_glyphs[glyph_name].draw(left)
        restored_glyphs[glyph_name].draw(right)
        assert left.value == right.value, (weight, glyph_name, "outline")
        assert original["hmtx"][glyph_name] == restored["hmtx"][glyph_name]
    assert restored.getBestCmap() == web_font.getBestCmap()
    assert original["head"].unitsPerEm == restored["head"].unitsPerEm
    records.append({
        "weight": weight, "glyphs": len(restored.getGlyphOrder()),
        "sourceBytes": source_path.stat().st_size,
        "webBytes": output_path.stat().st_size,
        "sourceSha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "webSha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
    })

coverage = {
    "family": "Ayman Sans Web", "derivedFrom": "Mona Sans",
    "license": "SIL OFL 1.1; original copyright and license retained in ../OFL.txt",
    "scope": "Latin-1, general punctuation, currencies, arrows, minus and checkmark",
    "codepoints": sorted(web_font.getBestCmap()),
    "originalCodepoints": sorted(original.getBestCmap()),
    "checks": "All retained glyph outlines, horizontal metrics, cmap and unitsPerEm match originals after WOFF2 roundtrip; all layout features retained during subsetting",
    "fonts": records,
}
(WEB / "coverage.json").write_text(json.dumps(coverage, indent=2) + "\n", encoding="utf8")
print(json.dumps(records, indent=2))
