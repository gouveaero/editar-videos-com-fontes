#!/usr/bin/env python3
"""Render the two approved benchmark components and compare six reference frames.

python3 regression.py --output /absolute/path/to/new/qa-folder
Writes only under --output. The benchmark and approved delivery stay read-only.
"""
import argparse
import copy
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageStat, ImageDraw
from video_pipeline import Project, SKILL, run, write, digest


def main(output):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    benchmark=SKILL/'assets/benchmark'
    config=json.loads((benchmark/'project.json').read_text())
    for c in config['components'].values():
        c['master']=str(benchmark/c['master']);c['captions']=str(benchmark/c['captions'])
    for a in config['assets'].values():a['file']=str(benchmark/a['file'])
    config['output']='build'
    manifest=output/'project.json';write(manifest,config)
    p=Project(manifest);p.render();technical=p.verify()
    built=json.loads((p.out/'build.json').read_text())['components'];results=[]
    sheet=Image.new('RGB',(1080,6*984),(25,25,25));draw=ImageDraw.Draw(sheet)
    for i,sample in enumerate(json.loads((benchmark/'samples.json').read_text())):
        actual=output/f'actual_{i}.png';golden=benchmark/sample['golden']
        run(['ffmpeg','-y','-v','error','-ss',sample['time'],'-i',Path(built[sample['component']]['folder'])/'render.mp4','-frames:v','1','-vf','scale=540:960',actual])
        expected=Image.open(golden).convert('RGB');observed=Image.open(actual).convert('RGB')
        # Tolerance allows minor codec rounding but catches layout/font/zoom drift.
        diff=ImageChops.difference(expected,observed);mae=sum(ImageStat.Stat(diff).mean)/3
        caption_diff=diff.crop((0,730,540,860));caption_mae=sum(ImageStat.Stat(caption_diff).mean)/3
        result=dict(sample,mean_absolute_error=round(mae,4),caption_error=round(caption_mae,4),ok=mae<=2 and caption_mae<=3)
        results.append(result)
        y=i*984;draw.text((6,y+5),f'{sample["component"]} {sample["time"]}s | approved left / reproduced right | MAE {mae:.3f}',fill='white')
        sheet.paste(expected,(0,y+24));sheet.paste(observed,(540,y+24))
    sheet.save(output/'comparison.jpg',quality=90)
    summary={'ok':all(r['ok'] for r in results),'technical':technical,'visual':results,
             'scope':'Two supplied-footage components, six approved frames. Editorial selection and other footage still require review.',
             'engine_sha256':digest(SKILL/'scripts/video_pipeline.py'),'style_sha256':digest(SKILL/'assets/style.json')}
    write(output/'regression.json',summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if not summary['ok']:raise SystemExit(1)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True)
    main(parser.parse_args().output)
