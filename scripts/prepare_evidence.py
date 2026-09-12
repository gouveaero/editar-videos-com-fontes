#!/usr/bin/env python3
"""Crop a real screenshot and highlight selected lines without retyping them.

python3 prepare_evidence.py evidence.json
Requires Pillow. Paths resolve relative to the manifest, never the current cwd.
Coordinates [left, top, right, bottom] refer to the ORIGINAL screenshot.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw


def rectangle(value, bounds, label):
    if not isinstance(value, list) or len(value) != 4 or any(type(x) is not int for x in value):
        raise ValueError(f'{label}: expected four integer pixel coordinates')
    l, t, r, b = value
    bl, bt, br, bb = bounds
    if not (bl <= l < r <= br and bt <= t < b <= bb):
        raise ValueError(f'{label}: rectangle falls outside its bounds')
    return l, t, r, b


def prepare(manifest):
    manifest = Path(manifest).resolve()
    config = json.loads(manifest.read_text(encoding='utf-8'))
    for field in ('source_url', 'source_name', 'claim', 'excerpt', 'relation'):
        if not isinstance(config.get(field), str) or not config[field].strip():
            raise ValueError(f'Missing editorial metadata: {field}')
    source = (manifest.parent / config['screenshot']).resolve()
    output = (manifest.parent / config['output']).resolve()
    if output.suffix.lower() != '.png':
        raise ValueError('Output must be PNG')
    provenance = output.with_suffix('.provenance.json')
    if output in (source, manifest) or output.exists() or provenance.exists():
        raise ValueError('Choose a new output filename; existing files are preserved')
    with Image.open(source) as original:
        original = original.convert('RGB')
        crop = rectangle(config['crop'], (0, 0, *original.size), 'crop')
        lines = [rectangle(x, crop, 'highlight') for x in config.get('highlights', [])]
        result = original.crop(crop)
    # Multiply keeps dark glyphs legible while tinting the paper behind them.
    if lines:
        mask = Image.new('L', result.size, 0)
        draw = ImageDraw.Draw(mask)
        for l, t, r, b in lines:
            draw.rectangle((l-crop[0], t-crop[1], r-crop[0]-1, b-crop[1]-1), fill=150)
        tint = ImageChops.multiply(result, Image.new('RGB', result.size, (255, 233, 102)))
        result = Image.composite(tint, result, mask)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    record = dict(config, screenshot=str(source), output=str(output),
                  screenshot_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  output_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  output_size=list(result.size), text_redrawn=False)
    provenance.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    args = parser.parse_args()
    print(json.dumps(prepare(args.manifest), ensure_ascii=False, indent=2))
