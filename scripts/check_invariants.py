#!/usr/bin/env python3
"""Exercise failure behavior and caption import without touching real exports."""
import copy
import json
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw
from video_pipeline import Project, SKILL, write
from import_words import convert
from prepare_evidence import prepare


def main():
    b=SKILL/'assets/benchmark';base=json.loads((b/'project.json').read_text())
    for c in base['components'].values():
        c['master']=str(b/c['master']);c['captions']=str(b/c['captions'])
    for a in base['assets'].values():a['file']=str(b/a['file'])
    passed=[]
    with tempfile.TemporaryDirectory(prefix='video-skill-tests-') as folder:
        root=Path(folder);manifest=root/'project.json';write(manifest,base)
        p=Project(manifest);p.validate();passed.append('approved inputs accepted')
        cases={
            'automatic zoom rejected':lambda x:x.update(style={'speaker':{'zoom':1.025}}),
            'unknown variant component rejected':lambda x:x['variants'][0].update(components=['missing']),
            'caption touching beard rejected':lambda x:x['components']['01_principal'].update(face_bounds=[100,700,900,1700]),
            'evidence touching hair rejected':lambda x:x['components']['01_principal'].update(face_bounds=[100,580,900,1400]),
            'missing provenance rejected':lambda x:x['assets']['quanta_manchete'].pop('source_url'),
            'unreadable screenshot rejected':lambda x:x['assets']['quanta_manchete'].update(text_height_px=1),
        }
        for label,change in cases.items():
            changed=copy.deepcopy(base);change(changed);write(manifest,changed)
            try:Project(manifest).validate()
            except (ValueError,KeyError):passed.append(label)
            else:raise AssertionError(label)
        changed=copy.deepcopy(base);changed['components']['01_principal']['captions']='invalid.json'
        bad=[{'start':0,'end':1,'text':'Uma frase.'},{'start':0.8,'end':2,'text':'Outra frase.'}]
        write(root/'invalid.json',bad);write(manifest,changed)
        try:Project(manifest).validate()
        except ValueError:passed.append('overlapping subtitles rejected')
        else:raise AssertionError('overlapping subtitles accepted')
        bad=[{'start':0,'end':1,'text':'Uma frase.','display_text':'Uma frase inventada.'}];write(root/'invalid.json',bad)
        try:Project(manifest).validate()
        except ValueError:passed.append('invented display words rejected')
        else:raise AssertionError('display words changed')
        changed=copy.deepcopy(base);changed['components']['01_principal']['captions']='imported.json';write(manifest,changed)
        words={'segments':[{'words':[{'word':'Uma','start':0.1,'end':0.4},{'word':'frase.','start':0.45,'end':0.9}]}]}
        write(root/'words.json',words);dest=convert(manifest,'01_principal',root/'words.json')
        cues=json.loads(dest.read_text());assert cues[0]['text']=='Uma frase.' and abs(cues[0]['start']-.075)<.001
        passed.append('real word times retained during import')
        try:convert(manifest,'01_principal',root/'words.json')
        except ValueError:passed.append('reviewed captions not overwritten')
        else:raise AssertionError('captions overwritten')
        write(manifest,base);p=Project(manifest);a=p.build()['01_principal']['fingerprint']
        changed=copy.deepcopy(base);changed['components']['01_principal']['shift_y']=-81;write(manifest,changed)
        z=Project(manifest).build()['01_principal']['fingerprint'];assert a!=z
        passed.append('framing change invalidates render cache')
        picture=Image.new('RGB',(200,100),'white');ImageDraw.Draw(picture).rectangle((40,40,55,45),fill='black');picture.save(root/'source.png')
        original=(root/'source.png').read_bytes()
        evidence={'screenshot':'source.png','output':'marked.png','source_url':'https://example.org/fixture','source_name':'Synthetic fixture','claim':'test','excerpt':'test','relation':'test','crop':[20,20,180,80],'highlights':[[30,35,100,50]]}
        write(root/'evidence.json',evidence);prepare(root/'evidence.json');marked=Image.open(root/'marked.png')
        assert marked.size==(160,60) and marked.getpixel((25,22))==(0,0,0)
        assert marked.getpixel((100,40))==(255,255,255) and marked.getpixel((15,18))!=(255,255,255)
        assert (root/'source.png').read_bytes()==original
        passed.append('highlight preserves original, glyphs and unselected pixels')
        try:prepare(root/'evidence.json')
        except ValueError:passed.append('evidence output not overwritten')
        else:raise AssertionError('evidence overwritten')
        evidence['output']='invalid-crop.png';evidence['highlights']=[[0,0,40,40]];write(root/'evidence.json',evidence)
        try:prepare(root/'evidence.json')
        except ValueError:passed.append('highlight outside crop rejected')
        else:raise AssertionError('highlight outside crop accepted')
    print(json.dumps({'ok':True,'checks':passed},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
