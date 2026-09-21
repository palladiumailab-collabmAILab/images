"""Validate the repository's image manifest and stored image artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

MAX_ASSET_BYTES = 25 * 1024 * 1024
ASSET_ROOT = PurePosixPath("assets/files")
MEDIA_TYPES = {
    ".gif": "image/gif",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}
SECRET_PATTERNS = (
    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(rb"(?:AIza[0-9A-Za-z_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,})"),
    re.compile(rb"(?:github_pat_|xox[baprs]-|sk-)[A-Za-z0-9_-]{20,}"),
)


def _error(errors: list[str], message: str) -> None:
    errors.append(message)


def _read_manifest(manifest_path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        _error(errors, f"missing manifest: {manifest_path.as_posix()}")
        return {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _error(errors, f"invalid manifest {manifest_path.as_posix()}: {exc}")
        return {}

    if not isinstance(data, dict):
        _error(errors, "manifest root must be a JSON object")
        return {}
    return data


def _asset_files(root: Path, errors: list[str]) -> dict[str, Path]:
    asset_root = root / Path(*ASSET_ROOT.parts)
    if not asset_root.exists():
        return {}
    if not asset_root.is_dir():
        _error(errors, f"asset root is not a directory: {ASSET_ROOT.as_posix()}")
        return {}

    files: dict[str, Path] = {}
    for candidate in sorted(asset_root.rglob("*")):
        relative = candidate.relative_to(root).as_posix()
        if candidate.is_symlink():
            _error(errors, f"symlinks are not allowed: {relative}")
            continue
        if candidate.is_dir():
            continue
        if candidate.suffix.lower() not in MEDIA_TYPES:
            _error(errors, f"unsupported or forbidden asset file type: {relative}")
            continue
        files[relative] = candidate
    return files


def _manifest_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return None
    if len(path.parts) <= len(ASSET_ROOT.parts) or path.parts[: len(ASSET_ROOT.parts)] != ASSET_ROOT.parts:
        return None
    return path.as_posix()


def _contains_secret(data: bytes) -> bool:
    return any(pattern.search(data) for pattern in SECRET_PATTERNS)


def validate(root: Path) -> list[str]:
    """Return all contract violations found below ``root``."""

    root = root.resolve()
    errors: list[str] = []
    manifest_path = root / "assets" / "manifest.json"
    manifest = _read_manifest(manifest_path, errors)

    if manifest.get("schema_version") != 1:
        _error(errors, "manifest schema_version must be 1")
    if manifest.get("asset_root") != ASSET_ROOT.as_posix():
        _error(errors, f"manifest asset_root must be {ASSET_ROOT.as_posix()!r}")

    entries = manifest.get("assets")
    if not isinstance(entries, list):
        _error(errors, "manifest assets must be an array")
        entries = []

    actual_files = _asset_files(root, errors)
    declared_paths: set[str] = set()
    declared_hashes: dict[str, str] = {}

    for index, entry in enumerate(entries):
        prefix = f"manifest asset[{index}]"
        if not isinstance(entry, dict):
            _error(errors, f"{prefix} must be an object")
            continue

        path = _manifest_path(entry.get("path"))
        if path is None:
            _error(errors, f"{prefix}.path must be a safe path below {ASSET_ROOT.as_posix()}/")
            continue
        if path in declared_paths:
            _error(errors, f"duplicate manifest path: {path}")
        declared_paths.add(path)

        actual = actual_files.get(path)
        if actual is None:
            _error(errors, f"manifest path does not exist: {path}")
            continue

        expected_media_type = MEDIA_TYPES.get(actual.suffix.lower())
        if entry.get("media_type") != expected_media_type:
            _error(errors, f"{prefix}.media_type must be {expected_media_type!r} for {path}")

        for field in ("source", "license", "provenance"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                _error(errors, f"{prefix}.{field} must be a non-empty string")

        content = actual.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        size = actual.stat().st_size
        if size > MAX_ASSET_BYTES:
            _error(errors, f"asset exceeds {MAX_ASSET_BYTES} bytes: {path}")
        if entry.get("bytes") != size:
            _error(errors, f"{prefix}.bytes does not match {path}")
        if entry.get("sha256") != digest:
            _error(errors, f"{prefix}.sha256 does not match {path}")
        if digest in declared_hashes and declared_hashes[digest] != path:
            _error(errors, f"duplicate asset content: {declared_hashes[digest]} and {path}")
        declared_hashes[digest] = path

        if _contains_secret(content):
            _error(errors, f"possible secret or private key pattern in asset: {path}")

    for path in sorted(set(actual_files) - declared_paths):
        _error(errors, f"asset is not listed in manifest: {path}")

    try:
        manifest_bytes = manifest_path.read_bytes()
    except OSError:
        manifest_bytes = b""
    if _contains_secret(manifest_bytes):
        _error(errors, "possible secret or private key pattern in manifest")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: the parent of tools/)",
    )
    args = parser.parse_args(argv)
    errors = validate(args.root)
    if errors:
        print("Asset validation failed:", file=sys.stderr)
        for message in errors:
            print(f"- {message}", file=sys.stderr)
        return 1

    print("Asset validation passed: manifest and stored files are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
