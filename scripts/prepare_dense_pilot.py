"""Extract core-aligned dense frames for pilot016; no cloud calls, no detector.

Control (013/015 sparse): 6 frames spanning core +/-2s, so 2.4s apart across 12s.
This (016 dense):        6 frames spanning exactly the core window, so 1.6s apart across 8s.

The provider rejected 12-image requests in 013, so at a fixed 6-image budget density and
span are coupled: denser necessarily means narrower. That coupling is a provider constraint,
not a separable variable, and is declared in the plan rather than hidden.
Decode, resize and JPEG settings are copied from prepare_evidence_pilot.py so the only
difference from the control frames is which timestamps are sampled.
"""
from pathlib import Path
import hashlib, json
from datetime import datetime
import cv2
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evals/iterations/dense-pilot-016'
FRAMES = 6


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def now():
    return datetime.now().astimezone().isoformat()


def note(s):
    with (ROOT / 'evals/IMPLEMENTATION_NOTES.md').open('a') as f:
        f.write('\n### ' + now() + ' — dense pilot016 preparation\n\n' + s + '\n')


def encoded(im, path, edge=768):
    h, w = im.shape[:2]
    scale = min(1, edge / max(h, w))
    if scale < 1:
        im = cv2.resize(im, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
    if not cv2.imwrite(str(path), im, [cv2.IMWRITE_JPEG_QUALITY, 85]):
        raise RuntimeError('JPEG write failed')
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'width': im.shape[1], 'height': im.shape[0]}


def main():
    media = OUT / 'media'
    media.mkdir(parents=True, exist_ok=False)
    fixture = json.loads((ROOT / 'evals/experiments/all-events-v2/diagnostic-009.json').read_text())
    baseline = json.loads((ROOT / 'evals/iterations/evidence-pilot-013/prepared.json').read_text())
    if set(fixture['source_files']) != {'east-bay-elite-vs-spartans', 'unlimited-vs-campus'}:
        raise ValueError('Source allowlist')
    for game, path in fixture['source_files'].items():
        if sha(ROOT / path) != baseline['source_sha256'][game]:
            raise ValueError('Source changed since the control frames were cut')
    result = {'name': 'dense-pilot-016-preparation', 'started_at': now(), 'status': 'running',
              'sampling': 'six frames spanning exactly [core.start, core.end]; 1.6s apart across 8s',
              'control_sampling': 'six frames spanning [core.start-2, core.end+2]; 2.4s apart across 12s',
              'source_sha256': baseline['source_sha256'], 'frames_per_window': FRAMES, 'windows': []}
    for i, w in enumerate(fixture['windows']):
        cap = cv2.VideoCapture(str(ROOT / fixture['source_files'][w['game_id']]))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            raise ValueError('Invalid video FPS')
        entry = {'index': i, 'window': w, 'fps': fps, 'frames': []}
        for j in range(FRAMES):
            t = w['start'] + j * (w['end'] - w['start']) / (FRAMES - 1)
            frame_index = int(t * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, im = cap.read()
            if not ok:
                raise RuntimeError(f'Frame read failed at window {i} time {t}')
            entry['frames'].append(dict(encoded(im, media / f'w{i}-dense{j}.jpg'),
                                        time=t, actual_time=frame_index / fps, frame_index=frame_index, view='wide'))
        cap.release()
        spacing = entry['frames'][1]['time'] - entry['frames'][0]['time']
        entry['spacing_seconds'] = spacing
        result['windows'].append(entry)
        print(f"w{i} {w['game_id']} core {w['start']}-{w['end']} spacing {spacing:.2f}s "
              f"times {[round(f['time'],2) for f in entry['frames']]}", flush=True)
    result['status'] = 'completed'
    result['ended_at'] = now()
    (OUT / 'prepared.json').write_text(json.dumps(result, indent=2) + '\n')
    note('Cut ' + str(FRAMES * len(result['windows'])) + ' core-aligned dense frames for the8 frozen windows, '
         '768px longest edge, JPEG85, same decode/resize path as the013 control frames. Spacing1.6s across the8s core '
         'versus the control2.4s across12s including2s outer context either side. At the provider 6-image limit found '
         'in013, density and span cannot be varied independently; narrowing is the cost of density and is declared, '
         'not hidden. No cloud call, no detector, no reference label consulted. Sources verified unchanged against the '
         '013 preparation hashes. Third dataset untouched.')
    print(json.dumps({'status': result['status'], 'windows': len(result['windows']),
                      'frames': FRAMES * len(result['windows'])}))


if __name__ == '__main__':
    raise SystemExit(main())
