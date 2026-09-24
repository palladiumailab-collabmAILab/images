# Design

## Purpose

複数projectで利用する画像資産を、出所・権利・ハッシュ・来歴を伴う監査可能なcatalogとして管理する。

## Design principles

- **manifest-first。** assetそのものだけでなく、canonical manifestを管理対象とする。
- **provenance必須。** source、license/rights basis、生成由来を記録する。
- **content-addressable verification。** SHA-256とsizeで実体を検証する。
- **reviewed assets only。** 一時exportや由来不明の画像を混在させない。
- **repositoryを汎用blob storageにしない。** 大容量物や非画像payloadは別経路で扱う。

## Non-goals

application source、model weight、credential、任意download、未レビューtemporary exportの保管。

## Source of truth

machine-readable catalogは `assets/manifest.json`、field contractは `docs/asset-contract.md` を正本とする。
