"""Add the verified Siemens internship context without changing ownership claims."""
import json
import shutil
from pathlib import Path
from figcraft_mcp import Figcraft

D = Path(__file__).resolve().parents[1]
native = D / 'ayman-portfolio-v2.figcraft'
shutil.copy2(native, D / 'checkpoints/before-secure-notes-affiliation.figcraft')
data = json.loads((D / 'screen-content.json').read_text())
project = next(p for p in data['projects'] if p['slug'] == 'secure-notes-organizer')
new = {
    'kind': 'Siemens DISW internship final project',
    'status': 'Internship project · Public code',
    'summary': 'A C++/Qt notes application built for the Siemens DISW internship final project, with encrypted storage and client-server communication.',
    'overview': 'A team project completed during the Siemens Digital Industries Software (DISW) internship, covering note creation, tags, search, authentication and client-server storage.',
    'role': 'Contributed encrypted storage and socket communication, alongside memory and performance refactoring, as part of the Siemens DISW internship project team.',
}
replace = {project[k]: v for k, v in new.items() if k != 'status'}
m = Figcraft()
try:
    m.tool('open_file', {'path': str(native)})
    frames = json.loads((D / 'screen-manifest.json').read_text())
    changed = 0
    for f in frames:
        root = m.tool('get_node', {'id': f['id'], 'depth': 2})
        children = root['children']
        for c in sorted(children, key=lambda n: n['y']):
            if c['type'] != 'TEXT':
                continue
            text = c.get('characters')
            value = replace.get(text)
            if f['slug'] == 'project:secure-notes-organizer' and text == project['status']:
                value = new['status']
            if value is None:
                continue
            old_bottom = c['y'] + c['height']
            m.command('node.set', {'ids': [c['id']], 'characters': value})
            after = m.tool('get_node', {'id': c['id']})
            delta = after['height'] - c['height']
            if delta:
                for other in children:
                    if other['id'] != c['id'] and other['y'] >= old_bottom - .1:
                        other['y'] += delta
                        m.command('node.set', {'ids': [other['id']], 'y': other['y']})
                root['height'] += delta
                m.command('node.set', {'ids': [root['id']], 'height': root['height']})
            c.update(characters=value, height=after['height'])
            changed += 1
        f['height'] = root['height']
    m.tool('save_file', {'path': str(native)})
    m.save_log(D / 'secure-notes-affiliation-mcp-calls.json')
    (D / 'screen-manifest.json').write_text(json.dumps(frames, indent=2))
    project.update(new)
    project['affiliation'] = 'Siemens Digital Industries Software (DISW) internship final project'
    project['affiliationSource'] = 'User confirmation and public repository About: This is a repo to deliver Siemens Final Project.'
    (D / 'screen-content.json').write_text(json.dumps(data, indent=2))
    print('Siemens DISW internship affiliation updated in', changed, 'native text nodes.')
finally:
    m.close()
