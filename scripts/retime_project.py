#!/usr/bin/env python3
"""Trim/speed existing edited masters into a NEW revision, with one timing map.
No ASR, breath detection or automatic authorization is implied by this helper.
"""
import argparse
import copy
import json
from pathlib import Path
from video_pipeline import Project, run, write, digest


def atempo(speed):
    stages=[]
    while speed>2:stages.append('atempo=2');speed/=2
    while speed<.5:stages.append('atempo=0.5');speed/=.5
    return ','.join(stages+[f'atempo={speed:.12g}'])


def transform_component(component,cues,head_frames=0,tail_frames=0,speed=1,boundary_note=None):
    c=copy.deepcopy(component);original_frames=c['frames'];a=head_frames/30;b=(original_frames-tail_frames)/30
    if type(head_frames)!=int or type(tail_frames)!=int or min(head_frames,tail_frames)<0 or not a<b or not .25<=speed<=4:raise ValueError('Invalid frame cut or speed')
    frames=round((original_frames-head_frames-tail_frames)/speed);duration=frames/30
    if frames<1:raise ValueError('Retime removes the whole component')
    def mapped(t):return min(duration,max(0,(t-a)/speed))
    new=[]
    for cue in copy.deepcopy(cues):
        if cue['end']<=a or cue['start']>=b:raise ValueError('Cut would discard spoken cue; choose the edit manually')
        for w in cue.get('words',[]):
            if (w['start']<a<w['end'] or w['start']<b<w['end'] or w['end']<=a or w['start']>=b) and not boundary_note:raise ValueError('Cut intersects ASR word; inspect actual audio and supply --boundary-note only if timing is wrong')
            w['start']=mapped(w['start']);w['end']=mapped(w['end'])
            if w['end']<=w['start']:raise ValueError('A word would disappear; revise the transcript from the actual audio')
        cue['start']=mapped(cue['start']);cue['end']=mapped(cue['end']);new.append(cue)
    for field in ('scenes','evidence','music_duck'):
        changed=[]
        for event in c.get(field,[]):
            if event['end']<=a or event['start']>=b:continue
            if field=='scenes' and (event['start']<a or event['end']>b):raise ValueError('Cut crosses an animation; split/review that scene explicitly')
            event['start']=mapped(event['start']);event['end']=mapped(event['end'])
            for states in ('states','events'):
                for state in event.get(states,[]):state['at']/=speed
            if event.get('physics'):
                phy=event['physics']
                if 'change_at' in phy:phy['change_at']/=speed
                phy['clock_rate']=phy.get('clock_rate',1)*speed
            changed.append(event)
        if field in c:c[field]=changed
    c['sfx']=[dict(e,start=mapped(e['start'])) for e in c.get('sfx',[]) if a<=e['start']<b]
    c['frames']=frames
    return c,new


def retime(manifest,output,components=None,head_frames=0,tail_frames=0,speed=1,reason='',boundary_note=None):
    p=Project(manifest);root=Path(output).resolve()
    if root.exists():raise ValueError('Revision folder already exists; preserve prior delivery')
    if not reason.strip():raise ValueError('Record the editorial reason')
    chosen=components or list(p.components)
    if set(chosen)-set(p.components):raise ValueError('Unknown component')
    if (head_frames or tail_frames) and len(chosen)!=1:raise ValueError('Measure each cut; trim one named component at a time')
    data=copy.deepcopy(p.data);data['output']='build';prepared={};records=[]
    # Validate every time transformation before creating output or transcoding anything.
    for name in chosen:prepared[name]=transform_component(data['components'][name],p.captions(name),head_frames,tail_frames,speed,boundary_note)
    for asset in data.get('assets',{}).values():asset['file']=str(p.path(asset['file']))
    for sound in data.get('editorial',{}).get('sounds',{}).values():sound['file']=str(p.path(sound['file']))
    if data.get('music'):data['music']['file']=str(p.path(data['music']['file']))
    root.mkdir(parents=True);(root/'masters').mkdir();(root/'captions').mkdir()
    for name,original in list(data['components'].items()):
        source=p.master_path(name)
        if name in chosen:
            c,cues=prepared[name];duration=c['frames']/30;dest=root/'masters'/f'{name}.mp4';stop=original['frames']-tail_frames;start=head_frames/30;end=stop/30
            # Video and audio use the identical frame-derived interval and speed map.
            vf=f'trim=start_frame={head_frames}:end_frame={stop},setpts=(PTS-STARTPTS)/{speed},fps=30,tpad=stop_mode=clone:stop_duration=0.1,trim=end_frame={c["frames"]},setsar=1'
            af=f'atrim=start_sample={round(start*48000)}:end_sample={round(end*48000)},asetpts=PTS-STARTPTS,{atempo(speed)},afade=t=in:d=0.008,afade=t=out:st={max(0,duration-.008)}:d=0.008,apad,atrim=end_sample={round(duration*48000)}'
            run(['ffmpeg','-y','-v','error','-i',source,'-vf',vf,'-af',af,'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t',duration,'-movflags','+faststart',dest])
            c.pop('cuts',None);c['master']=str(dest.relative_to(root));c['captions']=f'captions/{name}.json';write(root/c['captions'],cues);data['components'][name]=c
            records.append({'component':name,'source':str(source),'source_sha256':digest(source),'head_frames':head_frames,'tail_frames':tail_frames,'speed':speed,'new_frames':c['frames'],'reason':reason,'boundary_note':boundary_note,'time_map':'(old_seconds - head_frames / 30) / speed'})
        else:original['master']=str(source);original.pop('cuts',None);original['captions']=str(p.path(original['captions']))
        for s in data['components'][name].get('scenes',[]):
            if s['type']=='chronology':
                for event in s['events']:event['document']['href']=str(p.path(event['document']['href']))
    write(root/'project.json',data);write(root/'retime.json',records)
    return root/'project.json'


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('manifest');a.add_argument('--output',required=True);a.add_argument('--component',action='append');a.add_argument('--head-frames',type=int,default=0);a.add_argument('--tail-frames',type=int,default=0);a.add_argument('--speed',type=float,default=1);a.add_argument('--reason',required=True);a.add_argument('--boundary-note');v=a.parse_args();print(retime(v.manifest,v.output,v.component,v.head_frames,v.tail_frames,v.speed,v.reason,v.boundary_note))
