"""Refine approved A screens through the native Figcraft stdio MCP engine.

Preserves route frame IDs and existing prototype targets; no website code.
"""
import json
import pathlib
import shutil
import sys
import xml.etree.ElementTree as ET

from figcraft_mcp import Figcraft
from create_screens import Screens, PAPER, TEXT, MUTED, RUST, LINE, SURFACE, SKILLS

ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / 'design'
sys.stdout.reconfigure(encoding='utf-8')


def walk(n):
    yield n
    for c in n.get('children', []):
        yield from walk(c)


def prepare_media():
    data = json.loads((D / 'screen-content.json').read_text(encoding='utf-8-sig'))
    captures = json.loads((D / 'capture-manifest.json').read_text())
    live = {'helixtra': 'helixtra', 'wear-instant': 'wearinstant', 'ibrahim-awad': 'ibrahim-awad',
            'tapora': 'tapora', 'maysa-waheed': 'maysa', 'supreme-sparkle': 'supreme-sparkle', 'arkedia': 'arkedia'}
    extra = {'cheque-printer': ('cheque-main.png', 'https://github.com/aymanashrafmounir/Cheque_printer/blob/81622e2f86183ae4d2be7e0b01b9542f751d9982/Screenshots/Main%20Page.png', 'Original desktop app capture; entry fields and table are empty.'),
             'quantitator': ('quantitator-chat.png', 'https://github.com/aymanashrafmounir/Quantitator/blob/1982ca641e06c51bdec7de168ae689191b62e82d/Screenshots/Chat_With_AI.png', 'Original assistant dialog with cleared history and no data access.'),
             'blitzchatbot': ('blitz-labels-desktop.png', 'D:/AQ/BlitzChatbot/project-react/output/playwright/labels-desktop-1440.png', 'Original labels interface. No contacts or account credentials shown.'),
             'artline': ('artline-ui.png', 'https://github.com/aymanashrafmounir/Artline/tree/7234390dfcfc2ec89ec359fb598bbcca1b9ac87a/frontend', 'Original public frontend captured locally, unchanged; empty uploader.')}
    for project in data['projects']:
        slug = project['slug']
        if slug in live:
            stem = slug + '-loaded'
            src = D / 'research-candidates/live-captures' / (live[slug] + '-loaded.png')
            prior = next((c for c in captures if c['project'] == slug), None)
            source = prior['source'] if prior else 'https://supreme-sparkle.pages.dev'
            caption = prior['caption'] if prior else 'Genuine public storefront capture.'
            classification = 'genuine-public-site-capture'
        elif slug in extra:
            filename, source, caption = extra[slug]
            stem = slug + '-app'
            src = D / 'research-candidates' / filename
            classification = 'genuine-original-application-capture'
        else:
            continue
        assert src.is_file(), src
        dst = D / 'assets/captures' / (stem + '.png')
        shutil.copy2(src, dst)
        project['capture'] = stem
        entry = {'project': slug, 'path': dst.relative_to(ROOT).as_posix(), 'classification': classification,
                 'observed': '2026-10-14', 'source': source, 'caption': caption,
                 'use': 'Native design review. Preserve stated project publication status.',
                 'framing': 'Complete capture, fit without zoom or crop.'}
        if slug in live:
            entry['captureDetails'] = '1440x1000, DPR 1, browser scale 1, >=12s wait plus fonts and image decode.'
        captures = [c for c in captures if c['project'] != slug] + [entry]
    (D / 'screen-content.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
    (D / 'capture-manifest.json').write_text(json.dumps(captures, indent=2), encoding='utf-8')
    return data


LABELS = {'java': 'Java', 'spring': 'Spring Boot', 'typescript': 'TypeScript', 'cloudflare': 'Cloudflare',
          'react': 'React', 'python': 'Python', 'cplusplus': 'C++', 'qt': 'Qt', 'postgresql': 'PostgreSQL',
          'mysql': 'MySQL', 'sqlite': 'SQLite', 'docker': 'Docker', 'git': 'Git', 'vitest': 'Vitest',
          'playwright': 'Playwright', 'github': 'GitHub', 'linkedin': 'LinkedIn', 'javascript': 'JavaScript'}
KEYS = {'Java': 'java', 'Spring Boot': 'spring', 'TypeScript': 'typescript', 'React': 'react', 'Python': 'python',
        'C++': 'cplusplus', 'Qt 6': 'qt', 'PostgreSQL': 'postgresql', 'SQLite': 'sqlite', 'Docker': 'docker',
        'Cloudflare Workers': 'cloudflare', 'Workers': 'cloudflare', 'Pages Functions': 'cloudflare',
        'Workers Static Assets': 'cloudflare'}


class Refine:
    def __init__(self, data):
        self.data = data
        self.projects = {p['slug']: p for p in data['projects']}
        self.m = Figcraft()
        self.m.tool('open_file', {'path': str(D / 'ayman-portfolio-v2.figcraft')})
        self.frames = json.loads((D / 'screen-manifest.json').read_text())
        self.tree = self.m.tool('inspect_document', {'depth': 20, 'allPages': True})
        assert self.tree['path'] == str(D / 'ayman-portfolio-v2.figcraft')
        self.nodes = {n['id']: n for page in self.tree['pages'] for n in walk(page)}
        self.s = Screens.__new__(Screens)
        self.s.mcp, self.s.links, self.s.text_nodes = self.m, [], []
        self.s.components = {'primary': 27, 'secondary': 29}
        # Discover the approved button components rather than relying on stale IDs.
        for n in self.nodes.values():
            if n.get('type') == 'COMPONENT' and n.get('name') in ['Button/Primary', 'Button/Secondary']:
                self.s.components[n['name'].split('/')[1].lower()] = n['id']
        self.icons = {}

    def set(self, n, **props):
        self.m.command('node.set', {'ids': [n['id']], **props})
        n.update(props)

    def shift(self, frame, y, delta, exclude=()):
        if abs(delta) < .05:
            return
        for c in frame.get('children', []):
            if c['id'] not in exclude and c.get('y', 0) >= y - .1:
                self.set(c, y=round(c['y'] + delta, 2))
        self.set(frame, height=round(frame['height'] + delta, 2))

    def foundation(self):
        self.m.command('page.select', {'id': 1})
        # Remove only the temporary import used to inspect the native SVG API.
        if 4272 in self.nodes:
            self.m.command('edit.delete', {'ids': [4272]})
        board, _ = self.s.node('frame', 'Technology marks / editable SVG components', 1700, 0, 1440, 920,
                               props={'fill': PAPER})
        self.s.text(board, 'Technology, recognized at a glance.', 80, 65, 1260, 42, TEXT, 'SemiBold')
        self.s.text(board, 'Original Devicon vectors. Small marks, readable names, verified stacks.', 80, 135, 1260, 20, MUTED)
        for i, (key, label) in enumerate(LABELS.items()):
            path = D / 'assets/icons' / (key + '.svg')
            vb = ET.parse(path).getroot().get('viewBox').split()
            size = max(float(vb[2]), float(vb[3]))
            result = self.m.command('file.import', {'path': str(path), 'x': 0, 'y': 0})
            ident = result['id']
            self.m.command('transform.scale', {'ids': [ident], 'factor': 20 / size})
            self.m.command('component.create', {'ids': [ident]})
            self.m.command('node.reparent', {'ids': [ident], 'parent': board})
            x, y = 80 + i % 4 * 310, 235 + i // 4 * 100
            self.m.command('node.set', {'ids': [ident], 'name': 'Technology/' + label, 'x': x, 'y': y,
                                      'description': 'Original editable Devicon SVG. ' + label})
            self.icons[key] = ident
            self.s.text(board, label, x + 36, y - 1, 235, 16, TEXT, 'Medium')
        self.s.text(board, 'Use 20px in core stack and 18px in project metadata. Labels remain visible.\nBrand marks retain their identity; surrounding typography stays warm and quiet.', 80, 785, 1260, 16, MUTED)
        (D / 'technology-components.json').write_text(json.dumps(self.icons, indent=2))
        print('Editable technology foundations created', flush=True)

    def icon(self, parent, key, x, y, size=20):
        r = self.m.command('instance.create', {'component': self.icons[key], 'parent': parent, 'x': x, 'y': y})
        if size != 20:
            self.m.command('transform.scale', {'ids': [r['id']], 'factor': size / 20})
        return r['id']

    def stack(self, parent, items, x, y, width, size=18, font=13, gap=20, name='Verified project stack'):
        row, _ = self.s.node('frame', name, x, y, width, 24, parent=parent, props={'fills': [], 'clip': False})
        px, py = 0, 0
        for key, label in items:
            span = size + 8 + len(label) * font * .56
            if px + span > width + .1:
                px, py = 0, py + 30
            self.icon(row, key, px, py, size)
            self.s.text(row, label, px + size + 8, py - 1, span - size, font, MUTED, 'Medium')
            px += span + gap
        self.m.command('node.set', {'ids': [row], 'height': py + 24})
        return py + 24

    def project_items(self, project):
        items, seen = [], set()
        for tech in project['stack']:
            key = KEYS.get(tech)
            if key and key not in seen:
                seen.add(key)
                items.append((key, 'Cloudflare' if key == 'cloudflare' else tech))
        return items[:3]

    def replace_capture(self, wrapper, path):
        old = [c['id'] for c in wrapper.get('children', [])]
        self.m.command('image.place', {'path': str(path), 'parent': wrapper['id'], 'x': 0, 'y': 0,
                                     'width': wrapper['width'], 'height': wrapper['height'], 'mode': 'fit'})
        if old:
            self.m.command('edit.delete', {'ids': old})

    def media_and_cases(self):
        for f in self.frames:
            frame = self.nodes[f['id']]
            width = f['width']
            if f['slug'].startswith('project:'):
                project = self.projects[f['slug'].split(':')[1]]
                caps = [c for c in frame['children'] if c.get('name', '').startswith('Genuine public capture /')]
                # Add the newly found original app captures where the approved layout had no imagery.
                if project.get('capture') and not caps:
                    buttons = [c for c in frame['children'] if c['type'] == 'INSTANCE' and c.get('y', 0) < 750]
                    bottom = max((c['y'] + c['height'] for c in buttons), default=500)
                    divider = next(c for c in frame['children'] if c.get('name') == 'Section divider' and c['y'] > 100)
                    if width >= 1200:
                        new_y = max(710, divider['y'])
                        self.shift(frame, divider['y'], new_y - divider['y'])
                        self.new_image(frame['id'], project, 770, 180, 590, 410)
                    else:
                        h = 365 if width >= 700 else 235
                        self.shift(frame, divider['y'], h + 65)
                        self.new_image(frame['id'], project, 40 if width >= 700 else 24, bottom + 30, width - (80 if width >= 700 else 48), h)
                # Case core stack sits after its primary actions; reserve its own space on narrow screens.
                buttons = [c for c in frame['children'] if c['type'] == 'INSTANCE' and c.get('y', 0) < 750]
                bottom = max((c['y'] + c['height'] for c in buttons), default=450)
                if width < 1200:
                    self.shift(frame, bottom + 15, 76)
                    # Newly added captures are not in the initial inspection tree.
                    if project.get('capture') and not caps:
                        for img in self.new_images.get(frame['id'], []):
                            self.m.command('node.set', {'ids': [img], 'y': bottom + 106})
                self.stack(frame['id'], self.project_items(project), 80 if width >= 1200 else 40 if width >= 700 else 24,
                           bottom + 24, 570 if width >= 1200 else width - (80 if width >= 700 else 48), 20, 14)
                # Reading text uses a comfortable 800px column; reflow subsequent content when it wraps.
                if width >= 1200:
                    for c in sorted(frame['children'], key=lambda c: c.get('y', 0)):
                        if c['type'] == 'TEXT' and c.get('x', 0) >= 390 and c.get('width', 0) >= 948 and c.get('y', 0) > 700:
                            old_bottom = c['y'] + c['height']
                            self.set(c, width=778 if c['x'] > 390 else 800)
                            updated = self.m.tool('get_node', {'id': c['id']})
                            updated = updated.get('node', updated)
                            delta = updated['height'] - c['height']
                            self.shift(frame, old_bottom, delta, [c['id']])
                            c['height'] = updated['height']
            # Replace original public captures with stabilized, complete images.
            slug = f['slug'].split(':', 1)[1] if f['slug'].startswith('project:') else None
            for c in frame.get('children', []):
                name = c.get('name', '')
                pslug = name.split(' / ')[1] if name.startswith('Genuine public capture / ') else slug if name == 'Genuine public capture' else None
                if pslug and self.projects[pslug].get('capture'):
                    self.replace_capture(c, D / 'assets/captures' / (self.projects[pslug]['capture'] + '.png'))
        print('Real project captures corrected without crop; cases refined', flush=True)

    def new_image(self, parent, project, x, y, w, h):
        wrapper, _ = self.s.node('frame', 'Genuine public capture / ' + project['slug'], x, y, w, h, parent=parent,
                                 props={'fill': SURFACE, 'cornerRadius': 6, 'clip': True})
        self.m.command('image.place', {'path': str(D / 'assets/captures' / (project['capture'] + '.png')),
                                     'parent': wrapper, 'x': 0, 'y': 0, 'width': w, 'height': h, 'mode': 'fit'})
        self.new_images.setdefault(parent, []).append(wrapper)
        return wrapper

    def homes_and_skills(self):
        cats = {'Backend engineering': [('java', 'Java'), ('spring', 'Spring Boot')],
                'Frontend engineering': [('react', 'React'), ('typescript', 'TypeScript')],
                'Data and persistence': [('postgresql', 'PostgreSQL'), ('mysql', 'MySQL')],
                'Cloud and infrastructure': [('cloudflare', 'Cloudflare'), ('docker', 'Docker')],
                'Testing and quality': [('vitest', 'Vitest'), ('playwright', 'Playwright')],
                'Architecture and collaboration': [('git', 'Git')]}
        for f in self.frames:
            frame, width = self.nodes[f['id']], f['width']
            if f['slug'] == 'home':
                margin = 80 if width >= 1200 else 40 if width >= 700 else 24
                y = 676 if width >= 1200 else 1008 if width >= 700 else 925
                core = [('java', 'Java'), ('spring', 'Spring Boot'), ('typescript', 'TypeScript'), ('cloudflare', 'Cloudflare')]
                if width < 700:
                    self.stack(frame['id'], core[:2], margin, y, width - margin * 2, 20, 14, 22, 'Core stack / first row')
                    self.stack(frame['id'], core[2:], margin, y + 30, width - margin * 2, 20, 14, 22, 'Core stack / second row')
                else:
                    self.stack(frame['id'], core, margin, y, 650 if width >= 1200 else width - margin * 2, 20, 14, 22, 'Core stack')
                # First selected cards have 48px breathing space before the next row.
                for p in list(self.projects.values())[:2]:
                    title = next(c for c in frame['children'] if c.get('characters') == p['title'])
                    link = next(c for c in frame['children'] if c.get('name') == 'Navigate to Read case study' and c['x'] == title['x'] and c['y'] > title['y'])
                    if width < 1200:
                        self.shift(frame, link['y'], 34)
                    self.stack(frame['id'], self.project_items(p), title['x'], link['y'] - 26 if width < 1200 else link['y'] + 43,
                               title['width'], 18, 13, 16)
            for heading in frame.get('children', []):
                if heading.get('type') == 'TEXT' and heading.get('fontSize') == 21 and heading.get('characters') in cats:
                    self.stack(frame['id'], cats[heading['characters']], heading['x'], heading['y'] + 107,
                               heading['width'], 18, 13, 18, 'Skill identities / ' + heading['characters'])
        print('Core stack and categorized skills added', flush=True)

    def card(self, frame, project, x, y, width, image_height):
        self.new_image(frame, project, x, y, width, image_height)
        _, title = self.s.text(frame, project['title'], x, y + image_height + 22, width, 26, TEXT, 'SemiBold')
        y += image_height + 22 + title['height']
        self.s.text(frame, project['kind'], x, y + 8, width, 15, RUST)
        _, body = self.s.text(frame, project['summary'], x, y + 42, width, 16, MUTED)
        y += 42 + body['height'] + 19
        h = self.stack(frame, self.project_items(project), x, y, width, 18, 13, 16)
        y += h + 8
        self.s.nav_link(frame, 'Read case study', x, y, 176, 'project:' + project['slug'])
        return y + 44

    def listings(self):
        for f in self.frames:
            if f['slug'] not in ['projects', 'filter-products', 'filter-public']:
                continue
            frame, width = self.nodes[f['id']], f['width']
            self.s.current_width = width
            # Keep all approved header/filter nodes and their interactions intact.
            count = next(c for c in frame['children'] if c.get('type') == 'TEXT' and c.get('characters', '').endswith(' projects'))
            start_y = count['y'] + 50
            obsolete = [c['id'] for c in frame['children'] if c['y'] >= start_y]
            self.m.command('edit.delete', {'ids': obsolete})
            frame['children'] = [c for c in frame['children'] if c['id'] not in obsolete]
            shown = list(self.projects.values())
            if f['slug'] != 'projects':
                cat = 'Products & Client Work' if f['slug'] == 'filter-products' else 'Public Repositories'
                shown = [p for p in shown if p['category'] == cat]
            columns = 3 if width >= 1200 else 2 if width >= 700 else 1
            margin, gap = (80, 34) if width >= 1200 else (40, 26) if width >= 700 else (24, 26)
            inner = width - 2 * margin
            cw = (inner - (columns - 1) * gap) / columns
            visual = [p for p in shown if p.get('capture')]
            y = start_y
            for start in range(0, len(visual), columns):
                ends = [self.card(frame['id'], p, margin + i * (cw + gap), y, cw, 224 if width >= 1200 else 210)
                        for i, p in enumerate(visual[start:start + columns])]
                y = max(ends) + 58
            for p in shown:
                if p.get('capture'):
                    continue
                self.s.divider(frame['id'], margin, y, inner)
                self.s.text(frame['id'], p['title'], margin, y + 24, inner, 25, TEXT, 'SemiBold')
                _, body = self.s.text(frame['id'], p['summary'], margin, y + 74, min(inner, 800), 16, MUTED)
                sy = y + 74 + body['height'] + 20
                h = self.stack(frame['id'], self.project_items(p), margin, sy, inner, 18, 13)
                self.s.nav_link(frame['id'], 'Read case study', margin, sy + h + 8, 176, 'project:' + p['slug'])
                y = sy + h + 82
            self.s.footer(frame['id'], width, y + 20)
            print('Project collection rebuilt', f['slug'], width, flush=True)

    def details(self):
        tree = self.m.tool('inspect_document', {'depth': 20, 'allPages': True})
        for f in self.frames:
            frame = next(n for p in tree['pages'] for n in p.get('children', []) if n['id'] == f['id'])
            for c in frame.get('children', []):
                name = c.get('name', '')
                if name in ['Navigate to GitHub', 'Navigate to LinkedIn']:
                    key = 'github' if name.endswith('GitHub') else 'linkedin'
                    child = next((n for n in c.get('children', []) if n['type'] == 'TEXT'), None)
                    if child:
                        self.m.command('node.set', {'ids': [child['id']], 'x': 23, 'width': c['width'] - 20, 'fontSize': 13})
                        self.icon(c['id'], key, 0, 13, 16)
                if name == 'Navigate to Read case study':
                    # Add a simple editable navigation arrow as native geometry.
                    self.m.tool('create_node', {'type': 'vector', 'name': 'Case study arrow', 'x': 145, 'y': 15,
                                               'width': 14, 'height': 14, 'parent': c['id'],
                                               'path': 'M1 7H13M8 2L13 7L8 12',
                                               'props': {'fills': [], 'stroke': RUST, 'strokeWeight': 1.5, 'strokeCap': 'round', 'strokeJoin': 'round'}})
                if c['type'] == 'FRAME' and c.get('y') == 22 and name.startswith('Navigate to '):
                    child = next((n for n in c.get('children', []) if n['type'] == 'TEXT'), None)
                    if child and child.get('fills', [{}])[0].get('color') == RUST:
                        self.s.rect(c['id'], 'Active navigation underline', 0, 39, min(c['width'] - 12, len(child['characters']) * 7), 2, RUST)
        print('Navigation details added', flush=True)

    def finish(self):
        destinations = {(f['width'], f['slug']): f['id'] for f in self.frames}
        for ident, target, width in self.s.links:
            if target.startswith('external:'):
                self.m.command('proto.interaction.add', {'id': ident, 'trigger': {'type': 'onClick'},
                                                       'action': {'type': 'openUrl', 'url': self.data['identity'][target.split(':')[1]]}})
            else:
                self.m.command('proto.interaction.add', {'id': ident, 'dest': destinations[(width, target)]})
        self.m.tool('save_file', {'path': str(D / 'ayman-portfolio-v2.figcraft')})
        tree = self.m.tool('inspect_document', {'depth': 20, 'allPages': True})
        (D / 'native-document-inspection.json').write_text(json.dumps(tree, indent=2), encoding='utf-8')
        nodes = {n['id']: n for p in tree['pages'] for n in walk(p)}
        for f in self.frames:
            f['height'] = nodes[f['id']]['height']
        (D / 'screen-inspection.json').write_text(json.dumps([{'frame': f, 'node': nodes[f['id']]} for f in self.frames], indent=2), encoding='utf-8')
        (D / 'screen-manifest.json').write_text(json.dumps(self.frames, indent=2), encoding='utf-8')
        self.m.save_log(D / 'refinement-mcp-calls.json')
        print('Native refinement saved', flush=True)

    def run(self):
        self.new_images = {}
        self.foundation()
        self.media_and_cases()
        self.homes_and_skills()
        self.listings()
        self.details()
        self.finish()


if __name__ == '__main__':
    r = Refine(prepare_media())
    try:
        r.run()
    finally:
        r.m.close()
