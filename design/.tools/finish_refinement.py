"""Fit intrinsic icon labels, export native screens, and refresh inspection."""
import json
from pathlib import Path
from figcraft_mcp import Figcraft

D = Path(__file__).resolve().parents[1]
frames = json.loads((D / 'screen-manifest.json').read_text())


def walk(n):
    yield n
    for c in n.get('children', []):
        yield from walk(c)


m = Figcraft()
try:
    m.tool('open_file', {'path': str(D / 'ayman-portfolio-v2.figcraft')})
    doc = m.tool('inspect_document', {'depth': 20, 'allPages': True})
    for page in doc['pages']:
        for n in walk(page):
            name = n.get('name', '')
            if name in ['Navigate to GitHub', 'Navigate to LinkedIn']:
                for c in n.get('children', []):
                    if c['type'] == 'TEXT':
                        m.command('node.set', {'ids': [c['id']], 'width': n['width'] - 23})
            if n['type'] == 'FRAME' and name.startswith(('Core stack', 'Verified project stack', 'Skill identities /')):
                pairs = []
                icon = None
                for c in n.get('children', []):
                    if c['type'] == 'INSTANCE':
                        icon = c
                    elif c['type'] == 'TEXT' and icon:
                        m.command('node.set', {'ids': [c['id']], 'textAutoResize': 'widthAndHeight'})
                        label = m.tool('get_node', {'id': c['id']})
                        pairs.append((icon, label))
                        icon = None
                px, py = 0, 0
                gap = 22 if name.startswith('Core') else 16
                for icon, label in pairs:
                    span = icon['width'] + 8 + label['width']
                    if px and px + span > n['width']:
                        px, py = 0, py + 30
                    m.command('node.set', {'ids': [icon['id']], 'x': px, 'y': py})
                    m.command('node.set', {'ids': [label['id']], 'x': px + icon['width'] + 8, 'y': py - 1})
                    px += span + gap
                m.command('node.set', {'ids': [n['id']], 'height': py + 24})
    m.tool('save_file', {'path': str(D / 'ayman-portfolio-v2.figcraft')})
    doc = m.tool('inspect_document', {'depth': 20, 'allPages': True})
    nodes = {n['id']: n for p in doc['pages'] for n in walk(p)}
    (D / 'native-document-inspection.json').write_text(json.dumps(doc, indent=2))
    (D / 'screen-inspection.json').write_text(json.dumps([{'frame': f, 'node': nodes[f['id']]} for f in frames], indent=2))
    for f in frames:
        m.tool('export', {'ids': [f['id']], 'path': str(D.parent / f['export']), 'format': 'png'})
    for ident, filename in [(2, 'foundations.png')]:
        m.tool('export', {'ids': [ident], 'path': str(D / 'screens' / filename), 'format': 'png'})
    tech = next(n for n in doc['pages'][0]['children'] if n['name'].startswith('Technology marks /'))
    m.tool('export', {'ids': [tech['id']], 'path': str(D / 'screens/technology-foundations.png'), 'format': 'png'})
    m.save_log(D / 'refinement-final-mcp-calls.json')
    print('All 68 native screen exports refreshed; intrinsic stack labels fitted.')
finally:
    m.close()
