"""Resolve master once, verify exact bytes, and retain upstream rights evidence."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def download(url):
    with urlopen(Request(url, headers={"User-Agent": "ClubOps-Portfolio"}), timeout=40) as response:
        return response.read()


def main():
    config_path = ROOT / "configs/sources.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    commit = json.loads(download("https://api.github.com/repos/openfootball/football.json/commits/master"))["sha"]
    base = f"https://raw.githubusercontent.com/openfootball/football.json/{commit}"
    evidence = ROOT / "data/provenance"
    evidence.mkdir(parents=True, exist_ok=True)
    records = []
    for src in config["sources"]:
        url = f"{base}/{src['season']}/es.1.json"
        raw = download(url)
        local = ROOT / "data/raw" / f"{src['season']}.json"
        if local.read_bytes() != raw:
            raise ValueError(f"{src['season']}: pinned bytes differ; review before replacing snapshot")
        sha = hashlib.sha256(raw).hexdigest()
        records.append({"season": src["season"], "original_acquisition_url": src["url"],
                        "pinned_url": url, "sha256": sha, "bytes": len(raw)})
        src.update(url=url, sha256=sha)
    for name in ("README.md", "LICENSE.md"):
        (evidence / name).write_bytes(download(f"{base}/{name}"))
    manifest = {"verified_at_utc": datetime.now(timezone.utc).isoformat(), "commit": commit,
                "repository": config["source_repository"], "sources": records}
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
