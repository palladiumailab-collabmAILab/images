import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.validate_assets import validate


class ValidateAssetsBoundaryTests(unittest.TestCase):
    def _write_manifest(self, root: Path, assets: list[dict[str, object]]) -> None:
        path = root / "assets" / "manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"schema_version": 1, "asset_root": "assets/files", "assets": assets}),
            encoding="utf-8",
        )

    def test_rejects_path_traversal_in_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_manifest(
                root,
                [{
                    "path": "assets/files/../escape.png",
                    "sha256": "0" * 64,
                    "bytes": 0,
                    "media_type": "image/png",
                    "source": "fixture",
                    "license": "fixture",
                    "provenance": "fixture",
                }],
            )
            errors = validate(root)
            self.assertTrue(any(".path must be a safe path" in error for error in errors))

    def test_duplicate_content_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b"same"
            files = root / "assets" / "files"
            files.mkdir(parents=True)
            entries = []
            for name in ("a.png", "b.png"):
                path = files / name
                path.write_bytes(payload)
                entries.append({
                    "path": f"assets/files/{name}",
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "bytes": len(payload),
                    "media_type": "image/png",
                    "source": "fixture",
                    "license": "fixture",
                    "provenance": "fixture",
                })
            self._write_manifest(root, entries)
            errors = validate(root)
            self.assertTrue(any("duplicate asset content" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
