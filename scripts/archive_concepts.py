"""归档内置生图的固定输入并记录哈希；禁止覆盖不同内容的同版本概念图。"""
import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('concept_id')
parser.add_argument('source', type=Path)
parser.add_argument('--request-file', default='design/concepts/generation-requests-v1.json')
parser.add_argument('--manifest-file', default='design/concepts/manifest-v1.json')
parser.add_argument('--asset-dir', default='design/concepts')
args = parser.parse_args()
requests = json.loads((ROOT / args.request_file).read_text())
request = next(x for x in requests if x['id'] == args.concept_id)
raw = args.source.read_bytes()
if raw[:8] != b'\x89PNG\r\n\x1a\n':
    raise SystemExit('只归档实际PNG图片，请先核对工具输出')
width, height = struct.unpack('>II', raw[16:24])
target = ROOT / args.asset_dir / (args.concept_id + '.png')
target.parent.mkdir(parents=True, exist_ok=True)
if target.exists() and target.read_bytes() != raw:
    raise SystemExit('同版本已存在不同图片，请使用新版本名')
if not target.exists():
    shutil.copy2(args.source, target)
manifest_path = ROOT / args.manifest_file
manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
manifest[args.concept_id] = {
    'path': str(target.relative_to(ROOT)),
    'sha256': hashlib.sha256(raw).hexdigest(),
    'actualPixelSize': [width, height],
    'targetViewport': json.loads((ROOT / 'planning/project.json').read_text())['project']['viewport'],
    'sourceOutput': str(args.source),
    'tool': request['tool'],
    'requestFile': args.request_file,
    'requestSha256': hashlib.sha256(json.dumps(request['arguments'], ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
    'planningSha256': hashlib.sha256((ROOT / 'planning/project.json').read_bytes()).hexdigest(),
    'userApproval': 'pending',
    'referenceInputs': [{'path': path, 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()} for path in request['arguments'].get('referenced_image_paths', [])]
}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(manifest[args.concept_id], ensure_ascii=False))
