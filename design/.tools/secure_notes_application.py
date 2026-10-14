"""Place verified captures of the original Qt application in the native design.

Consumes reviewed capture assets and their provenance, never creates app imagery.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path
from PIL import Image
from refine_native import Refine, SURFACE, TEXT, MUTED, RUST, walk

D = Path(__file__).resolve().parents[1]


def full_size_caption(r, parent, stem, label, x, y, width, size=14):
    """Keep the caption baseline while giving its image link a 44px target."""
    target, _ = r.s.node('frame', 'View full-size / ' + stem, x, y - 10, width, 44,
                         parent=parent, props={'fills': [], 'clip': False})
    text = r.s.text(target, label + ' · View full-size ↗', 0, 10, width, size, RUST)
    path = D / 'assets/captures' / (stem + '.png')
    r.m.command('proto.interaction.add', {'id': target, 'trigger': {'type': 'onClick'},
                                        'action': {'type': 'openUrl', 'url': path.as_uri()}})
    return text


def main():
    # Prepared only after the original application's captures pass visual review.
    plan = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    assert plan['classification'] == 'genuine-original-application-capture'
    data = json.loads((D / 'screen-content.json').read_text())
    project = next(p for p in data['projects'] if p['slug'] == 'secure-notes-organizer')
    captures = json.loads((D / 'capture-manifest.json').read_text())
    captures = [c for c in captures if c['project'] != project['slug']]
    sizes = {}
    for i, asset in enumerate(plan['images']):
        src = Path(asset['sourcePath'])
        assert src.is_file(), src
        stem = asset['stem']
        dst = D / 'assets/captures' / (stem + '.png')
        shutil.copy2(src, dst)
        sizes[stem] = Image.open(dst).size
        captures.append({
            'project': project['slug'], 'assetKey': project['slug'] if i == 0 else stem,
            'path': dst.relative_to(D.parent).as_posix(),
            'sha256': hashlib.sha256(dst.read_bytes()).hexdigest(),
            'source': plan['repository'], 'sourceCommit': plan['sourceCommit'],
            'classification': plan['classification'], 'observed': '2026-10-14',
            'caption': asset['caption'], 'captureDetails': plan['captureDetails'],
            'use': 'Original application interface captured locally for the requested native portfolio review.',
            'framing': 'Complete original application widget; fit without crop or zoom.',
        })
    project['capture'] = plan['images'][0]['stem']
    project['caption'] = plan['images'][0]['caption']
    project['gallery'] = [a['stem'] for a in plan['images'][1:]]
    project['captureMethod'] = plan['captureDetails']
    shutil.copy2(D / 'ayman-portfolio-v2.figcraft', D / 'checkpoints/before-original-qt-captures.figcraft')
    (D / 'capture-manifest.json').write_text(json.dumps(captures, indent=2))
    (D / 'screen-content.json').write_text(json.dumps(data, indent=2))
    r = Refine(data)
    r.icons = json.loads((D / 'technology-components.json').read_text())
    r.new_images = {}

    def image(parent, stem, x, y, width, height):
        ident, _ = r.s.node('frame', 'Original Qt application / ' + stem, x, y, width, height,
                            parent=parent, props={'fill': SURFACE, 'cornerRadius': 6, 'clip': True})
        path = D / 'assets/captures' / (stem + '.png')
        r.m.command('image.place', {'path': str(path), 'parent': ident, 'x': 0, 'y': 0,
                                  'width': width, 'height': height, 'mode': 'fit'})
        r.m.command('proto.interaction.add', {'id': ident, 'trigger': {'type': 'onClick'},
                                            'action': {'type': 'openUrl', 'url': path.as_uri()}})
        return ident

    def arrow(parent):
        r.m.tool('create_node', {'type': 'vector', 'name': 'Case study arrow', 'x': 145, 'y': 15,
                               'width': 14, 'height': 14, 'parent': parent,
                               'path': 'M1 7H13M8 2L13 7L8 12',
                               'props': {'fills': [], 'stroke': RUST, 'strokeWeight': 1.5,
                                         'strokeCap': 'round', 'strokeJoin': 'round'}})

    def home(f):
        root = r.m.tool('get_node', {'id': f['id'], 'depth': 6})
        title = next(c for c in root['children'] if c.get('characters') == project['title'])
        button = next(c for c in root['children'] if c['type'] == 'INSTANCE' and
                      any(n.get('characters') == 'All projects' for n in walk(c)))
        start, end = title['y'], button['y']
        obsolete = [c['id'] for c in root['children'] if start <= c['y'] < end]
        r.m.command('edit.delete', {'ids': obsolete})
        root['children'] = [c for c in root['children'] if c['id'] not in obsolete]
        width = f['width']; r.s.current_width = width
        margin = 80 if width >= 1200 else 40 if width >= 700 else 24
        inner = width - 2 * margin
        iw = (315 if width >= 1200 else 240) if width >= 700 else inner
        ow, oh = sizes[project['capture']]
        ih = iw * oh / ow
        image(root['id'], project['capture'], margin, start, iw, ih)
        tx = margin + iw + (40 if width >= 1200 else 28) if width >= 700 else margin
        tw = inner - (tx - margin)
        y = start + 6 if width >= 700 else start + ih + 22
        _, box = r.s.text(root['id'], project['title'], tx, y, tw,
                          28 if width >= 1200 else 25, TEXT, 'SemiBold')
        y += box['height'] + 8
        _, box = r.s.text(root['id'], project['kind'], tx, y, tw, 14, RUST)
        y += box['height'] + 14
        _, box = r.s.text(root['id'], project['summary'], tx, y, tw, 17, MUTED)
        y += box['height'] + 16
        y += r.stack(root['id'], [('cplusplus', 'C++'), ('qt', 'Qt 6')], tx, y, tw, 18, 13) + 6
        arrow(r.s.nav_link(root['id'], 'Read case study', tx, y, 180, 'project:' + project['slug']))
        r.shift(root, end, max(y + 44, start + ih) + 36 - end)

    def case(f):
        root = r.m.tool('get_node', {'id': f['id'], 'depth': 4})
        width = f['width']; margin = 80 if width >= 1200 else 40 if width >= 700 else 24
        divider = next(c for c in root['children'] if c.get('name') == 'Section divider' and c['y'] > 100)
        if width >= 1200:
            x, y, iw = 770, 180, 590
        else:
            stack = next(c for c in root['children'] if c.get('name') == 'Verified project stack' and c['y'] < 1000)
            x, y, iw = margin, stack['y'] + stack['height'] + 30, width - 2 * margin
        ow, oh = sizes[project['capture']]
        ih = iw * oh / ow
        r.shift(root, divider['y'], max(0, y + ih + 74 - divider['y']))
        image(root['id'], project['capture'], x, y, iw, ih)
        full_size_caption(r, root['id'], project['capture'], 'Notes editor', x, y + ih + 10, iw, 12)
        if not project['gallery']:
            return
        root = r.m.tool('get_node', {'id': f['id'], 'depth': 4})
        explore = next(c for c in root['children'] if c.get('characters') == 'Explore more work')
        line = max((c for c in root['children'] if c.get('name') == 'Section divider' and c['y'] < explore['y']), key=lambda c: c['y'])
        start = line['y']; y = start
        cx, cw = (390, 800) if width >= 1200 else (margin, width - 2 * margin)
        _, heading = r.s.text(root['id'], 'Application interface', cx, y, cw,
                              32 if width >= 1200 else 28, TEXT, 'SemiBold')
        y += heading['height'] + 30
        for asset in plan['images'][1:]:
            ow, oh = sizes[asset['stem']]; height = cw * oh / ow
            image(root['id'], asset['stem'], cx, y, cw, height)
            _, caption = full_size_caption(r, root['id'], asset['stem'], 'Sign-in screen',
                                           cx, y + height + 10, cw, 14)
            y += height + 10 + caption['height'] + 48
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
                    label = next(n for n in c['children'] if n['type'] == 'TEXT')
                    r.m.command('node.set', {'ids': [label['id']], 'x': 23, 'width': c['width'] - 23, 'fontSize': 13})
                    r.icon(c['id'], 'github' if name.endswith('GitHub') else 'linkedin', 0, 13, 16)
        r.finish()
        r.m.save_log(D / 'secure-notes-application-mcp-calls.json')
        print('Original Qt application captures added to Selected work, collection and case study.')
    finally:
        r.m.close()


if __name__ == '__main__':
    main()
