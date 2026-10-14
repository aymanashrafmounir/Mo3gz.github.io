"""Rejected experiment retained for provenance; terminal captures are not covers."""
raise SystemExit('Rejected by user: do not use terminal/test screenshots as application imagery.')
import json
import shutil
from pathlib import Path
from refine_native import Refine, PAPER, SURFACE, TEXT, MUTED, RUST, LINE

D = Path(__file__).resolve().parents[1]
data = json.loads((D / 'screen-content.json').read_text())
project = next(p for p in data['projects'] if p['slug'] == 'secure-notes-organizer')
source = json.loads((D / 'research-candidates/secure-notes-current/download-provenance.json').read_text())
chosen = [('add-tag-integration.png', 'secure-notes-integration', 'Tag creation and malformed requests'),
          ('create-note-integration.png', 'secure-notes-create-note', 'Note creation and malformed requests'),
          ('list-note-tags-integration.png', 'secure-notes-list-tags', 'Listing note tags and invalid requests')]
manifest = json.loads((D / 'capture-manifest.json').read_text())
manifest = [c for c in manifest if c['project'] != 'secure-notes-organizer']
for filename, stem, label in chosen:
    original = next(c for c in source if Path(c['localPath']).name == filename)
    dst = D / 'assets/captures' / (stem + '.png')
    shutil.copy2(original['localPath'], dst)
    manifest.append({'project': project['slug'], 'assetKey': project['slug'] if filename == chosen[0][0] else stem,
                     'path': dst.relative_to(D.parent).as_posix(), 'source': original['sourceUrl'],
                     'sourceCommit': original['sourceCommit'], 'sha256': original['sha256'],
                     'observed': '2026-10-14', 'classification': original['classification'],
                     'caption': label + ' · GTest integration-test repository capture.',
                     'use': 'User requested use of original repository screenshots. Preserve test-evidence labels; no fresh test-run claim.',
                     'framing': 'Complete original capture, fit without crop.'})
project['capture'] = chosen[0][1]
project['caption'] = 'GTest integration-test capture from the public project repository.'
project['evidenceType'] = 'repository integration-test screenshots'
project['gallery'] = [stem for _, stem, _ in chosen[1:]]
(D / 'capture-manifest.json').write_text(json.dumps(manifest, indent=2))
(D / 'screen-content.json').write_text(json.dumps(data, indent=2))
shutil.copy2(D / 'ayman-portfolio-v2.figcraft', D / 'checkpoints/before-secure-notes-evidence.figcraft')

r = Refine(data)
r.new_images = {}
r.icons = json.loads((D / 'technology-components.json').read_text())


def image(parent, stem, x, y, w, h):
    root, _ = r.s.node('frame', 'Repository integration-test capture / ' + stem, x, y, w, h,
                        parent=parent, props={'fill': SURFACE, 'cornerRadius': 6, 'clip': True})
    path = D / 'assets/captures' / (stem + '.png')
    r.m.command('image.place', {'path': str(path), 'parent': root, 'x': 0, 'y': 0,
                              'width': w, 'height': h, 'mode': 'fit'})
    r.m.command('proto.interaction.add', {'id': root, 'trigger': {'type': 'onClick'},
                                       'action': {'type': 'openUrl', 'url': path.as_uri()}})
    return root


def source_link(parent, stem, label, x, y, w):
    root, _ = r.s.node('frame', 'Open original GTest capture', x, y, w, 44, parent=parent, props={'fills': []})
    r.s.text(root, label + ' ↗', 0, 10, w, 13, RUST, 'Medium')
    r.m.command('proto.interaction.add', {'id': root, 'trigger': {'type': 'onClick'},
                                       'action': {'type': 'openUrl', 'url': (D / 'assets/captures' / (stem + '.png')).as_uri()}})


def arrow(parent):
    r.m.tool('create_node', {'type': 'vector', 'name': 'Case study arrow', 'x': 145, 'y': 15,
                           'width': 14, 'height': 14, 'parent': parent, 'path': 'M1 7H13M8 2L13 7L8 12',
                           'props': {'fills': [], 'stroke': RUST, 'strokeWeight': 1.5, 'strokeCap': 'round', 'strokeJoin': 'round'}})


def home(f):
    root = r.m.tool('get_node', {'id': f['id'], 'depth': 6})
    title = next(c for c in root['children'] if c.get('characters') == project['title'])
    # The All projects action immediately follows the selected-work rows.
    button = next(c for c in root['children'] if c['type'] == 'INSTANCE' and any(n.get('characters') == 'All projects' for n in walk(c)))
    start, end = title['y'], button['y']
    obsolete = [c['id'] for c in root['children'] if start <= c['y'] < end]
    r.m.command('edit.delete', {'ids': obsolete})
    root['children'] = [c for c in root['children'] if c['id'] not in obsolete]
    w = f['width']; r.s.current_width = w
    margin = 80 if w >= 1200 else 40 if w >= 700 else 24
    inner = w - margin * 2
    if w >= 700:
        iw = 315 if w >= 1200 else 240
        ih = iw * 632 / 1634
        tx, tw, y = margin + iw + (40 if w >= 1200 else 28), inner - iw - (40 if w >= 1200 else 28), start + 6
    else:
        iw, ih = inner, inner * 632 / 1634
        tx, tw, y = margin, inner, start + ih + 44
    image(root['id'], project['capture'], margin, start, iw, ih)
    r.s.text(root['id'], 'GTest integration-test capture', margin, start + ih + 8, iw, 12, MUTED)
    _, box = r.s.text(root['id'], project['title'], tx, y, tw, 28 if w >= 1200 else 25, TEXT, 'SemiBold')
    y += box['height'] + 8
    _, box = r.s.text(root['id'], project['kind'], tx, y, tw, 14, RUST)
    y += box['height'] + 14
    _, box = r.s.text(root['id'], project['summary'], tx, y, tw, 17, MUTED)
    y += box['height'] + 16
    y += r.stack(root['id'], [('cplusplus', 'C++'), ('qt', 'Qt 6')], tx, y, tw, 18, 13) + 6
    link = r.s.nav_link(root['id'], 'Read case study', tx, y, 180, 'project:' + project['slug'])
    arrow(link)
    new_end = max(y + 44, start + ih + 32) + 36
    r.shift(root, end, new_end - end)


def walk(n):
    yield n
    for c in n.get('children', []):
        yield from walk(c)


def case(f):
    root = r.m.tool('get_node', {'id': f['id'], 'depth': 4})
    w = f['width']; margin = 80 if w >= 1200 else 40 if w >= 700 else 24
    divider = next(c for c in root['children'] if c.get('name') == 'Section divider' and c['y'] > 100)
    if w >= 1200:
        x, y, iw = 770, 180, 590
        ih = iw * 632 / 1634
    else:
        stack = next(c for c in root['children'] if c.get('name') == 'Verified project stack' and c['y'] < 1000)
        x, y, iw = margin, stack['y'] + stack['height'] + 30, w - margin * 2
        ih = iw * 632 / 1634
        r.shift(root, divider['y'], max(0, y + ih + 74 - divider['y']))
    image(root['id'], project['capture'], x, y, iw, ih)
    source_link(root['id'], project['capture'], 'View full-size GTest capture', x, y + ih + 6, iw)
    # Original screenshots show backend integration output, so their section is explicit.
    explore = next(c for c in root['children'] if c.get('characters') == 'Explore more work')
    line = max((c for c in root['children'] if c.get('name') == 'Section divider' and c['y'] < explore['y']), key=lambda c: c['y'])
    start = line['y']
    cx, cw = (390, 800) if w >= 1200 else (margin, w - margin * 2)
    y = start
    _, heading = r.s.text(root['id'], 'Integration-test evidence', cx, y, cw, 32 if w >= 1200 else 28, TEXT, 'SemiBold')
    y += heading['height'] + 30
    for stem, label, original_w, original_h in [
        ('secure-notes-create-note', 'Note creation · GTest repository capture', 1620, 364),
        ('secure-notes-list-tags', 'Listing note tags · GTest repository capture', 1579, 473),
    ]:
        h = cw * original_h / original_w
        image(root['id'], stem, cx, y, cw, h)
        source_link(root['id'], stem, label, cx, y + h + 6, cw)
        y += h + 78
    r.shift(root, start, y + 25 - start)


try:
    for f in r.frames:
        if f['slug'] == 'home':
            home(f)
        elif f['slug'] == 'project:secure-notes-organizer':
            case(f)
    r.listings()
    for f in r.frames:
        if f['slug'] not in ['projects', 'filter-public', 'filter-products']:
            continue
        root = r.m.tool('get_node', {'id': f['id'], 'depth': 3})
        for c in root['children']:
            name = c.get('name', '')
            if name == 'Navigate to Read case study':
                arrow(c['id'])
            if name in ['Navigate to GitHub', 'Navigate to LinkedIn']:
                text = next(n for n in c['children'] if n['type'] == 'TEXT')
                r.m.command('node.set', {'ids': [text['id']], 'x': 23, 'width': c['width'] - 23, 'fontSize': 13})
                r.icon(c['id'], 'github' if name.endswith('GitHub') else 'linkedin', 0, 13, 16)
            if name == 'Genuine public capture / secure-notes-organizer':
                r.s.text(root['id'], 'GTest integration-test capture', c['x'], c['y'] + c['height'] + 3, c['width'], 12, MUTED)
    r.finish()
    r.m.save_log(D / 'secure-notes-evidence-mcp-calls.json')
    print('Secure Notes repository evidence added; all test captures are explicitly labelled.')
finally:
    r.m.close()
