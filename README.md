# oscar-record

**The published record. One source, fetched the same way by every public surface.**

Do not edit `record.json`. It is generated.

- **Source of truth:** the vault, `00 Dashboard/record.md` (Oscar's call, Jul 17).
- **Publish:** `python3 publish.py`
- **Is it current?** `python3 publish.py --check` (exit 1 = the vault moved and nobody published)

## Why this exists

The registry had 38 initiatives. The portfolio had 20 projects and **zero** of the three
shipped that week, because adding one meant hand-typing into two `data.ts` files that had
already forked. Meanwhile the site rendered the sentence "everything i do flows into one
vault" from a hand-typed constant.

The record was single-source. Every *rendering* was a fork. This closes that.

## The split

| Layer | Lives | Rule |
|---|---|---|
| **Facts** (numbers, what exists, links, dates) | here | identical everywhere |
| **Form** (story, voice, colour, image, order, skin) | each site | distinct everywhere |

Prose stays in each site because prose interpolates the numbers. Flattening it here would
bake values back in and recreate the restatements the portfolio spent a whole pass killing.

## Guards (run at publish, so a bad record never reaches a site)

- ETH column must sum to `stats.totalEthWon`
- competed rows must equal `stats.hackathonCount`
- a price must carry its `as_of` (`prizes` needs `prizesAsOf`) — a price without one rots
- no duplicate slugs

All four are proven to fire, not assumed.

## Consuming it

```
curl -s https://raw.githubusercontent.com/Morkeeth/oscar-record/main/record.json
```

`_meta.sourceHash` identifies the exact vault body a build came from.
