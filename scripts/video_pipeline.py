#!/usr/bin/env python3
"""Data-driven local video pipeline. No topic-specific timing or source paths.

Usage: python3 video_pipeline.py {validate,masters,build,render,verify} project.json
Inputs stay read-only. Derived files live under the manifest's output directory.
Requires Python 3.9+, Pillow, ffmpeg/ffprobe and npx HyperFrames 0.8.33.
"""
import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from PIL import Image, ImageFont

SKILL = Path(__file__).resolve().parents[1]


def run(args, log=None):
    result = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if log:
        Path(log).write_text(result.stdout+'\n'+result.stderr)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed: {result.stderr[-4000:]} {result.stdout[-1000:]}')
    return result.stdout


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2)+'\n' if not isinstance(value, str) else value
    temp = path.with_name(path.name+'.tmp')
    temp.write_text(text, encoding='utf-8')
    temp.replace(path)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path]))


def stream(info, kind):
    return next(s for s in info['streams'] if s['codec_type'] == kind)


def merge(base, overrides):
    out = dict(base)
    for k, v in overrides.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def stamp(t):
    n = round(t*1000)
    return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'


class Project:
    def __init__(self, manifest):
        self.manifest = Path(manifest).resolve()
        self.root = self.manifest.parent
        self.data = json.loads(self.manifest.read_text())
        if self.data.get('schema_version') != 2:
            raise ValueError('Expected schema_version 2')
        self.style = merge(json.loads((SKILL/'assets/style.json').read_text()), self.data.get('style', {}))
        self.out = self.path(self.data.get('output', 'build'))
        if self.out == self.root or self.out in self.root.parents:
            raise ValueError('Output must be a separate build directory, not the input directory or its parent')
        self.fps = self.style['fps']
        self.font_path = SKILL/'assets/ArialBold.ttf'
        self.font = ImageFont.truetype(str(self.font_path), self.style['caption']['font_size'])
        self.components = self.data['components']
        self.assets = self.data.get('assets', {})
        self.variants = self.data['variants']
        self.hashes = {}
        self.validate_names()

    def path(self, value):
        return (self.root/value).resolve()

    def file_hash(self, path):
        key = str(path)
        if key not in self.hashes:
            self.hashes[key] = digest(path)
        return self.hashes[key]

    def validate_names(self):
        ids = list(self.components)+list(self.assets)+[v['id'] for v in self.variants]
        if any(not re.fullmatch(r'[a-zA-Z0-9_-]+', x) for x in ids):
            raise ValueError('IDs must contain letters, digits, hyphens or underscores')
        if len({v['id'] for v in self.variants}) != len(self.variants) or not self.variants:
            raise ValueError('Variant IDs must be unique and at least one variant is required')
        for v in self.variants:
            if not v['components'] or any(c not in self.components for c in v['components']):
                raise ValueError('Variant references an unknown component')
        if self.style['speaker']['zoom'] != 1:
            raise ValueError('This profile preserves camera scale; zoom must be 1')
        if (self.style['width'], self.style['height'], self.fps) != (1080,1920,30):
            raise ValueError('This renderer is validated for 1080x1920/30 only; create a separate profile for other formats')

    def master_path(self, name):
        c = self.components[name]
        return self.path(c['master']) if c.get('master') else self.out/'masters'/f'{name}.mp4'

    def duration(self, name):
        frames = self.components[name]['frames']
        if type(frames) is not int or frames <= 0:
            raise ValueError(f'{name}: frames must be a positive integer')
        return frames/self.fps

    def width(self, text):
        return self.font.getlength(text)+self.style['caption']['letter_spacing']*len(text)

    def wrap(self, text):
        limit = self.style['caption']['width']-10
        if self.width(text) <= limit:
            return text
        tokens = text.split()
        choices = []
        for i in range(1,len(tokens)):
            a,b = ' '.join(tokens[:i]),' '.join(tokens[i:])
            if max(self.width(a),self.width(b)) <= limit:
                penalty = abs(self.width(a)-self.width(b))+(200 if len(tokens[i:])==1 and len(tokens[-1])<4 else 0)
                choices.append((penalty,a+'\n'+b))
        if not choices:
            raise ValueError(f'Caption cannot fit two lines: {text!r}; split the cue using actual word times')
        return min(choices)[1]

    def captions(self, name):
        cues = json.loads(self.path(self.components[name]['captions']).read_text())
        previous = 0
        if not isinstance(cues,list) or not cues:
            raise ValueError(f'{name}: captions must be a nonempty cue list')
        for cue in cues:
            a,b = cue['start'],cue['end']
            if not 0 <= a < b <= self.duration(name)+0.001 or a < previous-0.001:
                raise ValueError(f'{name}: invalid or overlapping caption times')
            text = cue['text'].strip()
            if not text:
                raise ValueError('Empty caption')
            displayed = cue.get('display_text') or self.wrap(text)
            if displayed.split() != text.split():
                raise ValueError('Display text must contain exactly the spoken cue words')
            lines = displayed.split('\n')
            if len(lines)>2 or any(self.width(line)>self.style['caption']['width'] for line in lines):
                raise ValueError(f'{name}: caption exceeds layout bounds')
            cue['display_text'] = displayed
            previous = b
        return cues

    def events(self, name):
        c = self.components[name]
        style = self.style['evidence']
        result, previous = [], 0
        face = c.get('face_bounds')
        shift = c.get('shift_y',0)
        if not -500 <= shift <= 0:
            raise ValueError('shift_y must be between -500 and 0; positive values need a different framing profile')
        if face:
            if len(face)!=4 or not (0<=face[0]<face[2]<=1080 and 0<=face[1]<face[3]<=1920):
                raise ValueError('Invalid face_bounds measured on the unshifted 1080x1920 frame')
            if face[3]+shift+style['face_gap']>self.style['caption']['top']:
                raise ValueError(f'{name}: captions overlap the measured beard/face envelope')
        for original in c.get('evidence',[]):
            event = dict(original)
            if event['asset'] not in self.assets:
                raise ValueError(f'{name}: missing evidence asset')
            if not 0<=event['start']<event['end']<=self.duration(name)+0.001 or event['start']<previous-0.001:
                raise ValueError(f'{name}: invalid or overlapping evidence intervals')
            a = self.assets[event['asset']]
            for field in ('source_url','source_name','kind'):
                if not a.get(field): raise ValueError(f'Evidence missing {field}')
            if a['kind'] not in ('screenshot','photo','diagram'):
                raise ValueError('Unsupported evidence kind; synthesized news cards are not an evidence source')
            for field in ('claim','relation'):
                if not event.get(field):raise ValueError(f'{name}: evidence event missing {field}')
            path = self.path(a['file'])
            with Image.open(path) as im:w,h=im.size
            limit = style['close_max_height'] if c.get('close') else style['max_height']
            scale = min(style['max_width']/w,limit/h)
            ow,oh = round(w*scale),round(h*scale)
            top = style['top_margin']+limit-oh
            if face and top+oh+style['face_gap']>face[1]+shift:
                raise ValueError(f'{name}: evidence overlaps the measured hair/face envelope')
            if a.get('text_height_px') and a['text_height_px']*scale<24:
                raise ValueError(f'{name}: selected paragraph is too small after scaling; use a more focused crop')
            event.update(width=ow,height=oh,top=top,file=str(path),source_url=a['source_url'])
            result.append(event);previous=event['end']
        return result

    def validate(self, media=True):
        issues = []
        for name,c in self.components.items():
            self.duration(name);self.captions(name);self.events(name)
            inputs=[self.path(c['captions'])]+[self.path(a['file']) for a in self.assets.values()]
            if c.get('master'):inputs.append(self.path(c['master']))
            if any(self.out==f or self.out in f.parents for f in inputs):
                raise ValueError('Declared inputs cannot live in the output directory')
            if media:
                info=probe(self.master_path(name));v=stream(info,'video');a=stream(info,'audio')
                if (v['width'],v['height'])!=(1080,1920) or Fraction(v['avg_frame_rate'])!=30:
                    raise ValueError(f'{name}: master must be 1080x1920/30 without added zoom')
                if abs(float(v['duration'])-self.duration(name))>.034 or abs(float(a['duration'])-self.duration(name))>.04:
                    raise ValueError(f'{name}: master duration does not match planned frames')
                if int(a['sample_rate'])!=48000 or int(a['channels'])!=2:
                    raise ValueError('Master audio must be stereo 48kHz')
            if not c.get('face_bounds'):
                issues.append(f'{name}: face envelope not measured; manual framing review required')
        return issues

    def masters(self):
        self.out.mkdir(parents=True,exist_ok=True)
        for name,c in self.components.items():
            if c.get('master'):continue
            cuts=c.get('cuts',[])
            if not cuts:raise ValueError(f'{name}: provide master or cuts')
            parts=[];total=0
            for cut in cuts:
                source=self.path(self.data['sources'][cut['source']]);info=probe(source)
                a,b=cut['in'],cut['out'];frames=round((b-a)*self.fps);d=frames/self.fps
                if not 0<=a<b<=float(info['format']['duration']) or frames<1 or not cut.get('reason'):
                    raise ValueError('Cut requires valid input times and an editorial reason')
                v=stream(info,'video')
                if abs(v['width']/v['height']-9/16)>.001:
                    raise ValueError('Source is not 9:16; an explicit reframing decision is needed')
                key=hashlib.sha256(json.dumps([self.file_hash(source),cut,self.style,self.file_hash(__file__)]).encode()).hexdigest()[:20]
                part=self.out/'cuts'/f'{key}.mov';part.parent.mkdir(exist_ok=True)
                if not part.exists():
                    temp=part.with_name(key+'.tmp.mov')
                    run(['ffmpeg','-y','-v','error','-ss',a,'-i',source,'-map','0:v:0','-map','0:a:0','-vf','setpts=PTS-STARTPTS,scale=1080:1920,setsar=1,fps=30,format=yuv420p','-af',f'asetpts=PTS-STARTPTS,aresample=48000,highpass=f=65,afade=t=in:d=0.006,afade=t=out:st={max(0,d-.008)}:d=0.008,apad,atrim=duration={d}','-t',d,'-frames:v',frames,'-c:v','libx264','-preset','fast','-crf','18','-c:a','pcm_s16le','-ar','48000','-ac','2',temp]);temp.replace(part)
                parts.append(part);total+=frames
            if total!=c['frames']:raise ValueError(f'{name}: sum of cuts differs from component frames')
            listing=self.out/'cuts'/f'{name}.ffconcat'
            write(listing,'ffconcat version 1.0\n'+''.join(f"file '{p.name}'\n" for p in parts))
            dest=self.master_path(name);dest.parent.mkdir(exist_ok=True);temp=dest.with_suffix('.tmp.mp4')
            audio=self.style['audio']
            run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',listing,'-c:v','copy','-af',f"loudnorm=I={audio['lufs']}:TP={audio['true_peak']}:LRA=9,aresample=48000,apad",'-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t',self.duration(name),'-movflags','+faststart',temp]);temp.replace(dest)
            print('MASTER',name,flush=True)

    def build(self):
        warnings=self.validate();built={}
        for name,c in self.components.items():
            master=self.master_path(name);cues=self.captions(name);events=self.events(name)
            resources=[master,self.font_path,SKILL/'assets/gsap.min.js',SKILL/'assets/composition.css',Path(__file__)]+[Path(e['file']) for e in events]
            receipt={'component':c,'style':self.style,'captions':cues,'events':events,'resources':{str(f):self.file_hash(f) for f in resources}}
            key=hashlib.sha256(json.dumps(receipt,sort_keys=True).encode()).hexdigest()
            folder=self.out/'compositions'/name/key[:20];assets=folder/'assets';assets.mkdir(parents=True,exist_ok=True)
            for source,dest in [(master,'speaker.mp4'),(self.font_path,'ArialBold.ttf'),(SKILL/'assets/gsap.min.js','gsap.min.js')]:
                shutil.copyfile(source,assets/dest)
            elements=[];actions=[]
            def visible(identifier,start,end):
                actions.extend([f'tl.set("#{identifier}",{{opacity:1}},{start:.6f});',f'tl.set("#{identifier}",{{opacity:0}},{end:.6f});'])
            for i,cue in enumerate(cues):
                a,b=cue['start'],cue['end'];visible('cap'+str(i),a,b)
                elements.append(f'<div id="cap{i}" class="caption clip" data-start="{a:.6f}" data-duration="{b-a:.6f}" data-track-index="20"><div class="line">{html.escape(cue["display_text"])}</div></div>')
            for i,e in enumerate(events):
                dest=e['asset']+Path(e['file']).suffix.lower();shutil.copyfile(e['file'],assets/dest);a,b=e['start'],e['end'];visible('art'+str(i),a,b)
                elements.append(f'<img id="art{i}" class="evidence clip" src="assets/{dest}" alt="" style="top:{e["top"]}px;width:{e["width"]}px;height:{e["height"]}px" data-start="{a:.6f}" data-duration="{b-a:.6f}" data-track-index="30">')
            cap=self.style['caption']
            css=(SKILL/'assets/composition.css').read_text()
            for k,v in cap.items():css=css.replace('{{'+k+'}}',str(v))
            css=css.replace('{{shift_y}}',str(c.get('shift_y',0))).replace('{{mask_start}}',str(self.style['speaker']['mask_start_percent']))
            d=self.duration(name)
            doc=f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{name}</title><script src="assets/gsap.min.js"></script><style>{css}</style></head><body><div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-duration="{d:.9f}" data-fps="30"><video id="speaker" class="clip" src="assets/speaker.mp4" data-start="0" data-duration="{d:.9f}" data-track-index="0" muted playsinline></video><audio id="speech" src="assets/speaker.mp4" data-start="0" data-duration="{d:.9f}" data-track-index="10" data-volume="1"></audio>{"".join(elements)}</div><script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});{"".join(actions)}window.__timelines.main=tl;</script></body></html>'
            write(folder/'index.html',doc);write(folder/'receipt.json',receipt)
            write(folder/'captions.json',cues);write(folder/'evidence_timeline.json',events)
            built[name]={'folder':str(folder),'fingerprint':key,'frames':c['frames']}
        write(self.out/'build.json',{'components':built,'warnings':warnings})
        return built

    def render(self):
        self.masters();built=self.build()
        for name,item in built.items():
            folder=Path(item['folder']);dest=folder/'render.mp4';ok=folder/'render.ok.json'
            reuse=dest.exists() and ok.exists() and json.loads(ok.read_text()).get('sha256')==digest(dest)
            if not reuse:
                temp=folder/'render.tmp.mp4'
                run(['npx','--yes',f'hyperframes@{self.style["hyperframes_version"]}','render',folder,'--output',temp,'--fps','30','--quality','high','--workers','2','--gpu','--sdr','--strict','--video-bitrate',self.style['video_bitrate']],folder/'render.log')
                v=stream(probe(temp),'video')
                if int(v.get('nb_frames',0))!=item['frames']:raise ValueError('Rendered frame count differs from plan')
                temp.replace(dest);write(ok,{'sha256':digest(dest),'fingerprint':item['fingerprint']})
            print('RENDER',name,flush=True)
        self.assemble(built)

    def assemble(self,built):
        exports=self.out/'versions';exports.mkdir(exist_ok=True);entries=[]
        for variant in self.variants:
            name=variant['id'];sequence=variant['components'];d=sum(self.duration(n) for n in sequence)
            # Use relative names in concat lists, so source paths with apostrophes are safe.
            stage=self.out/'assembly'/name;stage.mkdir(parents=True,exist_ok=True)
            for i,n in enumerate(sequence):shutil.copyfile(Path(built[n]['folder'])/'render.mp4',stage/f'{i}.mp4')
            listing=stage/'input.ffconcat';write(listing,'ffconcat version 1.0\n'+''.join(f"file '{i}.mp4'\nduration {self.duration(n):.9f}\n" for i,n in enumerate(sequence)))
            args=['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',listing];filters=[]
            for i,n in enumerate(sequence,1):
                args+=['-i',self.master_path(n)];cd=self.duration(n)
                filters.append(f'[{i}:a]atrim=0:{cd:.9f},asetpts=PTS-STARTPTS,aresample=48000:async=1:first_pts=0:min_hard_comp=0.001,apad=whole_len={round(cd*48000)},atrim=end_sample={round(cd*48000)},asetpts=N/SR/TB[a{i}]')
            filters.append(''.join(f'[a{i}]' for i in range(1,len(sequence)+1))+f'concat=n={len(sequence)}:v=0:a=1[voice]')
            music=self.data.get('music');mix='voice'
            if music:
                args+=['-stream_loop','-1','-i',self.path(music['file'])];idx=len(sequence)+1
                filters.append(f'[{idx}:a]atrim=0:{d:.9f},asetpts=PTS-STARTPTS,volume={float(music["gain"])},afade=t=in:d=0.2,afade=t=out:st={max(0,d-.6):.9f}:d=0.6[bed]')
                filters.append('[voice][bed]amix=inputs=2:duration=first:normalize=0[musicmix]');mix='musicmix'
            filters.append(f'[{mix}]alimiter=limit=0.891:level=false:latency=true,aresample=48000,apad=whole_len={round(d*48000)},atrim=end_sample={round(d*48000)},asetpts=N/SR/TB[final]')
            dest=exports/f'{name}.mp4';temp=exports/f'{name}.tmp.mp4'
            args+=['-filter_complex',';'.join(filters),'-map','0:v:0','-map','[final]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t',f'{d:.9f}','-movflags','+faststart',temp]
            run(args,stage/'assembly.log');temp.replace(dest)
            cues=[];offset=0
            for n in sequence:
                for cue in self.captions(n):
                    joined=dict(cue,start=cue['start']+offset,end=cue['end']+offset)
                    if cue.get('words'):
                        joined['words']=[dict(w,start=w['start']+offset,end=w['end']+offset) for w in cue['words']]
                    cues.append(joined)
                offset+=self.duration(n)
            write(exports/f'{name}.srt','\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["display_text"]}' for i,c in enumerate(cues))+'\n')
            write(exports/f'{name}.captions.json',cues)
            entries.append(dict(variant,frames=round(d*30),duration=d,file=str(dest),sha256=digest(dest),
                                captions_sha256=digest(exports/f'{name}.captions.json'),srt_sha256=digest(exports/f'{name}.srt')))
        write(self.out/'delivery.json',entries)

    def verify(self):
        entries=json.loads((self.out/'delivery.json').read_text());report=[]
        for e in entries:
            path=Path(e['file']);info=probe(path);v=stream(info,'video');a=stream(info,'audio');issues=[]
            if (v['width'],v['height'],v['codec_name'],v['pix_fmt'])!=(1080,1920,'h264','yuv420p') or Fraction(v['avg_frame_rate'])!=30:issues.append('video format')
            if int(v.get('nb_frames',0))!=e['frames'] or abs(float(v['duration'])-e['duration'])>.0011:issues.append('frame count/duration')
            if (a['codec_name'],int(a['sample_rate']),int(a['channels']))!=('aac',48000,2):issues.append('audio format')
            if abs(float(a['duration'])-e['duration'])>.002 or abs(float(v.get('start_time',0))-float(a.get('start_time',0)))>1/30:issues.append('audio/video timing')
            decoded=subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(path),'-map','0:v:0','-map','0:a:0','-progress','pipe:1','-nostats','-f','null','-'],capture_output=True,text=True)
            write(self.out/f'{e["id"]}_decode.log',decoded.stdout+'\n'+decoded.stderr)
            if decoded.returncode or decoded.stderr.strip():issues.append('decode error')
            count=re.findall(r'^frame=(\d+)\s*$',decoded.stdout,re.M)
            if not count or int(count[-1])!=e['frames']:issues.append('decoded frames')
            if digest(path)!=e['sha256']:issues.append('export changed')
            for suffix,key in [('captions.json','captions_sha256'),('srt','srt_sha256')]:
                if digest(path.with_suffix('.'+suffix))!=e.get(key):issues.append('subtitle sidecar changed after render')
            report.append({'id':e['id'],'ok':not issues,'issues':issues,'frames':e['frames']})
        write(self.out/'technical_qa.json',report)
        if any(not r['ok'] for r in report):raise ValueError('Technical QA failed; see technical_qa.json')
        return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['validate','masters','build','render','verify'])
    parser.add_argument('manifest')
    args=parser.parse_args();p=Project(args.manifest)
    print(getattr(p,args.command)())
