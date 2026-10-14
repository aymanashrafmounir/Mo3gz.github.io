"""Install the user-approved AI-edited Blitz demo into the native design.

The original empty chat capture, exact prompt, and capture provenance are kept
in the repository. The edited preview is explicitly classified as fictional.
"""
import hashlib
import json
from pathlib import Path

from refine_native import Refine, walk

D = Path(__file__).resolve().parents[1]
ROOT = D.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    image = D / 'assets/captures/blitzchatbot-demo.png'
    base = D / 'assets/source/blitzchatbot-blank-base.png'
    assert image.is_file() and base.is_file()
    provenance = {
        'classification': 'ai-edited-application-demo',
        'project': 'blitzchatbot',
        'approvedAt': '2026-10-14',
        'approval': 'User approved the generated fictional chat and contacts preview for use in the final design.',
        'tool': 'built-in image_gen__imagegen',
        'image': {'path': image.relative_to(ROOT).as_posix(), 'sha256': digest(image)},
        'originalBase': {'path': base.relative_to(ROOT).as_posix(), 'sha256': digest(base)},
        'prompt': 'design/provenance/blitzchatbot/imagegen-prompt-v1.txt',
        'baseCaptureProvenance': 'design/provenance/blitzchatbot/blank-capture-provenance.json',
        'sourceProvenance': 'design/provenance/blitzchatbot/source-provenance.json',
        'captureHarness': 'design/provenance/blitzchatbot/capture.cjs',
        'sourceGitCommit': '09b4368b422752b62e48fcbc9de3bb9f38bb07a0',
        'data': 'Six fictional Arabic first names and a fictional generic exchange. No real account, phone number, contact or message records were supplied.',
        'disclosure': 'The image includes the Arabic label بيانات تجريبية; native case-study caption also identifies an AI-edited demo.',
        'limits': 'This is an image-generator edit of an original empty app interface, not a genuine populated application capture or evidence of delivered messages.',
    }
    (D / 'provenance/blitzchatbot/approved-demo.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')

    data = json.loads((D / 'screen-content.json').read_text())
    project = next(p for p in data['projects'] if p['slug'] == 'blitzchatbot')
    project.update(capture='blitzchatbot-demo', caption='AI-edited preview with fictional contacts and chat.',
                   mediaClassification=provenance['classification'],
                   mediaProvenance='design/provenance/blitzchatbot/approved-demo.json')
    (D / 'screen-content.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
    captures = json.loads((D / 'capture-manifest.json').read_text())
    capture = next(c for c in captures if c['project'] == 'blitzchatbot')
    capture.update(path=image.relative_to(ROOT).as_posix(), sha256=digest(image),
                   classification=provenance['classification'], observed='2026-10-14',
                   source='design/assets/source/blitzchatbot-blank-base.png',
                   sourceCommit=provenance['sourceGitCommit'], caption=project['caption'],
                   provenance='design/provenance/blitzchatbot/approved-demo.json',
                   use='User approved for the final portfolio design and implementation on 2026-10-14.',
                   framing='Complete approved image; fit without zoom or crop.',
                   captureDetails=provenance['limits'])
    (D / 'capture-manifest.json').write_text(json.dumps(captures, indent=2), encoding='utf-8')

    r = Refine(data)
    try:
        wrappers = [n for n in r.nodes.values() if n.get('name') in
                    ['Genuine public capture / blitzchatbot', 'AI-edited demo / blitzchatbot']]
        assert len(wrappers) == 12, len(wrappers)
        for wrapper in wrappers:
            r.replace_capture(wrapper, image)
            r.set(wrapper, name='AI-edited demo / blitzchatbot')
        links = []
        for frame in r.frames:
            if frame['slug'] != 'project:blitzchatbot':
                continue
            node = r.nodes[frame['id']]
            target = next(c for c in node['children'] if c.get('name') in
                          ['Open original full-size screenshot', 'Open approved full-size demo'])
            r.set(target, name='Open approved full-size demo')
            label = next(c for c in target['children'] if c['type'] == 'TEXT')
            r.set(label, characters='AI-edited demo · View full-size ↗', name='AI-edited demo · View full-size')
            r.m.command('proto.interaction.set', {'id': target['id'], 'index': 0,
                         'action': {'type': 'openUrl', 'url': image.as_uri()}})
            links.append(target['id'])
        r.finish()
        r.m.save_log(D / 'blitz-approved-demo-mcp-calls.json')
        print(json.dumps({'nativeSaved': True, 'imageWrappersReplaced': len(wrappers),
                          'captionLinksUpdated': links, 'approvedImageSha256': digest(image)}))
    finally:
        r.m.close()


if __name__ == '__main__':
    main()
