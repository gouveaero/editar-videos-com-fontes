#!/usr/bin/env python3
"""Package verified exports, publication caption and editable compositions.

python3 package_project.py project.json --caption post.txt --review review.json
Review is a record of work actually performed, not a user approval requirement.
"""
import argparse
import copy
import html
import json
import zipfile
from pathlib import Path
from video_pipeline import Project, run, write, digest


def package(manifest,caption,review):
    data=json.loads(Path(manifest).read_text())
    enhanced='editorial' in data or any(any(k in c for k in ('scenes','framing','sfx','music_duck','caption_highlights')) for c in data['components'].values())
    if enhanced:
        from editorial_pipeline import EditorialProject
        p=EditorialProject(manifest)
    else:p=Project(manifest)
    p.verify()
    entries=json.loads((p.out/'delivery.json').read_text())
    reviews=json.loads(Path(review).read_text())
    for e in entries:
        r=next((r for r in reviews if r.get('id')==e['id']),None)
        if not r or any(not r.get(k) for k in ('speech_note','visual_note','evidence_note','checked_frames')):
            raise ValueError(f'{e["id"]}: missing documented editorial review')
        for f in r['checked_frames']:
            if not (Path(review).resolve().parent/f).is_file():raise ValueError('A reviewed frame file is missing')
    caption=Path(caption).read_text().strip()
    if not caption:raise ValueError('Publication caption is empty')
    write(p.out/'LEGENDA_PARA_PUBLICAR.txt',caption+'\n')
    cards=[]
    for e in entries:
        name=e['id'];poster=p.out/'versions'/f'{name}.jpg'
        run(['ffmpeg','-y','-v','error','-ss',min(1.5,e['duration']/2),'-i',e['file'],'-frames:v','1','-vf','scale=540:960',poster])
        title=html.escape(e.get('title',name));d=round(e['duration'])
        cards.append(f'<article><h2>{title}</h2><p>{d//60}:{d%60:02}</p><video controls playsinline preload="none" poster="versions/{name}.jpg" src="versions/{name}.mp4"></video><p><a href="versions/{name}.mp4" download>MP4</a> · <a href="versions/{name}.srt" download>SRT</a></p></article>')
    doc=f'<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Vídeos para teste</title><style>body{{background:#101d22;color:#f5f5e8;font:16px Arial;margin:0;padding:30px}}main{{max-width:1200px;margin:auto}}section{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px}}article{{background:#1b2c31;padding:18px;border-radius:16px}}video{{width:100%;aspect-ratio:9/16}}a{{color:#d5e995}}pre{{white-space:pre-wrap;font:inherit;max-width:780px;line-height:1.5}}</style><main><h1>Vídeos para teste</h1><p><a href="delivery.zip" download>Baixar pacote completo</a> · <a href="LEGENDA_PARA_PUBLICAR.txt" download>Legenda para publicar</a></p><details><summary>Ver legenda</summary><pre>{html.escape(caption)}</pre></details><section>{"".join(cards)}</section></main><script>const vs=[...document.querySelectorAll("video")];vs.forEach(v=>v.addEventListener("play",()=>vs.forEach(o=>{{if(o!==v)o.pause()}})));</script></html>'
    write(p.out/'assistir.html',doc)
    built=json.loads((p.out/'build.json').read_text())['components']
    portable=copy.deepcopy(p.data);portable['output']='build';portable.pop('sources',None);portable.pop('music',None)
    portable['style']=p.style;asset_locations={}
    archive=p.out/'delivery.zip';temp=p.out/'delivery.tmp.zip'
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_STORED) as z:
        for e in entries:
            for ext in ('mp4','srt','captions.json','jpg'):z.write(p.out/'versions'/f'{e["id"]}.{ext}',f'versions/{e["id"]}.{ext}')
        for name,item in built.items():
            folder=Path(item['folder']);prefix=f'project/components/{name}'
            for f in folder.rglob('*'):
                if f.is_file() and (f.parent.name=='assets' or f.name in ('index.html','captions.json','evidence_timeline.json','editorial_timeline.json')):
                    z.write(f,f'{prefix}/{f.relative_to(folder)}')
            c=portable['components'][name];c.pop('cuts',None);c['master']=f'components/{name}/assets/speaker.mp4';c['captions']=f'components/{name}/captions.json'
            for event in p.events(name):asset_locations[event['asset']]=f'components/{name}/assets/{event["asset"]}{Path(event["file"]).suffix.lower()}'
        portable['assets']={k:dict(p.assets[k],file=loc) for k,loc in asset_locations.items()}
        if p.data.get('music'):
            music=p.data['music'];source=p.path(music['file']);loc='audio/music'+source.suffix;z.write(source,'project/'+loc);portable['music']=dict(music,file=loc)
        if enhanced:
            from video_pipeline import SKILL
            # Original sources, editable models, bundled fonts/licenses and runtime travel
            # together. No dependency on the previous project or another skill remains.
            for key,asset in p.assets.items():
                if key not in asset_locations:
                    source=p.path(asset['file']);loc=f'media/{key}{source.suffix}'
                    z.write(source,'project/'+loc);portable['assets'][key]=dict(asset,file=loc)
            for key,source in portable.get('editorial',{}).get('sounds',{}).items():
                original=p.path(source['file']);loc=f'audio/{key}{original.suffix}';z.write(original,'project/'+loc);source['file']=loc
            for name,c in portable['components'].items():
                for i,s in enumerate(c.get('scenes',[])):
                    if s['type']=='chronology':
                        for j,event in enumerate(s['events']):
                            source=p.path(event['document']['href']);loc=f'documents/{name}-{i}-{j}{source.suffix}';z.write(source,'project/'+loc);event['document']['href']=loc
            for folder in ('scripts','assets'):
                for source in (SKILL/folder).rglob('*'):
                    if source.is_file() and '__pycache__' not in source.parts and 'benchmark' not in source.parts:
                        z.write(source,'project/skill/'+str(source.relative_to(SKILL)))
            for source in (p.out/'audio').glob('*.wav'):z.write(source,'project/stems/'+source.name)
            portable['style'].pop('editorial_receipt',None)
            for name in ('retime.json','edit_plan.json','CREDITS.md'):
                source=p.root/name
                if source.exists():z.write(source,name)
        z.writestr('project/project.json',json.dumps(portable,ensure_ascii=False,indent=2))
        z.writestr('FONTES.json',json.dumps(p.assets,ensure_ascii=False,indent=2))
        z.writestr('assistir.html',doc.replace('<a href="delivery.zip" download>Baixar pacote completo</a> · ',''))
        for f in ('LEGENDA_PARA_PUBLICAR.txt','technical_qa.json'):z.write(p.out/f,f)
        z.writestr('REVISAO.json',json.dumps(reviews,ensure_ascii=False,indent=2))
        z.writestr('COMECAR_AQUI.txt',('Reconstruir: python3 project/skill/scripts/editorial_pipeline.py render project/project.json. Requer Python/Pillow, FFmpeg, Node/npm; HyperFrames 0.8.33. Fontes, modelos e sons locais incluídos.\n' if enhanced else '')+'Abra assistir.html. MP4 já contém legenda; SRT é opcional. project/components contém composições HyperFrames editáveis e mídia. Para remontar por JSON, use video_pipeline.py da skill editar-videos-com-fontes com project/project.json.\n')
    with zipfile.ZipFile(temp) as z:
        if z.testzip() is not None:raise ValueError('Package failed CRC verification')
    temp.replace(archive);write(p.out/'package.json',{'file':str(archive),'sha256':digest(archive),'bytes':archive.stat().st_size})
    return archive


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('manifest');parser.add_argument('--caption',required=True);parser.add_argument('--review',required=True)
    a=parser.parse_args();print(package(a.manifest,a.caption,a.review))
