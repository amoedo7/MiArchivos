#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import os
from pathlib import Path

SCHEMA = "desarrollamo.miarchivos.v1"


def sha256_file(path: Path, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            data = f.read(chunk)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def scan(root: Path, top: int, max_files: int, duplicates: bool) -> dict:
    extension_bytes = collections.Counter()
    extension_files = collections.Counter()
    largest: list[tuple[int, str]] = []
    files = 0
    directories = 0
    total_bytes = 0
    errors = 0
    candidates: dict[int, list[Path]] = collections.defaultdict(list)
    truncated = False

    for current, dirs, names in os.walk(root, followlinks=False):
        directories += len(dirs)
        for name in names:
            if files >= max_files:
                truncated = True
                break
            path = Path(current) / name
            try:
                if path.is_symlink() or not path.is_file():
                    continue
                size = path.stat().st_size
            except Exception:
                errors += 1
                continue
            files += 1
            total_bytes += size
            ext = path.suffix.lower() or "(sin extensión)"
            extension_files[ext] += 1
            extension_bytes[ext] += size
            largest.append((size, str(path.relative_to(root))))
            if duplicates and size > 0:
                candidates[size].append(path)
        if truncated:
            break

    largest.sort(reverse=True)
    largest_json = [{"path": p, "bytes": s} for s, p in largest[:top]]
    extensions = [
        {"extension": ext, "files": extension_files[ext], "bytes": size}
        for ext, size in extension_bytes.most_common()
    ]

    dup_groups = []
    if duplicates:
        for size, group in candidates.items():
            if len(group) < 2:
                continue
            by_hash: dict[str, list[str]] = collections.defaultdict(list)
            for path in group:
                try:
                    by_hash[sha256_file(path)].append(str(path.relative_to(root)))
                except Exception:
                    errors += 1
            for digest, paths in by_hash.items():
                if len(paths) > 1:
                    dup_groups.append({"sha256": digest, "bytes_each": size, "files": paths, "potential_savings_bytes": size * (len(paths) - 1)})
        dup_groups.sort(key=lambda x: x["potential_savings_bytes"], reverse=True)

    return {
        "schema": SCHEMA,
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "root": str(root.resolve()),
        "privacy": {"files_uploaded": False, "files_modified": False, "symlinks_followed": False},
        "summary": {
            "files": files,
            "directories": directories,
            "total_bytes": total_bytes,
            "read_errors": errors,
            "truncated": truncated,
            "max_files": max_files,
        },
        "largest_files": largest_json,
        "extensions": extensions,
        "duplicates": {"enabled": duplicates, "groups": dup_groups if duplicates else []},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="MiArchivos: análisis local y de sólo lectura")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--max-files", type=int, default=100000)
    parser.add_argument("--duplicates", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    root = Path(args.path).expanduser()
    if not root.exists() or not root.is_dir():
        parser.error("la ruta debe ser una carpeta existente")
    report = scan(root, max(1, args.top), max(1, args.max_files), args.duplicates)
    text = json.dumps(report, ensure_ascii=False, indent=None if args.compact else 2)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
