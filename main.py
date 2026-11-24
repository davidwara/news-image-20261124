#!/usr/bin/env python3
"""news-image-20261124 entrypoint.

Renders the front page and copies entry.png to $MAKEFUN_OUTPUT_DIR
(default /output), with a PNG magic + IEND sanity check.
Run:  python3 main.py
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import render  # noqa: E402


def main():
    out_path = render()
    with open(out_path, "rb") as fh:
        data = fh.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a valid PNG (bad magic)")
    if not data.endswith(b"IEND\xaeB`\x82"):
        raise SystemExit("entry.png is truncated (no IEND trailer)")
    if len(data) > 1024 * 1024:
        raise SystemExit("entry.png exceeds the 1 MiB cap: %d bytes" % len(data))
    from PIL import Image

    with Image.open(out_path) as im:
        if im.size != (1024, 1024) or im.mode != "RGB":
            raise SystemExit("entry.png must be 1024x1024 RGB, got %s %s"
                             % (im.size, im.mode))
    dest_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "entry.png")
    shutil.copyfile(out_path, dest)
    print("wrote %s (%d bytes)" % (dest, len(data)))


if __name__ == "__main__":
    main()
