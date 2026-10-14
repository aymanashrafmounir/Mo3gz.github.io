"""Remove rejected terminal imagery while preserving the approved design edits."""
import json
import shutil
from pathlib import Path
from figcraft_mcp import Figcraft

D = Path(__file__).resolve().parents[1]
native = D / 'ayman-portfolio-v2.figcraft'
checkpoint = D / 'checkpoints/before-secure-notes-evidence.figcraft'
assert checkpoint.is_file()
shutil.copy2(native, D / 'checkpoints/rejected-terminal-covers.figcraft')
shutil.copy2(checkpoint, native)
data = json.loads((D / 'screen-content.json').read_text())
project = next(p for p in data['projects'] if p['slug'] == 'secure-notes-organizer')
project.update(capture=None, caption=None, gallery=[])
project.pop('evidenceType', None)
captures = json.loads((D / 'capture-manifest.json').read_text())
rejected = [c for c in captures if c['project'] == 'secure-notes-organizer']
(D / 'rejected-terminal-evidence.json').write_text(json.dumps({
    'decision': 'User rejected terminal screenshots as application imagery.',
    'active': False,
    'assets': rejected,
}, indent=2))
(D / 'capture-manifest.json').write_text(json.dumps([c for c in captures if c['project'] != 'secure-notes-organizer'], indent=2))
(D / 'screen-content.json').write_text(json.dumps(data, indent=2))
# Preserve original evidence in ignored research, outside active selected media.
rejected_dir = D / 'research-candidates/rejected-terminal-covers'
rejected_dir.mkdir(exist_ok=True)
for c in rejected:
    path = (D.parent / c['path']).resolve()
    assert path.is_relative_to((D / 'assets/captures').resolve())
    if path.is_file():
        shutil.move(str(path), str(rejected_dir / path.name))
    for width in [480, 960, 1440]:
        variant = D / 'assets/selected-web' / ((c.get('assetKey') or c['project']) + '-' + str(width) + '.webp')
        if variant.is_file():
            shutil.move(str(variant), str(rejected_dir / variant.name))


def walk(n):
    yield n
    for c in n.get('children', []):
        yield from walk(c)


m = Figcraft()
try:
    m.tool('open_file', {'path': str(native)})
    doc = m.tool('inspect_document', {'depth': 20, 'allPages': True})
    nodes = {n['id']: n for p in doc['pages'] for n in walk(p)}
    frames = json.loads((D / 'screen-manifest.json').read_text())
    for f in frames:
        f['height'] = nodes[f['id']]['height']
    assert any('Siemens DISW internship final project' == n.get('characters') for n in nodes.values())
    assert sum(n.get('name') == 'Experience timeline' for n in nodes.values()) == 9
    (D / 'screen-manifest.json').write_text(json.dumps(frames, indent=2))
    print('Rejected terminal imagery removed. Timeline, selected projects and Siemens affiliation preserved.')
finally:
    m.close()
