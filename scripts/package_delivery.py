"""核对新目录的核心源码与生产构建，生成带哈希清单的评审包；排除缓存和外部参考。"""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--rebuilt', type=Path, required=True)
parser.add_argument('--archive', type=Path, required=True)
args = parser.parse_args()
rebuilt = args.rebuilt.resolve()
archive = args.archive.resolve()
if archive.exists():
    raise SystemExit('交付包已存在，请使用新文件名。')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
source_paths = [root/'planning/project.json', *(root/'scripts').glob('*.py'), *(root/'assets/materials').glob('*.*'),
                *[root/name for name in ['package.json','package-lock.json','index.html','vite.config.js','jsconfig.json','.prettierrc.json']],
                *[p for directory in ['src','tests'] for p in (root/directory).rglob('*') if p.is_file()]]
comparisons = []
for path in source_paths:
    other = rebuilt / path.relative_to(root)
    comparisons.append({'path': str(path.relative_to(root)), 'kind': 'source', 'sha256': sha(path), 'identical': other.exists() and sha(path) == sha(other)})
for other in sorted((rebuilt / 'dist').rglob('*')):
    if not other.is_file():
        continue
    path = root / other.relative_to(rebuilt)
    comparisons.append({'path': str(path.relative_to(root)), 'kind': 'production', 'sha256': sha(other), 'identical': path.exists() and sha(path) == sha(other)})
if not all(item['identical'] for item in comparisons):
    print(json.dumps([item for item in comparisons if not item['identical']], ensure_ascii=False, indent=2))
    raise SystemExit('核心源码或生产构建与新输出目录不一致，请重新构建。')
excluded = {'work', 'node_modules', '__pycache__', '.git', 'references'}
files = [path for path in sorted(root.rglob('*')) if path.is_file() and not (set(path.relative_to(root).parts) & excluded)
         and path.name != 'delivery-manifest.json' and path.suffix != '.pyc' and path.name != '.DS_Store']
manifest = {'scope': '可运行评审版，非最终视觉验收', 'rebuiltRoot': str(rebuilt), 'coreComparisons': comparisons,
            'files': {str(path.relative_to(root)): {'sha256': sha(path), 'bytes': path.stat().st_size} for path in files},
            'excluded': sorted(excluded), 'extraOriginalDistAssets': [str(p.relative_to(root)) for p in (root / 'dist').rglob('*') if p.is_file() and not (rebuilt / p.relative_to(root)).exists()]}
manifest_path = root / 'delivery-manifest.json'
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
archive.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as out:
    for path in [*files, manifest_path]:
        out.write(path, 'gaoxin-digital-building/' + str(path.relative_to(root)))
print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size, 'sha256': sha(archive), 'files': len(files) + 1,
                  'coreAndProductionFilesCompared': len(comparisons)}, ensure_ascii=False, indent=2))
