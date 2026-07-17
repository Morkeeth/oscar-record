#!/usr/bin/env python3
"""
record-publish: vault (source)  ->  record.json (public, what sites fetch).

Oscar's call Jul 17: the vault is the source of truth, published to a repo. He named the
risk himself: "forget to publish = drift". So publishing is not the only job here.
`--check` exits 1 when the published record no longer matches the vault, which turns a
silent fork into a loud failure. Run it in CI, in /bonjour, wherever.

The record carries a sourceHash of the vault body. A consumer can prove what it built from.
"""
import sys, json, hashlib, pathlib, datetime
try:
    import yaml
except ImportError:
    sys.exit("pyyaml missing: pip3 install pyyaml")

VAULT = pathlib.Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian LIFE/00 Dashboard/record.md"
OUT   = pathlib.Path(__file__).parent / "record.json"

def load():
    raw = VAULT.read_text()
    # strip frontmatter + the prose header; the YAML body starts at the first top-level key
    idx = raw.find("\nstats:")
    if idx == -1:
        sys.exit("FAIL: no `stats:` block in the vault record. Did the file get reformatted?")
    body = raw[idx:]
    data = yaml.safe_load(body)
    return data, hashlib.sha256(body.encode()).hexdigest()[:16]

def guards(d):
    """The invariants that used to live in data.ts. They belong with the record, not with
    one renderer, or each site re-implements them and they drift (they already did)."""
    errs = []
    s, tl = d["stats"], d["timeline"]
    eth = round(sum(float(r["eth"]) for r in tl if str(r.get("eth","")).strip()), 2)
    want = float(str(s["totalEthWon"]).split()[0])
    if eth != want:
        errs.append(f"ETH drift: timeline sums to {eth} but stats.totalEthWon says {s['totalEthWon']}")
    competed = sum(1 for r in tl if r.get("competed") is not False)
    if competed != s["hackathonCount"]:
        errs.append(f"count drift: {competed} competed rows but stats.hackathonCount says {s['hackathonCount']}")
    for k in ("prizes",):
        if k in s and f"{k}AsOf" not in s:
            errs.append(f"{k} is a price with no {k}AsOf. A price without an as_of is a claim that rots.")
    slugs = [p["slug"] for p in d["projects"]]
    if len(slugs) != len(set(slugs)):
        errs.append("duplicate project slugs")
    return errs

def build():
    d, h = load()
    errs = guards(d)
    if errs:
        print("RECORD GUARDS FAILED:", file=sys.stderr)
        for e in errs: print("  -", e, file=sys.stderr)
        sys.exit(1)
    d["_meta"] = {"sourceHash": h, "generatedFrom": "vault:00 Dashboard/record.md"}
    return json.dumps(d, indent=2, ensure_ascii=False) + "\n"

if __name__ == "__main__":
    new = build()
    if "--check" in sys.argv:
        cur = OUT.read_text() if OUT.exists() else ""
        a = json.loads(new); b = json.loads(cur) if cur else {}
        if a.get("_meta",{}).get("sourceHash") != b.get("_meta",{}).get("sourceHash"):
            print(f"STALE: record.json does not match the vault.\n  vault  {a['_meta']['sourceHash']}\n  published {b.get('_meta',{}).get('sourceHash','(none)')}\n  fix: python3 publish.py", file=sys.stderr)
            sys.exit(1)
        print(f"record.json is current (sourceHash {a['_meta']['sourceHash']})")
    else:
        OUT.write_text(new)
        d = json.loads(new)
        print(f"published record.json  {len(d['projects'])} projects · {len(d['timeline'])} timeline · {len(d['stats'])} stats")
        print(f"  sourceHash {d['_meta']['sourceHash']}")
