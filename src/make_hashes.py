"""
Generate SHA-256 hashes for all data files. Writes data/SHA256SUMS in the
standard `sha256sum` format (compatible with `sha256sum -c`).

Usage:
    python ./src/make_hashes.py
"""

import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"


def sha256_hex(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    files = sorted(p for p in DATA.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No JSON files in {DATA}")

    out_path = DATA / "SHA256SUMS"
    lines = []
    print(f"Computing SHA-256 for {len(files)} files in {DATA}/")
    for path in files:
        digest = sha256_hex(path)
        # Standard format: "<hash>  <filename>" (two spaces, then relative name)
        lines.append(f"{digest}  {path.name}")
        print(f"  {path.name:<35} {digest}")

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print()
    print(f"Wrote: {out_path}")
    print()
    print("Verify with:")
    print("  cd data && sha256sum -c SHA256SUMS")
    print("  (POSIX; on Windows: certutil -hashfile <file> SHA256)")


if __name__ == "__main__":
    main()
