import tempfile
import unittest
from pathlib import Path

from engine.scripts.component_manifest import (
    ManifestError,
    collect_component_selection,
)


class TestComponentManifest(unittest.TestCase):
    def test_collect_component_selection_filters_unlisted_components(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            components_dir = root / "components"
            components_dir.mkdir()

            for name in ["astronverse-a", "astronverse-b", "astronverse-demo"]:
                component_dir = components_dir / name
                component_dir.mkdir()
                (component_dir / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")

            manifest = components_dir / "manifest.toml"
            manifest.write_text(
                "[components]\ninclude = [\n  'astronverse-a',\n  'astronverse-b',\n]\n",
                encoding="utf-8",
            )

            selection = collect_component_selection(components_dir, manifest)

            self.assertEqual(selection.discovered, ["astronverse-a", "astronverse-b", "astronverse-demo"])
            self.assertEqual(selection.included, ["astronverse-a", "astronverse-b"])
            self.assertEqual(selection.ignored, ["astronverse-demo"])

    def test_collect_component_selection_rejects_unknown_manifest_components(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            components_dir = root / "components"
            components_dir.mkdir()

            component_dir = components_dir / "astronverse-a"
            component_dir.mkdir()
            (component_dir / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")

            manifest = components_dir / "manifest.toml"
            manifest.write_text(
                "[components]\ninclude = [\n  'astronverse-a',\n  'astronverse-missing',\n]\n",
                encoding="utf-8",
            )

            with self.assertRaises(ManifestError):
                collect_component_selection(components_dir, manifest)
