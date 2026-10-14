"""Narrow native correction: six explicit, accessible full-size image links."""
import json
from pathlib import Path
from refine_native import Refine, walk
from secure_notes_application import full_size_caption

D = Path(__file__).resolve().parents[1]


def main():
    data = json.loads((D / 'screen-content.json').read_text(encoding='utf-8'))
    project = next(p for p in data['projects'] if p['slug'] == 'secure-notes-organizer')
    r = Refine(data)
    count = 0
    try:
        for frame in r.frames:
            if frame['slug'] != 'project:secure-notes-organizer':
                continue
            root = r.nodes[frame['id']]
            for prefix, stem, label in [
                ('Notes editor', project['capture'], 'Notes editor'),
                ('Sign-in screen', project['gallery'][0], 'Sign-in screen'),
            ]:
                caption = next(n for n in root['children']
                               if n.get('type') == 'TEXT' and n.get('characters', '').startswith(prefix))
                full_size_caption(r, root['id'], stem, label, caption['x'], caption['y'],
                                  caption['width'], caption['fontSize'])
                r.m.command('edit.delete', {'ids': [caption['id']]})
                count += 1
        assert count == 6, count
        r.m.tool('save_file', {'path': str(D / 'ayman-portfolio-v2.figcraft')})
        tree = r.m.tool('inspect_document', {'depth': 20, 'allPages': True})
        nodes = {n['id']: n for page in tree['pages'] for n in walk(page)}
        for frame in r.frames:
            frame['height'] = nodes[frame['id']]['height']
        (D / 'native-document-inspection.json').write_text(json.dumps(tree, indent=2), encoding='utf-8')
        (D / 'screen-manifest.json').write_text(json.dumps(r.frames, indent=2), encoding='utf-8')
        (D / 'screen-inspection.json').write_text(json.dumps(
            [{'frame': f, 'node': nodes[f['id']]} for f in r.frames], indent=2), encoding='utf-8')
        r.m.save_log(D / 'secure-notes-caption-links-mcp-calls.json')
        print('Native file saved: six 44px full-size caption links; manifest/inspection refreshed. No exports or QA run.')
    finally:
        r.m.close()


if __name__ == '__main__':
    main()
