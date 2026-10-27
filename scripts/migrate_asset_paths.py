"""仅为 app/public → public 的目录迁移重新绑定资产清单；拒绝规划语义或资产内容变化。"""
import argparse
import copy
import hashlib
import json
from pathlib import Path


def migrate(root, previous_planning):
    """全部校验成功后再写清单；保留原 MCP 制作记录与迁移前规划哈希。"""
    previous_raw = previous_planning.read_bytes()
    current_raw = (root / 'planning/project.json').read_bytes()
    previous = json.loads(previous_raw)
    current = json.loads(current_raw)
    expected = copy.deepcopy(previous)
    for spec in [expected['production'], expected['production']['city']]:
        for key in ['scene', 'grayScene']:
            old = spec['assets'][key]
            if not old.startswith('app/public/assets/'):
                raise ValueError('迁移源必须使用 app/public/assets 路径')
            spec['assets'][key] = old.removeprefix('app/')
    if current != expected:
        raise ValueError('规划不仅包含资产路径迁移，拒绝沿用旧模型')

    before = hashlib.sha256(previous_raw).hexdigest()
    after = hashlib.sha256(current_raw).hexdigest()
    runtime = json.loads((root / 'public/assets/runtime.json').read_text())
    if runtime['planningSha256'] != before:
        raise ValueError('迁移前运行配置与原规划不一致')

    outputs = {}
    pairs = [
        ('campus', 'assets/manifest.json', 'public/assets/build-info.json'),
        ('city', 'assets/city-manifest.json', 'public/assets/city-build-info.json'),
    ]
    for level, manifest_path, info_path in pairs:
        spec = current['production'] if level == 'campus' else current['production']['city']
        scene_path = spec['assets']['scene']
        asset = (root / scene_path).read_bytes()
        asset_hash = hashlib.sha256(asset).hexdigest()
        for name in [manifest_path, info_path]:
            document = json.loads((root / name).read_text())
            if (document['planningSha256'] != before
                    or document['assetSha256'] != asset_hash
                    or document['bytes'] != len(asset)):
                raise ValueError('原规划或模型哈希不匹配：' + name)
            for operation, digest in document.get('operations', {}).items():
                if hashlib.sha256((root / operation).read_bytes()).hexdigest() != digest:
                    raise ValueError('MCP 制作记录被改变：' + operation)
            files = {}
            for path, entry in document.get('files', {}).items():
                target = scene_path if path == 'app/' + scene_path else path
                data = (root / target).read_bytes()
                if hashlib.sha256(data).hexdigest() != entry['sha256'] or len(data) != entry['bytes']:
                    raise ValueError('制作资产内容改变：' + target)
                files[target] = entry
            if 'files' in document:
                document['files'] = files
            document['planningSha256'] = after
            document['layoutMigration'] = {
                'fromPlanningSha256': before,
                'toPlanningSha256': after,
                'fromScene': 'app/' + scene_path,
                'toScene': scene_path,
                'assetSha256': asset_hash,
                'scope': '仅调整仓库路径；模型内容和原 MCP 制作记录保持一致',
            }
            outputs[root / name] = document

    for path, document in outputs.items():
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n')
    return {'fromPlanningSha256': before, 'toPlanningSha256': after, 'manifests': len(outputs)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous-planning', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(migrate(args.root.resolve(), args.previous_planning), ensure_ascii=False))
