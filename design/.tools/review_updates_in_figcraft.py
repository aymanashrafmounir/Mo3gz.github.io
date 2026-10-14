"""Show the two requested sections in native Figcraft app tabs.

Attached MCP only. Reads the saved document; does not change design content.
"""
import base64
import json
import shutil
import sys
from pathlib import Path
from figcraft_mcp import Figcraft

D = Path(__file__).resolve().parents[1]
NATIVE = str(D / 'ayman-portfolio-v2.figcraft')


def descendants(n):
    yield n
    for c in n.get('children', []):
        yield from descendants(c)


port = int(sys.argv[1]) if len(sys.argv) > 1 else 47800
review = D / 'checkpoints/Timeline review.figcraft'
shutil.copy2(NATIVE, review)
m = Figcraft(attach_port=port, timeout=10)
record = {'backend': m.initialized.get('instructions', ''), 'views': []}
try:
    # Distinct review path keeps both camera views in separate tabs in one window.
    # Figcraft moves a document between windows when its exact path is reopened.
    initial = m.tool('inspect_document', {'depth': 1})
    empty = initial.get('path') is None and not initial.get('dirty') and all(not p.get('children') for p in initial.get('pages', []))
    m.tool('open_file', {'path': str(review)})
    if m.tool('inspect_document', {'depth': 0}).get('dirty'):
        raise RuntimeError('The review tab has unsaved edits; preserve them before reloading.')
    m.command('file.revert')
    m.command('file.rename', {'name': 'Timeline review'})
    m.tool('save_file', {'path': str(review)})
    timeline = m.tool('get_node', {'id': 1283, 'depth': 8})
    timeline_block = next(n for n in descendants(timeline) if n.get('name') == 'Experience timeline')
    assert sum(n.get('name', '').startswith('Timeline dates /') for n in descendants(timeline_block)) == 5
    m.tool('select', {'ids': [1283]})
    m.command('view.zoomAt', {'x': timeline['absoluteBounds']['x'] + 40, 'y': 120, 'width': 1200, 'height': 1280})
    ui = m.tool('inspect_ui')
    timeline_window = ui['window']
    screenshot = m.tool('screenshot', {'window': True, 'maxSize': 1800})
    for block in screenshot.get('content', []):
        if block.get('type') == 'image':
            (D / 'screens/figcraft-timeline-review.png').write_bytes(base64.b64decode(block['data']))
    record['views'].append({'section': 'Experience timeline', 'window': timeline_window, 'ui': ui})
    print('Timeline displayed in native window', timeline_window, flush=True)

    m.tool('open_file', {'path': NATIVE})
    document = m.tool('inspect_document', {'depth': 0})
    assert document.get('path') == NATIVE, document
    if document.get('dirty'):
        raise RuntimeError('The portfolio tab has unsaved edits; preserve them before reloading.')
    m.command('file.revert')
    home = m.tool('get_node', {'id': 41, 'depth': 6})
    titles = {n.get('characters') for n in descendants(home)}
    assert {'Helixtra', 'Wear Instant', 'BlitzChatbot', 'Secure Notes Organizer'} <= titles
    assert 'Arkedia' not in titles and 'Tapora' not in titles
    heading = next(n for n in home['children'] if n.get('characters') == 'Selected work')
    all_projects = next(n for n in home['children'] if n['type'] == 'INSTANCE' and any(c.get('characters') == 'All projects' for c in descendants(n)))
    m.tool('select', {'ids': [41]})
    m.tool('select', {'ids': []})
    bounds = {'x': home['absoluteBounds']['x'] + 48, 'y': heading['absoluteBounds']['y'] - 32,
              'width': 1344, 'height': all_projects['absoluteBounds']['y'] + all_projects['height'] - heading['absoluteBounds']['y'] + 64}
    m.command('view.zoomAt', bounds)
    ui = m.tool('inspect_ui')
    files = next(w['files'] for w in ui['windows'] if w['id'] == ui['window'])
    if empty and files == ['Untitled', 'Timeline review', 'Ayman Portfolio V2']:
        m.command('file.close', {'index': 0})
    ui = m.tool('inspect_ui')
    screenshot = m.tool('screenshot', {'window': True, 'maxSize': 1800})
    for block in screenshot.get('content', []):
        if block.get('type') == 'image':
            (D / 'screens/figcraft-selected-work-review.png').write_bytes(base64.b64decode(block['data']))
    record['views'].append({'section': 'Selected work', 'window': ui['window'], 'ui': ui})
    (D / 'updates-review-ui.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    m.save_log(D / 'updates-review-attached-mcp-calls.json')
    print(json.dumps({'displayed': [v['section'] for v in record['views']], 'windows': ui['windows'], 'active': ui['window'], 'status': ui['status']}), flush=True)
finally:
    m.close()
