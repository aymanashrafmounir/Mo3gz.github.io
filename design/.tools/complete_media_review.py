"""Apply the two concrete findings from Astra's independent native-screen review."""
import json
import shutil
from pathlib import Path
from figcraft_mcp import Figcraft

D = Path(__file__).resolve().parents[1]
shutil.copy2(D / 'research-candidates/quantitator-upload.png', D / 'assets/captures/quantitator-app.png')
manifest = json.loads((D / 'capture-manifest.json').read_text())
for item in manifest:
    if item['project'] == 'quantitator':
        item['source'] = 'https://github.com/aymanashrafmounir/Quantitator/blob/1982ca641e06c51bdec7de168ae689191b62e82d/Screenshots/Upload_File_Page.png'
        item['caption'] = 'Original public input-mapping and optimization-parameter interface. Values are configuration inputs, not achieved results.'
(D / 'capture-manifest.json').write_text(json.dumps(manifest, indent=2))


def walk(n):
    yield n
    for c in n.get('children', []):
        yield from walk(c)


m = Figcraft()
try:
    m.tool('open_file', {'path': str(D / 'ayman-portfolio-v2.figcraft')})
    doc = m.tool('inspect_document', {'depth': 20, 'allPages': True})
    data = json.loads((D / 'screen-content.json').read_text())
    projects = {p['slug']: p for p in data['projects']}
    frames = json.loads((D / 'screen-manifest.json').read_text())
    nodes = {n['id']: n for p in doc['pages'] for n in walk(p)}
    for n in list(nodes.values()):
        if n.get('name') == 'Genuine public capture / quantitator':
            old = [c['id'] for c in n.get('children', [])]
            m.command('image.place', {'path': str(D / 'assets/captures/quantitator-app.png'), 'parent': n['id'],
                                    'x': 0, 'y': 0, 'width': n['width'], 'height': n['height'], 'mode': 'fit'})
            m.command('edit.delete', {'ids': old})
        if n.get('name') == 'Skill identities / Architecture and collaboration':
            extra = [c['id'] for c in n.get('children', []) if c.get('characters') in ['C++', 'Python'] or c.get('name') in ['Technology/C++', 'Technology/Python']]
            if extra:
                m.command('edit.delete', {'ids': extra})
    for f in frames:
        if not f['slug'].startswith('project:'):
            continue
        project = projects[f['slug'].split(':')[1]]
        if not project.get('capture'):
            continue
        frame = nodes[f['id']]
        image = next(c for c in frame['children'] if c.get('name') == 'Genuine public capture / ' + project['slug'])
        file_url = (D / 'assets/captures' / (project['capture'] + '.png')).as_uri()
        # The original Helixtra lightbox interaction stays intact on its image.
        if not image.get('interactions'):
            m.command('proto.interaction.add', {'id': image['id'], 'trigger': {'type': 'onClick'}, 'action': {'type': 'openUrl', 'url': file_url}})
        old_caption = next((c for c in frame['children'] if c.get('characters') == 'Public website capture' and abs(c['x'] - image['x']) < 1), None)
        if old_caption:
            m.command('edit.delete', {'ids': [old_caption['id']]})
        link = m.tool('create_node', {'type': 'frame', 'name': 'Open original full-size screenshot',
                                     'x': image['x'], 'y': image['y'] + image['height'] + 6,
                                     'width': image['width'], 'height': 44, 'parent': frame['id'], 'props': {'fills': []}})['id']
        m.tool('create_node', {'type': 'text', 'name': 'View full-size screenshot', 'text': 'View full-size screenshot ↗',
                              'x': 0, 'y': 11, 'width': image['width'], 'parent': link,
                              'props': {'fontFamily': 'Mona Sans', 'fontStyle': 'Medium', 'fontSize': 13,
                                        'lineHeight': 19, 'fill': '#AE3A24', 'textAutoResize': 'height'}})
        m.command('proto.interaction.add', {'id': link, 'trigger': {'type': 'onClick'}, 'action': {'type': 'openUrl', 'url': file_url}})
    m.tool('save_file', {'path': str(D / 'ayman-portfolio-v2.figcraft')})
    m.save_log(D / 'media-review-mcp-calls.json')
    print('Optimization cover corrected; every genuine case capture has a full-size source action.')
finally:
    m.close()
