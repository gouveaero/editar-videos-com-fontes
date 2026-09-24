"""Local SFX stems with provenance. No synthesis or automatic sound selection."""
import json
import re
from pathlib import Path
from video_pipeline import run, write, digest


def make_stem(project, name):
    c=project.components[name];events=c.get('sfx',[]);duration=project.duration(name)
    directory=project.out/'audio';directory.mkdir(parents=True,exist_ok=True)
    sources=project.data.get('editorial',{}).get('sounds',{})
    receipt={'duration':duration,'events':events,'sounds':{e['sound']:dict(sources[e['sound']],sha256=digest(project.path(sources[e['sound']]['file']))) for e in events},'engine':digest(__file__)}
    key=__import__('hashlib').sha256(json.dumps(receipt,sort_keys=True).encode()).hexdigest()[:20]
    dest=directory/f'{name}-{key}.wav'
    if dest.exists():return dest
    args=['ffmpeg','-y','-v','error','-f','lavfi','-i',f'anullsrc=r=48000:cl=stereo:d={duration}'];filters=[];labels=['[0:a]']
    for i,event in enumerate(events,1):
        source=sources[event['sound']];start=source.get('trim_in',0);length=min(source.get('duration',.3),duration-event['start'])
        # Measure the selected fragment, not a different peak elsewhere in the source.
        measured=__import__('subprocess').run(['ffmpeg','-hide_banner','-ss',str(start),'-t',str(length),'-i',str(project.path(source['file'])),'-vn','-af','volumedetect','-f','null','-'],capture_output=True,text=True,check=True)
        m=re.search(r'max_volume: ([\-\d.]+) dB',measured.stderr)
        if not m:raise ValueError('Sound fragment is silent or could not be measured')
        gain=source.get('peak_dbfs',-27)-float(m[1]);delay=round(event['start']*48000);fade=min(.005,length/4)
        args+=['-ss',start,'-t',length,'-i',project.path(source['file'])]
        filters.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,volume={gain}dB,volume={event.get("gain",1)},afade=t=in:d={fade},afade=t=out:st={length-fade}:d={fade},adelay={delay}S:all=1[s{i}]');labels.append(f'[s{i}]')
    filters.append(''.join(labels)+f'amix=inputs={len(labels)}:normalize=0:duration=first,atrim=end_sample={round(duration*48000)}[out]')
    args+=['-filter_complex',';'.join(filters),'-map','[out]','-c:a','pcm_s24le',dest];run(args);write(dest.with_suffix('.json'),receipt)
    return dest
