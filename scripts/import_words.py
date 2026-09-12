#!/usr/bin/env python3
"""Import a word-timed transcription of a component's own edited audio.

python3 import_words.py project.json component whisper.json
Accepts Whisper segments[].words[] or a top-level words[] list. Does not run ASR.
"""
import argparse
import json
import re
from pathlib import Path
from video_pipeline import Project, write, digest


def convert(project, name, transcript):
    p=Project(project);dest=p.path(p.components[name]['captions'])
    if dest.exists():raise ValueError('Caption file exists; choose a new caption path to preserve reviewed cues')
    raw=json.loads(Path(transcript).read_text())
    words=raw.get('words')
    if words is None:words=[w for s in raw['segments'] for w in s.get('words',[])]
    words=[dict(w,word=w['word'].strip()) for w in words if w.get('word','').strip()]
    if not words:raise ValueError('No word timestamps; use ASR with word timestamps on the edited component audio')
    previous=0;groups=[];current=[];style=p.style['caption'];duration=p.duration(name)
    for w in words:
        if not 0<=w['start']<w['end']<=duration+.04 or w['start']<previous-.025:
            raise ValueError('Invalid word times or transcript from a different audio duration')
        combined=' '.join(x['word'] for x in current+[w])
        if current and (len(current)>=style['max_words'] or len(combined)>style['max_chars'] or w['start']-current[-1]['end']>.32):
            groups.append(current);current=[]
        current.append(w);previous=w['end']
        if re.search(r'[.!?;]$',w['word']):groups.append(current);current=[]
    if current:groups.append(current)
    cues=[]
    for i,g in enumerate(groups):
        a=max(0,g[0]['start']-style['lead']);b=min(duration,g[-1]['end']+style['tail'])
        if i+1<len(groups):b=min(b,groups[i+1][0]['start']-style['lead'])
        if b<=a:raise ValueError('Word grouping created an empty interval; review transcript')
        text=' '.join(w['word'] for w in g)
        cues.append({'start':a,'end':b,'text':text,'display_text':p.wrap(text),'words':g})
    write(dest,cues)
    write(dest.with_suffix('.import.json'),{'source':str(Path(transcript).resolve()),'sha256':digest(transcript),'component':name,'review_required':'Compare proper names, numbers and all spoken words with this component audio.'})
    return dest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project');parser.add_argument('component');parser.add_argument('transcript')
    a=parser.parse_args();print(convert(a.project,a.component,a.transcript))
