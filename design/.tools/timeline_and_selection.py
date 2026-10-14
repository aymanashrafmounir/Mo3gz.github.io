"""Apply the requested timeline and homepage project selection via native MCP."""
import json
from pathlib import Path
from figcraft_mcp import Figcraft
from create_screens import Screens, CAREER, PAPER, SURFACE, TEXT, MUTED, RUST, LINE

D = Path(__file__).resolve().parents[1]


def walk(n):
    yield n
    for child in n.get('children', []):
        yield from walk(child)


class Edit:
    def __init__(self):
        self.m = Figcraft()
        self.m.tool('open_file', {'path': str(D / 'ayman-portfolio-v2.figcraft')})
        self.frames = json.loads((D / 'screen-manifest.json').read_text())
        self.data = json.loads((D / 'screen-content.json').read_text())
        self.projects = {p['slug']: p for p in self.data['projects']}
        self.icons = json.loads((D / 'technology-components.json').read_text())
        self.s = Screens.__new__(Screens)
        self.s.mcp, self.s.links, self.s.text_nodes = self.m, [], []
        self.targets = {(f['slug'], f['width']): f['id'] for f in self.frames}

    def set(self, n, **props):
        self.m.command('node.set', {'ids': [n['id']], **props})
        n.update(props)

    def shift(self, frame, from_y, delta):
        for c in frame['children']:
            if c['y'] >= from_y - .05:
                self.set(c, y=round(c['y'] + delta, 2))
        self.set(frame, height=round(frame['height'] + delta, 2))

    def icon_stack(self, parent, items, x, y, width):
        root, _ = self.s.node('frame', 'Verified project stack', x, y, width, 24, parent=parent,
                              props={'fills': [], 'clip': False})
        px, py = 0, 0
        for key, label in items:
            icon = self.m.command('instance.create', {'component': self.icons[key], 'parent': root, 'x': 0, 'y': 0})
            self.m.command('transform.scale', {'ids': [icon['id']], 'factor': .9})
            tid, text = self.s.text(root, label, 0, 0, width, 13, MUTED, 'Medium')
            self.m.command('node.set', {'ids': [tid], 'textAutoResize': 'widthAndHeight'})
            text = self.m.tool('get_node', {'id': tid})
            span = 26 + text['width']
            if px and px + span > width:
                px, py = 0, py + 30
            self.m.command('node.set', {'ids': [icon['id']], 'x': px, 'y': py})
            self.m.command('node.set', {'ids': [tid], 'x': px + 26, 'y': py - 1})
            px += span + 18
        self.m.command('node.set', {'ids': [root], 'height': py + 24})
        return py + 24

    def case_link(self, parent, project, x, y, width):
        link = self.s.nav_link(parent, 'Read case study', x, y, 180, 'project:' + project['slug'])
        self.m.tool('create_node', {'type': 'vector', 'name': 'Case study arrow', 'x': 145, 'y': 15,
                                  'width': 14, 'height': 14, 'parent': link,
                                  'path': 'M1 7H13M8 2L13 7L8 12',
                                  'props': {'fills': [], 'stroke': RUST, 'strokeWeight': 1.5,
                                            'strokeCap': 'round', 'strokeJoin': 'round'}})
        return y + 44

    def selected(self, f):
        frame = self.m.tool('get_node', {'id': f['id'], 'depth': 12})
        width = f['width']
        self.s.current_width = width
        margin = 80 if width >= 1200 else 40 if width >= 700 else 24
        inner = width - margin * 2
        first_title = next(c for c in frame['children'] if c.get('characters') == 'Arkedia')
        first_image = next((c for c in frame['children'] if c.get('name') == 'Genuine public capture / arkedia'), None)
        start = min(first_title['y'], first_image['y'] if first_image else first_title['y'])
        all_projects = next(c for c in frame['children'] if c['type'] == 'INSTANCE' and any(n.get('characters') == 'All projects' for n in walk(c)))
        old_end = all_projects['y']
        remove = [c['id'] for c in frame['children'] if start <= c['y'] < old_end]
        self.m.command('edit.delete', {'ids': remove})
        frame['children'] = [c for c in frame['children'] if c['id'] not in remove]
        blitz, secure = self.projects['blitzchatbot'], self.projects['secure-notes-organizer']
        y = start
        if width >= 700:
            iw, ih = (315, 177) if width >= 1200 else (240, 150)
            tx, tw = margin + iw + (40 if width >= 1200 else 28), inner - iw - (40 if width >= 1200 else 28)
            top = y + 6
        else:
            iw, ih = inner, inner * 900 / 1440
            tx, tw, top = margin, inner, y + ih + 22
        image, _ = self.s.node('frame', 'Genuine public capture / blitzchatbot', margin, y, iw, ih,
                               parent=frame['id'], props={'fill': SURFACE, 'cornerRadius': 6, 'clip': True})
        self.m.command('image.place', {'path': str(D / 'assets/captures' / (blitz['capture'] + '.png')),
                                     'parent': image, 'x': 0, 'y': 0, 'width': iw, 'height': ih, 'mode': 'fit'})
        _, box = self.s.text(frame['id'], blitz['title'], tx, top, tw, 28 if width >= 1200 else 25, TEXT, 'SemiBold')
        cy = top + box['height'] + 8
        _, box = self.s.text(frame['id'], blitz['kind'], tx, cy, tw, 14, RUST)
        cy += box['height'] + 14
        _, box = self.s.text(frame['id'], blitz['summary'], tx, cy, tw, 17, MUTED)
        cy += box['height'] + 16
        cy += self.icon_stack(frame['id'], [('java', 'Java'), ('spring', 'Spring Boot'), ('react', 'React')], tx, cy, tw) + 6
        cy = self.case_link(frame['id'], blitz, tx, cy, width)
        y = max(y + ih, cy) + 32
        self.s.divider(frame['id'], margin, y, inner)
        y += 28
        _, title = self.s.text(frame['id'], secure['title'], margin, y, min(inner, 850), 28 if width >= 1200 else 25, TEXT, 'SemiBold')
        if width >= 1200:
            self.icon_stack(frame['id'], [('cplusplus', 'C++'), ('qt', 'Qt 6')], width - margin - 250, y + 9, 250)
        y += title['height'] + 14
        _, body = self.s.text(frame['id'], secure['summary'], margin, y, min(inner, 900), 17, MUTED)
        y += body['height'] + 18
        if width < 1200:
            y += self.icon_stack(frame['id'], [('cplusplus', 'C++'), ('qt', 'Qt 6')], margin, y, inner) + 8
        y = self.case_link(frame['id'], secure, margin, y, width)
        self.shift(frame, old_end, y + 36 - old_end)
        print('Selected work replaced', width, flush=True)

    def timeline(self, f):
        frame = self.m.tool('get_node', {'id': f['id'], 'depth': 3})
        start_node = next(c for c in frame['children'] if c.get('characters') == CAREER[0][0])
        start, x, old_width = start_node['y'], start_node['x'], start_node['width']
        # The original career block has three text nodes and a divider per role.
        candidates = sorted([c for c in frame['children'] if c['y'] >= start and c.get('x') == x and c['type'] in ['TEXT', 'RECTANGLE']], key=lambda c: c['y'])
        entries, remove = [], []
        for i in range(5):
            title, meta, body, divider = candidates[i * 4:i * 4 + 4]
            assert title['type'] == meta['type'] == body['type'] == 'TEXT'
            assert divider.get('name') == 'Section divider'
            company, dates = meta['characters'].rsplit('  /  ', 1)
            entries.append((title['characters'], company, dates, body['characters']))
            remove += [title['id'], meta['id'], body['id'], divider['id']]
        old_end = divider['y'] + 32
        self.m.command('edit.delete', {'ids': remove})
        frame['children'] = [c for c in frame['children'] if c['id'] not in remove]
        width = f['width']
        inset = 36 if width >= 1200 else 32 if width >= 700 else 28
        body_width = min(old_width - inset, 800)
        root, _ = self.s.node('frame', 'Experience timeline', x, start, old_width, 5000,
                              parent=frame['id'], props={'fills': [], 'clip': False,
                                                        'pluginData': {'timeline': 'Career order; dates overlap; spacing is not proportional to elapsed time.'}})
        rail = self.s.rect(root, 'Career timeline rail', 5, 0, 2, 1, LINE)
        y, points = 0, []
        for title, company, dates, description in entries:
            _, box = self.s.text(root, dates.replace(' to ', ' – '), inset, y, body_width, 14, RUST, 'Medium', 'Timeline dates / ' + company)
            y += box['height'] + 10
            title_top = y
            _, box = self.s.text(root, title, inset, y, body_width, 23 if width >= 1200 else 21 if width >= 700 else 20, TEXT, 'SemiBold')
            y += box['height'] + 8
            _, box = self.s.text(root, company, inset, y, body_width, 16 if width >= 700 else 14, TEXT, 'Medium')
            y += box['height'] + 14
            _, box = self.s.text(root, description, inset, y, body_width, 18 if width >= 1200 else 17 if width >= 700 else 16, MUTED)
            y += box['height'] + (44 if width >= 700 else 40)
            dot_y = title_top + (16 if width >= 1200 else 14)
            points.append(dot_y)
            self.s.node('ellipse', 'Current role' if 'Present' in dates else 'Completed role', 1, dot_y - 5, 10, 10,
                        parent=root, props={'fill': RUST if 'Present' in dates else PAPER, 'stroke': RUST, 'strokeWeight': 1.5})
        self.m.command('node.set', {'ids': [rail], 'y': points[0], 'height': points[-1] - points[0]})
        self.m.command('node.set', {'ids': [root], 'height': y})
        self.shift(frame, old_end, start + y - old_end)
        print('Timeline created', f['slug'], width, flush=True)

    def finish(self):
        for ident, target, width in self.s.links:
            self.m.command('proto.interaction.add', {'id': ident, 'dest': self.targets[(target, width)]})
        self.m.tool('save_file', {'path': str(D / 'ayman-portfolio-v2.figcraft')})
        doc = self.m.tool('inspect_document', {'depth': 20, 'allPages': True})
        nodes = {n['id']: n for p in doc['pages'] for n in walk(p)}
        for f in self.frames:
            f['height'] = nodes[f['id']]['height']
        (D / 'screen-manifest.json').write_text(json.dumps(self.frames, indent=2))
        (D / 'native-document-inspection.json').write_text(json.dumps(doc, indent=2))
        (D / 'screen-inspection.json').write_text(json.dumps([{'frame': f, 'node': nodes[f['id']]} for f in self.frames], indent=2))
        self.data['selectedWork'] = ['helixtra', 'wear-instant', 'blitzchatbot', 'secure-notes-organizer']
        self.data['experiencePresentation'] = 'Vertical timeline on homepage, Experience and Resume; original overlapping dates retained.'
        (D / 'screen-content.json').write_text(json.dumps(self.data, indent=2))
        self.m.save_log(D / 'timeline-selected-mcp-calls.json')

    def run(self):
        for f in self.frames:
            if f['slug'] == 'home':
                self.selected(f)
        for f in self.frames:
            if f['slug'] in ['home', 'experience', 'resume']:
                self.timeline(f)
        self.finish()


if __name__ == '__main__':
    edit = Edit()
    try:
        edit.run()
    finally:
        edit.m.close()
