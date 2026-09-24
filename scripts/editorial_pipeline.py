#!/usr/bin/env python3
"""Self-contained editorial layer over the stable talking-head pipeline.
python3 editorial_pipeline.py {validate,masters,build,render,verify} project.json
"""
import argparse
import copy
import html
import json
import math
import re
import shutil
from pathlib import Path
from PIL import Image
from video_pipeline import Project, SKILL, run, write, digest
from editorial_scenes import scene, js
from sound_design import make_stem

LIB=SKILL/'assets/editorial'
DEMOS={'prototype','pendulum','chronology'}
TYPES=DEMOS|{'image','evidence','title','word','connections','bar'}


def overlaps(a,b):
    return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]


def box(value):
    if len(value)!=4 or any(not isinstance(x,(int,float)) or not math.isfinite(x) for x in value) or not 0<=value[0]<value[2]<=1080 or not 0<=value[1]<value[3]<=1920:
        raise ValueError('Rectangle must be [left, top, right, bottom] inside 1080x1920')
    return value


class EditorialProject(Project):
    def face(self,name):
        c=self.components[name];f=c.get('framing',{})
        if f.get('measured_face_bounds'):return box(f['measured_face_bounds'])
        if not c.get('face_bounds'):return None
        z=f.get('scale',1);ox,oy=f.get('origin',[.5,.5]);ox*=1080;oy*=1920
        x1,y1,x2,y2=c['face_bounds'];dy=c.get('shift_y',0)
        return [ox+(x1-ox)*z,oy+(y1-oy)*z+dy,ox+(x2-ox)*z,oy+(y2-oy)*z+dy]

    def scene_rect(self,s):
        full=s['type'] in DEMOS or s.get('mode','full' if s['type']=='image' else 'overlay')=='full'
        return [0,0,1080,1920] if full else s.get('rect',[60,250,1020,560])

    def validate(self,media=True):
        issues=super().validate(media);sounds=self.data.get('editorial',{}).get('sounds',{})
        for key,source in sounds.items():
            if not re.fullmatch(r'[\w-]+',key):raise ValueError('Invalid sound ID')
            if not self.path(source['file']).is_file() or not source.get('source') or not source.get('license'):raise ValueError('Sound requires local file, source and license (unknown permitted, never invented)')
            if not -60<=source.get('peak_dbfs',-27)<=-12 or not .01<=source.get('duration',.3)<=10 or source.get('trim_in',0)<0:raise ValueError('Invalid sound fragment/gain')
        for key,value in self.data.get('editorial',{}).get('palette',{}).items():
            if key not in {'ink','paper','muted','gold','accent'} or not re.fullmatch(r'#[a-fA-F0-9]{6}',value):raise ValueError('Invalid palette token')
        for name,c in self.components.items():
            for duck in c.get('music_duck',[]):
                if not 0<=duck['start']<duck['end']<=self.duration(name) or not 0<=duck['gain']<=1:raise ValueError('Invalid music duck interval')
            f=c.get('framing',{});z=f.get('scale',1);origin=f.get('origin',[.5,.5])
            if not 1<=z<=2.5 or len(origin)!=2 or any(not 0<=v<=1 for v in origin):raise ValueError('Framing requires scale 1..2.5 and normalized origin')
            face=self.face(name)
            if face:
                box(face)
                if face[3]+24>self.style['caption']['top']:raise ValueError(f'{name}: reframed beard overlaps subtitles')
            elif f:issues.append(f'{name}: zoom requires measured frame inspection')
            previous=0
            for s in c.get('scenes',[]):
                kind=s['type'];a,b=s['start'],s['end'];duration=b-a
                if kind not in TYPES or not 0<=a<b<=self.duration(name)+.001 or a<previous:raise ValueError('Invalid or overlapping editorial scenes')
                previous=b;r=box(self.scene_rect(s));full=r==[0,0,1080,1920]
                if not full:
                    if r[1]<250 or r[3]>self.style['caption']['top']-24:raise ValueError('Scene violates title/caption safe area')
                    if face and overlaps(r,face):raise ValueError(f'{name}: scene covers reframed face; reposition it')
                if kind in ('image','evidence'):
                    asset=self.assets[s['asset']]
                    if not asset.get('source_name') or not asset.get('source_url') or not asset.get('kind'):raise ValueError('Image provenance required')
                    if kind=='evidence' and (asset['kind']!='screenshot' or not s.get('claim') or not s.get('relation')):raise ValueError('Evidence requires actual screenshot, claim and relation')
                    if s.get('mode') not in (None,'full','overlay'):raise ValueError('Image mode must be full or overlay')
                    if asset.get('text_height_px'):
                        with Image.open(self.path(asset['file'])) as im:w,h=im.size
                        rw,rh=(970,1060) if full else (r[2]-r[0],r[3]-r[1])
                        if asset['text_height_px']*min(rw/w,rh/h)<24:raise ValueError('Evidence text too small; crop the actual source')
                if kind=='connections' and (len(s['labels'])!=3 or any(len(x)>17 for x in s['labels'])):raise ValueError('Connections need three concise labels')
                if kind=='bar' and (not 0<=s['value']<=s['reference'] or s['reference']<=0 or not s.get('reference_label')):raise ValueError('Bar requires value, positive reference and reference label')
                if kind in DEMOS:
                    if 'demo_crop' not in c:raise ValueError('Measure and declare demo_crop before using a presenter window')
                    crop=box(c.get('demo_crop',[90,440,990,1470]))
                    raw=c.get('face_bounds')
                    if raw and not (crop[0]<=raw[0] and crop[1]<=raw[1] and crop[2]>=raw[2] and crop[3]>=raw[3]):raise ValueError('Presenter window crops measured face')
                if kind in ('prototype','chronology'):
                    states=s['states' if kind=='prototype' else 'events'];ids=[e['id'] for e in states]
                    if not states or len(ids)!=len(set(ids)) or states[0]['at']!=0 or any(not 0<=e['at']<duration for e in states) or [e['at'] for e in states]!=sorted(e['at'] for e in states):raise ValueError('States need unique IDs and ordered local times starting at zero')
                    if kind=='prototype' and any(e.get('next') and e['next'] not in ids for e in states):raise ValueError('Prototype navigation points to unknown state')
                    if kind=='chronology':
                        for e in states:
                            d=e['document'];href=d['href']
                            if not d.get('title') or not d.get('body') or not href:raise ValueError('Every event needs an actual linked document')
                            if re.match(r'^[a-zA-Z]+:',href):raise ValueError('Illustrative document must be a local fixture')
                            if not self.path(href).is_file():raise ValueError('Linked illustrative document missing')
                if kind=='pendulum':
                    phy=s.get('physics',{})
                    if not 0<=phy.get('change_at',duration/2)<duration or min(phy.get('length_from',1),phy.get('length_to',2),phy.get('gravity',9.81),phy.get('clock_rate',1))<=0:raise ValueError('Invalid pendulum model')
            for e in c.get('sfx',[]):
                if e['sound'] not in sounds or not 0<=e['start']<self.duration(name) or not 0<=e.get('gain',1)<=2:raise ValueError('Invalid SFX event')
        return issues

    def build(self):
        # Local component fields are already in the base receipt; include ALL added code,
        # fonts, settings and source bytes. A new framing or event can never reuse stale media.
        resources=[Path(__file__),SKILL/'scripts/editorial_scenes.py',SKILL/'scripts/sound_design.py']+[p for p in LIB.rglob('*') if p.is_file()]
        resources += [self.path(a['file']) for a in self.assets.values()]
        resources += [self.path(s['file']) for s in self.data.get('editorial',{}).get('sounds',{}).values()]
        for c in self.components.values():
            for s in c.get('scenes',[]):
                if s['type']=='chronology':resources += [self.path(e['document']['href']) for e in s['events']]
        self.style['editorial_receipt']={'config':self.data.get('editorial',{}),'resources':{str(f):digest(f) for f in resources}}
        built=super().build()
        for name,item in built.items():
            folder=Path(item['folder']);assets=folder/'assets';p=folder/'index.html';doc=p.read_text();c=self.components[name];f=c.get('framing',{});z=f.get('scale',1);ox,oy=f.get('origin',[.5,.5])
            for font in (LIB/'fonts').iterdir():shutil.copy2(font,assets/font.name)
            shutil.copy2(LIB/'demo_runtime.js',assets/'demo_runtime.js')
            css=(LIB/'style.css').read_text()
            palette=self.data.get('editorial',{}).get('palette',{})
            if palette:css+=':root{'+''.join(f'--{k}:{v};' for k,v in palette.items())+'}'
            elements=[];actions=[f'tl.set("#speaker",{{scale:{z},transformOrigin:"{ox*100}% {oy*100}%"}},0);'];manifest=[]
            for i,original in enumerate(c.get('scenes',[])):
                s=copy.deepcopy(original);kind=s['type'];identifier=f'ev{i}';selector='#'+identifier;r=self.scene_rect(s);full=r==[0,0,1080,1920];url=None
                if kind in ('image','evidence'):
                    source=self.path(self.assets[s['asset']]['file']);filename='ev-'+s['asset']+source.suffix.lower()
                    if kind=='image' and source.suffix.lower() in ('.jpg','.jpeg'):
                        with Image.open(source) as im:
                            im.thumbnail((2400,2400),Image.Resampling.LANCZOS);im.convert('RGB').save(assets/filename,quality=97)
                    else:shutil.copy2(source,assets/filename)
                    url='assets/'+filename
                if kind=='chronology':
                    for j,e in enumerate(s['events']):
                        source=self.path(e['document']['href']);filename=f'doc-{i}-{j}'+source.suffix;shutil.copy2(source,assets/filename);e['document']['href']='assets/'+filename
                content,motion=scene(s,selector,url)
                classes='ev-scene clip'+(' ev-full' if full else '')+(' ev-demo' if kind in DEMOS else '')+(' ev-dark' if s.get('on_dark') else '')
                rect_css=f'left:{r[0]}px;top:{r[1]}px;width:{r[2]-r[0]}px;height:{r[3]-r[1]}px;'
                if s.get('on_dark'):rect_css+='color:#fff;text-shadow:0 2px 4px #000;'
                elements.append(f'<div id="{identifier}" class="{classes}" style="{rect_css}" data-start="{s["start"]}" data-duration="{s["end"]-s["start"]}" data-track-index="10">{content}</div>')
                actions += [f'tl.set({js(selector)},{{opacity:1,pointerEvents:"auto"}},{s["start"]});',f'tl.set({js(selector)},{{opacity:0,pointerEvents:"none"}},{s["end"]});']+motion
                if kind in DEMOS:
                    x1,y1,x2,y2=c.get('demo_crop',[90,440,990,1470]);scale=min(382/(x2-x1),432/(y2-y1));x=578-x1*scale;y=1015-y1*scale
                    actions += [f'tl.set("#speaker",{{transformOrigin:"0 0",x:{x},y:{y-c.get("shift_y",0)},scale:{scale},clipPath:"inset({y1}px {1080-x2}px {1920-y2}px {x1}px round 24px)",zIndex:22}},{s["start"]});',f'tl.set("#speaker",{{transformOrigin:"{ox*100}% {oy*100}%",x:0,y:0,scale:{z},clipPath:"none",zIndex:0}},{s["end"]});']
                manifest.append(dict(original,rectangle=r))
            highlights=c.get('caption_highlights',[])
            if highlights:
                pattern=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(html.escape(word)) for word in sorted(highlights,key=len,reverse=True))+r')(?!\w)',re.I)
                doc=re.sub(r'(<div class="line">)(.*?)(</div>)',lambda m:m[1]+pattern.sub(lambda match:'<span class="ev-highlight">'+match[0]+'</span>',m[2])+m[3],doc,flags=re.S)
            doc=doc.replace('</style>',css+'</style><script src="assets/demo_runtime.js"></script>').replace('</div><script>',''.join(elements)+'</div><script>').replace('window.__timelines.main=tl;',''.join(actions)+'window.__timelines.main=tl;')
            p.write_text(doc);write(folder/'editorial_timeline.json',manifest)
        return built

    def assemble(self,built):
        if self.data.get('music') and any(c.get('music_duck') for c in self.components.values()):
            original_music=copy.deepcopy(self.data['music']);original_variants=self.variants;entries=[]
            try:
                for v in original_variants:
                    offset=0;factors=[]
                    for name in v['components']:
                        for d in self.components[name].get('music_duck',[]):factors.append(f"if(between(t,{offset+d['start']},{offset+d['end']}),{d['gain']},1)")
                        offset+=self.duration(name)
                    bed=self.out/'audio'/f"music-{v['id']}.wav";bed.parent.mkdir(parents=True,exist_ok=True)
                    expr='*'.join(factors) or '1'
                    run(['ffmpeg','-y','-v','error','-stream_loop','-1','-i',self.path(original_music['file']),'-af',f"volume='{expr}':eval=frame",'-t',offset,'-ar','48000','-ac','2',bed])
                    self.data['music']=dict(original_music,file=str(bed));self.variants=[v];super().assemble(built);entries+=json.loads((self.out/'delivery.json').read_text())
            finally:self.data['music']=original_music;self.variants=original_variants
            write(self.out/'delivery.json',entries)
        else:super().assemble(built)
        if not any(c.get('sfx') for c in self.components.values()):return
        stems={n:make_stem(self,n) for n in self.components}
        entries=json.loads((self.out/'delivery.json').read_text())
        for e in entries:
            path=Path(e['file']);tmp=path.with_name(path.stem+'.sound.tmp.mp4');args=['ffmpeg','-y','-v','error','-i',path]
            for n in e['components']:args+=['-i',stems[n]]
            graph=''.join(f'[{i}:a]' for i in range(1,len(e['components'])+1))+f'concat=n={len(e["components"])}:v=0:a=1[fx];[0:a][fx]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.891:level=false:latency=true,aresample=48000,apad,atrim=end_sample={round(e["duration"]*48000)}[mix]'
            run(args+['-filter_complex',graph,'-map','0:v:0','-map','[mix]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t',e['duration'],'-movflags','+faststart',tmp]);tmp.replace(path);e['sha256']=digest(path)
        write(self.out/'delivery.json',entries)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['validate','masters','build','render','verify']);parser.add_argument('project');a=parser.parse_args();p=EditorialProject(a.project);result=getattr(p,a.command)()
    if result is not None:print(json.dumps(result,ensure_ascii=False,indent=2))
