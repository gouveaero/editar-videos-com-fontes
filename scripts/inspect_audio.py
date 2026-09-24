#!/usr/bin/env python3
"""Create local listening/spectral evidence. Does NOT label breaths automatically."""
import argparse
from pathlib import Path
from video_pipeline import run, write, digest


def inspect(source,output,start=0,duration=3):
    source=Path(source).resolve();output=Path(output).resolve()
    if output.exists():raise ValueError('Choose a new inspection folder')
    if start<0 or duration<=0:raise ValueError('Invalid inspection interval')
    output.mkdir(parents=True)
    wav=output/'listen.wav';run(['ffmpeg','-y','-v','error','-ss',start,'-i',source,'-t',duration,'-vn','-ar','16000','-ac','1',wav])
    run(['ffmpeg','-y','-v','error','-i',wav,'-lavfi','showspectrumpic=s=1500x600:legend=1:scale=log:fscale=log',output/'spectrum.png'])
    run(['ffmpeg','-y','-v','error','-i',wav,'-lavfi','showwavespic=s=1500x300:colors=0x275c48',output/'waveform.png'])
    write(output/'inspection.json',{'source':str(source),'sha256':digest(source),'source_start':start,'duration':duration,'decision':None,'note':'Listen and inspect before selecting a cut. ASR word starts, amplitude thresholds and harmonic onset alone do not prove the first consonant is preserved.'})
    return output


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('--output',required=True);p.add_argument('--start',type=float,default=0);p.add_argument('--duration',type=float,default=3);a=p.parse_args();print(inspect(a.source,a.output,a.start,a.duration))
