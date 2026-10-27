"""验证目录迁移只能重新绑定内容一致的资产，不能掩盖规划或模型变化。"""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from migrate_asset_paths import migrate


class AssetPathMigrationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.previous = self.root / 'previous.json'
        self.plan = {'production': {'height': 24, 'assets': {
            'scene': 'app/public/assets/campus.glb',
            'grayScene': 'app/public/assets/campus-gray.glb',
        }, 'city': {'assets': {
            'scene': 'app/public/assets/city.glb',
            'grayScene': 'app/public/assets/city-gray.glb',
        }}}}
        self.write('previous.json', self.plan)
        self.old_hash = hashlib.sha256(self.previous.read_bytes()).hexdigest()
        current = copy.deepcopy(self.plan)
        for spec in [current['production'], current['production']['city']]:
            spec['assets'] = {k: v.removeprefix('app/') for k, v in spec['assets'].items()}
        self.write('planning/project.json', current)
        self.write('public/assets/runtime.json', {'planningSha256': self.old_hash})
        self.manifests = []
        for level, manifest, info in [
            ('campus', 'manifest', 'build-info'),
            ('city', 'city-manifest', 'city-build-info'),
        ]:
            data = level.encode()
            (self.root / f'public/assets/{level}.glb').write_bytes(data)
            digest = hashlib.sha256(data).hexdigest()
            document = {'planningSha256': self.old_hash, 'assetSha256': digest,
                        'bytes': len(data), 'operations': {}}
            self.write(f'public/assets/{info}.json', document)
            document['files'] = {f'app/public/assets/{level}.glb': {
                'sha256': digest, 'bytes': len(data),
            }}
            self.write(f'assets/{manifest}.json', document)
            self.manifests += [self.root / f'assets/{manifest}.json',
                               self.root / f'public/assets/{info}.json']
        self.before = {p: p.read_bytes() for p in self.manifests}

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    def assert_rejected_without_writes(self):
        with self.assertRaises(ValueError):
            migrate(self.root, self.previous)
        self.assertEqual(self.before, {p: p.read_bytes() for p in self.manifests})

    def test_path_only_migration_preserves_provenance_and_asset(self):
        result = migrate(self.root, self.previous)
        self.assertEqual(result['manifests'], 4)
        for path in self.manifests:
            after = json.loads(path.read_text())
            original = json.loads(self.before[path])
            self.assertEqual(after['assetSha256'], original['assetSha256'])
            self.assertEqual(after['layoutMigration']['fromPlanningSha256'], self.old_hash)
            self.assertEqual(after['planningSha256'], result['toPlanningSha256'])
            self.assertTrue(all(not name.startswith('app/') for name in after.get('files', {})))
        self.assertEqual((self.root / 'public/assets/campus.glb').read_bytes(), b'campus')

    def test_changed_planning_is_rejected(self):
        path = self.root / 'planning/project.json'
        current = json.loads(path.read_text())
        current['production']['height'] = 25
        self.write('planning/project.json', current)
        self.assert_rejected_without_writes()

    def test_changed_second_model_does_not_partially_write_first(self):
        (self.root / 'public/assets/city.glb').write_bytes(b'changed')
        self.assert_rejected_without_writes()

    def test_stale_runtime_is_rejected(self):
        self.write('public/assets/runtime.json', {'planningSha256': 'stale'})
        self.assert_rejected_without_writes()


if __name__ == '__main__':
    unittest.main()
