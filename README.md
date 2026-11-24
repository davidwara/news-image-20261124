# THE WORLD IN ONE DAY — Tuesday 24 November 2026

Entry for the make.fun daily competition
[**news-image-20261124**](https://make.fun/competitions/news-image-20261124)
— "Sum up 24 November's world news in one image". $100 in USDC, 50 places paid.

## What the image is

A dense 1024×1024 newspaper front page covering **36 real stories** from
Tuesday 24 November 2026, every one dated and sourced:

- 3 large lead stories with custom code-drawn illustrations (Nvidia
  reinstates Jensen Huang; COP31 collapses with no deal; NATO sends AWACS
  jets to Poland)
- 12 more stories (4–15), each with a small code-drawn pictogram
- A "WHERE IT HAPPENED" world map with 15 numbered pins and a pin key
- A region colour bar (Europe 12, Americas 9, Asia-Pacific 8,
  Middle East 6, Africa 1)
- "THE DAY IN UTC" timeline of the day's key moments
- A KPI number strip (Nvidia +33%, Nasdaq +6%, 258 House seats,
  24 dead in Banten, 46 COP31 decisions, 12,000 evacuated in Manchester)
- "ALSO ON TUESDAY 24 NOVEMBER — 21 MORE STORIES" numbered list
- A "DATE CHECK" box explaining what was left out and why, plus a
  "CERTAINTY: REPORTED / CLAIM / FORECAST" legend and a sources line

No stock photos and no external images: every illustration, the map and
every chart are drawn in code by the renderer.

## How to run

```sh
python3 main.py
```

This renders `entry.png` (1024×1024 RGB PNG, under 1 MiB) and copies it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`), after a PNG magic,
IEND trailer, size and dimension sanity check.

Requirements: Python 3.12+ with Pillow (`pip install pillow`). Rendering is
fully deterministic — two runs produce byte-identical output.

## Files

- `main.py` — entrypoint: renders and exports `entry.png`
- `render.py` — the whole front page: story data, icons, map, layout

## Sources

Reuters, CNN, AP, BBC, Dow Jones, The Times, Times of India, France 24,
Computer Weekly. Stories first reported 22–24 November 2026; events from
earlier days are named only in the DATE CHECK box.

## License

MIT — see `LICENSE`.
