# Image asset contract

`assets/manifest.json` is the source of truth for every file under `assets/files/`.

The top-level object is:

```json
{
  "schema_version": 1,
  "asset_root": "assets/files",
  "assets": []
}
```

Each entry in `assets` must contain:

| Field | Contract |
| --- | --- |
| `path` | Repository-relative POSIX path below `assets/files/`; no absolute path or `..`. |
| `sha256` | Lowercase SHA-256 digest of the exact file bytes. |
| `bytes` | Exact non-negative byte count. |
| `media_type` | One of `image/png`, `image/jpeg`, `image/webp`, `image/gif`, or `image/svg+xml`, matching the extension. |
| `source` | Non-empty source URL, collection identifier, or an explicit description such as `generated`. |
| `license` | Non-empty license or rights basis, such as `CC-BY-4.0`, `CC0-1.0`, or `internal-original`. |
| `provenance` | Non-empty description of acquisition or generation, including the tool/model and reference needed for review when applicable. |

The validator enforces these rules:

- Every image file is listed exactly once; every listed file exists.
- Duplicate paths and duplicate SHA-256 content are rejected.
- Files over 25 MiB, unsupported extensions, symlinks, and non-image payloads are rejected.
- Common credential/private-key patterns are rejected from asset bytes and the manifest.
- The empty `assets` list is valid when no approved images are present.

Direct Git storage is limited to the formats and size above. Introducing another storage backend requires a contract change, validator support, and a documented immutable locator plus hash for each externally stored artifact.
